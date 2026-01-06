import requests
from bs4 import BeautifulSoup
import json
import re
import time

# ON DÉFINIT LES DEUX SOURCES SÉPARÉMENT
URLS = {
    "playstation": "https://www.exophase.com/user/vegazvegaz/?platform=playstation",
    "steam": "https://www.exophase.com/user/vegazvegaz/?platform=steam"
}

def fetch_platform(platform, url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        print(f"Extraction {platform}...")
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for item in soup.select('.item.game'):
            try:
                name = item.select_one('h3 a').text.strip()
                hours = 0
                for li in item.select('.game-stats li'):
                    if 'Hours' in li.text:
                        h_match = re.findall(r"(\d+\.?\d*)", li.text.replace(',', ''))
                        if h_match: hours = float(h_match[0])
                
                comp = 0
                prog = item.select_one('.progress-bar span')
                if prog and 'style' in prog.attrs:
                    c_match = re.search(r"width:\s*(\d+)%", prog['style'])
                    if c_match: comp = int(c_match.group(1))
                
                img = item.select_one('.game-image img')['src']
                
                results.append({
                    "name": name,
                    "sH": hours if platform == "steam" else 0,
                    "pH": hours if platform == "playstation" else 0,
                    "img": img,
                    "last": int(time.time()),
                    "color": "#45b1e8" if platform == "steam" else "#00439C",
                    "comp": comp,
                    "desc": f"Donnée synchronisée via {platform.upper()}."
                })
            except: continue
        return results
    except Exception as e:
        print(f"Erreur sur {platform}: {e}")
        return []

if __name__ == "__main__":
    all_games = []
    
    # 1. On récupère Steam
    steam_data = fetch_platform("steam", URLS["steam"])
    # 2. On récupère PSN
    psn_data = fetch_platform("playstation", URLS["playstation"])
    
    # 3. Fusion (Si un jeu est sur les deux, on cumule)
    merged = {}
    for g in steam_data + psn_data:
        name = g["name"]
        if name not in merged:
            merged[name] = g
        else:
            merged[name]["sH"] += g["sH"]
            merged[name]["pH"] += g["pH"]
    
    final_list = list(merged.values())
    final_list.sort(key=lambda x: (x["sH"] + x["pH"]), reverse=True)
    
    if final_list:
        with open('data.js', 'w', encoding='utf-8') as f:
            f.write(f"const gamesData = {json.dumps(final_list, indent=4, ensure_ascii=False)};")
        print(f"Félicitations : {len(final_list)} jeux fusionnés dans data.js")
