from concurrent.futures import ThreadPoolExecutor
from typing import Generic, TypeVar

from src.genetic_alghoritm.chromosome import Chromosome
from src.genetic_alghoritm.genetic_algorithm import GeneticAlgorithm

C = TypeVar("C", bound=Chromosome)


class IslandModelGeneticAlgorithm(Generic[C]):

    def __init__(
        self,
        initial_population: list[C],
        threshold: float,
        islands_numbers=5,
        max_generations=100,
        mutation_chance=0.01,
        crossover_chance=0.7,
        selection_type=GeneticAlgorithm.SelectionType.TOURNAMENT,
    ):
        self._islands_numbers = islands_numbers
        self._population = initial_population
        self._threshold = threshold
        self._max_generations = max_generations
        self._mutation_chance = mutation_chance
        self._crossover_chance = crossover_chance
        self._selection_type = selection_type
        self._fitness_key = type(self._population[0]).fitness

    def run(self):
        futures = []
        sub_population_size = len(self._population) // self._islands_numbers
        sub_populations = [
            self._population[i : i + sub_population_size]
            for i in range(0, len(self._population), sub_population_size)
        ]

        with ThreadPoolExecutor(max_workers=self._islands_numbers) as executor:
            for population in sub_populations:
                island = GeneticAlgorithm(
                    initial_population=population,
                    threshold=self._threshold,
                    max_generations=self._max_generations,
                    mutation_chance=self._mutation_chance,
                    crossover_chance=self._crossover_chance,
                    selection_type=self._selection_type,
                )
                futures.append(executor.submit(island.run))

        results = []
        for future in futures:
            results.extend(future.result())

        return results
