import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from groq import Groq

def encontrar_ultimo_trace(traces_dir: Path) -> list | None:
    """Lê o trace mais recente do canary."""
    arquivos = sorted(traces_dir.glob("canary_*.json"), reverse=True)
    if not arquivos:
        return None
    return json.loads(arquivos[0].read_text(encoding="utf-8"))

def detectar_necessidade_rollback(trace: list) -> tuple[bool, dict]:
    """Verifica se alguma fase ultrapassou os thresholds."""
    for fase in trace:
        if (
            fase.get("cpu_pct", 0) >= 80 or
            fase.get("memory_pct", 0) >= 85 or
            fase.get("error_rate_pct", 0) >= 5.0 or
            fase.get("latency_ms", 0) >= 800
        ):
            return True, fase
    
    # Se não chegou a 100%, algo interrompeu o fluxo
    fases_aprovadas = [f["percentual_trafego"] for f in trace if f.get("fase_aprovada")]
    if 100 not in fases_aprovadas:
        return True, trace[-1] if trace else {}
        
    return False, {}

def executar_rollback_simulado(versao_anterior: str = "v1.0.0") -> str:
    """Simula rollback para versão anterior."""
    print(f"\n[Rollback] Executando rollback para a versão {versao_anterior}...")
    timestamp = datetime.now().isoformat()
    # Em um cenário real, aqui rodariam comandos de helm rollback, git revert, etc.
    print(f"[Rollback] Rollback concluído em {timestamp}")
    return timestamp

def gerar_relatorio_ia(trace, metricas_falha, timestamp_rollback) -> str:
    """Gera relatório de incidente usando Groq."""
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQCLOUD_API_KEY")
    if not api_key:
        return "Erro: GROQ_API_KEY não configurada. Não foi possível gerar o relatório via IA."

    client = Groq(api_key=api_key)
    
    prompt = f"""
Você é um engenheiro SRE (Site Reliability Engineer) sênior.
Analise o incidente ocorrido durante o Canary Deploy e produza um relatório técnico detalhado.

HISTÓRICO DO CANARY (TRACE):
{json.dumps(trace, indent=2, ensure_ascii=False)}

MÉTRICAS DA FASE QUE FALHOU:
{json.dumps(metricas_falha, indent=2, ensure_ascii=False)}

HORÁRIO DO ROLLBACK: {timestamp_rollback}

Instruções para o relatório:
1. Escreva em português.
2. Seja técnico e objetivo.
3. Estrutura:
   - Resumo do incidente
   - Causa Raiz Identificada (baseada nos thresholds de CPU, Memória, Erro ou Latência)
   - Impacto Estimado
   - Ações de Remediação Tomadas
   - Próximos Passos Recomendados
Máximo de 400 palavras.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_completion_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar Groq: {str(e)}"

def abrir_issue_github(titulo, corpo, labels=None):
    """Cria Issue usando gh CLI ou exibe localmente se falhar."""
    print("\n[GitHub] Tentando abrir issue de incidente...")
    cmd = ["gh", "issue", "create", "--title", titulo, "--body", corpo]
    
    if labels:
        for label in labels:
            cmd.extend(["--label", label])
            
    try:
        # Verifica se gh está autenticado
        auth_check = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        if auth_check.returncode != 0:
            raise FileNotFoundError("gh CLI não autenticado")

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[GitHub] Issue criada com sucesso: {result.stdout.strip()}")
        else:
            print(f"[GitHub] Falha ao criar issue: {result.stderr}")
            print(f"\n--- CONTEÚDO DA ISSUE (LOCAL) ---\nTítulo: {titulo}\n{corpo}\n")
    except (FileNotFoundError, Exception):
        print("[GitHub] gh CLI não disponível ou não autenticado. Exibindo relatório localmente:")
        print(f"\n--- CONTEÚDO DA ISSUE (LOCAL) ---\nTítulo: {titulo}\n{corpo}\n")

def main():
    raiz = Path(__file__).parent.parent
    traces_dir = raiz / "traces"
    
    print("\n" + "="*40)
    print("      SRE ROLLBACK TRIGGER & ANALYSIS")
    print("="*40 + "\n")

    trace = encontrar_ultimo_trace(traces_dir)
    if not trace:
        print("[Erro] Nenhum trace de canary encontrado em /traces.")
        sys.exit(0)

    precisa_rollback, metricas_falha = detectar_necessidade_rollback(trace)
    
    if not precisa_rollback:
        print("[Status] Deploy estável. Nenhuma anomalia detectada nos traces.")
        sys.exit(0)

    fase = metricas_falha.get("percentual_trafego", "Desconhecida")
    print(f"[Alerta] Anomalia detectada na fase {fase}%!")
    
    # 1. Executar rollback
    timestamp_rollback = executar_rollback_simulado()

    # 2. IA gera relatório
    print("\n[IA] Solicitando análise técnica ao Groq...")
    relatorio = gerar_relatorio_ia(trace, metricas_falha, timestamp_rollback)
    
    # 3. Abrir issue no GitHub
    titulo = (f"🔴 [ROLLBACK] Incidente Detectado no Deploy Canary - "
              f"Fase {fase}% - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    corpo = f"""## 🛡️ Relatório de Rollback Automático

{relatorio}

---
_Relatório gerado automaticamente pelo Pipeline DevOps + IA Generativa._
_ID do Trace: {datetime.now().strftime('%Y%m%d_%H%M%S')}_
"""
    
    abrir_issue_github(titulo, corpo, labels=["bug", "rollback", "automated-sre"])
    
    # Sai com erro para sinalizar falha no pipeline (mesmo após rollback)
    sys.exit(1)

if __name__ == "__main__":
    main()
