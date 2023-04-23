from fastapi import HTTPException

class ErrorBL:
    def error_handling(self, status_code, detail):
        raise HTTPException(status_code=status_code, detail=detail)