from fastapi import Header, HTTPException
from backend.password import ADMIN_NAME, ADMIN_PASS

def verify_admit(authorization: str = Header(...)):
    if authorization != f"{ADMIN_NAME}:{ADMIN_PASS}":
        raise HTTPException(status_code=401, detail="no autorizado")