import pytest
from pathlib import Path
from app.services.image_validator import validate_artwork_image, ImageValidationError

ASSETS_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_assets"

def test_valid_poster():
    poster_path = ASSETS_DIR / "poster_good.jpg"
    if poster_path.exists():
        data = poster_path.read_bytes()
        res = validate_artwork_image(data, "poster")
        assert res["width"] == 600
        assert res["height"] == 900
        assert res["file_size_kb"] <= 200

def test_wrong_ratio_poster():
    poster_path = ASSETS_DIR / "poster_wrong_ratio.jpg"
    if poster_path.exists():
        data = poster_path.read_bytes()
        with pytest.raises(ImageValidationError) as exc:
            validate_artwork_image(data, "poster")
        assert "Incorrect aspect ratio" in str(exc.value)

def test_tiny_thumbnail():
    thumb_path = ASSETS_DIR / "thumb_tiny.jpg"
    if thumb_path.exists():
        data = thumb_path.read_bytes()
        with pytest.raises(ImageValidationError) as exc:
            validate_artwork_image(data, "thumbnail")
        assert "too small" in str(exc.value)

def test_valid_banner():
    banner_path = ASSETS_DIR / "banner_good.jpg"
    if banner_path.exists():
        data = banner_path.read_bytes()
        res = validate_artwork_image(data, "banner")
        assert res["width"] == 1280
        assert res["height"] == 720
        assert res["file_size_kb"] <= 200
