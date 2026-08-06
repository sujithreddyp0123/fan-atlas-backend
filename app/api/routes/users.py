from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.repositories.store import get_store
from app.schemas.users import UpdateProfileRequest, UserPublic

router = APIRouter()


@router.get("/me", response_model=UserPublic)
def me(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    return current_user


@router.patch("/me/profile", response_model=UserPublic)
def update_profile(
    payload: UpdateProfileRequest,
    current_user: UserPublic = Depends(get_current_user),
) -> UserPublic:
    return get_store().update_user_profile(current_user.id, payload)

