import sys
import json
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings

def test_seed_json_integrity_and_imperfections():
    seed_path = Path(settings.SEED_DATA_PATH)
    assert seed_path.exists(), f"Seed data file not found at {seed_path}"
    
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert len(data) == 95, f"Expected 95 episode records, found {len(data)}"
    
    # 1. Check duplicate (content_group, language) trap
    cg_lang_counts = {}
    for ep in data:
        key = (ep["content_group"], ep["language"])
        cg_lang_counts[key] = cg_lang_counts.get(key, 0) + 1
    
    duplicates = {k: v for k, v in cg_lang_counts.items() if v > 1}
    assert ("motis-many-lives-s01e02", "hi") in duplicates
    assert duplicates[("motis-many-lives-s01e02", "hi")] == 2
    
    # 2. Check missing section show trap
    shows_missing_section = {ep["show_title"] for ep in data if not ep.get("section")}
    assert "Rhyme Rangers" in shows_missing_section
    
    # 3. Check missing artwork trap
    eps_missing_artwork = [ep["episode_id"] for ep in data if not ep.get("artwork_available")]
    assert "ep_0036" in eps_missing_artwork
    
    # 4. Check Season 0 trailers
    trailers = [ep["episode_id"] for ep in data if ep.get("season_number") == 0]
    assert "ep_0093" in trailers
    assert "ep_0094" in trailers

if __name__ == "__main__":
    test_seed_json_integrity_and_imperfections()
    print("[PASS] Seed data integrity & 4 deliberate imperfection traps verified!")
