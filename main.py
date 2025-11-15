from src.market.yahoo_finance_market_engine import YahooFinanceMarketEngine

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]

random_distribuited_wallets = [
    YahooFinanceMarketEngine.get_random_distribuited_wallet(tickers) for _ in range(50)
]

repo = YahooFinanceMarketEngine(tickers, "2023-01-01", "2024-01-01", risk_free_rate=0.05)

from src.strategies.triple_risk_effiiciency import TripleRiskEfficiencyChromosome

initial_generation = [
    TripleRiskEfficiencyChromosome(wallet, repo, 0.05) for wallet in random_distribuited_wallets
]

from src.genetic_alghoritm.genetic_algorithm import GeneticAlgorithm
from src.genetic_alghoritm.island_model import IslandModelGeneticAlgorithm

isga: IslandModelGeneticAlgorithm[TripleRiskEfficiencyChromosome] = IslandModelGeneticAlgorithm(
    initial_population=initial_generation,
    threshold=1.10,
    max_generations=10,
    mutation_chance=0.1,
    crossover_chance=0.7,
)
result: list[TripleRiskEfficiencyChromosome] = isga.run()

ga: GeneticAlgorithm[TripleRiskEfficiencyChromosome] = GeneticAlgorithm(
    initial_population=result,
    threshold=1.10,
    max_generations=20,
    mutation_chance=0.1,
    crossover_chance=0.7,
)
final_result: set[TripleRiskEfficiencyChromosome] = ga.run()
for chromosome in final_result:
    print(chromosome.fitness())
    print(chromosome._stocks)
    print("-----")
