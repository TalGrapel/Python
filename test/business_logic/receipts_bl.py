from app.models import Receipt, User
import re
from mongoengine import Q

"""
Description: Business logic class for Receipt database collection operations 
"""
class ReceiptBL:
    
    """
    Description: Create new receipt 
    Params: title (str), description (str), ingredients (list(str)),
            instructions (str), author (User), category (str), 
            estimated_time (float)
    Return value: Receipt
    Notes: None
    """
    def create_receipt(self, title, 
                             description, 
                             ingredients, 
                             instructions, 
                             author,
                             category,
                             estimated_time):
        
        receipt = Receipt(title=title,
                          description=description,
                          ingredients=ingredients,
                          instructions=instructions,
                          author=author,
                          category=category,
                          estimated_time=estimated_time)
        
        return receipt
    
    """
    Description: Save receipt data in database 
    Params: receipt (Receipt)
    Return value: None
    Notes: None
    """
    def save(self, receipt: Receipt):
        receipt.save()
    
    """
    Description: Get receipt object by id 
    Params: receipt_id (int)
    Return value: Receipt
    Notes: If no receipt is found, the function will return None
    """
    async def get_receipt_by_id(self, receipt_id):
        return Receipt.objects(id=receipt_id).first()
    
    """
    Description: Get a receipts list of a given user 
    Params: cur_user (User)
    Return value: Receipts list (json)
    Notes: None
    """
    async def get_receipts_of_user(self, cur_user: User):
        return [receipt.to_dict() for receipt in cur_user.receipts]
    
    """
    Description: Get receipts list by title
    Params: title (str)
    Return value: list of Receipt objects
    Notes: 1.Partial title is acceptable (if title = "Co") all the receipts
            that their title contains "Co" will be considered
           2. Case insensitive ("Co" and "co" will generate the same result) 
    """
    async def get_receipts_by_title(self ,title):
        regex = re.compile(f".*{title}.*", re.IGNORECASE)
        return Receipt.objects(title__regex=regex).all()
    
    """
    Description: Get receipts list by specific ingredient 
    Params: ingredient (str)
    Return value: list of Receipt objects
    Notes: 1. Partial ingredient name is acceptable (if ingredient = "Po")
            the function will return all the receipts that have an ingredient 
            that contains the string "Po"
            2. Case insensitive
    """
    async def get_receipts_by_ingredient(self, ingredient):
        regex = re.compile(f".*{ingredient}.*", re.IGNORECASE)
        return Receipt.objects(ingredients__in=[regex]).all()
    
    """
    Description: Get receipts list by a given category 
    Params: category (str)
    Return value: List of Receipt objects
    Notes: 1. Partial category name is acceptable (if category = "Sa")
            the function will return all the receipts that their category
            contains the string "Sa" (for example "Salads")
            2. Case insensitive
    """
    async def get_receipts_by_category(self, category):
        regex = re.compile(f".*{category}.*", re.IGNORECASE)
        return Receipt.objects(category__regex=regex).all()
    
    """
    Description: Modify specific receipt 
    Params: receipt (Receipt), request (json)
    Return value: None
    Notes: The function will modify only the specified fields given
            in the request json
    """
    async def modify_receipt(self, receipt: Receipt, request):
        for field in request.__dict__.keys():
            if field != "_sa_instance_state":
                setattr(receipt, field, getattr(request, field))
        
        self.save(receipt)
    
    """
    Description: Get all Receipt objects 
    Params: None
    Return value: List of Receipt objects
    Notes: None
    """    
    def get_all(self):
        return Receipt.objects.all()
    
    """
    Description: Delete a given receipt from the database 
    Params: receipt (Receipt)
    Return value: None
    Notes: None
    """
    def delete(self, receipt: Receipt):
        receipt.delete()
    
    """
    Description: Get the average number of ingredients per receipt  
    Params: None
    Return value: Average number of ingredients (float)
    Notes: None
    """
    async def get_avg_ingredients_per_receipt(self):
        receipts = self.get_all()
        
        total_ing = sum(len(receipt.ingredients) for receipt in receipts)
        
        return total_ing / len(receipts)
    
    """
    Description: Get the average estimated time of receipt 
    Params: None
    Return value: Average estimated time of a receipt (float)
    Notes: None
    """
    async def get_average_time_of_receipts(self):
        receipts = self.get_all()
        
        total_time = sum(receipt.estimated_time for receipt in receipts)
        
        return total_time / len(receipts)
    
    """
    Description: Get the number of distinct ingredients in all receipts 
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
        
        distinct_ingredients = Receipt.objects.aggregate(*pipe)
        
        return len(list(distinct_ingredients))
    
    """
    Description: Get the total number of receipts 
    Params: None
    Return value: Total amount of receipts (int)
    Notes: None
    """
    async def get_num_of_receipts(self):
        return Receipt.objects.count()
    
    """
    Description: Get the total number of categories 
    Params: None
    Return value: Total number of categories (int)
    Notes: None
    """
    async def get_num_of_categories(self):
        return len(Receipt.objects.distinct("category"))
    
    """
    Description: Get list of Receipt objects with less than a specific
                    number of ingredients 
    Params: max_ingredients (int)
    Return value: List of Receipt objects
    Notes: None
    """
    async def get_receipts_with_less_ingredients(self, max_ingredients):
        return Receipt.objects.filter(Q(__raw__={"$where": f"this.ingredients.length < {max_ingredients}"}))
    
    """
    Description: Get all receipts that found on the estimated time given range 
    Params: min_time (float), max_time (float)
    Return value: List of Receipt objects
    Notes: None
    """
    async def get_receipts_estimated_time_range(self, min_time, max_time):
        return Receipt.objects.filter(estimated_time__gte=min_time,
                                      estimated_time__lte=max_time)
                
                
    