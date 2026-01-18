import os
import re
import logging
from collections import defaultdict
from datetime import datetime
from celery import Celery
from dotenv import load_dotenv
from app.core.database import SessionLocal
from app.models import match as match_models

# from app.models.user import User # Import se necessário

load_dotenv()

# Configuração de Log Profissional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "tasks", broker=os.getenv("REDIS_URL"), backend=os.getenv("REDIS_URL")
)


def split_log_into_match_chunks(log_content: str) -> list:
    logger.info("--- START: Split Log Chunks ---")
    lines = log_content.strip().split("\n")
    matches = []
    current_match_lines = []
    current_match_id = None
    current_start_time = None
    in_match = False

    start_pattern = re.compile(
        r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}) - New match (.*?) has started$"
    )

    logger.info(f"Total lines received: {len(lines)}")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        start_match = start_pattern.search(line)
        if start_match:
            # Lógica de fechamento da match anterior
            if in_match and current_match_lines and current_match_id:
                last_timestamp_end = None
                for l_end in reversed(current_match_lines):
                    ts_match_end = re.match(
                        r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", l_end
                    )
                    if ts_match_end:
                        try:
                            last_timestamp_end = datetime.strptime(
                                ts_match_end.group(1), "%d/%m/%Y %H:%M:%S"
                            )
                            break
                        except ValueError:
                            pass
                matches.append(
                    {
                        "match_id": current_match_id,
                        "lines": current_match_lines,
                        "start_time": current_start_time,
                        "end_time": last_timestamp_end,
                    }
                )

            timestamp_str, current_match_id = start_match.groups()
            try:
                current_start_time = datetime.strptime(
                    timestamp_str, "%d/%m/%Y %H:%M:%S"
                )
            except ValueError:
                logger.warning(f"Data inválida no início: {line}")
                current_start_time = None

            current_match_lines = [line]
            in_match = True

        elif in_match:
            current_match_lines.append(line)
            expected_end_line = f"Match {current_match_id} has ended"

            if expected_end_line in line:
                end_timestamp_str_match = re.match(
                    r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", line
                )
                current_end_time = None
                if end_timestamp_str_match:
                    try:
                        current_end_time = datetime.strptime(
                            end_timestamp_str_match.group(1), "%d/%m/%Y %H:%M:%S"
                        )
                    except ValueError:
                        logger.warning(f"Data inválida no fim: {line}")

                matches.append(
                    {
                        "match_id": current_match_id,
                        "lines": current_match_lines,
                        "start_time": current_start_time,
                        "end_time": current_end_time,
                    }
                )
                in_match = False
                current_match_lines = []
                current_match_id = None
                current_start_time = None

    if in_match and current_match_lines and current_match_id:
        last_timestamp_final = None
        for l_final in reversed(current_match_lines):
            ts_match_final = re.match(
                r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", l_final
            )
            if ts_match_final:
                try:
                    last_timestamp_final = datetime.strptime(
                        ts_match_final.group(1), "%d/%m/%Y %H:%M:%S"
                    )
                    break
                except ValueError:
                    pass
        logger.info(f"EOF Alcançado. Adicionando última partida {current_match_id}.")
        matches.append(
            {
                "match_id": current_match_id,
                "lines": current_match_lines,
                "start_time": current_start_time,
                "end_time": last_timestamp_final,
            }
        )

    logger.info(f"--- END: Split finished. Found {len(matches)} matches. ---")
    return matches


def process_match_chunk(match_lines: list) -> dict:
    players_stats = defaultdict(lambda: {"frags": 0, "deaths": 0})
    kills_log = []
    players_discovered = set()

    kill_pattern = re.compile(
        r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}) - (.*) killed (.*) using (.*)$"
    )
    world_kill_pattern = re.compile(
        r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}) - <WORLD> killed (.*) by (.*)$"
    )

    for line in match_lines:
        kill_match = kill_pattern.search(line)
        world_kill_match = world_kill_pattern.search(line)
        kill_time_obj = None

        if kill_match:
            timestamp_str, killer_name, victim_name, weapon = kill_match.groups()
            try:
                kill_time_obj = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
            except ValueError:
                pass

            players_discovered.add(killer_name)
            players_discovered.add(victim_name)
            players_stats[killer_name]["frags"] += 1
            players_stats[victim_name]["deaths"] += 1
            kills_log.append(
                {
                    "killer_name": killer_name,
                    "victim_name": victim_name,
                    "weapon": weapon,
                    "kill_time": kill_time_obj,
                }
            )

        elif world_kill_match:
            timestamp_str, victim_name, cause_of_death = world_kill_match.groups()
            try:
                kill_time_obj = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
            except ValueError:
                pass

            players_discovered.add(victim_name)
            players_stats[victim_name]["deaths"] += 1
            kills_log.append(
                {
                    "killer_name": "<WORLD>",
                    "victim_name": victim_name,
                    "weapon": cause_of_death,
                    "kill_time": kill_time_obj,
                }
            )

    players_final = []
    for player_name in players_discovered:
        stats = players_stats[player_name]
        players_final.append(
            {
                "player_name": player_name,
                "frags": stats["frags"],
                "deaths": stats["deaths"],
            }
        )

    return {"players": players_final, "kills": kills_log}


@celery_app.task(name="process_match_log_file_task", bind=True)
def process_match_log_file_task(self, file_path: str, task_id_str: str, user_id: int):
    logger.info(f"[TASK: {task_id_str}] INICIANDO: Processamento User ID {user_id}")
    db = SessionLocal()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            log_content = f.read()

        match_chunks = split_log_into_match_chunks(log_content)
        total_matches = len(match_chunks)

        if total_matches == 0:
            logger.warning(f"[TASK: {task_id_str}] Nenhuma partida encontrada.")
            return {"status": "completo", "total_processado": 0}

        for index, chunk in enumerate(match_chunks):
            match_id = chunk.get("match_id", f"unknown_match_{index}")
            start_time = chunk.get("start_time")
            end_time = chunk.get("end_time")

            try:
                processed_data = process_match_chunk(chunk.get("lines", []))
            except ValueError as e:
                logger.error(f"[TASK: {task_id_str}] Erro ao processar chunk: {e}")
                continue

            if not processed_data.get("players"):
                continue

            # Inserção com user_id
            new_match = match_models.Match(
                match_id=match_id,
                start_time=start_time,
                end_time=end_time,
                user_id=user_id,
            )
            db.add(new_match)
            db.commit()
            db.refresh(new_match)

            generated_uuid = new_match.id

            db_players = [
                match_models.Player(**player_data, match_id=generated_uuid)
                for player_data in processed_data["players"]
            ]
            db_kills = [
                match_models.Kill(**kill_data, match_id=generated_uuid)
                for kill_data in processed_data["kills"]
            ]

            db.add_all(db_players)
            db.add_all(db_kills)
            db.commit()

        logger.info(f"[TASK: {task_id_str}] CONCLUÍDO COM SUCESSO.")

    except Exception as e:
        logger.error(f"[TASK: {task_id_str}] ERRO FATAL: {e}")
        db.rollback()
        raise self.retry(exc=e, countdown=60)

    finally:
        db.close()
        # Limpeza do arquivo temporário (Reativada e Segura)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"🧹 Arquivo limpo: {file_path}")
            except OSError as e:
                logger.warning(f"⚠️ Falha ao deletar arquivo: {e}")

    return {"status": "completo", "total_processado": total_matches}
