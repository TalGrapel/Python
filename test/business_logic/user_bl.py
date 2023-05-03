from app.models import User
from app.models import Recipe
from .recipes_bl import RecipeBL

ACCESS_TOKEN_STR = "access_token"

recipe_bl = RecipeBL()

"""
Description: Business logic class for User database collection operations
"""

class UserBL:
    
    """
    Description: Get user object by id 
    Params: id (int)
    Return value: User
    Notes: None
    """
    def get_user_by_id(self, id: int) -> User:
        return User.objects(id=id).first()
    
    """
    Description: Get user object by username
    Params: username (str)
    Return value: User
    Notes: None
    """
    def get_user_by_username(self ,username: str) -> User:
        return User.objects(username=username).first()
    
    """
    Description: Create new user object 
    Params: username (str), email (str), password (str)
    Return value: User
    Notes: None
    """
    def create_user(self, username: str, email: str, password: str) -> User:
        return User(username=username, email=email, password=password)
    
    """
    Description: Save user data in database 
    Params: user (User)
    Return value: None
    Notes: None
    """
    def save(self, user: User) -> None:
        user.save()
    
    """
    Description: Add recipe to user's favorites list 
    Params: user (User), recipe (Recipe)
    Return value: None
    Notes: None
    """
    async def add_favorite(self, user: User, recipe: Recipe):
        if recipe not in user.favorites:
            user.favorites.append(recipe)
            self.save(user)
    
    """
    Description: Remove recipe from user's favorites list 
    Params: user (User), recipe (Recipe)
    Return value: None
    Notes: None
    """        
    async def remove_favorite(self, user: User, recipe: Recipe):
        if recipe in user.favorites:
            user.favorites.remove(recipe)
            self.save(user)
    
    """
    Description: Get user's recipes amount 
    Params: user (User)
    Return value: User's recipes list length (int)
    Notes: None
    """        
    async def get_recipes_amount(self, user: User):
        return len(user.recipes)
    
    """
    Description: Get user's favorites amount 
    Params: user (User)
    Return value: User's favorites list length (int)
    Notes: None
    """
    async def get_favorites_amount(self, user: User):
        return len(user.favorites)
    
    """
    Description: Update user data 
    Params: user (User), request (json)
    Return value: None
    Notes: The function will update only the specified fields
    """
    async def update_user(self, user: User, request):
        for field in request.__dict__.keys():
            if field != "_sa_instance_state":
                setattr(user, field, getattr(request, field)) 
                
        self.save(user)
    
    """
    Description: Remove recipe from user's recipes list  
    Params: user (User), recipe (Recipe)
    Return value: None
    Notes: None
    """    
    async def remove_recipe(self, user: User, recipe: Recipe):
        user.recipes.remove(recipe)
        recipe_bl.delete(recipe)
        self.save(user)
    
    """
    Description: Add recipe to the user's recipes list 
    Params: user (User), recipe (Recipe)
    Return value: None
    Notes: None
    """    
    async def add_recipe(self, user: User, recipe: Recipe):
        user.recipes.append(recipe)
        recipe_bl.save(recipe)
        self.save(user)
               
        
                                    
        