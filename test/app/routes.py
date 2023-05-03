from fastapi import Depends, Query
from fastapi.security import HTTPBasicCredentials
from fastapi_mail import FastMail, MessageSchema
from app import connection_config
from app import fast_app
from app.models import User, CreateUserRequest, UpdateUserRequest, CreateRecipeRequest, UpdateRecipeRequest
from app.models import ForgotPasswordRequest
from business_logic.authentication_bl import AuthBL
from business_logic.error_bl import ErrorBL
from business_logic.recipes_bl import RecipeBL
from business_logic.user_bl import UserBL
from business_logic.convertions_bl import ConvertionsBL

#Business logic objects init
auth_bl = AuthBL()
error_bl = ErrorBL()
recipe_bl = RecipeBL()
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

#Add recipe to current logged in user endpoint
@fast_app.post("/recipes")
async def create_recipe(
    request: CreateRecipeRequest,
    current_user: User = Depends(auth_bl.get_current_user)
):
    receipt = recipe_bl.create_recipe(request.title,
                                        request.description,
                                        request.ingredients,
                                        request.instructions,
                                        current_user,
                                        request.category,
                                        request.estimated_time)
    
    await user_bl.add_recipe(current_user, receipt)
    return {"recipe_title": str(receipt.title)}

#Get recipe by id endpoint
@fast_app.get("/recipes")
async def get_receipt_by_id(recipe_id: str = Query(..., alias="recipe_id")):
    try:
        recipe_id = convertions_bl.convert_objectid(recipe_id)
    except:
        error_bl.error_handling(422, "Invalid ObjectID")

    recipe = recipe_bl.get_recipe_by_id(id)

    if not recipe:
        error_bl.error_handling(401, "Recipe not found!")

    return recipe.to_dict()

#Get all current user's recipes endpoint 
@fast_app.get("/user/recipes")
async def get_recipes_of_user(current_user: User = Depends(auth_bl.get_current_user)):
    return [recipe.to_dict() for recipe in current_user.recipes]

#search recipes by title(partial title is acceptable) endpoint
@fast_app.get("/recipes/search")
async def get_recipes_by_title(title: str = Query(..., alias="title")) -> dict:
    recipes = await recipe_bl.get_recipes_by_title(title)
    
    return {"recipes": [recipe.to_dict() for recipe in recipes]}

#search recipes by ingredient(partial ingredient name is acceptable) endpoint
@fast_app.get("/recipes/search/ingredient")
async def get_recipes_by_ingredient(ing:str = Query(..., alias="ing")) -> dict:
    recipes = await recipe_bl.get_recipes_by_ingredient(ing)
    
    return {"recipes": [recipe.to_dict() for recipe in recipes]}

#search recipes by category(partial category name is acceptable) endpoint
@fast_app.get("/recipes/search/category")
async def get_recipes_by_category(cat: str = Query(...,alias="cat")) -> dict:
    recipes = await recipe_bl.get_recipes_by_category(cat)
    
    return {"recipes": [recipe.to_dict() for recipe in recipes]}

#delete recipe of the current user endpoint
@fast_app.delete("/users/recipes/delete")
async def remove_recipe_from_user(
    recipe_id: str = Query(..., alias="recipe_id"),
    current_user: User = Depends(auth_bl.get_current_user)
):
    print(recipe_id)
    try:
        recipe_id = await convertions_bl.convert_objectid(recipe_id)
        print(recipe_id)
    except:
        await error_bl.error_handling(422, "Invalid ObjectID!")
    
    recipe = await recipe_bl.get_recipe_by_id(recipe_id)
    print(recipe.title)
    if not recipe:
        await error_bl.error_handling(404, "Recipe not found!")
        
    if not recipe.author == current_user:
        await error_bl.error_handling(403, "You dont have permission to delete this recipe!")
        
    await user_bl.remove_recipe(current_user, recipe)

    return {"message": f"Recipe {recipe_id} has been removed from user {current_user.id}"}

#modify recipe of the current user endpoint 
@fast_app.put("/users/modify_recipe")
async def modify_user_recipe(
    request: UpdateRecipeRequest,
    recipe_id: str = Query(..., alias="recipe_id"),
    current_user: User = Depends(auth_bl.get_current_user)
):
    try:
        recipe_id = await convertions_bl.convert_objectid(recipe_id)
    except:
        await error_bl.error_handling(422, "Invalid ObjectID!!")
            
    recipe = await recipe_bl.get_recipe_by_id(recipe_id)
    if not recipe:
        await error_bl.error_handling(404, "Recipe not found!")
        
    if not recipe.author == current_user:
        await error_bl.error_handling(403, "You dont have permission to modify this recipe!")
        
    await recipe_bl.modify_recipe(recipe ,request)

    return {"message": f"Recipe {recipe_id} has been updated for user {current_user.id}"}

