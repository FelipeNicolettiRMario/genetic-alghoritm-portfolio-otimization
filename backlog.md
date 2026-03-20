# Backlog — Robustez para Mercado

Itens organizados por área e prioridade. Cada épico tem critério de aceitação claro.

---

## Épico 1 — Validação Estatística (Prioridade: Crítica)

Sem isso, qualquer resultado do GA é anedótico.

### BL-01 · Walk-forward validation
**Por quê:** O modelo atualmente treina e avalia no mesmo período — isso é overfitting garantido.
**O que fazer:**
- Implementar janela rolante: treinar em N anos, testar em 1 ano fora da amostra
- Repetir para múltiplos períodos e agregar métricas (média, desvio, pior caso)
- Nenhum resultado deve ser reportado sem out-of-sample period

**Critério de aceite:** Sistema produz curva de equity out-of-sample para pelo menos 3 janelas distintas.

---

### BL-02 · Benchmark obrigatório
**Por quê:** Um portfólio com Sharpe 0.8 não diz nada sem comparação.
**O que fazer:**
- Adicionar benchmark configurable (default: IBOV, alternativa: CDI)
- Calcular alpha, beta, information ratio e tracking error vs benchmark
- Backtester deve retornar métricas relativas, não só absolutas

**Critério de aceite:** Todo relatório de backtest inclui comparação side-by-side com benchmark.

---

### BL-03 · Testes estatísticos de significância
**Por quê:** Retorno superior pode ser sorte.
**O que fazer:**
- Implementar bootstrap para intervalo de confiança do Sharpe ratio
- Adicionar p-value para alpha positivo (teste t)
- Registrar número de períodos testados por métrica

**Critério de aceite:** Output inclui IC 95% para Sharpe e alpha.

---

## Épico 2 — Backtester Realista (Prioridade: Alta)

### BL-04 · Custos de transação
**Por quê:** O backtester atual assume execução a custo zero, o que é impossível.
**O que fazer:**
- Adicionar modelo de custos configurável: corretagem fixa + spread percentual
- Modelo sugerido: R$ 5,00/ordem + 0.025% spread (referência B3/XP)
- Aplicar custo em todo evento de compra/venda no DCA

**Critério de aceite:** Performance com custos nunca igual à sem custos.

---

### BL-05 · Impostos (IR sobre ganhos de capital)
**Por quê:** Para o investidor pessoa física brasileiro, IR impacta diretamente o retorno líquido.
**O que fazer:**
- Implementar regra de isenção mensal até R$ 20.000 em vendas (ações)
- Aplicar alíquota de 15% sobre lucro nas vendas acima do limite
- Separar curto prazo (day trade, 20%) de longo prazo

**Critério de aceite:** Backtester produz resultado bruto e líquido de IR separados.

---

### BL-06 · Liquidez e slippage
**Por quê:** Ativos com baixo volume não conseguem ser comprados/vendidos ao preço de fechamento.
**O que fazer:**
- Adicionar filtro de volume mínimo diário configurável (sugestão: > R$ 1M/dia médio)
- Modelar slippage como função do tamanho da ordem vs volume médio
- Remover ativos ilíquidos do universo elegível automaticamente

**Critério de aceite:** Portfólio gerado passa em filtro de liquidez antes de ser executado.

---

### BL-07 · Rebalanceamento periódico
**Por quê:** Pesos do portfólio derivam com o tempo; o portfólio ótimo do GA fica obsoleto.
**O que fazer:**
- Implementar rebalanceamento por calendário (mensal/trimestral) e por drift (peso > threshold)
- Re-executar GA periodicamente com dados atualizados (ex: trimestral)
- Registrar custo de cada rebalanceamento

**Critério de aceite:** Backtester simula rebalanceamento dinâmico ao longo da série histórica.

---

## Épico 3 — Motor Genético (Prioridade: Alta)

### BL-08 · Calibração dos hiperparâmetros do GA
**Por quê:** `max_generations=10`, `mutation_chance=0.1` são valores arbitrários sem evidência de convergência.
**O que fazer:**
- Implementar curva de convergência (fitness vs geração) para diagnóstico
- Adicionar critério de parada por platô (ex: sem melhora por N gerações)
- Grid search nos hiperparâmetros principais: tamanho de população, gerações, taxa de mutação

**Critério de aceite:** GA demonstra convergência antes do limite de gerações em 80% das execuções de teste.

---

### BL-09 · Normalização da função fitness com base em dados
**Por quê:** Os divisores atuais (`/3`, `/4`, `/5`) são arbitrários e fazem a normalização depender dos dados específicos do período.
**O que fazer:**
- Calcular min/max dos ratios no universo de ativos para normalizar dinamicamente
- Ou substituir por z-score com média e desvio do período de treino
- Documentar e justificar os pesos (0.4 Sharpe, 0.3 Sortino, 0.3 Calmar)

**Critério de aceite:** Fitness sempre produz valor em [0, 1] independente do período.

---

