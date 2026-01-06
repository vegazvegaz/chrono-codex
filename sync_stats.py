import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://www.exophase.com/user/vegazvegaz/"

def get_stats():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(URL, headers=headers, timeout=25)
        soup = BeautifulSoup(response.text, 'html.parser')
        games = []

        for item in soup.select('.item.game'):
            try:
                name_tag = item.select_one('h3 a')
                if not name_tag: continue
                name = name_tag.text.strip()
                
                stats_list = item.select('.game-stats li')
                hours = 0
                for li in stats_list:
                    if 'Hours' in li.text:
                        found = re.findall(r"(\d+\.?\d*)", li.text.replace(',', ''))
                        if found: hours = float(found[0])
                
                comp = 0
                prog = item.select_one('.progress-bar span')
                if prog and 'style' in prog.attrs:
                    comp_match = re.search(r"width:\s*(\d+)%", prog['style'])
                    if comp_match: comp = int(comp_match.group(1))
                
                platform_icon = str(item.select_one('.platform-icon')['class']).lower()
                is_steam = 'steam' in platform_icon
                img = item.select_one('.game-image img')['src']

                games.append({
                    "name": name, "sH": hours if is_steam else 0, "pH": 0 if is_steam else hours,
                    "img": img, "last": 1736100000, "color": "#45b1e8" if is_steam else "#00439C",
                    "dev": "Exophase Sync", "rel": 2025, "comp": comp, 
                    "desc": f"Synchronisé depuis Exophase. Temps : {hours}h."
                })
            except: continue
        
        games.sort(key=lambda x: (x["sH"] + x["pH"]), reverse=True)
        return games
    except Exception as e:
        print(f"ERREUR : {e}")
        return None

def update_html(games):
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    json_data = json.dumps(games, indent=4, ensure_ascii=False)
    # Remplacement ultra-précis pour éviter de casser le design
    new_data_block = f"// START_DATA\n        const gamesData = {json_data};\n        // END_DATA"
    updated_content = re.sub(r"// START_DATA.*?// END_DATA", new_data_block, content, flags=re.DOTALL)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_content)

if __name__ == "__main__":
    new_games = get_stats()
    if new_games:
        update_html(new_games)
        print(f"OK : {len(new_games)} jeux injectés !")
