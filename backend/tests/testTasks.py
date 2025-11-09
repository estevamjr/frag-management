# backend/tests/test_tasks.py
import os
from app.tasks import split_log_into_match_chunks

# Define o caminho para o nosso log de amostra
SAMPLE_LOG_FILE = os.path.join(os.path.dirname(__file__), 'sample_log.txt')

def test_split_log_into_match_chunks():
    """
    Testa a função principal de divisão de log.
    Este é um teste unitário: ele testa apenas esta função,
    sem depender de banco de dados ou API.
    """
    
    # 1. Preparação (Arrange)
    # Garante que nosso arquivo de log de exemplo existe
    assert os.path.exists(SAMPLE_LOG_FILE), "O arquivo sample_log.txt não foi encontrado na pasta 'tests/'"
    
    # Lê o conteúdo do log de exemplo
    with open(SAMPLE_LOG_FILE, 'r') as f:
        log_content = f.read()
    
    # 2. Ação (Act)
    # Roda a função que queremos testar
    matches = split_log_into_match_chunks(log_content)
    
    # 3. Verificação (Assert)
    # Verifica se os resultados são os esperados
    
    # Deve encontrar exatamente 2 partidas neste log
    assert len(matches) == 2, f"Esperado 2 partidas, mas {len(matches)} foram encontradas"
    
    # Verifica a primeira partida
    match_1 = matches[0]
    assert match_1["match_id"] == "match_001"
    assert match_1["start_time"] is not None
    assert match_1["end_time"] is not None
    # Verifica se a linha de kill está presente (total de 5 linhas de log)
    assert len(match_1["lines"]) == 5 

    # Verifica a segunda partida
    match_2 = matches[1]
    assert match_2["match_id"] == "match_002"
    assert match_2["start_time"] is not None
    # A segunda partida não tem "end_time" explícito no log
    assert match_2["end_time"] is not None, "O end_time da segunda partida (extraído da última linha) não foi pego"
    assert len(match_2["lines"]) == 4