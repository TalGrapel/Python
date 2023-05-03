from app.models import Recipe, User
import re
from mongoengine import Q

"""
Description: Business logic class for Recipe database collection operations 
"""
class RecipeBL:
    
    """
    Description: Create new recipe 
    Params: title (str), description (str), ingredients (list(str)),
            instructions (str), author (User), category (str), 
            estimated_time (float)
    Return value: Recipe
    Notes: None
    """
    def create_recipe(self, title, 
                             description, 
                             ingredients, 
                             instructions, 
                             author,
                             category,
                             estimated_time):
        
        recipe = Recipe(title=title,
                          description=description,
                          ingredients=ingredients,
                          instructions=instructions,
                          author=author,
                          category=category,
                          estimated_time=estimated_time)
        
        return recipe
    
    """
    Description: Save recipe data in database 
    Params: recipe (Recipe)
    Return value: None
    Notes: None
    """
    def save(self, recipe: Recipe):
        recipe.save()
    
    """
    Description: Get recipe object by id 
    Params: recipe_id (int)
    Return value: Recipe
    Notes: If no recipe is found, the function will return None
    """
    async def get_recipe_by_id(self, recipe_id):
        return Recipe.objects(id=recipe_id).first()
    
    """
    Description: Get a recipes list of a given user 
    Params: cur_user (User)
    Return value: Recipes list (json)
    Notes: None
    """
    async def get_recipes_of_user(self, cur_user: User):
        return [recipe.to_dict() for recipe in cur_user.recipes]
    
    """
    Description: Get recipes list by title
    Params: title (str)
    Return value: list of Recipe objects
    Notes: 1.Partial title is acceptable (if title = "Co") all the recipes
            that their title contains "Co" will be considered
           2. Case insensitive ("Co" and "co" will generate the same result) 
    """
    async def get_recipes_by_title(self ,title):
        regex = re.compile(f".*{title}.*", re.IGNORECASE)
        return Recipe.objects(title__regex=regex).all()
    
    """
    Description: Get recipes list by specific ingredient 
    Params: ingredient (str)
    Return value: list of Recipe objects
    Notes: 1. Partial ingredient name is acceptable (if ingredient = "Po")
            the function will return all the recipes that have an ingredient 
            that contains the string "Po"
            2. Case insensitive
    """
    async def get_recipes_by_ingredient(self, ingredient):
        regex = re.compile(f".*{ingredient}.*", re.IGNORECASE)
        return Recipe.objects(ingredients__in=[regex]).all()
    
    """
    Description: Get recipes list by a given category 
    Params: category (str)
    Return value: List of Recipe objects
    Notes: 1. Partial category name is acceptable (if category = "Sa")
            the function will return all the recipes that their category
            contains the string "Sa" (for example "Salads")
            2. Case insensitive
    """
    async def get_recipes_by_category(self, category):
        regex = re.compile(f".*{category}.*", re.IGNORECASE)
        return Recipe.objects(category__regex=regex).all()
    
    """
    Description: Modify specific recipe 
    Params: recipe (Recipe), request (json)
    Return value: None
    Notes: The function will modify only the specified fields given
            in the request json
    """
    async def modify_recipe(self, recipe: Recipe, request):
        for field in request.__dict__.keys():
            if field != "_sa_instance_state":
                setattr(recipe, field, getattr(request, field))
        
        self.save(recipe)
    
    """
    Description: Get all Recipe objects 
    Params: None
    Return value: List of Recipe objects
    Notes: None
    """    
    def get_all(self):
        return Recipe.objects.all()
    
    """
    Description: Delete a given recipe from the database 
    Params: recipe (Recipe)
    Return value: None
    Notes: None
    """
    def delete(self, recipe: Recipe):
        recipe.delete()
    
    """
    Description: Get the average number of ingredients per recipe  
    Params: None
    Return value: Average number of ingredients (float)
    Notes: None
    """
    async def get_avg_ingredients_per_recipe(self):
        recipes = self.get_all()
        
        total_ing = sum(len(recipe.ingredients) for recipe in recipes)
        
        return total_ing / len(recipes)
    
    """
    Description: Get the average estimated time of recipe 
    Params: None
    Return value: Average estimated time of a recipe (float)
    Notes: None
    """
    async def get_average_time_of_recipes(self):
        recipes = self.get_all()
        
        total_time = sum(recipe.estimated_time for recipe in recipes)
        
        return total_time / len(recipes)
    
    """
    Description: Get the number of distinct ingredients in all recipes 
    Params: None
    Return value: Number of distinct ingredients (int)
    Notes: None
    """
    async def get_number_of_distinct_ingredients(self):
        
        pipe = [
            {"$unwind": "$ingredients"},
            {"$project": {"ingredients": {"$toLower": "$ingredients"}}},
            {"$project": {"ingredients": {"regexReplace": {"input": "$ingredients",
                                                           "regex": "[0-9]", 
                                                           "replacement": ""}}}},
            {"$group": {"_id": "$ingredients"}},
            {"$sort": {"_id": 1}}
        ]            
        
        distinct_ingredients = Recipe.objects.aggregate(*pipe)
        
        return len(list(distinct_ingredients))
    
    """
    Description: Get the total number of recipes 
    Params: None
    Return value: Total amount of recipes (int)
    Notes: None
    """
    async def get_num_of_recipes(self):
        return Recipe.objects.count()
    
    """
    Description: Get the total number of categories 
    Params: None
    Return value: Total number of categories (int)
    Notes: None
    """
    async def get_num_of_categories(self):
        return len(Recipe.objects.distinct("category"))
    
    """
    Description: Get list of Recipe objects with less than a specific
                    number of ingredients 
    Params: max_ingredients (int)
    Return value: List of Recipe objects
    Notes: None
    """
    async def get_recipes_with_less_ingredients(self, max_ingredients):
        return Recipe.objects.filter(Q(__raw__={"$where": f"this.ingredients.length < {max_ingredients}"}))
    
    """
    Description: Get all recipes that found on the estimated time given range 
    Params: min_time (float), max_time (float)
    Return value: List of Recipe objects
    Notes: None
    """
    async def get_recipes_estimated_time_range(self, min_time, max_time):
        return Recipe.objects.filter(estimated_time__gte=min_time,
                                      estimated_time__lte=max_time)
                
                
    