# Projeto de Otimização de Carteiras com Algoritmo Genético

Este projeto utiliza um algoritmo genético para otimizar carteiras de investimentos, buscando maximizar o retorno ajustado ao risco com base em dados históricos do mercado financeiro.

## Estrutura do Projeto

A estrutura do projeto está organizada da seguinte forma:

```
project/
│
├── src/
│   ├── genetic_alghoritm/
│   │   ├── __init__.py
│   │   ├── chromosome.py
│   │   ├── genetic_algorithm.py
│   │   └── island_model.py
│   │
│   ├── market/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── yahoo_finance_market_engine.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── stock.py
│   │
│   └── usecases/
│       ├── __init__.py
│       ├── fundamentalist.py
│       └── volatility.py
│
├── main.py
├── main.ipynb
├── readme.md
└── requirements.txt
```


---

## Descrição dos Diretórios

### `genetic_alghoritm/`
Implementação do núcleo evolutivo.

- `chromosome.py`  
  Classe base para cromossomos; define operações essenciais como aptidão, mutação e crossover.

- `genetic_algorithm.py`  
  Loop evolutivo principal: seleção, crossover, mutação e critério de parada.

- `island_model.py`  
  Versão multi-população (ilhas), usada para diversidade genética e redução de overfitting evolutivo.

---

### `market/`
Camada de aquisição e abstração de dados do mercado.

- `base.py`  
  Classe base para engines de mercado.

- `yahoo_finance_market_engine.py`  
  Implementação que extrai preços históricos e métricas via Yahoo Finance.

---

### `models/`
Modelos de domínio.

- `stock.py`  
  Representação de um ativo individual, contendo preços, retornos e metadados úteis ao algoritmo.

---

### `usecases/`
Estratégias de avaliação e heurísticas de risco-retorno.

- `volatility.py`  
  Implementa uma estratégia combinando Sharpe, volatilidade e eficiência de distribuição para encontrar os indíviduos que maximizam retorno ajustado ao risco.

- `fundamentalist.py`
  Implementa uma estratégia baseada em indicadores fundamentalistas (ROIC, Crescimento, ROE, Dívida/Patrimônio) para selecionar carteiras com bons fundamentos financeiros.
---

## Arquivos Principais

- `main.py`  
  Script principal para execução da otimização.

- `main.ipynb`  
  Experimentos exploratórios, gráficos, testes e tuning de parâmetros.

- `requirements.txt`  
  Dependências do projeto.

---

## Como o Algoritmo Funciona

### 1. População Inicial
Uma coleção de carteiras é criada aleatoriamente, cada uma representada como cromossomo.

### 2. Avaliação de Aptidão
Cada cromossomo calcula sua eficiência usando dados históricos + estratégia escolhida (ex: Sharpe).

### 3. Seleção
Os melhores indivíduos são escolhidos por torneio ou rank.

### 4. Crossover
Combinação de duas carteiras para gerar novas distribuições.

### 5. Mutação
Pequenas alterações nas alocações para promover diversidade e escapar de ótimos locais.

### 6. Island Model (opcional)
Populações evoluem separadamente, trocando indivíduos após algumas gerações.

### Resultado
Após muitas gerações, obtemos uma carteira com melhor relação risco-retorno segundo o critério definido.

---

### Exemplo de Uso

O arquivo `main.py` executa o algoritmo genético para otimizar carteiras com o seguinte fluxo:

```python
from src.market.yahoo_finance_market_engine import YahooFinanceMarketEngine
from src.genetic_alghoritm.genetic_algorithm import GeneticAlgorithm
from src.genetic_alghoritm.island_model import IslandModelGeneticAlgorithm
from src.usecases.fundamentalist import FundamentalistChromosome
from src.usecases.volatility import TripleRiskEfficiencyChromosome

tickers = [
        "PETR4.SA",
        "VALE3.SA",
        "ITUB4.SA",
        "BBDC4.SA",
        "ABEV3.SA",
        "MGLU3.SA",
        "B3SA3.SA",
        "BBAS3.SA",
        "GGBR4.SA",
        "RENT3.SA",
        "SUZB3.SA",
        "LREN3.SA",
        "WEGE3.SA",
        "RADL3.SA",
        "HYPE3.SA",
        "UGPA3.SA",
    ]

engine = YahooFinanceMarketEngine(
    tickers, "2023-01-01", "2024-01-01", risk_free_rate=0.05
)

random_assets_combinations = [engine.get_random_assets_wallet(
    tickers=tickers,
    max_assets=7
) for _ in range(50)]

map_key_to_fundamental_data = engine.get_multiple_fundamentalist_data(tickers)

fundamentalist_chromosomes = [
    FundamentalistChromosome(
        tickers=asset_combination,
        fundamental_scores=map_key_to_fundamental_data,
    )
    for asset_combination in random_assets_combinations
]

isga_fundamentalist: IslandModelGeneticAlgorithm[FundamentalistChromosome] = (
    IslandModelGeneticAlgorithm(
        initial_population=fundamentalist_chromosomes,
        threshold=0.8,
        max_generations=10,
        mutation_chance=0.1,
        crossover_chance=0.7,
    )
)
result_fundamentalist: list[FundamentalistChromosome] = isga_fundamentalist.run()

print("------------------- FIM DO PROCESSO GENETICO FUNDAMENTALISTA -------------------")

best_wallet = max(
    result_fundamentalist,
    key=lambda chromosome: chromosome.fitness(),
)

random_distribuited_wallets = [YahooFinanceMarketEngine.get_random_distribuited_wallet(
    wallet=best_wallet.tickers, total_number_of_stocks=100
) for _ in range(50)]

initial_generation = [
    TripleRiskEfficiencyChromosome(wallet, engine, 0.05)
    for wallet in random_distribuited_wallets
] 

isga: IslandModelGeneticAlgorithm[TripleRiskEfficiencyChromosome] = (
    IslandModelGeneticAlgorithm(
        initial_population=initial_generation,
        threshold=1.10,
        max_generations=10,
        mutation_chance=0.1,
        crossover_chance=0.7,
    )
)
result: list[TripleRiskEfficiencyChromosome] = isga.run()

```

## Requisitos

- Python 3.12 ou superior
- Bibliotecas listadas no arquivo `requirements.txt`

## Instalação e Execução

1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd project
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o script principal:
   ```bash
   python main.py
   ```
