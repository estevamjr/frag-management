import json
import uuid
import random
from datetime import datetime, timedelta

print("Iniciando a geração de 1000 partidas completas...")

# --- Configurações da Simulação ---
NUM_MATCHES = 1000
PLAYERS_PER_MATCH = (5, 15)  # Gera entre 5 e 15 jogadores por partida
KILLS_PER_MATCH = (10, 50) # Gera entre 10 e 50 kills por partida
WEAPONS = ["AK-47", "M4A4", "AWP", "Desert Eagle", "USP-S"]
# ---------------------------------

all_matches = []
base_time = datetime.now()

for i in range(NUM_MATCHES):
    match_id = f"match_complex_{uuid.uuid4()}"
    
    # 1. Gera Players para esta partida
    players_list = [f"Player_{uuid.uuid4().hex[:6]}" for _ in range(random.randint(*PLAYERS_PER_MATCH))]
    players_data = []
    for player in players_list:
        players_data.append({
            "player_name": player,
            "frags": random.randint(0, 30),
            "deaths": random.randint(0, 20)
        })
        
    # 2. Gera Kills para esta partida
    kills_data = []
    for _ in range(random.randint(*KILLS_PER_MATCH)):
        kills_data.append({
            "killer_name": random.choice(players_list),
            "victim_name": random.choice(players_list),
            "weapon": random.choice(WEAPONS)
        })

    start_time = base_time + timedelta(minutes=i*10)
    end_time = start_time + timedelta(minutes=9)
        
    # 3. Monta o objeto da Partida
    match_object = {
        "match_id": match_id,
        "players": players_data,
        "kills": kills_data,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    all_matches.append(match_object)

# 4. Salva o arquivo JSON
file_name = "test_1000_matches_full.json"
with open(file_name, 'w') as f:
    json.dump(all_matches, f, indent=2)

print(f"Sucesso! Arquivo '{file_name}' criado com {NUM_MATCHES} partidas (com players e kills).")