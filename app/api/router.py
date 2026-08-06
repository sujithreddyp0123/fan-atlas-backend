from fastapi import APIRouter

from app.api.routes import auth, feedback, leaderboard, matches, predictions, realtime, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(predictions.router, tags=["predictions"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(realtime.router, tags=["realtime"])
