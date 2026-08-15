from typing import List, Optional
from fastapi import Header, HTTPException, status

def get_current_user_role(
    x_user_role: Optional[str] = Header(None, alias="X-User-Role", description="Role header: 'editor' or 'admin'"),
    x_role: Optional[str] = Header(None, alias="X-Role", description="Alternative role header: 'editor' or 'admin'"),
) -> str:
    raw_role = x_user_role or x_role or "admin"
    role = raw_role.lower().strip()
    if role not in {"editor", "admin", "viewer"}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication role '{raw_role}'. Allowed roles: 'editor', 'admin'.",
        )
    return role

def require_roles(allowed_roles: List[str]):
    def role_checker(
        x_user_role: Optional[str] = Header(None, alias="X-User-Role", description="Role header: 'editor' or 'admin'"),
        x_role: Optional[str] = Header(None, alias="X-Role", description="Alternative role header: 'editor' or 'admin'"),
    ) -> str:
        current_role = (x_user_role or x_role or "admin").lower().strip()
        if current_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Role '{current_role}' lacks required permissions. Required one of: {allowed_roles}.",
            )
        return current_role
    return role_checker
