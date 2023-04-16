from bson.objectid import ObjectId
from fastapi import Request, HTTPException, Depends ,Query
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasicCredentials
from fastapi_mail import FastMail, MessageSchema
from datetime import datetime, timedelta, timezone
from app import connection_config
import jwt
import re
import bcrypt
from app import fast_app, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import User, CreateUserRequest, UpdateUserRequest, Receipt ,CreateReceiptRequest, UpdateReceiptRequest
from app.models import ForgotPasswordRequest

async def get_current_user(request: Request) -> User:
    access_token = request.cookies.get("access_token")
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    user = User.objects(username=username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

@fast_app.post("/login")
async def login(credentials: HTTPBasicCredentials):
    user = User.objects(username=credentials.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    elif not await verify_password(credentials.password.encode('utf-8'), user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    response = JSONResponse({"token_type": "bearer"})
    expires = datetime.now(timezone.utc) + access_token_expires

    # set the access token as the value for the "access_token" cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        expires=expires,
        path="/",
    )

    return response

async def get_user(username: str) -> User:
    user = User.objects(username=username).first()
    return user

async def verify_password(plain_password, hashed_password):
    if isinstance(hashed_password ,str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)

async def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@fast_app.post("/register")
async def create_user(request: CreateUserRequest) -> dict:
    pwd = request.password
    bytePwd = pwd.encode('utf-8')
    mySalt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(bytePwd, mySalt)
    user = User(username=request.username, email=request.email, password=pwd_hash)
    try:
        user.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"user_id": str(user.id)}

@fast_app.post("/receipts")
async def create_receipt(
    request: CreateReceiptRequest,
    current_user: User = Depends(get_current_user)
):
    receipt = Receipt(
        title=request.title,
        description=request.description,
        ingredients=request.ingredients,
        instructions=request.instructions,
        author=current_user,
        category=request.category,
        estimated_time=request.estimated_time
    )
    receipt.save()
    current_user.receipts.append(receipt.id)
    current_user.save()
    return {"receipt_id": str(receipt.id)}

@fast_app.get("/receipts")
async def get_receipt_by_id(receipt_id: str = Query(..., alias="receipt_id")):
    try:
        receipt_id = ObjectId(receipt_id)
    except:
        raise HTTPException(status_code=422, detail="Invalid ObjectId")

    receipt = Receipt.objects(id=receipt_id).first()

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found!")

    return receipt.to_dict()

@fast_app.get("/user/receipts")
async def get_receipts_of_user(current_user: User = Depends(get_current_user)):
    return [receipt.to_dict() for receipt in current_user.receipts]

@fast_app.get("/receipts/search")
async def get_receipts_by_title(title: str = Query("", alias="title")) -> dict:
    regex = re.compile(f".*{title}.*", re.IGNORECASE)
    receipts = Receipt.objects(title__regex=regex).all()
    
    return {"receipts": [receipt.to_dict() for receipt in receipts]}

@fast_app.get("/receipts/search/ingredient")
async def get_receipts_by_ingredient(ing:str = Query("", alias="ing")) -> dict:
    regex = re.compile(f".*{ing}.*", re.IGNORECASE)
    receipts = Receipt.objects(ingredients__in=[regex]).all()
    
    return {"receipts": [receipt.to_dict() for receipt in receipts]}

@fast_app.get("/receipts/search/category")
async def get_receipts_by_category(cat: str = Query("",alias="cat")) -> dict:
    regex = re.compile(f".*{cat}.*", re.IGNORECASE)
    receipts = Receipt.objects(category=regex).all()
    
    return {"receipts": [receipt.to_dict() for receipt in receipts]}

@fast_app.post("/users/add_receipt")
async def add_receipt_to_user(request: CreateReceiptRequest, current_user: User = Depends(get_current_user)):
    receipt = Receipt(
        title=request.title,
        description=request.description,
        ingredients=request.ingredients,
        instructions=request.instructions,
        category=request.category,
        estimated_time=request.estimated_time
    )

    current_user.receipts.append(receipt)
    receipt.author = current_user
    receipt.save()
    current_user.save()

    return {"message": f"Receipt added successfully to {current_user.username} - {current_user.id}"}

@fast_app.delete("/users/receipts/delete")
async def remove_receipt_from_user(
    receipt_id: str = Query(..., alias="receipt_id"),
    current_user: User = Depends(get_current_user)
):
    try:
        receipt_id = ObjectId(receipt_id)
    except:
        raise HTTPException(status_code=422, detail="Invalid ObjectId")
    
    receipt = Receipt.objects.get(id=receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    if not receipt.author == current_user:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this receipt")

    current_user.receipts.remove(receipt)
    current_user.save()
    receipt.delete()

    return {"message": f"Receipt {receipt_id} has been removed from user {current_user.id}"}

@fast_app.put("/users/modify_receipt")
async def modify_user_receipt(
    request: UpdateReceiptRequest,
    receipt_id: str = Query(..., alias="receipt_id"),
    current_user: User = Depends(get_current_user)
):
    try:
        receipt_id = ObjectId(receipt_id)
    except:
        raise HTTPException(status_code=422, detail="Invalid ObjectId")
    
    receipt = Receipt.objects.get(id=receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    if not receipt.author == current_user:
        raise HTTPException(status_code=403, detail="You do not have permission to modify this receipt")

    for field in request.__dict__.keys():
        if field != "_sa_instance_state":
            setattr(receipt, field, getattr(request, field))
    receipt.save()

    return {"message": f"Receipt {receipt_id} has been updated for user {current_user.id}"}

@fast_app.put("/users/add_favorite")
async def add_favorite_receipt(
    user: User = Depends(get_current_user),
    receipt_id: str = Query(..., alias="receipt_id")
):
    try:
        receipt_id = ObjectId(receipt_id)
    except:
        raise HTTPException(status_code=422, detail="Invalid ObjectId")
    
    receipt = Receipt.objects(id=receipt_id).first()
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")

    if receipt not in user.favorites:
        user.favorites.append(receipt)
        user.save()

    return {"message": f"Receipt {receipt_id} has been added to favorites for user {user.id}"}

# Remove favorite receipt from user
@fast_app.put("/users/remove_favorite")
async def remove_favorite_receipt(
    user: User = Depends(get_current_user),
    receipt_id: str = Query(..., alias="receipt_id")
):
    try:
        receipt_id = ObjectId(receipt_id)
    except:
        raise HTTPException(status_code=422, detail="Invalid ObjectId")
    
    receipt = Receipt.objects(id=receipt_id).first()
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")

    if receipt in user.favorites:
        user.favorites.remove(receipt)
        user.save()

    return {"message": f"Receipt {receipt_id} has been removed from favorites for user {user.id}"}


@fast_app.get("/receipts/less_ingredients")
async def get_receipts_less_ingredients(max_ingredients: int = Query(..., description="Maximum number of ingredients")):

    receipts = Receipt.objects.filter(ingredients__size__lt=max_ingredients).to_list(length=1000)

    return {"receipts": receipts}

@fast_app.get("/receipts/estimated_time_range")
async def get_receipts_estimated_time_range(min_time: int = Query(..., description="Minimum estimated time (in minutes)"),
                                      max_time: int = Query(..., description="Maximum estimated time (in minutes)")):
    receipts = Receipt.objects.filter(estimated_time__gte=min_time, estimated_time__lte=max_time).to_list(length=1000)

    return {"receipts": receipts}

@fast_app.get("/user/receipts/amount")
async def get_num_of_receipts_of_user(current_user: User = Depends(get_current_user)):
    receipts_num = current_user.receipts.len()

    return {"username": current_user.username, "num_of_receipts": receipts_num}

@fast_app.get("/user/favorites/amount")
async def get_num_of_favorites_of_user(current_user: User = Depends(get_current_user)):
    favorites_num = current_user.favorites.len()

    return {"username": current_user.username, "num_of_favorites": favorites_num}

@fast_app.get("/receipts/amount")
async def get_num_of_receipts():
    receipts_amount = Receipt.objects.count()

    return {"receipts_amount": receipts_amount}

@fast_app.get("/receipts/category")
async def get_number_of_categories():
    categories = Receipt.objects.distinct("category")

    num_categories = len(categories)

    return {"categories_amount": num_categories}

@fast_app.get("/receipts/ingredient")
async def get_number_of_ingredients():

    pipeline = [
        {"$unwind": "$ingredients"},
        {"$project": {"ingredients": {"$toLower": "$ingredients"}}},
        {"$project": {"ingredients": {"$regexReplace": {"input": "$ingredients", "regex": "[0-9]", "replacement": ""}}}},
        {"$group": {"_id": "$ingredients"}},
        {"$sort": {"_id": 1}}
    ]
    distinct_ingredients = Receipt.objects.aggregate(*pipeline)

    return {"ingredients_amount": len(list(distinct_ingredients))}

@fast_app.get("/receipts/avg_time")
async def get_avg_time_of_receipt():
    receipts = Receipt.objects.all()

    if not receipts:
        return {"message": "No receipts found."}

    total_time = sum(receipt.estimated_time for receipt in receipts)
    avg_time = total_time / len(receipts)

    return {"average_time": avg_time}

@fast_app.get("/receipts/avg-ingredients")
async def avg_ingredients():
    receipts = Receipt.objects.all()

    total_ingredients = sum(len(receipt.ingredients) for receipt in receipts)

    if not receipts:
        return {"message": "No receipts found."}

    avg_ingredients = total_ingredients / len(receipts)

    return {"average_ingredients": avg_ingredients}

@fast_app.put("/update_user")
async def update_date(request: UpdateUserRequest, 
                      cur_user: User = Depends(get_current_user)):
    for field in request.__dict__.keys():
        if field != "_sa_instance_state":
            setattr(cur_user, field, getattr(request, field))
    
    cur_user.save()
    
@fast_app.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):

    message = MessageSchema(
        subject="Password Reset Instructions",
        recipients=[request.email],
        body="Please follow the instructions in the email to reset your password.",
        subtype="html"
    )

    fm = FastMail(connection_config)
    await fm.send_message(message)

    return {"message": "Password reset instructions sent to your email."}
     
@fast_app.post("/make_shop_list")
async def make_shop_list(cur_user: User = Depends(get_current_user), receipt_id: str = Query("", alias="receipt_id")):
    try:
        receipt_id = ObjectId(receipt_id)
    except:
        raise HTTPException(status_code=422, detail="Invalid ObjectId")
    
    receipt = Receipt.objects(id=receipt_id).first()
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    message = MessageSchema(
        subject=f"Shop list for {receipt.title}",
        recipients=[cur_user.email],
        body="<ul>\n" + "\n".join([f"<li>{i}</li>" for i in receipt.ingredients]) + "\n</ul>",
        subtype="html"
)
    
    fm = FastMail(connection_config)
    await fm.send_message(message) 
            
    
 #todo:
 #make shop list
 #send via email/sms
 #forget password
