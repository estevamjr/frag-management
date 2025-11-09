# backend/app/tasks.py

import os
import time
import re # Módulo de Expressões Regulares
import uuid
from collections import defaultdict # Para contar frags/deaths facilmente
from datetime import datetime # Para conversão de timestamp
from celery import Celery
from dotenv import load_dotenv
from app.core.database import SessionLocal
from app.models import match as match_models

load_dotenv()

celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
)

# --- FUNÇÕES DE LÓGICA DE PARSING (COM TIMESTAMPS E CORREÇÃO) ---

def split_log_into_match_chunks(log_content: str) -> list:
    """
    Divide o log (formato simulado ou CSGO.txt) em blocos, um por partida,
    incluindo start_time e end_time.
    """
    print("--- DEBUG: split_log_into_match_chunks ---")
    lines = log_content.strip().split('\n')
    matches = []
    current_match_lines = []
    current_match_id = None
    current_start_time = None # Armazena o datetime do início
    in_match = False

    # Regex para capturar timestamp e ID do início
    start_pattern = re.compile(r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}) - New match (.*?) has started$")

    print(f"Total lines received: {len(lines)}")
    line_counter = 0

    for line in lines:
        line_counter += 1
        line = line.strip()
        if not line:
            continue

        start_match = start_pattern.search(line)
        if start_match:
            print(f"!!! START MATCH FOUND on line {line_counter}: '{line}'")
            # Salva partida anterior, se houver
            if in_match and current_match_lines and current_match_id:
                 last_timestamp_end = None
                 for l_end in reversed(current_match_lines):
                     ts_match_end = re.match(r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", l_end)
                     if ts_match_end:
                         try:
                             last_timestamp_end = datetime.strptime(ts_match_end.group(1), '%d/%m/%Y %H:%M:%S')
                             break
                         except ValueError:
                             pass
                 matches.append({
                    "match_id": current_match_id,
                    "lines": current_match_lines,
                    "start_time": current_start_time,
                    "end_time": last_timestamp_end
                })

            # Inicia nova partida
            timestamp_str, current_match_id = start_match.groups()
            try:
                current_start_time = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                 print(f"AVISO: Formato de data inválido na linha de início: {line}")
                 current_start_time = None

            current_match_lines = [line]
            in_match = True

        elif in_match:
            current_match_lines.append(line)

            # --- CORREÇÃO: Use simple string checking instead of regex format ---
            # Monta a string exata que esperamos para o fim da partida
            expected_end_line = f"Match {current_match_id} has ended"

            # Verifica se a linha ATUAL contém a string de fim
            if expected_end_line in line:
                print(f"!!! END MATCH FOUND for {current_match_id} on line {line_counter}: '{line}'")

                # Extrai o timestamp do início da linha de fim
                end_timestamp_str_match = re.match(r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", line)
                current_end_time = None
                if end_timestamp_str_match:
                    try:
                        current_end_time = datetime.strptime(end_timestamp_str_match.group(1), '%d/%m/%Y %H:%M:%S')
                    except ValueError:
                        print(f"AVISO: Formato de data inválido na linha de fim: {line}")
                else:
                     print(f"AVISO: Não foi possível extrair timestamp da linha de fim: {line}")
                # --- FIM DA CORREÇÃO ---

                matches.append({
                    "match_id": current_match_id,
                    "lines": current_match_lines,
                    "start_time": current_start_time,
                    "end_time": current_end_time # Usa o timestamp extraído da linha de fim
                })
                # Reseta para a próxima partida
                in_match = False
                current_match_lines = []
                current_match_id = None
                current_start_time = None

    # Adiciona a última partida se o log terminar sem uma linha de fim explícita
    if in_match and current_match_lines and current_match_id:
         last_timestamp_final = None
         for l_final in reversed(current_match_lines):
             ts_match_final = re.match(r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", l_final)
             if ts_match_final:
                 try:
                     last_timestamp_final = datetime.strptime(ts_match_final.group(1), '%d/%m/%Y %H:%M:%S')
                     break
                 except ValueError:
                     pass
         print(f"!!! EOF REACHED: Adding last match {current_match_id} found.")
         matches.append({
            "match_id": current_match_id,
            "lines": current_match_lines,
            "start_time": current_start_time,
            "end_time": last_timestamp_final
        })

    print(f"--- DEBUG: Finished splitting. Found {len(matches)} matches. ---")

    if not matches:
        print("WARNING: No matches were added to the list.")

    return matches

def process_match_chunk(match_lines: list) -> dict:
    """
    Recebe as linhas de UMA partida (formato CSGO.txt) e extrai
    jogadores (com frags/deaths) e kills (com kill_time).
    """
    players_stats = defaultdict(lambda: {"frags": 0, "deaths": 0})
    kills_log = []
    players_discovered = set()

    # Regex com captura de timestamp
    kill_pattern = re.compile(r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}) - (.*) killed (.*) using (.*)$")
    world_kill_pattern = re.compile(r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}) - <WORLD> killed (.*) by (.*)$")

    for line in match_lines:
        kill_match = kill_pattern.search(line)
        world_kill_match = world_kill_pattern.search(line)

        kill_time_obj = None # Reseta para cada linha

        if kill_match:
            timestamp_str, killer_name, victim_name, weapon = kill_match.groups()
            try:
                kill_time_obj = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                print(f"AVISO: Formato de data inválido na linha de kill: {line}")

            players_discovered.add(killer_name)
            players_discovered.add(victim_name)
            players_stats[killer_name]["frags"] += 1
            players_stats[victim_name]["deaths"] += 1
            kills_log.append({
                "killer_name": killer_name,
                "victim_name": victim_name,
                "weapon": weapon,
                "kill_time": kill_time_obj
            })

        elif world_kill_match:
            timestamp_str, victim_name, cause_of_death = world_kill_match.groups()
            try:
                kill_time_obj = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                print(f"AVISO: Formato de data inválido na linha de world kill: {line}")

            players_discovered.add(victim_name)
            players_stats[victim_name]["deaths"] += 1
            kills_log.append({
                "killer_name": "<WORLD>",
                "victim_name": victim_name,
                "weapon": cause_of_death,
                "kill_time": kill_time_obj
            })

    players_final = []
    for player_name in players_discovered:
         stats = players_stats[player_name]
         players_final.append({
             "player_name": player_name, "frags": stats["frags"], "deaths": stats["deaths"]
         })

    if not players_final:
         print(f"WARNING: No players found for this chunk starting with: {match_lines[0] if match_lines else 'EMPTY CHUNK'}")
         return {"players": [], "kills": []}

    return {"players": players_final, "kills": kills_log}


# --- TAREFA PRINCIPAL DO CELERY ---

@celery_app.task(name="process_match_log_file_task", bind=True)
def process_match_log_file_task(self, file_path: str, task_id_str: str):
    """
    3. POST /matches/upload (Padrão Ouro)
    Orquestra o processamento de um arquivo de log (formato CSGO.txt),
    partida por partida, incluindo timestamps.
    """
    print(f"[TASK: {task_id_str}] INICIANDO: Processamento do arquivo {file_path}")
    db = SessionLocal()

    try:
        # --- ETAPA 1: LER O ARQUIVO DE LOG ---
        with open(file_path, 'r', encoding='utf-8') as f:
            log_content = f.read()

        # --- ETAPA 2: DIVIDIR O LOG EM PARTIDAS ---
        match_chunks = split_log_into_match_chunks(log_content)
        total_matches = len(match_chunks)
        print(f"[TASK: {task_id_str}] Resultado do split: Encontradas {total_matches} partidas.")

        if total_matches == 0:
             print(f"[TASK: {task_id_str}] Nenhuma partida encontrada. Encerrando processamento.")
             return {"status": "completo", "total_processado": 0}

        # --- ETAPA 3: PROCESSAR CADA PARTIDA (LOOP) ---
        for index, chunk in enumerate(match_chunks):
            match_id = chunk.get('match_id', f'unknown_match_{index}')
            start_time = chunk.get('start_time') # Pega o datetime do início
            end_time = chunk.get('end_time')     # Pega o datetime do fim
            print(f"[TASK: {task_id_str}] Processando partida {index + 1}/{total_matches} (ID: {match_id})")

            # --- ETAPA 4: PROCESSAR LINHAS DA PARTIDA ---
            try:
                processed_data = process_match_chunk(chunk.get('lines', []))
            except ValueError as e:
                print(f"[TASK: {task_id_str}] AVISO: Pulando partida {match_id}. Motivo: {e}")
                continue

            if not processed_data.get('players'):
                 print(f"[TASK: {task_id_str}] AVISO: Pulando partida {match_id}. Nenhum jogador processado.")
                 continue

            # --- ETAPA 5: INSERÇÃO NO BANCO (Partida por Partida) ---
            new_match = match_models.Match(
                match_id=match_id,
                start_time=start_time,
                end_time=end_time
            )
            db.add(new_match)
            db.commit()
            db.refresh(new_match)

            generated_uuid = new_match.id

            db_players = [
                match_models.Player(**player_data, match_id=generated_uuid)
                for player_data in processed_data['players']
            ]
            db_kills = [
                match_models.Kill(**kill_data, match_id=generated_uuid)
                for kill_data in processed_data['kills']
            ]

            db.add_all(db_players)
            db.add_all(db_kills)
            db.commit()

        print(f"[TASK: {task_id_str}] TERMINADO: Processamento concluído.")

    except ValueError as ve: # Pega o erro se NENHUMA partida for encontrada
        print(f"[TASK: {task_id_str}] ERRO DE PROCESSAMENTO: {ve}")
        db.rollback()
        raise ve

    except Exception as e:
        print(f"[TASK: {task_id_str}] ERRO INESPERADO: {e}")
        db.rollback()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()
        # Opcional: Excluir o arquivo temporário
        # try:
        #     os.remove(file_path)
        # except OSError:
        #     pass

    return {"status": "completo", "total_processado": total_matches}