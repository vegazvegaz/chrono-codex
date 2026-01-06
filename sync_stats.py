import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://www.exophase.com/user/vegazvegaz/"

def get_stats():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        print(f"Visite de {URL}...")
        response = requests.get(URL, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        games = []

        # Ciblage des éléments de jeux
        items = soup.select('.item.game')
        print(f"Trouvé {len(items)} éléments de jeux potentiels.")

        for item in items:
            try:
                name_tag = item.select_one('h3 a')
                if not name_tag: continue
                name = name_tag.text.strip()
                
                # Heures - On cherche le LI qui contient 'Hours'
                hours = 0
                stats = item.select('.game-stats li')
                for s in stats:
                    if 'Hours' in s.text:
                        h_match = re.search(r"(\d+\.?\d*)", s.text.replace(',', ''))
                        if h_match: hours = float(h_match.group(1))
                
                # Complétion
                comp = 0
                prog = item.select_one('.progress-bar span')
                if prog and 'style' in prog.attrs:
                    c_match = re.search(r"width:\s*(\d+)%", prog['style'])
                    if c_match: comp = int(c_match.group(1))
                
                # Plateforme (Steam ou PS)
                p_icon = str(item.select_one('.platform-icon')['class']).lower()
                is_steam = 'steam' in p_icon
                
                # Image
                img = item.select_one('.game-image img')['src']

                games.append({
                    "name": name, "sH": hours if is_steam else 0, "pH": 0 if is_steam else hours,
                    "img": img, "last": 1736100000, "color": "#45b1e8" if is_steam else "#00439C",
                    "dev": "Exophase Sync", "rel": 2025, "comp": comp, 
                    "desc": f"Dernière session : {hours}h jouées."
                })
            except Exception as e:
                print(f"Erreur sur un jeu : {e}")
                continue
        
        print(f"Total de {len(games)} jeux validés.")
        games.sort(key=lambda x: (x["sH"] + x["pH"]), reverse=True)
        return games
    except Exception as e:
        print(f"ERREUR SYNC : {e}")
        return None

def update_html(games):
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    json_data = json.dumps(games, indent=4, ensure_ascii=False)
    # Marqueur ultra-simple pour éviter les erreurs de regex
    pattern = r"/\* START_DATA \*/.*?/\* END_DATA \*/"
    new_block = f"/* START_DATA */\n        const gamesData = {json_data};\n        /* END_DATA */"
    
    if "/* START_DATA */" not in content:
        print("CRITIQUE : Marqueurs START_DATA non trouvés dans index.html !")
        return

    updated_content = re.sub(pattern, new_block, content, flags=re.DOTALL)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print("Mise à jour de index.html terminée.")

if __name__ == "__main__":
    new_games = get_stats()
    if new_games and len(new_games) > 0:
        update_html(new_games)
        print("SYNCHRONISATION REUSSIE ✅")
    else:
        print("AUCUNE DONNÉE TROUVÉE ❌")
