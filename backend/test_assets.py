import urllib.request
import json

def check_catalog():
    with urllib.request.urlopen("http://localhost:8000/catalog") as resp:
        data = json.load(resp)
        print(f"Total Shows: {data.get('total_shows')}")
        for sec_name, shows in data.get("sections", {}).items():
            print(f"\n=== Section: {sec_name} ({len(shows)} shows) ===")
            for s in shows[:2]:
                print(f"  * {s['title']}")
                print(f"    - Show Artworks: {s.get('artworks')}")
                if s.get("trailers"):
                    print(f"    - Trailer 1 Artworks: {s['trailers'][0].get('artworks')}")
                if s.get("seasons") and s["seasons"][0].get("episodes"):
                    ep1 = s["seasons"][0]["episodes"][0]
                    print(f"    - Ep 1 ({ep1['title']}) Artworks: {ep1.get('artworks')}")

def check_sample_assets():
    print("\n=== Checking Static Asset Endpoints ===")
    assets = [
        "http://localhost:8000/sample_assets/poster_good.jpg",
        "http://localhost:8000/sample_assets/banner_good.jpg",
        "http://localhost:8000/sample_assets/thumb_good.jpg",
        "http://localhost:3000/sample_assets/poster_good.jpg",
        "http://localhost:3001/sample_assets/poster_good.jpg",
    ]
    for url in assets:
        try:
            with urllib.request.urlopen(url) as resp:
                print(f"[+] {url} -> HTTP {resp.status} (Content-Type: {resp.headers.get('Content-Type')}, Length: {resp.headers.get('Content-Length')})")
        except Exception as e:
            print(f"[-] {url} -> FAILED: {e}")

if __name__ == "__main__":
    check_catalog()
    check_sample_assets()
