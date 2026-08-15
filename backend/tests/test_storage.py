import os
import json
import pytest
from pathlib import Path
from app.services.storage import LocalStorage

@pytest.mark.asyncio
async def test_atomic_write_json(tmp_path):
    storage = LocalStorage(
        base_upload_dir=str(tmp_path / "uploads"),
        base_published_dir=str(tmp_path / "published"),
    )
    
    test_data = {"catalogue": "test", "items": [1, 2, 3]}
    target_file = "catalogue.json"
    
    saved_path = await storage.atomic_write_json(target_file, test_data)
    assert os.path.exists(saved_path)
    
    with open(saved_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded == test_data
