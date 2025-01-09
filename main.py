from services.wallet.get import GetWalletDataTools

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]

random_distribuited_wallets = [
    GetWalletDataTools.get_random_distribuited_wallet(tickers) for _ in range(200)
]

repo = GetWalletDataTools(tickers, "2023-01-01", "2024-01-01")

from services.genetic_alghoritm.wallet_chromosome import WalletChromosome

initial_generation = [
    WalletChromosome(wallet, repo, 0.05) for wallet in random_distribuited_wallets
]

from services.genetic_alghoritm.genetic_algorithm import GeneticAlgorithm

ga: GeneticAlgorithm[WalletChromosome] = GeneticAlgorithm(
    initial_population=initial_generation,
    threshold=1.0,
    max_generations=700,
    mutation_chance=0.1,
    crossover_chance=0.7,
)
result: WalletChromosome = ga.run()
print(result)
