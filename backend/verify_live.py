import urllib.request
import urllib.error
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_ASSETS_DIR = BASE_DIR / "data" / "sample_assets"

def request(url, method="GET", data=None, raw_data=None, headers=None):
    if headers is None:
        headers = {}
    if data is not None:
        encoded_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif raw_data is not None:
        encoded_data = raw_data
    else:
        encoded_data = None

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
            if "json" in content_type:
                return response.status, json.loads(raw.decode("utf-8"))
            elif "image" in content_type:
                return response.status, raw
            else:
                try:
                    return response.status, raw.decode("utf-8")
                except Exception:
                    return response.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw.decode("utf-8"))
        except Exception:
            return e.code, raw

def upload_artwork_file(episode_id: str, artwork_type: str, file_path: Path):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    filename = file_path.name
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
    
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "X-User-Role": "admin"
    }
    url = f"http://localhost:8000/admin/episodes/{episode_id}/artwork/{artwork_type}"
    return request(url, method="POST", raw_data=body, headers=headers)

def main():
    print("=================================================================")
    print("           Peblo TV Mini — Live Integration Verification          ")
    print("=================================================================\n")

    # 1. Test Health Endpoint
    status, body = request("http://localhost:8000/health")
    print(f"1. Core API Health Check (Port 8000):")
    print(f"   Status: HTTP {status}")
    print(f"   Response: {json.dumps(body, indent=2)}\n")
    assert status == 200, f"Expected 200, got {status}"
    assert body.get("status") == "healthy", "API not healthy"

    # 2. Test CMS UI (Port 3000)
    status, body = request("http://localhost:3000")
    print(f"2. Internal CMS UI (Port 3000):")
    print(f"   Status: HTTP {status} (Vite Serving HTML)")
    assert status == 200, f"Expected 200, got {status}"
    print(f"   Preview: {str(body)[:120]}...\n")

    # 3. Test Viewer UI (Port 3001)
    status, body = request("http://localhost:3001")
    print(f"3. Viewer UI (Port 3001):")
    print(f"   Status: HTTP {status} (Vite Serving HTML)")
    assert status == 200, f"Expected 200, got {status}"
    print(f"   Preview: {str(body)[:120]}...\n")

    # 4. Test Static Sample Assets on Port 8000, 3000, and 3001
    status_8000, body_8000 = request("http://localhost:8000/sample_assets/poster_good.jpg")
    status_3000, body_3000 = request("http://localhost:3000/sample_assets/poster_good.jpg")
    status_3001, body_3001 = request("http://localhost:3001/sample_assets/poster_good.jpg")
    print(f"4. Static Asset Availability:")
    print(f"   API (Port 8000): HTTP {status_8000} (Received {len(body_8000)} bytes)")
    print(f"   CMS UI (Port 3000): HTTP {status_3000} (Received {len(body_3000)} bytes)")
    print(f"   Viewer UI (Port 3001): HTTP {status_3001} (Received {len(body_3001)} bytes)\n")
    assert status_8000 == 200 and status_3000 == 200 and status_3001 == 200

    # 5. Test RBAC: Editor cannot trigger publish (403 Forbidden)
    status, body = request("http://localhost:8000/admin/catalog/publish", method="POST", headers={"X-User-Role": "editor"})
    print(f"5. RBAC Enforcement Check (POST /admin/catalog/publish with X-User-Role: editor):")
    print(f"   Status: HTTP {status}")
    print(f"   Response: {body}\n")
    assert status == 403, f"Expected 403 Forbidden for editor, got {status}"

    # 6. Test Validation Report Endpoint (Identifying Deliberate Imperfection Traps)
    status, body = request("http://localhost:8000/admin/validation-report", headers={"X-User-Role": "admin"})
    print(f"6. Pre-Flight Validation Report Scanner (GET /admin/validation-report):")
    print(f"   Status: HTTP {status}")
    print(f"   Can Publish: {body.get('can_publish')}")
    print(f"   Total Blockers: {body.get('total_blockers')}")
    print(f"   Total Warnings: {body.get('total_warnings')}")
    print(f"   Summary: {body.get('summary')}\n")
    assert status == 200, f"Expected 200, got {status}"

    # 7. Test Pre-Flight Publish Guard Enforcement
    # If blockers exist, publish MUST be rejected with HTTP 400 Bad Request
    if not body.get("can_publish"):
        status, publish_err = request("http://localhost:8000/admin/catalog/publish", method="POST", headers={"X-User-Role": "admin"})
        print(f"7. Pre-Flight Publish Guard Test (Attempting Publish with Blockers):")
        print(f"   Status: HTTP {status} (Correctly Rejected Bad Catalogue)")
        print(f"   Response: {publish_err.get('detail') if isinstance(publish_err, dict) else publish_err}\n")
        assert status == 400, f"Expected 400 Bad Request when blockers present, got {status}"

        # 8. Automated Admin Remediation via CMS REST API
        print(f"8. Content Editor Remediation via Admin API:")
        
        # A. Fix Show missing section ("Rhyme Rangers" -> section="songs")
        status, shows = request("http://localhost:8000/admin/shows", headers={"X-User-Role": "admin"})
        rhyme_rangers = next((s for s in shows if s["slug"] == "rhyme-rangers"), None)
        if rhyme_rangers and not rhyme_rangers.get("section"):
            s_status, _ = request(
                f"http://localhost:8000/admin/shows/{rhyme_rangers['id']}",
                method="PATCH",
                data={"section": "songs"},
                headers={"X-User-Role": "admin"}
            )
            print(f"   [+] Fixed Show 'Rhyme Rangers': Assigned section 'songs' (HTTP {s_status})")
        
        # B. Fix duplicate content_group (ep_9001)
        s_status, _ = request(
            "http://localhost:8000/admin/episodes/ep_9001",
            method="PATCH",
            data={"content_group": "motis-many-lives-s01e02-alt"},
            headers={"X-User-Role": "admin"}
        )
        print(f"   [+] Fixed Episode 'ep_9001': Reassigned unique content_group (HTTP {s_status})")

        # C. Upload missing artwork for ep_0036 (poster, banner, thumbnail)
        poster_file = SAMPLE_ASSETS_DIR / "poster_good.jpg"
        banner_file = SAMPLE_ASSETS_DIR / "banner_good.jpg"
        thumb_file = SAMPLE_ASSETS_DIR / "thumb_good.jpg"

        if poster_file.exists() and banner_file.exists() and thumb_file.exists():
            up_p_status, _ = upload_artwork_file("ep_0036", "poster", poster_file)
            up_b_status, _ = upload_artwork_file("ep_0036", "banner", banner_file)
            up_t_status, _ = upload_artwork_file("ep_0036", "thumbnail", thumb_file)
            print(f"   [+] Uploaded Artwork for 'ep_0036': Poster ({up_p_status}), Banner ({up_b_status}), Thumb ({up_t_status})")
        else:
            # Fallback: set to draft if sample image files not found
            request(
                "http://localhost:8000/admin/episodes/ep_0036",
                method="PATCH",
                data={"status": "draft"},
                headers={"X-User-Role": "admin"}
            )
            print(f"   [+] Set 'ep_0036' status to 'draft'")

        # 9. Verify Validation Report is Clean
        status, clean_report = request("http://localhost:8000/admin/validation-report", headers={"X-User-Role": "admin"})
        print(f"\n9. Re-Scan Validation Report Post-Remediation:")
        print(f"   Status: HTTP {status}")
        print(f"   Can Publish: {clean_report.get('can_publish')}")
        print(f"   Total Blockers: {clean_report.get('total_blockers')}")
        print(f"   Summary: {clean_report.get('summary')}\n")
        assert clean_report.get("can_publish") is True, f"Expected can_publish=True, got {clean_report.get('can_publish')}"

    # 10. Trigger Atomic Publication (Admin)
    status, body = request("http://localhost:8000/admin/catalog/publish", method="POST", headers={"X-User-Role": "admin"})
    print(f"10. Executing Atomic Catalogue Publication (Admin):")
    print(f"    Status: HTTP {status}")
    print(f"    Version: {body.get('catalogue_version')}")
    print(f"    Published Shows: {body.get('shows_count')}")
    print(f"    Published Episodes: {body.get('episodes_count')}")
    print(f"    File Path: {body.get('file_path')}\n")
    assert status == 200, f"Expected 200 OK on publish, got {status}"
    assert body.get("status") == "success", "Publish run status not success"

    # 11. Verify Viewer UI Catalogue Endpoint (GET /catalog)
    status, body = request("http://localhost:8000/catalog")
    print(f"11. Viewer Catalogue Verification (GET /catalog):")
    print(f"    Status: HTTP {status}")
    print(f"    Sections: {list(body.get('sections', {}).keys())}")
    print(f"    Total Shows in Published Feed: {body.get('total_shows')}")
    print(f"    Total Episodes in Published Feed: {body.get('total_episodes')}\n")
    assert status == 200, f"Expected 200 OK on /catalog, got {status}"
    assert body.get("total_shows", 0) > 0, "No shows found in published catalogue"

    # 12. Verify Composed Search Endpoint (GET /catalog/search)
    status, body = request("http://localhost:8000/catalog/search?q=moti&language=hi&section=featured")
    print(f"12. Composed Search Verification (GET /catalog/search?q=moti&language=hi&section=featured):")
    print(f"    Status: HTTP {status}")
    print(f"    Matched Shows: {body.get('matched_shows_count')}")
    print(f"    Result Titles: {[s['title'] for s in body.get('results', [])]}\n")
    assert status == 200, f"Expected 200 OK on /catalog/search, got {status}"
    assert body.get("matched_shows_count", 0) >= 1, "Expected at least 1 match for search query"

    print("=================================================================")
    print("    ALL LIVE INTEGRATION CHECKS PASSED PERFECTLY!               ")
    print("=================================================================")

if __name__ == "__main__":
    main()
