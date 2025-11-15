from src.market.yahoo_finance_market_engine import YahooFinanceMarketEngine
from src.genetic_alghoritm.genetic_algorithm import GeneticAlgorithm
from src.genetic_alghoritm.island_model import IslandModelGeneticAlgorithm
from src.strategies.triple_risk_effiiciency import TripleRiskEfficiencyChromosome

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]

random_distribuited_wallets = [
    YahooFinanceMarketEngine.get_random_distribuited_wallet(tickers) for _ in range(50)
]

engine = YahooFinanceMarketEngine(tickers, "2023-01-01", "2024-01-01", risk_free_rate=0.05)

initial_generation = [
    TripleRiskEfficiencyChromosome(wallet, engine, 0.05) for wallet in random_distribuited_wallets
]

isga: IslandModelGeneticAlgorithm[TripleRiskEfficiencyChromosome] = IslandModelGeneticAlgorithm(
    initial_population=initial_generation,
    threshold=1.10,
    max_generations=10,
    mutation_chance=0.1,
    crossover_chance=0.7,
)
result: list[TripleRiskEfficiencyChromosome] = isga.run()
