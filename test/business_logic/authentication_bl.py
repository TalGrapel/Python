import jwt
import bcrypt
from fastapi import Request
from app import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
from .user_bl import UserBL
from .error_bl import ErrorBL
from .convertions_bl import ConvertionsBL

ACCESS_TOKEN_STR = "access_token"
USERNAME_SUB = "sub"
ENCODE_FORMAT = 'utf-8'
TOKEN_EXP_FIELD = "exp"

userbl = UserBL()
errorbl = ErrorBL()
convertionsbl = ConvertionsBL()

"""
Description: Business logic class for authentication operations 
"""
class AuthBL:
    
    """
    Description: Get jwt token payload 
    Params: access_token (str), key (str), algo (str)
    Return value: payload (dict)
    Notes: None
    """
    async def get_payload(self, access_token, key, algo):
        return jwt.decode(access_token, key, algorithms=[algo])
    
    """
    Description: Get current user object 
    Params: request (Request)
    Return value: User
    Notes: None
    """
    async def get_current_user(self, request: Request):
        access_token = request.cookies.get(ACCESS_TOKEN_STR)
        if access_token is None:
            await errorbl.error_handling(401,"Not authenticated!")
        try:
            payload = await self.get_payload(access_token ,SECRET_KEY, ALGORITHM)
            username = payload.get(USERNAME_SUB)
            if username is None:
                await errorbl.error_handling(401,"Invalid authentication!!")
        except jwt.exceptions.DecodeError:
            await errorbl.error_handling(401,"Invalid authentication!!")
        except jwt.exceptions.ExpiredSignatureError:
            await errorbl.error_handling(401,"Invalid authentication!!")
            
        user = userbl.get_user_by_username(username)
        if user is None:
            await errorbl.error_handling(401,"Invalid authentication!")
        return user
    
    """
    Description: Verify given password with user password 
    Params: plain_password (str), user_password (str)
    Return value: bool
    Notes: None
    """
    async def verify_password(self, plain_password, user_password):
        return bcrypt.checkpw(await convertionsbl.encode(plain_password, ENCODE_FORMAT),
                              await convertionsbl.encode(user_password, ENCODE_FORMAT))
    
    """
    Description: Create access token for logged in user 
    Params: data (dict), expires_delta (timedelta)
    Return value: Jwt token (str)
    Notes: None
    """    
    async def create_access_token(self, data, expires_delta):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({TOKEN_EXP_FIELD: expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    """
    Description: Hash given password 
    Params: password (str)
    Return value: Hashed password (bytes)
    Notes: None
    """
    async def hash_password(self, password):
        byte_pwd = await convertionsbl.encode(password, ENCODE_FORMAT)
        salt = bcrypt.gensalt()
        hashed_pass = bcrypt.hashpw(byte_pwd, salt)
        return hashed_pass
    
    """
    Description: Registr new user to the system 
    Params: username (str), email (str), password (str)
    Return value: None
    Notes: None
    """
    async def register(self, username, email, password):
        hash_pass = await self.hash_password(password)
        user = userbl.create_user(username, email, hash_pass)
        await userbl.save(user)
    
    """
    Description: Set user's cookie 
    Params: response (JSONResponse), key (str), value (str), httponly (bool),
            expires(datetime), path (str)
    Return value: None
    Notes: None
    """    
    async def set_response(self, response, key, value, httponly, expires, path):
        response.set_cookie(
            key=key,
            value=value,
            httponly=httponly,
            expires=expires,
            path=path
        )
    
    """
    Description: Get token expire time 
    Params: time (datetime), timedelta (timedelta)
    Return value: Expire time (datetime)
    Notes: None
    """    
    async def get_expire_time(self, time ,timedelta):
        return time + timedelta        
    
    """
    Description: Login to the system 
    Params: username (str), password (str)
    Return value: Response (JSONResponse)
    Notes: None
    """
    async def login(self, username, password):
        print(username)
        user = userbl.get_user_by_username(username)
        print(user.username)
        if not user:
            await errorbl.error_handling(400,"Invalid username or password!")
        elif not await self.verify_password(password ,user.password):
            await errorbl.error_handling(400, "Invalid username or password!")
            
        expired_time = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await self.create_access_token(
            data={'sub': user.username},
            expires_delta=expired_time)
        
        response = JSONResponse({"token_type": "bearer"})
        expires = await self.get_expire_time(datetime.now(timezone.utc), 
                                             expired_time)
        
        await self.set_response(response=response,
                          key="access_token", 
                          value=access_token, 
                          httponly=True, 
                          expires=expires, 
                          path="/")
        
        return response
                               
        
          