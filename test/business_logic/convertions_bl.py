import json
from bson.objectid import ObjectId


"""
Description: Business logic for convertions operations 
"""
class ConvertionsBL:
    
    """
    Description: convert object using encode 
    Params: object (any), format (str)
    Return value: encoded object (bytes)
    Notes: None
    """
    async def encode(self, object, format):
        return object.encode(format)
    
    """
    Description: decode object using decode 
    Params: object (bytes), format (str)
    Return value: object (any)
    Notes: None
    """
    async def decode(self, object, format):
        return object.decode(format)
    
    """
    Description: convert dictionary to json 
    Params: dict (dict)
    Return value: object (json)
    Notes: None
    """
    async def encode_to_json(self, dict):
        return json.dumps(dict)
    
    """
    Description: convert json to dictionary 
    Params: json_obj (json)
    Return value: object (dict)
    Notes: None
    """
    async def decode_to_dict(self, json_obj):
        return json.loads(json_obj)
    
    """
    Description: convert id to ObjectID 
    Params: object_id (str)
    Return value: ObjectId
    Notes: None
    """
    async def convert_objectid(self, object_id):
        return ObjectId(object_id)