import pytest
from fastapi import HTTPException
from app.routers.auth import require_roles, get_current_user_role

def test_rbac_admin_allowed():
    checker = require_roles(["admin"])
    # Allowed when X-User-Role is admin
    assert checker(x_user_role="admin", x_role=None) == "admin"
    assert checker(x_user_role=None, x_role="ADMIN") == "admin"

def test_rbac_editor_rejected_on_admin_only():
    checker = require_roles(["admin"])
    with pytest.raises(HTTPException) as exc_info:
        checker(x_user_role="editor", x_role=None)
    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail

def test_rbac_editor_allowed_on_crud():
    checker = require_roles(["editor", "admin"])
    assert checker(x_user_role="editor", x_role=None) == "editor"
    assert checker(x_user_role="admin", x_role=None) == "admin"
