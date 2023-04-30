from mongoengine import Document, fields
from pydantic import BaseModel
from typing import List

"""
Description: an ODM User class for User collection in database
"""
class User(Document):
    username = fields.StringField(required=True, unique=True)
    email = fields.EmailField(required=True, unique=True)
    password = fields.StringField(required=True)
    receipts = fields.ListField(fields.ReferenceField('Receipt'))
    favorites = fields.ListField(fields.ReferenceField('Receipt'))
    
    """
    Description: Convert User to dictionary 
    Params: None
    Return value: Dictionary
    Notes: None
    """
    def to_dict(self):
        return {
            'username':self.username,
            'email':self.email,
            'receipts': [receipt.title for receipt in self.receipts],
            'favorites': [receipt.title for receipt in self.favorites]
        }

"""
Description: an ODM class for Receipt collection in database 
"""
class Receipt(Document):
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    ingredients = fields.ListField(fields.StringField())
    instructions = fields.StringField(required=True)
    author = fields.ReferenceField('User')
    category = fields.StringField(required=True)
    estimated_time = fields.IntField(required=True)
    
    """
    Description: Convert Receipt to dictionary 
    Params: None
    Return value: Dictionary
    Notes: None
    """
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'ingredients': [ingredient for ingredient in self.ingredients],
            'instructions': self.instructions,
            'author': self.author.username,
            'category': self.category,
            'estimated_time': self.estimated_time
        }

"""
Description: Request json template for creating new User 
"""    
class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str

"""
Description: Request json template for creating new Receipt 
"""        
class CreateReceiptRequest(BaseModel):
    title: str
    description: str
    ingredients: List[str]
    instructions: str
    category: str
    estimated_time: int

"""
Description: Request json template for update Receipt 
"""        
class UpdateReceiptRequest(BaseModel):
    title: str = None
    description: str = None
    ingredients: List[str] = None
    instructions: str = None
    category: str = None
    estimated_time: int = None

"""
Description: Request json template for update User 
"""        
class UpdateUserRequest(BaseModel):
    username: str = None
    email: str = None
    password: str = None

"""
Description: Request json template for 'forgot password' operation 
"""        
class ForgotPasswordRequest(BaseModel):
    email: str      
