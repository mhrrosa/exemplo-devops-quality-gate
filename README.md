# exemplo-devops-quality-gate

## Objetivo do projeto

Automatizar decisões em um fluxo DevOps usando pipelines inteligentes com suporte de IA generativa para quality gates, observabilidade e agentes autônomos aplicados à SmartShop Cloud.

## Descrição dos pipelines

- Quality Gate com IA: executa testes com `pytest`, gera relatório de cobertura (`pytest-cov`) e consulta uma API de IA para decidir `APROVADO` ou `BLOQUEADO`.
- Observabilidade (Logs): analisa arquivos em `logs/`, identifica erros críticos e cria issues automaticamente quando necessário.
- Observabilidade (Métricas): interpreta JSONs em `metrics/` para detectar degradação e risco operacional.
- Observabilidade (Traces): processa `traces/` para identificar gargalos e apontar serviços problemáticos.
- Agente de Testes: avalia cobertura e pode bloquear deploys ou criar issues sugerindo correções.

## Exemplos de execução

- Quality Gate: cobertura baixa → IA responde `BLOQUEADO` → workflow falha e bloqueia deploy.
- Logs: entrada `ERROR Database timeout` ou `CRITICAL Falha na tarefa` → IA classifica como crítica → issue criada automaticamente.
- Métricas: `{ "cpu": 92, "memory": 88, "latency_ms": 3000 }` → IA sinaliza risco operacional → alerta/issue gerado.
- Traces: `Frontend -> API Gateway -> Payment Service -> Database` com alta latência em `Payment Service` → IA indica `Payment Service` como gargalo.

## Tecnologias utilizadas

- Python 3.x
- pytest, pytest-cov
- GitHub Actions
- Ferramentas HTTP para consumir APIs de IA (configuradas via Secrets)

## Prints das execuções

_Seção reservada para capturas (manter em branco neste repositório)._ 

