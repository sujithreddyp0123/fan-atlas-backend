from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.core.security import create_access_token
from app.repositories.store import get_store
from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest
from app.schemas.common import MessageResponse
from app.schemas.users import UserPublic

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest) -> AuthResponse:
    store = get_store()
    if store.get_user_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = store.create_user(payload.email, payload.password, payload.display_name)
    token = create_access_token(user.id, {"email": user.email})
    return AuthResponse(access_token=token, user=user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    user = get_store().authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.id, {"email": user.email})
    return AuthResponse(access_token=token, user=user)


@router.post("/refresh", response_model=AuthResponse)
def refresh(current_user: UserPublic = Depends(get_current_user)) -> AuthResponse:
    token = create_access_token(current_user.id, {"email": current_user.email})
    return AuthResponse(access_token=token, user=current_user)


@router.post("/logout", response_model=MessageResponse)
def logout() -> MessageResponse:
    return MessageResponse(message="Logged out on client")

