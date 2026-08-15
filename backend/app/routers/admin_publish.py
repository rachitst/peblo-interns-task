from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.publish_run import PublishRun
from app.schemas.validation import ValidationReportResponse, PublishRunResponse
from app.services.validation_report import ValidationReportService
from app.services.publisher import PublishService
from app.routers.auth import require_roles

router = APIRouter(prefix="/admin", tags=["Admin CMS - Publish Pipeline"])

@router.get("/validation-report", response_model=ValidationReportResponse)
async def get_validation_report(
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    """
    Returns a comprehensive validation report detailing all blockers and warnings
    grouped by show to allow content editors to resolve data issues before publishing.
    """
    validator = ValidationReportService(db)
    return await validator.generate_report()

@router.post("/catalog/publish", status_code=status.HTTP_200_OK)
async def publish_catalogue(
    db: AsyncSession = Depends(get_db),
    role: str = Depends(require_roles(["admin"])), # STRICTLY ADMIN ONLY
):
    """
    Validates and executes an atomic catalogue publication.
    - Fails if blocking data validation issues exist.
    - Generates collapsed language variants deterministically.
    - Performs atomic file replacement in storage.
    - Records publish run history.
    """
    # 1. Check validation report for blockers
    validator = ValidationReportService(db)
    report = await validator.generate_report()
    if not report.can_publish:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Publishing blocked by validation errors.",
                "total_blockers": report.total_blockers,
                "issues": [i.model_dump() for i in report.issues if i.severity == "blocker"],
            },
        )

    # 2. Execute atomic publish
    publisher = PublishService(db)
    result = await publisher.generate_and_publish_catalogue(published_by=f"{role}@peblo.tv")
    return result

@router.get("/publish-runs", response_model=List[PublishRunResponse])
async def list_publish_runs(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles(["editor", "admin"])),
):
    """Lists history of catalogue publish runs."""
    stmt = (
        select(PublishRun)
        .order_by(PublishRun.published_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
