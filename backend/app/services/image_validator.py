import io
from typing import Tuple, Dict, Any
from PIL import Image

class ImageValidationError(Exception):
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

ARTWORK_SPECS = {
    "poster": {
        "aspect_ratio": 2 / 3, # 0.6667
        "aspect_label": "2:3",
        "target_px": (600, 900),
        "min_px": (300, 450),
        "max_kb": 200,
    },
    "banner": {
        "aspect_ratio": 16 / 9, # 1.7778
        "aspect_label": "16:9",
        "target_px": (1280, 720),
        "min_px": (640, 360),
        "max_kb": 200,
    },
    "thumbnail": {
        "aspect_ratio": 16 / 9, # 1.7778
        "aspect_label": "16:9",
        "target_px": (640, 360),
        "min_px": (320, 180),
        "max_kb": 200,
    },
}

ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}

def validate_artwork_image(
    file_bytes: bytes,
    artwork_type: str,
    aspect_tolerance: float = 0.05,
) -> Dict[str, Any]:
    """
    Validates uploaded image bytes against specifications defined in reference.json:
    - Checks file size against the 200 KB ceiling.
    - Inspects image dimensions and aspect ratio via Pillow.
    - Validates minimum dimension thresholds.
    - Returns editor-readable error explanations on failure.
    """
    if artwork_type not in ARTWORK_SPECS:
        raise ImageValidationError(
            f"Invalid artwork type '{artwork_type}'. Allowed types: {list(ARTWORK_SPECS.keys())}."
        )

    spec = ARTWORK_SPECS[artwork_type]
    file_size_bytes = len(file_bytes)
    file_size_kb = round(file_size_bytes / 1024, 2)

    # 1. Enforce 200 KB ceiling
    if file_size_kb > spec["max_kb"]:
        raise ImageValidationError(
            f"File size is {file_size_kb} KB, exceeding the {spec['max_kb']} KB limit. Please compress the image before uploading.",
            details={
                "actual_kb": file_size_kb,
                "max_kb": spec["max_kb"],
                "artwork_type": artwork_type,
            }
        )

    # 2. Inspect with Pillow
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
        # Re-open for dimension inspection after verify()
        image = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        raise ImageValidationError(
            f"Unable to decode image file. Please upload a valid JPEG, PNG, or WebP image. (Error: {str(e)})"
        )

    img_format = (image.format or "UNKNOWN").upper()
    if img_format not in ALLOWED_FORMATS:
        raise ImageValidationError(
            f"Unsupported image format '{img_format}'. Please upload a JPEG, PNG, or WebP image."
        )

    width, height = image.size
    if height == 0:
        raise ImageValidationError("Invalid image: height is 0 px.")

    actual_ratio = width / height
    expected_ratio = spec["aspect_ratio"]
    target_w, target_h = spec["target_px"]
    min_w, min_h = spec["min_px"]

    # 3. Check Minimum Dimensions
    if width < min_w or height < min_h:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height} px) are too small for {artwork_type}. "
            f"Minimum required is {min_w}x{min_h} px (target: {target_w}x{target_h} px).",
            details={
                "actual_px": (width, height),
                "min_px": (min_w, min_h),
                "target_px": (target_w, target_h),
            }
        )

    # 4. Aspect Ratio Check (with 5% tolerance)
    ratio_diff = abs(actual_ratio - expected_ratio) / expected_ratio
    if ratio_diff > aspect_tolerance:
        raise ImageValidationError(
            f"Incorrect aspect ratio for {artwork_type}. Required ratio is {spec['aspect_label']} (target ~{target_w}x{target_h} px), "
            f"but uploaded image is {width}x{height} px (ratio {actual_ratio:.2f}:1).",
            details={
                "actual_ratio": round(actual_ratio, 2),
                "expected_ratio": round(expected_ratio, 2),
                "aspect_label": spec["aspect_label"],
                "actual_px": (width, height),
                "target_px": (target_w, target_h),
            }
        )

    return {
        "width": width,
        "height": height,
        "format": img_format,
        "file_size_kb": file_size_kb,
        "mime_type": f"image/{img_format.lower()}",
    }
