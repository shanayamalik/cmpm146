
import copy
import heapq
import metrics
import multiprocessing.pool as mpool
import os
import random
import shutil
import time
import math

width = 200
height = 16

options = [
    "-",  # an empty space
    "X",  # a solid wall
    "?",  # a question mark block with a coin
    "M",  # a question mark block with a mushroom
    "B",  # a breakable block
    "o",  # a coin
    "|",  # a pipe segment
    "T",  # a pipe top
    "E",  # an enemy
    #"f",  # a flag, do not generate
    #"v",  # a flagpole, do not generate
    #"m"  # mario's start position, do not generate
]

# The level as a grid of tiles


class Individual_Grid(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None

    # Update this individual's estimate of its fitness.
    # This can be expensive so we do it once and then cache the result.
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Print out the possible measurements or look at the implementation of metrics.py for other keys:
        # print(measurements.keys())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Modify this, and possibly add more metrics.  You can replace this with whatever code you like.
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0
        )
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients))
        return self

    # Return the cached fitness value or calculate it as needed.
    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def mutate(self, genome):
        # Mutation probability per tile
        mutation_rate = 0.02
        
        left = 1
        right = width - 1
        
        for y in range(height):
            for x in range(left, right):
                if random.random() < mutation_rate:
                    # Different weights for different tiles
                    weights = [
                        0.55,  # "-" empty space (more common)
                        0.15,  # "X" solid wall
                        0.07,  # "?" question block
                        0.03,  # "M" mushroom block
                        0.05,  # "B" breakable block
                        0.07,  # "o" coin
                        0.04,  # "|" pipe segment
                        0.02,  # "T" pipe top
                        0.02   # "E" enemy
                    ]
                    
                    # Select new tile based on weights
                    genome[y][x] = random.choices(options, weights=weights)[0]
                    
                    # Fix structural issues after mutation
                    if genome[y][x] in ["T", "|"]:
                        if y < height-1:
                            genome[y+1][x] = "|"  # Add pipe body below pipe top
        
        return genome

    def generate_children(self, other):
        new_genome = copy.deepcopy(self.genome)
        
        # Leaving first and last columns alone
        left = 1
        right = width - 1
        
        # Two-point crossover
        for y in range(height):
            if random.random() < 0.5:  # 50% chance to crossover each row
                point1 = random.randint(left, right-1)
                point2 = random.randint(point1+1, right)
                
                # Take genes from self outside points, from other inside points
                for x in range(left, right):
                    if x >= point1 and x < point2:
                        new_genome[y][x] = other.genome[y][x]
        
                # Fix any structural issues
                self._fix_structural_issues(new_genome, y)
        
        # Create child and mutate
        child = Individual_Grid(new_genome)
        child.genome = self.mutate(child.genome)
        
        return (child,)

    def _fix_structural_issues(self, genome, y):
        """Fix any invalid tile combinations"""
        for x in range(1, width-1):
            # Fix floating pipes
            if y < height-1 and genome[y][x] == "T":
                genome[y+1][x] = "|"
            elif y > 0 and genome[y][x] == "|" and genome[y-1][x] not in ["T", "|"]:
                genome[y][x] = "-"
            
            # Prevent floating blocks (except coins and question blocks)
            if y < height-1 and genome[y][x] == "X":
                if genome[y+1][x] == "-":
                    genome[y][x] = "-"

    # Turn the genome into a level string (easy for this genome)
    def to_level(self):
        return self.genome

    # These both start with every floor tile filled with Xs
    # STUDENT Feel free to change these
    @classmethod
    def empty_individual(cls):
        g = [["-" for col in range(width)] for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"
        return cls(g)

    @classmethod
    def random_individual(cls):
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        g = [random.choices(options, k=width) for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        g[8:14][-1] = ["f"] * 6
        g[14:16][-1] = ["X", "X"]
        return cls(g)


def offset_by_upto(val, variance, min=None, max=None):
    val += random.normalvariate(0, variance**0.5)
    if min is not None and val < min:
        val = min
    if max is not None and val > max:
        val = max
    return int(val)


def clip(lo, val, hi):
    if val < lo:
        return lo
    if val > hi:
        return hi
    return val

# Inspired by https://www.researchgate.net/profile/Philippe_Pasquier/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000.pdf


class Individual_DE(object):
    # Calculating the level isn't cheap either so we cache it too.
    __slots__ = ["genome", "_fitness", "_level"]

    # Genome is a heapq of design elements sorted by X, then type, then other parameters
    def __init__(self, genome):
        self.genome = list(genome)
        heapq.heapify(self.genome)
        self._fitness = None
        self._level = None

    # Calculate and cache fitness
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Add more metrics?
        # STUDENT Improve this with any code you like
        coefficients = dict(
            meaningfulJumpVariance=0.6,  # Increase jump variety importance
            negativeSpace=0.6,
            pathPercentage=0.7,  # More emphasis on playable paths
            emptyPercentage=0.5,
            linearity=-0.3,  # Reduce linearity penalty for more structured levels
            solvability=2.5   # Heavily reward solvable levels
        )
        
        # Apply basic fitness calculation
        base_fitness = sum(map(lambda m: coefficients[m] * measurements[m], coefficients))
        
        # Add penalties/rewards based on design element composition
        penalties = 0
        
        # STUDENT For example, too many stairs are unaesthetic.  Let's penalize that
        if len(list(filter(lambda de: de[1] == "6_stairs", self.genome))) > 5:
            penalties -= 2
            
        # Penalize too many enemies to maintain level playability
        enemy_count = len(list(filter(lambda de: de[1] == "2_enemy", self.genome)))
        if enemy_count > 10:
            penalties -= (enemy_count - 10) * 0.2
            
        # Reward balanced distribution of coins and power-ups
        coin_count = len(list(filter(lambda de: de[1] == "3_coin", self.genome)))
        powerup_count = len(list(filter(lambda de: de[1] == "5_qblock", self.genome)))
        if 5 <= coin_count <= 15 and 2 <= powerup_count <= 5:
            penalties += 1
            
        # STUDENT If you go for the FI-2POP extra credit, you can put constraint calculation in here too and cache it in a new entry in __slots__.
        self._fitness = base_fitness + penalties
        return self

    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def mutate(self, new_genome):
        # STUDENT How does this work?  Explain it in your writeup.
        # STUDENT consider putting more constraints on this, to prevent generating weird things
        if random.random() < 0.1 and len(new_genome) > 0:
            to_change = random.randint(0, len(new_genome) - 1)
            de = new_genome[to_change]
            new_de = de
            x = de[0]
            de_type = de[1]
            choice = random.random()
            if de_type == "4_block":
                y = de[2]
                breakable = de[3]
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    breakable = not de[3]
                new_de = (x, de_type, y, breakable)
            elif de_type == "5_qblock":
                y = de[2]
                has_powerup = de[3]  # boolean
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    has_powerup = not de[3]
                new_de = (x, de_type, y, has_powerup)
            elif de_type == "3_coin":
                y = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                new_de = (x, de_type, y)
            elif de_type == "7_pipe":
                h = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    h = offset_by_upto(h, 2, min=2, max=height - 4)
                new_de = (x, de_type, h)
            elif de_type == "0_hole":
                w = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    w = offset_by_upto(w, 4, min=1, max=width - 2)
                new_de = (x, de_type, w)
            elif de_type == "6_stairs":
                h = de[2]
                dx = de[3]  # -1 or 1
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    h = offset_by_upto(h, 8, min=1, max=height - 4)
                else:
                    dx = -dx
                new_de = (x, de_type, h, dx)
            elif de_type == "1_platform":
                w = de[2]
                y = de[3]
                madeof = de[4]  # from "?", "X", "B"
                if choice < 0.25:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.5:
                    w = offset_by_upto(w, 8, min=1, max=width - 2)
                elif choice < 0.75:
                    y = offset_by_upto(y, height, min=0, max=height - 1)
                else:
                    madeof = random.choice(["?", "X", "B"])
                new_de = (x, de_type, w, y, madeof)
            elif de_type == "2_enemy":
                pass
            new_genome.pop(to_change)
            heapq.heappush(new_genome, new_de)
        return new_genome

    def generate_children(self, other):
        # STUDENT How does this work?  Explain it in your writeup.
        # Handle case where either parent has empty genome
        if len(self.genome) == 0 or len(other.genome) == 0:
            # Create a new genome with one random element
            g = [random.choice([
                (random.randint(1, width - 2), "0_hole", random.randint(1, 8)),
                (random.randint(1, width - 2), "1_platform", random.randint(1, 8), random.randint(0, height - 1), random.choice(["?", "X", "B"])),
                (random.randint(1, width - 2), "2_enemy"),
                (random.randint(1, width - 2), "3_coin", random.randint(0, height - 1)),
                (random.randint(1, width - 2), "4_block", random.randint(0, height - 1), random.choice([True, False])),
                (random.randint(1, width - 2), "5_qblock", random.randint(0, height - 1), random.choice([True, False])),
                (random.randint(1, width - 2), "6_stairs", random.randint(1, height - 4), random.choice([-1, 1])),
                (random.randint(1, width - 2), "7_pipe", random.randint(2, height - 4))
            ])]
            return Individual_DE(self.mutate(g)), Individual_DE(self.mutate(g))

        # Original crossover code
        pa = random.randint(0, len(self.genome) - 1)
        pb = random.randint(0, len(other.genome) - 1)
        a_part = self.genome[:pa]
        b_part = other.genome[pb:]
        ga = a_part + b_part
        b_part = other.genome[:pb]
        a_part = self.genome[pa:]
        gb = b_part + a_part
        return Individual_DE(self.mutate(ga)), Individual_DE(self.mutate(gb))

    # Apply the DEs to a base level.
    def to_level(self):
        if self._level is None:
            base = Individual_Grid.empty_individual().to_level()
            for de in sorted(self.genome, key=lambda de: (de[1], de[0], de)):
                # de: x, type, ...
                x = de[0]
                de_type = de[1]
                if de_type == "4_block":
                    y = de[2]
                    breakable = de[3]
                    base[y][x] = "B" if breakable else "X"
                elif de_type == "5_qblock":
                    y = de[2]
                    has_powerup = de[3]  # boolean
                    base[y][x] = "M" if has_powerup else "?"
                elif de_type == "3_coin":
                    y = de[2]
                    base[y][x] = "o"
                elif de_type == "7_pipe":
                    h = de[2]
                    base[height - h - 1][x] = "T"
                    for y in range(height - h, height):
                        base[y][x] = "|"
                elif de_type == "0_hole":
                    w = de[2]
                    for x2 in range(w):
                        base[height - 1][clip(1, x + x2, width - 2)] = "-"
                elif de_type == "6_stairs":
                    h = de[2]
                    dx = de[3]  # -1 or 1
                    for x2 in range(1, h + 1):
                        for y in range(x2 if dx == 1 else h - x2):
                            base[clip(0, height - y - 1, height - 1)][clip(1, x + x2, width - 2)] = "X"
                elif de_type == "1_platform":
                    w = de[2]
                    h = de[3]
                    madeof = de[4]  # from "?", "X", "B"
                    for x2 in range(w):
                        base[clip(0, height - h - 1, height - 1)][clip(1, x + x2, width - 2)] = madeof
                elif de_type == "2_enemy":
                    base[height - 2][x] = "E"
            self._level = base
        return self._level

    @classmethod
    def empty_individual(_cls):
        # STUDENT Maybe enhance this
        g = []
        return Individual_DE(g)

    @classmethod
    def random_individual(_cls):
        # STUDENT Maybe enhance this
        elt_count = random.randint(1, 128)
        g = [random.choice([
            (random.randint(1, width - 2), "0_hole", random.randint(1, 8)),
            (random.randint(1, width - 2), "1_platform", random.randint(1, 8), random.randint(0, height - 1), random.choice(["?", "X", "B"])),
            (random.randint(1, width - 2), "2_enemy"),
            (random.randint(1, width - 2), "3_coin", random.randint(0, height - 1)),
            (random.randint(1, width - 2), "4_block", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "5_qblock", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "6_stairs", random.randint(1, height - 4), random.choice([-1, 1])),
            (random.randint(1, width - 2), "7_pipe", random.randint(2, height - 4))
        ]) for i in range(elt_count)]
        return Individual_DE(g)

Individual = Individual_DE
#Individual = Individual_Grid

def generate_successors(population):
    """
    Generate a new population of individuals using tournament and roulette wheel selection.
    """
    results = []
    pop_size = len(population)
    
    # Selection strategy parameters
    tournament_size = 5  # Increased for more selection pressure
    tournament_probability = 0.7  # Use tournament selection 70% of the time
    elitism_count = int(pop_size * 0.1)  # Preserve top 10% of population
    
    # Add elite individuals
    sorted_population = sorted(population, key=lambda x: x.fitness(), reverse=True)
    results.extend(sorted_population[:elitism_count])
    
    def tournament_select(pop):
        """Tournament selection with tournament_size participants"""
        tournament = random.sample(pop, tournament_size)
        return max(tournament, key=lambda x: x.fitness())
    
    def roulette_select(pop):
        """Roulette wheel selection based on fitness"""
        total_fitness = sum(max(0, ind.fitness()) for ind in pop)
        if total_fitness == 0:
            return random.choice(pop)
            
        pick = random.uniform(0, total_fitness)
        current = 0
        
        for individual in pop:
            current += max(0, individual.fitness())
            if current > pick:
                return individual
        return pop[-1]
    
    # Keep generating children until reaching original population size
    while len(results) < pop_size:
        # Choose selection method
        if random.random() < tournament_probability:
            parent1 = tournament_select(population)
            parent2 = tournament_select(population)
        else:
            parent1 = roulette_select(population)
            parent2 = roulette_select(population)
        
        # Generate and add children
        children = parent1.generate_children(parent2)
        results.extend(children)
        
        if len(results) > pop_size:
            results = results[:pop_size]
    
    return results

def ga():
    # STUDENT Feel free to play with this parameter
    pop_limit = 480
    # Code to parallelize some computations
    batches = os.cpu_count()
    if pop_limit % batches != 0:
        print("It's ideal if pop_limit divides evenly into " + str(batches) + " batches.")
    batch_size = int(math.ceil(pop_limit / batches))
    with mpool.Pool(processes=os.cpu_count()) as pool:
        init_time = time.time()
        # STUDENT (Optional) change population initialization
        population = [Individual.random_individual() if random.random() < 0.9
                      else Individual.empty_individual()
                      for _g in range(pop_limit)]
        # But leave this line alone; we have to reassign to population because we get a new population that has more cached stuff in it.
        population = pool.map(Individual.calculate_fitness,
                              population,
                              batch_size)
        init_done = time.time()
        print("Created and calculated initial population statistics in:", init_done - init_time, "seconds")
        generation = 0
        start = time.time()
        now = start
        print("Use ctrl-c to terminate this loop manually.")
        try:
            while True:
                now = time.time()
                # Print out statistics
                if generation > 0:
                    best = max(population, key=Individual.fitness)
                    print("Generation:", str(generation))
                    print("Max fitness:", str(best.fitness()))
                    print("Average generation time:", (now - start) / generation)
                    print("Net time:", now - start)
                    with open("levels/last.txt", 'w') as f:
                        for row in best.to_level():
                            f.write("".join(row) + "\n")
                    
                    # STUDENT Determine stopping condition
                    stop_condition = (
                        generation > 15 or     # Either run for 15 generations
                        (generation > 5 and     # After at least 5 generations
                         len(set(best_fitness_history[-5:])) == 1) # No improvement in last 5 generations
                    )
                    if stop_condition:
                        break
                
                generation += 1
                # STUDENT Also consider using FI-2POP as in the Sorenson & Pasquier paper
                gentime = time.time()
                next_population = generate_successors(population)
                gendone = time.time()
                print("Generated successors in:", gendone - gentime, "seconds")
                # Calculate fitness in batches in parallel
                next_population = pool.map(Individual.calculate_fitness,
                                           next_population,
                                           batch_size)
                popdone = time.time()
                print("Calculated fitnesses in:", popdone - gendone, "seconds")
                population = next_population
        except KeyboardInterrupt:
            pass
    return population


if __name__ == "__main__":
    final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    best = final_gen[0]
    print("Best fitness: " + str(best.fitness()))
    now = time.strftime("%m_%d_%H_%M_%S")
    # STUDENT You can change this if you want to blast out the whole generation, or ten random samples, or...
    for k in range(0, 10):
        with open("levels/" + now + "_" + str(k) + ".txt", 'w') as f:
            for row in final_gen[k].to_level():
                f.write("".join(row) + "\n")
