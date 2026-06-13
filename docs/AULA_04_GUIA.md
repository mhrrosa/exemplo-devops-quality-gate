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

# Instalar biblioteca do Groq
pip install groq
```

### Configuração da API Key
Para que a IA funcione, você deve configurar a chave da API do Groq em seu ambiente:

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="sua_chave_aqui"
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="sua_chave_aqui"
```

---

## 🤖 Passo 2: Deploy Gate com IA (scripts/deploy_gate.py)

O script `deploy_gate.py` atua como um porteiro inteligente. Ele lê o arquivo `coverage.json` e os arquivos na pasta `logs/` para enviar um prompt estruturado ao modelo `llama-3.3-70b-versatile`.

**Como testar localmente:**
1.  Altere o arquivo `logs/app.log` para conter erros ou mensagens de sucesso.
2.  Execute o script:
    ```bash
    python scripts/deploy_gate.py
    ```

---

## 🐤 Passo 3: Canary Deploy Simulado (scripts/canary_simulator.py)

O Canary libera o código gradualmente. Ele monitora métricas de CPU, Memória, Erros e Latência.

**Thresholds configurados:**
*   **CPU**: < 80%
*   **Memória**: < 85%
*   **Erro**: < 5.0%
*   **Latência**: < 800ms

**Como testar localmente:**
1.  O script usa por padrão `metrics/system-aprovado.json`.
2.  Execute:
    ```bash
    python scripts/canary_simulator.py
    ```
3.  Para simular falha, altere o script para usar `metrics/system-reprovado.json`.

---

## 🛡️ Passo 4: Rollback Automático e Análise SRE (scripts/rollback_trigger.py)

Este é o componente mais avançado. Se o Canary falhar, este script:
1.  Localiza o último **Trace** (evidência) gerado pelo Canary.
2.  Executa um **Rollback simulado**.
3.  Envia os dados da falha para a IA (Groq) gerar um **Relatório Técnico de Incidente**.
4.  Abre uma **GitHub Issue** automaticamente com o relatório.

**Como testar localmente:**
```bash
# Primeiro, gere um trace de falha (ajustando o canary_simulator para falhar)
python scripts/canary_simulator.py

# Depois, execute o trigger de rollback
python scripts/rollback_trigger.py
```

---

## ⚙️ Passo 5: Integração com GitHub Actions

Para rodar tudo automaticamente no GitHub, adicione os steps ao seu workflow ou crie um novo `.github/workflows/deploy-completo.yml`.

### Exemplo de Steps no Workflow:

```yaml
      # === DEPLOY GATE COM IA ===
      - name: Deploy Gate (Groq)
        id: deploy-gate
        run: python scripts/deploy_gate.py
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}

      # === CANARY DEPLOY ===
      - name: Canary Deploy Simulator
        id: canary
        if: steps.deploy-gate.outcome == 'success'
        run: python scripts/canary_simulator.py

      # === ROLLBACK AUTOMATICO ===
      - name: Rollback + Relatorio IA
        if: failure() && steps.canary.outcome == 'failure'
        run: python scripts/rollback_trigger.py
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 💡 Dicas para a Apresentação

1.  **Explique o p99**: No Canary, usamos latência p99 porque médias escondem problemas graves.
2.  **IA como Decisora**: Destaque que a IA não está apenas "conversando", ela está retornando um JSON estruturado que o pipeline usa para tomar decisões lógicas (`sys.exit(0)` ou `1`).
3.  **Cultura SRE**: O relatório gerado pela IA poupa minutos preciosos do engenheiro durante um incidente, fornecendo a causa raiz imediatamente.

---
**Automação com DevOps e IA Generativa**
*PUCPR - Prof. Lisiane Reips*
