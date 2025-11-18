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
