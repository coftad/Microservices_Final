from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import requests
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/auth/login")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8001")

def verify_admin_token(token: str = Depends(oauth2_scheme)):
    """Verify admin access through auth service"""
    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail="Auth service unreachable")

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return response.json()