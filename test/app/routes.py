from fastapi import Depends, Query
from fastapi.security import HTTPBasicCredentials
from fastapi_mail import FastMail, MessageSchema
from app import connection_config
from app import fast_app
from app.models import User, CreateUserRequest, UpdateUserRequest, CreateReceiptRequest, UpdateReceiptRequest, Receipt
from app.models import ForgotPasswordRequest
from business_logic.authentication_bl import AuthBL
from business_logic.error_bl import ErrorBL
from business_logic.receipts_bl import ReceiptBL
from business_logic.user_bl import UserBL
from business_logic.convertions_bl import ConvertionsBL

#Business logic objects init
auth_bl = AuthBL()
error_bl = ErrorBL()
receipt_bl = ReceiptBL()
user_bl = UserBL()
convertions_bl = ConvertionsBL()

#Login endpoint
@fast_app.post("/login")
async def login(credentials: HTTPBasicCredentials):
    print(credentials.username)
    return await auth_bl.login(credentials.username, credentials.password)

#Register endpoint
@fast_app.post("/register")
async def create_user(request: CreateUserRequest) -> dict:
    encripted_password = await auth_bl.hash_password(request.password)
    user = user_bl.create_user(request.username, request.email, encripted_password)
    try:
        user_bl.save(user)
    except Exception as e:
        error_bl.error_handling(400, str(e))

    return {"user_id": str(user.id)}

#Add receipt to current logged in user endpoint
@fast_app.post("/receipts")
async def create_receipt(
    request: CreateReceiptRequest,
    current_user: User = Depends(auth_bl.get_current_user)
):
    receipt = receipt_bl.create_receipt(request.title,
                                        request.description,
                                        request.ingredients,
                                        request.instructions,
                                        current_user,
                                        request.category,
                                        request.estimated_time)
    
    await user_bl.add_receipt(current_user, receipt)
    return {"receipt_title": str(receipt.title)}

#Get receipt by id endpoint
@fast_app.get("/receipts")
async def get_receipt_by_id(receipt_id: str = Query(..., alias="receipt_id")):
    try:
        receipt_id = convertions_bl.convert_objectid(receipt_id)
    except:
        error_bl.error_handling(422, "Invalid ObjectID")

    receipt = receipt_bl.get_receipt_by_id(id)

    if not receipt:
        error_bl.error_handling(401, "Receipt not found!")

    return receipt.to_dict()

#Get all current user's receipts endpoint 
@fast_app.get("/user/receipts")
async def get_receipts_of_user(current_user: User = Depends(auth_bl.get_current_user)):
    return [receipt.to_dict() for receipt in current_user.receipts]

#search receipts by title(partial title is acceptable) endpoint
@fast_app.get("/receipts/search")
async def get_receipts_by_title(title: str = Query(..., alias="title")) -> dict:
    receipts = await receipt_bl.get_receipts_by_title(title)
    
    return {"receipts": [receipt.to_dict() for receipt in receipts]}

#search receipts by ingredient(partial ingredient name is acceptable) endpoint
@fast_app.get("/receipts/search/ingredient")
async def get_receipts_by_ingredient(ing:str = Query(..., alias="ing")) -> dict:
    receipts = await receipt_bl.get_receipts_by_ingredient(ing)
    
    return {"receipts": [receipt.to_dict() for receipt in receipts]}

#search receipts by category(partial category name is acceptable) endpoint
@fast_app.get("/receipts/search/category")
async def get_receipts_by_category(cat: str = Query(...,alias="cat")) -> dict:
    receipts = await receipt_bl.get_receipts_by_category(cat)
    
    return {"receipts": [receipt.to_dict() for receipt in receipts]}

#delete receipt of the current user endpoint
@fast_app.delete("/users/receipts/delete")
async def remove_receipt_from_user(
    receipt_id: str = Query(..., alias="receipt_id"),
    current_user: User = Depends(auth_bl.get_current_user)
):
    print(receipt_id)
    try:
        receipt_id = await convertions_bl.convert_objectid(receipt_id)
        print(receipt_id)
    except:
        await error_bl.error_handling(422, "Invalid ObjectID!")
    
    receipt = await receipt_bl.get_receipt_by_id(receipt_id)
    print(receipt.title)
    if not receipt:
        await error_bl.error_handling(404, "Receipt not found!")
        
    if not receipt.author == current_user:
        await error_bl.error_handling(403, "You dont have permission to delete this receipt!")
        
    await user_bl.remove_receipt(current_user, receipt)

    return {"message": f"Receipt {receipt_id} has been removed from user {current_user.id}"}

#modify receipt of the current user endpoint 
@fast_app.put("/users/modify_receipt")
async def modify_user_receipt(
    request: UpdateReceiptRequest,
    receipt_id: str = Query(..., alias="receipt_id"),
    current_user: User = Depends(auth_bl.get_current_user)
):
    try:
        receipt_id = await convertions_bl.convert_objectid(receipt_id)
    except:
        await error_bl.error_handling(422, "Invalid ObjectID!!")
            
    receipt = await receipt_bl.get_receipt_by_id(receipt_id)
    if not receipt:
        await error_bl.error_handling(404, "Receipt not found!")
        
    if not receipt.author == current_user:
        await error_bl.error_handling(403, "You dont have permission to modify this receipt!")
        
    await receipt_bl.modify_receipt(receipt ,request)

    return {"message": f"Receipt {receipt_id} has been updated for user {current_user.id}"}

