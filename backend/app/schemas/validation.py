from datetime import datetime
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, ConfigDict

class ValidationIssue(BaseModel):
    entity_type: Literal["show", "season", "episode", "artwork"]
    entity_id: str
    show_id: Optional[str] = None
    show_title: str
    season_number: Optional[int] = None
    episode_id: Optional[str] = None
    episode_number: Optional[int] = None
    severity: Literal["blocker", "warning"] = "blocker"
    code: str
    message: str
    fix_suggestion: str

class ValidationReportResponse(BaseModel):
    can_publish: bool
    total_blockers: int
    total_warnings: int
    summary: str
    issues: List[ValidationIssue] = []
    grouped_by_show: Dict[str, List[ValidationIssue]] = {}

class PublishRunResponse(BaseModel):
    id: str
    published_at: datetime
    published_by: str
    status: str
    catalogue_version: int
    shows_count: int
    episodes_count: int
    file_path: str
    error_message: Optional[str] = None
    metadata_json: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)
