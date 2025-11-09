import uuid
import random
from datetime import datetime, timedelta

print("Iniciando a geração do arquivo de log (.txt) com 1000 partidas...")

# --- Configurações da Simulação ---
NUM_MATCHES = 1000
PLAYERS_PER_MATCH = (5, 10)
KILLS_PER_MATCH = (10, 30)
WEAPONS = ["AK-47", "M4A4", "AWP", "Desert Eagle", "USP-S"]
# ---------------------------------

log_lines = []
current_time = datetime.now()

for i in range(NUM_MATCHES):
    match_id = f"sim_match_{i+1}_{uuid.uuid4().hex[:8]}"
    start_time_match = current_time
    
    # Linha de Início da Partida
    log_lines.append(f"{start_time_match.strftime('%d/%m/%Y %H:%M:%S')} - New match {match_id} has started")
    
    # Gera Players para esta partida
    players_list = [f"Player_{uuid.uuid4().hex[:4]}" for _ in range(random.randint(*PLAYERS_PER_MATCH))]
    
    # Gera Kills (simula eventos ao longo de 10 minutos)
    num_kills = random.randint(*KILLS_PER_MATCH)
    for k in range(num_kills):
        kill_time = start_time_match + timedelta(seconds=random.randint(10, 590))
        killer = random.choice(players_list)
        victim = random.choice([p for p in players_list if p != killer]) # Garante que não se mate
        weapon = random.choice(WEAPONS)
        log_lines.append(f"{kill_time.strftime('%d/%m/%Y %H:%M:%S')} - {killer} killed {victim} using {weapon}")

    # Linha de Fim da Partida (10 minutos depois do início)
    end_time_match = start_time_match + timedelta(minutes=10)
    log_lines.append(f"{end_time_match.strftime('%d/%m/%Y %H:%M:%S')} - Match {match_id} has ended")
    
    # Avança o tempo para a próxima partida
    current_time = end_time_match + timedelta(minutes=random.randint(1, 5))

# Salva as linhas no arquivo de log
file_name = "test_1000_matches.log"
with open(file_name, 'w', encoding='utf-8') as f:
    for line in log_lines:
        f.write(line + "\n")

print(f"Sucesso! Arquivo '{file_name}' criado com {NUM_MATCHES} partidas simuladas no formato de log.")