import json
import uuid
from datetime import datetime, timedelta

print("Iniciando a geração de 1000 objetos de partida...")

matches = []
base_time = datetime.now()

for i in range(1000):
    start_time = base_time + timedelta(minutes=i*10)
    end_time = start_time + timedelta(minutes=9)

    match = {
        "match_id": f"test_match_{uuid.uuid4()}",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    matches.append(match)

# Salva a lista de objetos em um arquivo JSON
file_name = "test_1000_matches.json"
with open(file_name, 'w') as f:
    json.dump(matches, f, indent=4)

print(f"Sucesso! Arquivo '{file_name}' criado com 1000 objetos.")