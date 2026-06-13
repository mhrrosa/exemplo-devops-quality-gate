# 🚀 Guia de Implementação: Pipeline DevOps + IA Generativa (Aula 04)

Este guia documenta o passo a passo para a implementação do pipeline completo apresentado na Aula 04. O foco é a automação pós-Quality Gate: Deploy Gate com IA, Canary Deploy e Rollback Automático com análise de SRE via Groq.

## 📋 Visão Geral do Fluxo

O pipeline segue a jornada:
1.  **[Commit]**: Push dispara o pipeline.
2.  **[Tests + Coverage Gate]**: Pytest garante cobertura > 80%.
3.  **[Deploy Gate IA]**: Groq analisa logs e cobertura para decidir: `APPROVE` ou `BLOCK`.
4.  **[Canary Deploy]**: Simulação de tráfego progressivo (10% -> 50% -> 100%).
5.  **[Rollback + Issue]**: Se falhar, executa rollback, IA gera relatório técnico e abre Issue no GitHub.

---

## 🛠️ Passo 1: Preparação do Ambiente

Antes de iniciar, certifique-se de estar na branch correta e com as dependências instaladas.

```bash
# Criar branch de trabalho
git checkout -b feature/deploy-ia-completo

# Instalar bibliotecas necessárias
pip install groq pytest pytest-cov
```

### Configuração da API Key (GitHub Secrets)
Para que a IA funcione no GitHub Actions, você deve configurar o Secret:
1. Vá em **Settings** > **Secrets and variables** > **Actions**.
2. Clique em **New repository secret**.
3. Nome: `DEVOPS_SECRET` | Valor: Sua chave da Groq Cloud.

---

## 📸 Guia para Prints de Execução

Para seu relatório, você precisará de 3 cenários principais. Veja como forçar cada um:

### 1. Sucesso Total (Happy Path)
*   **Requisito**: Cobertura > 80% e métricas estáveis.
*   **Como fazer**: 
    1. Garanta que `tests_alta/` cubra bem o código.
    2. No script `deploy/canary_simulator.py`, certifique-se de que ele aponta para `metrics/system-aprovado.json`.
    3. Faça o push. 
*   **Print**: Tela do GitHub Actions com todos os steps em verde (check).

### 2. Bloqueio no Deploy Gate (IA diz BLOCK)
*   **Objetivo**: Mostrar a IA impedindo o deploy por baixa qualidade.
*   **Como forçar**:
    1. Crie ou altere o arquivo `coverage.json` manualmente para ter `"percent_covered": 40.0`.
    2. Comente temporariamente a etapa de execução de testes no YAML ou apenas execute o script de gate com esse arquivo presente.
*   **Print**: Log do step **Deploy Gate (Groq)** exibindo `Decision: BLOCK` e o motivo da IA.

### 3. Falha no Canary e Rollback Automático
*   **Objetivo**: Mostrar o sistema detectando erro em tempo real e revertendo.
*   **Como forçar**:
    1. No arquivo `deploy/canary_simulator.py`, altere a linha do arquivo de métricas para:
       `arquivo_metricas = raiz / "metrics" / "system-reprovado.json"`
    2. Faça o push.
*   **Print**: 
    - Step **Canary Deploy Simulator** com erro (vermelho).
    - Step **Rollback + Relatório IA** executado com sucesso.
    - **GitHub Issue** criada automaticamente com o relatório técnico da IA.

---

## 🤖 Detalhes Técnicos dos Scripts (Pasta `deploy/`)

### Deploy Gate (`deploy/deploy_gate.py`)
Analisa `coverage.json` e `logs/*.log`. 
**Comando local:** `py deploy/deploy_gate.py`

### Canary Simulator (`deploy/canary_simulator.py`)
Simula fases de 10%, 50% e 100%. Se as métricas em `metrics/` excederem os limites, ele retorna erro.
**Thresholds**: CPU < 80%, Erro < 5%, Latência < 800ms.

### Rollback Trigger (`deploy/rollback_trigger.py`)
Acionado apenas se o Canary falhar. Ele lê o último "trace" gerado, consulta a IA para um relatório de SRE e abre a Issue.

---

## ⚙️ Configuração do Workflow (`.github/workflows/pipeline-devops-ia.yml`)

O workflow utiliza a secret `DEVOPS_SECRET` para autenticação na API do Groq e o `GITHUB_TOKEN` padrão para criar as Issues em caso de falha.

```yaml
      - name: Deploy Gate (Groq)
        run: python deploy/deploy_gate.py
        env:
          GROQ_API_KEY: ${{ secrets.DEVOPS_SECRET }}

      - name: Canary Deploy Simulator
        run: python deploy/canary_simulator.py

      - name: Rollback + Relatório IA
        if: failure()
        run: python deploy/rollback_trigger.py
        env:
          GROQ_API_KEY: ${{ secrets.DEVOPS_SECRET }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---
**Automação com DevOps e IA Generativa**
*PUCPR - Prof. Lisiane Reips*
