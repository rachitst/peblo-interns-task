import sys
import os
import asyncio
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.test_image_validator import (
    test_valid_poster,
    test_wrong_ratio_poster,
    test_tiny_thumbnail,
    test_valid_banner,
)
from tests.test_storage import test_atomic_write_json
from tests.test_seed_parser import test_seed_json_integrity_and_imperfections
from tests.test_rbac import (
    test_rbac_admin_allowed,
    test_rbac_editor_rejected_on_admin_only,
    test_rbac_editor_allowed_on_crud,
)
from tests.test_search import test_composed_search_filter_logic
import tempfile

def main():
    print("================ Running Backend Test Suite ================")
    
    # 1. Test image validation
    test_valid_poster()
    print("  [PASS] test_valid_poster (aspect 2:3, <=200KB)")
    
    test_wrong_ratio_poster()
    print("  [PASS] test_wrong_ratio_poster (rejected invalid ratio)")
    
    test_tiny_thumbnail()
    print("  [PASS] test_tiny_thumbnail (rejected dimensions too small)")
    
    test_valid_banner()
    print("  [PASS] test_valid_banner (aspect 16:9, <=200KB)")
    
    # 2. Test storage atomic swap
    with tempfile.TemporaryDirectory() as tmp_dir:
        asyncio.run(test_atomic_write_json(Path(tmp_dir)))
    print("  [PASS] test_atomic_write_json (atomic temp file replacement)")

    # 3. Test seed parser & imperfection traps
    test_seed_json_integrity_and_imperfections()
    print("  [PASS] test_seed_json_integrity_and_imperfections (95 records, 4 traps)")

    # 4. Test RBAC role enforcement
    test_rbac_admin_allowed()
    test_rbac_editor_rejected_on_admin_only()
    test_rbac_editor_allowed_on_crud()
    print("  [PASS] test_rbac (admin allowed, editor 403 on publish, editor allowed on CRUD)")

    # 5. Test search & composed filtering
    test_composed_search_filter_logic()
    print("  [PASS] test_search (case-insensitive search composed with filters)")

    print("================ All 10/10 Unit Tests Passed =================\n")

if __name__ == "__main__":
    main()
