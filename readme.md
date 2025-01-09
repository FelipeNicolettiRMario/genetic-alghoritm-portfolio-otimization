# Projeto de Otimização de Carteiras com Algoritmo Genético

Este projeto utiliza um algoritmo genético para otimizar distribuições de carteiras de ações com base em um conjunto de indicadores financeiros e dados históricos.

## Estrutura do Projeto

A estrutura do projeto está organizada da seguinte forma:

```
project/
|— env/
|— models/
|— services/
    |— genetic_alghoritm/
        |— __init__.py
        |— chromosome.py
        |— genetic_algorithm.py
        |— wallet_chromosome.py
    |— wallet/
|— main.ipynb
|— main.py
|— requirements.txt
```

### Principais Diretórios e Arquivos

- **`env/`**: Contém configurações do ambiente.
- **`models/`**: Contém definições e modelos de dados.
- **`services/`**: Implementações dos módulos de serviços.
  - **`genetic_alghoritm/`**: Implementação do algoritmo genético.
    - `chromosome.py`: Definição de cromossomos genéricos.
    - `genetic_algorithm.py`: Implementação do algoritmo genético.
    - `wallet_chromosome.py`: Definição de cromossomos especializados para carteiras.
  - **`wallet/`**: Implementação de funções para manipulação de carteiras.
- **`main.py`**: Script principal que executa o algoritmo genético.
- **`main.ipynb`**: Notebook para análise exploratória e testes.
- **`requirements.txt`**: Dependências do projeto.

## Como Funciona

### Passo a Passo
1. **Geração Inicial de Carteiras**
   - É criada uma população inicial de carteiras com distribuição aleatória de ações.

2. **Definição de Cromossomos**
   - Cada carteira é representada como um cromossomo, com características como alocação de ativos e desempenho histórico.

3. **Algoritmo Genético**
   - Utiliza-se o algoritmo genético para evoluir as carteiras até atingir uma solução ótima. Ele inclui:
     - **Seleção**: Escolha das melhores carteiras.
     - **Crossover**: Combinação de carteiras selecionadas.
     - **Mutação**: Pequenas alterações aleatórias para aumentar a diversidade.

4. **Resultado Final**
   - O algoritmo retorna a carteira otimizada após um número máximo de gerações ou ao atingir um limiar de desempenho.

### Exemplo de Uso

O arquivo `main.py` executa o algoritmo genético para otimizar carteiras com o seguinte fluxo:

```python
from services.wallet.get import GetWalletDataTools
from services.genetic_alghoritm.wallet_chromosome import WalletChromosome
from services.genetic_alghoritm.genetic_algorithm import GeneticAlgorithm

# Definir os ativos e período
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
repo = GetWalletDataTools(tickers, "2023-01-01", "2024-01-01")

# Geração inicial de carteiras
random_distribuited_wallets = [
    GetWalletDataTools.get_random_distribuited_wallet(tickers) for _ in range(200)
]

# Criar cromossomos
initial_generation = [
    WalletChromosome(wallet, repo, 0.05) for wallet in random_distribuited_wallets
]

# Configurar o algoritmo genético
ga: GeneticAlgorithm[WalletChromosome] = GeneticAlgorithm(
    initial_population=initial_generation,
    threshold=1.0,
    max_generations=700,
    mutation_chance=0.1,
    crossover_chance=0.7,
)

# Executar e imprimir o resultado
result: WalletChromosome = ga.run()
print(result)
```

## Requisitos

- Python 3.8 ou superior
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
