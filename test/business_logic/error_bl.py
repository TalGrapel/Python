from fastapi import HTTPException

"""
Description: Business logic class for error handling operations 
"""
class ErrorBL:
    
    """
    Description: Raise an exception for specified events 
    Params: status_code (int), detail (str)
    Return value: None
    Notes: None
    """
    def error_handling(self, status_code, detail):
        raise HTTPException(status_code=status_code, detail=detail)