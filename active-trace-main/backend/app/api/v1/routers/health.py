from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.core.dependencies import get_db

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Check DB readiness
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "up"
        }
    except Exception:
        return {
            "status": "unhealthy",
            "database": "down"
        }
