from app.models import User
from app.models import Receipt
from .receipts_bl import ReceiptBL


ACCESS_TOKEN_STR = "access_token"

receipt_bl = ReceiptBL()

class UserBL:
    
    def get_user_by_id(self, id: int) -> User:
        return User.objects(id=id).first()
    
    def get_user_by_username(self ,username: str) -> User:
        return User.objects(username=username).first()
    
    def create_user(self, username: str, email: str, password: str) -> User:
        return User(username=username, email=email, password=password)
    
    def save(self, user: User) -> None:
        user.save()
    
    async def add_favorite(self, user: User, receipt: Receipt):
        if receipt not in user.favorites:
            user.favorites.append(receipt)
            self.save(user)
            
    async def remove_favorite(self, user: User, receipt: Receipt):
        if receipt in user.favorites:
            user.favorites.remove(receipt)
            self.save(user)
            
    async def get_receipts_amount(self, user: User):
        return len(user.receipts)
    
    async def get_favorites_amount(self, user: User):
        return len(user.favorites)
    
    async def update_user(self, user: User, request):
        for field in request.__dict__.keys():
            if field != "_sa_instance_state":
                setattr(user, field, getattr(request, field)) 
                
        self.save(user)
        
    async def remove_receipt(self, user: User, receipt: Receipt):
        user.receipts.remove(receipt)
        receipt_bl.delete(receipt)
        self.save(user)
        
    async def add_receipt(self, user: User, receipt: Receipt):
        user.receipts.append(receipt)
        receipt_bl.save(receipt)
        self.save(user)
               
        
                                    
        