#add receipt to the current user's favorites endpoint
@fast_app.put("/users/add_favorite")
async def add_favorite_receipt(
    user: User = Depends(auth_bl.get_current_user),
    receipt_id: str = Query(..., alias="receipt_id")
):
    try:
        receipt_id = await convertions_bl.convert_objectid(receipt_id)
    except:
        await error_bl.error_handling(422, "Invalid ObjectId")
        
    receipt = await receipt_bl.get_receipt_by_id(receipt_id)
    if receipt is None:
        await error_bl.error_handling(404, "Receipt not found!")
        
    await user_bl.add_favorite(user, receipt)

    return {"message": f"Receipt {receipt_id} has been added to favorites for user {user.id}"}

#remove receipt from the current user's favorites endpoint
@fast_app.put("/users/remove_favorite")
async def remove_favorite_receipt(
    user: User = Depends(auth_bl.get_current_user),
    receipt_id: str = Query(..., alias="receipt_id")
):
    try:
        receipt_id = await convertions_bl.convert_objectid(receipt_id)
    except:
        await error_bl.error_handling(422, "Invalid ObjectID!")
        
    receipt = await receipt_bl.get_receipt_by_id(receipt_id)
    if receipt is None:
        await error_bl.error_handling(404, "Receipt not found!")

    await user_bl.remove_favorite(user, receipt)

    return {"message": f"Receipt {receipt_id} has been removed from favorites for user {user.id}"}

#get all receipts with less than a specific amount of ingredients endpoint
@fast_app.get("/receipts/less_ingredients")
async def get_receipts_less_ingredients(max_ingredients: int = Query(..., alias="max_ing")):

    receipts = await receipt_bl.get_receipts_with_less_ingredients(max_ingredients)
    return [receipt.to_dict() for receipt in receipts]

#get all receipts within the estimated time given range endpoint
@fast_app.get("/receipts/estimated_time_range")
async def get_receipts_estimated_time_range(min_time: int = Query(..., alias="min_time"),
                                      max_time: int = Query(..., alias="max_time")):
    receipts = await receipt_bl.get_receipts_estimated_time_range(min_time, max_time)

    return [receipt.to_dict() for receipt in receipts]

#get the amount number of the current user's receipts endpoint
@fast_app.get("/user/receipts/amount")
async def get_num_of_receipts_of_user(current_user: User = Depends(auth_bl.get_current_user)):
    receipts_num = await user_bl.get_receipts_amount(current_user)

    return {"username": current_user.username, "num_of_receipts": receipts_num}

#get the amount number of the current user's favorites endpoint
@fast_app.get("/user/favorites/amount")
async def get_num_of_favorites_of_user(current_user: User = Depends(auth_bl.get_current_user)):
    favorites_num = await user_bl.get_favorites_amount(current_user)

    return {"username": current_user.username, "num_of_favorites": favorites_num}

#get the total amount number of receipts endpoint
@fast_app.get("/receipts/amount")
async def get_num_of_receipts():
    receipts_amount = await receipt_bl.get_num_of_receipts()

    return {"receipts amount": receipts_amount}

#get the number of categories endpoint
@fast_app.get("/receipts/category")
async def get_number_of_categories():
    categories = await receipt_bl.get_num_of_categories()

    return {"categories amount": categories}

#get the total number of distinct ingredients of all receipts
@fast_app.get("/receipts/ingredient")
async def get_number_of_ingredients():

    num_of_distinct_ingredients = await receipt_bl.get_number_of_distinct_ingredients()

    return {"distinct ingredients amount": num_of_distinct_ingredients}

#get the average estimated time of a receipt endpoint
@fast_app.get("/receipts/avg_time")
async def get_avg_time_of_receipt():
    avg_time = await receipt_bl.get_average_time_of_receipts()

    return {"average time": avg_time}

#get the average number of ingredients of a receipt endpoint
@fast_app.get("/receipts/avg-ingredients")
async def avg_ingredients():
    avg_ingredients = await receipt_bl.get_avg_ingredients_per_receipt()

    return {"average_ingredients": avg_ingredients}

#update current user info endpoint
@fast_app.put("/update_user")
async def update_date(request: UpdateUserRequest, 
                      cur_user: User = Depends(auth_bl.get_current_user)):
    await user_bl.update_user(cur_user ,request)
    return {f"{cur_user.id} had been updated sucessfully"}

#forgot password endpoint    
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

#generate a shop list and sends it to the current user's mail     
@fast_app.post("/make_shop_list")
async def make_shop_list(cur_user: User = Depends(auth_bl.get_current_user), receipt_id: str = Query(..., alias="receipt_id")):
    try:
        receipt_id = await convertions_bl.convert_objectid(receipt_id)
    except:
        await error_bl.error_handling(422, "Invalid ObjectId")
    
    receipt = await receipt_bl.get_receipt_by_id(receipt_id)
    if receipt is None:
        await error_bl.error_handling(404, "Receipt not found!")
    
    message = MessageSchema(
        subject=f"Shop list for {receipt.title}",
        recipients=[cur_user.email],
        body="<ul>\n" + "\n".join([f"<li>{i}</li>" for i in receipt.ingredients]) + "\n</ul>",
        subtype="html"
)
    
    fm = FastMail(connection_config)
    await fm.send_message(message)
    
""" @fast_app.get("/search/ingredients")
async def get_receipts_by_ingredients_list(request: UpdateReceiptRequest):
    ingredient_list = request.ingredients
    if ingredient_list is None:
        error_bl.error_handling(400, "No ingerdients were provided!")
    
    regex = [re.sun(r'\W+','') for ingredient in ingredient_list]    
    regex_pattern = '|'.join([re.sub(r'\d+', r'\d*', re.escape(ingredient)) for ingredient in ingredient_list])
    receipts = Receipt.objects(ingerdients__iregex=regex_pattern)
    
    return [receipt.to_dict() for receipt in receipts] """
            
