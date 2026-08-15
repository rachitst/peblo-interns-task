import json
from pathlib import Path
from app.config import settings

def test_composed_search_filter_logic():
    # Mock catalogue data
    sample_catalogue = {
        "sections": {
            "featured": [
                {
                    "id": "show_1",
                    "title": "Moti's Many Lives",
                    "slug": "motis-many-lives",
                    "section": "featured",
                    "categories": ["adventure", "india", "friendship"],
                    "synopsis": "Moti the dog is reborn across India",
                    "seasons": [
                        {
                            "season_number": 1,
                            "episodes": [
                                {
                                    "title": "The Lost Kite",
                                    "languages": ["en", "hi"],
                                    "synopsis": "A fun kite adventure",
                                }
                            ]
                        }
                    ],
                    "trailers": []
                }
            ],
            "series": [
                {
                    "id": "show_2",
                    "title": "Number Nest",
                    "slug": "number-nest",
                    "section": "series",
                    "categories": ["learning", "maths"],
                    "synopsis": "Counting numbers with birds",
                    "seasons": [
                        {
                            "season_number": 1,
                            "episodes": [
                                {
                                    "title": "One to Ten",
                                    "languages": ["en"],
                                    "synopsis": "Sing along counting",
                                }
                            ]
                        }
                    ],
                    "trailers": []
                }
            ]
        }
    }
    
    # 1. Search by show title case-insensitive
    q = "moti"
    matched = [s for s in sample_catalogue["sections"]["featured"] if q in s["title"].lower()]
    assert len(matched) == 1
    
    # 2. Search by category
    q_cat = "maths"
    matched_cat = [s for s in sample_catalogue["sections"]["series"] if any(q_cat in c for c in s["categories"])]
    assert len(matched_cat) == 1
    
    # 3. Search by episode title
    q_ep = "lost kite"
    matched_ep = [
        s for s in sample_catalogue["sections"]["featured"]
        if any(q_ep in ep["title"].lower() for sea in s["seasons"] for ep in sea["episodes"])
    ]
    assert len(matched_ep) == 1

    # 4. Composed filter: query 'moti' + category 'adventure' + language 'hi' + section 'featured'
    q_query = "MOTI".lower()
    cat_filt = "adventure"
    lang_filt = "hi"
    sec_filt = "featured"
    
    all_shows = sample_catalogue["sections"]["featured"] + sample_catalogue["sections"]["series"]
    results = []
    for s in all_shows:
        if sec_filt and s["section"] != sec_filt:
            continue
        if cat_filt and cat_filt not in [c.lower() for c in s["categories"]]:
            continue
        s_langs = set(l for sea in s["seasons"] for ep in sea["episodes"] for l in ep["languages"])
        if lang_filt and lang_filt not in s_langs:
            continue
        if q_query:
            match = q_query in s["title"].lower() or any(q_query in c for c in s["categories"])
            if not match:
                continue
        results.append(s)
        
    assert len(results) == 1
    assert results[0]["id"] == "show_1"