#add recipe to the current user's favorites endpoint
@fast_app.put("/users/add_favorite")
async def add_favorite_recipe(
    user: User = Depends(auth_bl.get_current_user),
    recipe_id: str = Query(..., alias="recipe_id")
):
    try:
        recipe_id = await convertions_bl.convert_objectid(recipe_id)
    except:
        await error_bl.error_handling(422, "Invalid ObjectId")
        
    recipe = await recipe_bl.get_recipe_by_id(recipe_id)
    if recipe is None:
        await error_bl.error_handling(404, "Recipe not found!")
        
    await user_bl.add_favorite(user, recipe)

    return {"message": f"Recipe {recipe_id} has been added to favorites for user {user.id}"}

#remove recipe from the current user's favorites endpoint
@fast_app.put("/users/remove_favorite")
async def remove_favorite_recipe(
    user: User = Depends(auth_bl.get_current_user),
    recipe_id: str = Query(..., alias="recipe_id")
):
    try:
        recipe_id = await convertions_bl.convert_objectid(recipe_id)
    except:
        await error_bl.error_handling(422, "Invalid ObjectID!")
        
    recipe = await recipe_bl.get_recipe_by_id(recipe_id)
    if recipe is None:
        await error_bl.error_handling(404, "Recipe not found!")

    await user_bl.remove_favorite(user, recipe)

    return {"message": f"Recipe {recipe_id} has been removed from favorites for user {user.id}"}

#get all recipes with less than a specific amount of ingredients endpoint
@fast_app.get("/recipes/less_ingredients")
async def get_recipes_less_ingredients(max_ingredients: int = Query(..., alias="max_ing")):

    recipes = await recipe_bl.get_recipes_with_less_ingredients(max_ingredients)
    return [recipe.to_dict() for recipe in recipes]

#get all recipes within the estimated time given range endpoint
@fast_app.get("/recipes/estimated_time_range")
async def get_recipes_estimated_time_range(min_time: int = Query(..., alias="min_time"),
                                      max_time: int = Query(..., alias="max_time")):
    recipes = await recipe_bl.get_recipes_estimated_time_range(min_time, max_time)

    return [recipe.to_dict() for recipe in recipes]

#get the amount number of the current user's recipes endpoint
@fast_app.get("/user/recipes/amount")
async def get_num_of_recipes_of_user(current_user: User = Depends(auth_bl.get_current_user)):
    recipes_num = await user_bl.get_recipes_amount(current_user)

    return {"username": current_user.username, "num_of_recipes": recipes_num}

#get the amount number of the current user's favorites endpoint
@fast_app.get("/user/favorites/amount")
async def get_num_of_favorites_of_user(current_user: User = Depends(auth_bl.get_current_user)):
    favorites_num = await user_bl.get_favorites_amount(current_user)

    return {"username": current_user.username, "num_of_favorites": favorites_num}

#get the total amount number of recipes endpoint
@fast_app.get("/recipes/amount")
async def get_num_of_recipes():
    recipes_amount = await recipe_bl.get_num_of_recipes()

    return {"recipes amount": recipes_amount}

#get the number of categories endpoint
@fast_app.get("/recipes/category")
async def get_number_of_categories():
    categories = await recipe_bl.get_num_of_categories()

    return {"categories amount": categories}

#get the total number of distinct ingredients of all recipes
@fast_app.get("/recipes/ingredient")
async def get_number_of_ingredients():

    num_of_distinct_ingredients = await recipe_bl.get_number_of_distinct_ingredients()

    return {"distinct ingredients amount": num_of_distinct_ingredients}

#get the average estimated time of a recipe endpoint
@fast_app.get("/recipes/avg_time")
async def get_avg_time_of_recipe():
    avg_time = await recipe_bl.get_average_time_of_recipes()

    return {"average time": avg_time}

#get the average number of ingredients of a recipes endpoint
@fast_app.get("/recipes/avg-ingredients")
async def avg_ingredients():
    avg_ingredients = await recipe_bl.get_avg_ingredients_per_recipe()

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
    
    receipt = await recipe_bl.get_recipe_by_id(receipt_id)
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
            
