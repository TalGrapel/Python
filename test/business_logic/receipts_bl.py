from app.models import Receipt, User
import re
from mongoengine import Q

MAX_RECEIPTS = 25

class ReceiptBL:
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
    
    def save(self, receipt: Receipt):
        receipt.save()
    
    async def get_receipt_by_id(self, receipt_id):
        return Receipt.objects(id=receipt_id).first()
    
    async def get_receipts_of_user(self, cur_user: User):
        return [receipt.to_dict() for receipt in cur_user.receipts]
    
    async def get_receipts_by_title(self ,title):
        regex = re.compile(f".*{title}.*", re.IGNORECASE)
        return Receipt.objects(title__regex=regex).all()
    
    async def get_receipts_by_ingredient(self, ingredient):
        regex = re.compile(f".*{ingredient}.*", re.IGNORECASE)
        return Receipt.objects(ingredients__in=[regex]).all()
    
    async def get_receipts_by_category(self, category):
        regex = re.compile(f".*{category}.*", re.IGNORECASE)
        return Receipt.objects(category__regex=regex).all()
    
    async def modify_receipt(self, receipt: Receipt, request):
        for field in request.__dict__.keys():
            if field != "_sa_instance_state":
                setattr(receipt, field, getattr(request, field))
        
        self.save(receipt)
        
    def get_all(self):
        return Receipt.objects.all()
    
    def delete(self, receipt: Receipt):
        receipt.delete()
    
    async def get_avg_ingredients_per_receipt(self):
        receipts = self.get_all()
        
        total_ing = sum(len(receipt.ingredients) for receipt in receipts)
        
        return total_ing / len(receipts)
    
    async def get_average_time_of_receipts(self):
        receipts = self.get_all()
        
        total_time = sum(receipt.estimated_time for receipt in receipts)
        
        return total_time / len(receipts)
    
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
    
    async def get_num_of_receipts(self):
        return Receipt.objects.count()
    
    async def get_num_of_categories(self):
        return len(Receipt.objects.distinct("category"))
    
    async def get_receipts_with_less_ingredients(self, max_ingredients):
        return Receipt.objects.filter(Q(__raw__={"$where": f"this.ingredients.length < {max_ingredients}"}))
    
    async def get_receipts_estimated_time_range(self, min_time, max_time):
        return Receipt.objects.filter(estimated_time__gte=min_time,
                                      estimated_time__lte=max_time)
                
                
    