import json
from bson.objectid import ObjectId

class ConvertionsBL:
    async def encode(self, object, format):
        return object.encode(format)
    
    async def decode(self, object, format):
        return object.decode(format)
    
    async def encode_to_json(self, dict):
        return json.dumps(dict)
    
    async def decode_to_dict(self, json_obj):
        return json.loads(json_obj)
    
    async def convert_objectid(self, object_id):
        return ObjectId(object_id)