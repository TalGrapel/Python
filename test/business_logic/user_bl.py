from app.models import User
from app.models import Receipt
from .receipts_bl import ReceiptBL

ACCESS_TOKEN_STR = "access_token"

receipt_bl = ReceiptBL()

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
    Description: Add receipt to user's favorites list 
    Params: user (User), receipt (Receipt)
    Return value: None
    Notes: None
    """
    async def add_favorite(self, user: User, receipt: Receipt):
        if receipt not in user.favorites:
            user.favorites.append(receipt)
            self.save(user)
    
    """
    Description: Remove receipts from user's favorites list 
    Params: user (User), receipt (Receipt)
    Return value: None
    Notes: None
    """        
    async def remove_favorite(self, user: User, receipt: Receipt):
        if receipt in user.favorites:
            user.favorites.remove(receipt)
            self.save(user)
    
    """
    Description: Get user's receipts amount 
    Params: user (User)
    Return value: User's receipts list length (int)
    Notes: None
    """        
    async def get_receipts_amount(self, user: User):
        return len(user.receipts)
    
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
    Description: Remove receipt from user's receipts list  
    Params: user (User), receipt (Receipt)
    Return value: None
    Notes: None
    """    
    async def remove_receipt(self, user: User, receipt: Receipt):
        user.receipts.remove(receipt)
        receipt_bl.delete(receipt)
        self.save(user)
    
    """
    Description: Add receipt to the user's receipts list 
    Params: user (User), receipt (Receipt)
    Return value: None
    Notes: None
    """    
    async def add_receipt(self, user: User, receipt: Receipt):
        user.receipts.append(receipt)
        receipt_bl.save(receipt)
        self.save(user)
               
        
                                    
        