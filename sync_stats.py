import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://www.exophase.com/user/vegazvegaz/"

def get_stats():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(URL, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        games = []
        for item in soup.select('.item.game'):
            try:
                name = item.select_one('h3 a').text.strip()
                hours = 0
                for li in item.select('.game-stats li'):
                    if 'Hours' in li.text:
                        h_match = re.search(r"(\d+\.?\d*)", li.text.replace(',', ''))
                        if h_match: hours = float(h_match.group(1))
                comp = 0
                prog = item.select_one('.progress-bar span')
                if prog and 'style' in prog.attrs:
                    c_match = re.search(r"width:\s*(\d+)%", prog['style'])
                    if c_match: comp = int(c_match.group(1))
                platform = str(item.select_one('.platform-icon')['class']).lower()
                is_steam = 'steam' in platform
                img = item.select_one('.game-image img')['src']
                games.append({
                    "name": name, "sH": hours if is_steam else 0, "pH": 0 if is_steam else hours,
                    "img": img, "last": 1736150000, "color": "#45b1e8" if is_steam else "#00439C",
                    "dev": "Sync", "rel": 2025, "comp": comp, "desc": "Stats réelles Exophase."
                })
            except: continue
        if games:
            games.sort(key=lambda x: (x["sH"] + x["pH"]), reverse=True)
            return games
    except Exception as e:
        print(f"Erreur Sync : {e}")
    return None

def update_html(games):
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacement ciblé entre les marqueurs SYNC_ZONE
    json_data = json.dumps(games, ensure_ascii=False)
    pattern = r"// SYNC_ZONE_START.*?// SYNC_ZONE_END"
    replacement = f"// SYNC_ZONE_START\n        const gamesData = {json_data};\n        // SYNC_ZONE_END"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    data = get_stats()
    if data:
        update_html(data)
        print(f"SUCCÈS : {len(data)} jeux synchronisés dans index.html")
    else:
        print("ERREUR : Aucune donnée trouvée")
