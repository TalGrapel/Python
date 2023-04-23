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

class AuthBL:
    
    async def get_payload(self, access_token, key, algo):
        return jwt.decode(access_token, key, algorithms=[algo])
    
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
    
    async def verify_password(self, plain_password, user_password):
        return bcrypt.checkpw(await convertionsbl.encode(plain_password, ENCODE_FORMAT),
                              await convertionsbl.encode(user_password, ENCODE_FORMAT))
        
    async def create_access_token(self, data, expires_delta):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({TOKEN_EXP_FIELD: expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def hash_password(self, password):
        byte_pwd = await convertionsbl.encode(password, ENCODE_FORMAT)
        salt = bcrypt.gensalt()
        hashed_pass = bcrypt.hashpw(byte_pwd, salt)
        return hashed_pass
    
    async def register(self, username, email, password):
        hash_pass = await self.hash_password(password)
        user = userbl.create_user(username, email, hash_pass)
        await userbl.save(user)
        
    async def set_response(self, response, key, value, httponly, expires, path):
        response.set_cookie(
            key=key,
            value=value,
            httponly=httponly,
            expires=expires,
            path=path
        )
        
    async def get_expire_time(self, time ,timedelta):
        return time + timedelta        
    
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
                               
        
          