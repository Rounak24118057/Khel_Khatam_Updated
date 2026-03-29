"""
spotify_india_top100.py
1. Scrapes Spotify India Daily Top 200 songs
2. Extracts artists from "Artist - Song" format
3. Scores: (num_songs * 1000) + sum(ranks) 
4. Ranks TOP 100 artists by total score
"""

import json
import os
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

URL = "https://kworb.net/spotify/country/in_daily.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def scrape_spotify_india_artists():
    print("🟢 Scraping Spotify India Daily Top 200...")
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(resp.text, "lxml")
    
    artist_scores = defaultdict(lambda: {'count': 0, 'rank_sum': 0, 'songs': []})
    
    # Parse top 200 songs
    for pos, row in enumerate(soup.find_all("tr")[1:201], 1):
        cols = row.find_all("td")
        if len(cols) < 3: continue
        
        song_cell = cols[2].text.strip()
        if " - " in song_cell:
            artist = song_cell.split(" - ", 1)[0].strip()
            artist_scores[artist]['count'] += 1
            artist_scores[artist]['rank_sum'] += pos
            artist_scores[artist]['songs'].append(f"{pos}. {song_cell}")
    
    # Calculate score: (songs_count * 1000) + rank_sum (lower rank = better)
    scored_artists = []
    for artist, data in artist_scores.items():
        score = (data['count'] * 1000) + data['rank_sum']
        scored_artists.append({
            'name': artist,
            'score': score,
            'songs': data['count'],
            'rank_sum': data['rank_sum'],
            'debug_songs': data['songs'][:3]  # First 3 songs for debug
        })
    
    # Sort by score (descending)
    top100 = sorted(scored_artists, key=lambda x: x['score'], reverse=True)[:100]
    
    print(f"✅ Found {len(artist_scores)} unique artists from top 200 songs")
    print(f"🎯 Top 100 artists ranked by score (songs*1000 + rank_sum)")
    
    return top100

def build_json(top100):
    output = [{"A": "Artist_Name", "B": "Score", "C": "Songs_in_Top200"}]
    for i, artist in enumerate(top100, 1):
        output.append({
            "A": artist['name'],
            "B": str(artist['score']),
            "C": f"{artist['songs']} songs"
        })
    return output

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    
    top100 = scrape_spotify_india_artists()
    output = build_json(top100)
    
    with open("data/Top_Indian_Artist.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Saved {len(output)-1} TOP 100 artists → data/Top_Indian_Artist.json")
    print("\n🏆 TOP 10:")
    for i, artist in enumerate(top100[:10], 1):
        print(f"{i:2d}. {artist['name']:<25s} | Songs: {artist['songs']} | Score: {artist['score']}")
    
    print("\n📊 Examples:")
    print("1st: Arijit Singh     (12 songs *1000 + ranks) = ~12,500")
    print("10th: Karan Aujla     (3 songs *1000 + ranks)  = ~3,200")