### BL-10 · Diversidade genética e pressão seletiva
**Por quê:** Com população de 50 e 10 gerações, o GA converge rápido para ótimos locais.
**O que fazer:**
- Implementar métrica de diversidade (variância de fitness na população)
- Ajustar pressão seletiva dinamicamente: alta diversidade → mais seleção; baixa → mais mutação
- Aumentar tamanho padrão da população para ≥ 100

**Critério de aceite:** Diversidade de fitness não colapsa antes da geração 5 em testes.

---

### BL-11 · Migração real no Island Model
**Por quê:** Atualmente as ilhas evoluem de forma completamente independente — o Island Model nunca troca indivíduos entre ilhas.
**O que fazer:**
- Implementar migração periódica: a cada K gerações, mover os M melhores de cada ilha para outra
- Topologia configurável: ring, fully-connected, random
- Testar com e sem migração para validar ganho

**Critério de aceite:** Ilhas trocam indivíduos durante a execução; fitness final superior ao GA single-island.

---

## Épico 4 — Dados e Universo de Ativos (Prioridade: Média)

### BL-12 · Rotação de universo de ativos
**Por quê:** 15 tickers fixos não refletem a realidade — índices mudam, empresas entram e saem.
**O que fazer:**
- Carregar universo de ativos a partir de arquivo de configuração (JSON/YAML)
- Suportar filtros automáticos: componentes do IBOV, SMLL, IDIV
- Implementar point-in-time data: usar composição do índice na data de cada janela de treino

**Critério de aceite:** Universo de ativos pode ser atualizado sem alterar código.

---

### BL-13 · Qualidade e fallback de dados fundamentalistas
**Por quê:** Yahoo Finance tem dados fundamentalistas incompletos e inconsistentes para ações BR.
**O que fazer:**
- Adicionar fonte alternativa para fundamentalistas (ex: StatusInvest scraping, Economatica)
- Implementar cache persistente em disco (SQLite ou Parquet) com TTL configurável
- Logging quando dado fundamentalista está ausente ou estimado

**Critério de aceite:** Sistema não lança exceção para ≥ 95% dos tickers do IBOV.

---

### BL-14 · Detecção de regime de mercado
**Por quê:** Um portfólio ótimo em bull market performa mal em bear market.
**O que fazer:**
- Implementar detector de regime simples: tendência (SMA), volatilidade (VIX-like), correlação
- Ajustar pesos da função fitness por regime (ex: Calmar mais importante em bear)
- Registrar regime vigente em cada período do backtest

**Critério de aceite:** GA usa configuração de fitness diferente em períodos de alta volatilidade vs baixa.

---

## Épico 5 — Engenharia de Software (Prioridade: Média)

### BL-15 · Testes automatizados
**Por quê:** Nenhum teste existe; bugs críticos existiam em produção.
**O que fazer:**
- Unit tests para operadores genéticos (crossover, mutate): verificar invariantes
- Unit tests para cálculos financeiros (Sharpe, Sortino, Calmar) com valores conhecidos
- Integration test end-to-end com dataset sintético pequeno
- Target: cobertura ≥ 80% nos módulos `genetic_alghoritm/` e `market/`

**Critério de aceite:** `pytest` passa sem falhas; cobertura ≥ 80%.

---

### BL-16 · Configuração externalizada
**Por quê:** Parâmetros críticos estão hardcoded em `main.py`.
**O que fazer:**
- Mover todos os parâmetros para arquivo `config.yaml`
- Incluir: universo de ativos, datas, hiperparâmetros do GA, pesos do fitness, custos de transação
- Validar configuração na inicialização com schema (ex: pydantic)

**Critério de aceite:** Executar experimento diferente não requer alterar código.

---

### BL-17 · Logging e observabilidade
**Por quê:** `print()` não é logging; impossível diagnosticar problemas em produção.
**O que fazer:**
- Substituir todos os `print()` por `logging` com níveis adequados
- Serializar resultado de cada execução do GA em JSON com metadados (data, config, seed)
- Adicionar seed de aleatoriedade reproduzível para experimentos

**Critério de aceite:** Toda execução gera arquivo de log com resultados reproduzíveis dado a mesma seed.

---

### BL-18 · Relatório de resultado
**Por quê:** Atualmente o output é uma série de prints — não é auditável nem apresentável.
**O que fazer:**
- Gerar relatório HTML ou PDF com: curva de equity, drawdown, métricas, comparação vs benchmark
- Incluir tabela com histórico de rebalanceamentos e custos
- Export para CSV dos dados brutos

**Critério de aceite:** Relatório gerado automaticamente ao fim de cada backtest.

---

## Resumo por Prioridade

| Prioridade | Épico | Itens |
|---|---|---|
| Crítica | Validação Estatística | BL-01, BL-02, BL-03 |
| Alta | Backtester Realista | BL-04, BL-05, BL-06, BL-07 |
| Alta | Motor Genético | BL-08, BL-09, BL-10, BL-11 |
| Média | Dados e Universo | BL-12, BL-13, BL-14 |
| Média | Engenharia | BL-15, BL-16, BL-17, BL-18 |

**Sequência sugerida para MVP confiável:** BL-01 → BL-04 → BL-02 → BL-08 → BL-15 → BL-16

Sem BL-01 e BL-04, qualquer resultado publicado é enganoso.
