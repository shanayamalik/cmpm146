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
            pathPercentage=0.6,
            emptyPercentage=0.5,
            linearity=-0.4,
            solvability=2.0,
            rhythm=0.7,                  
            verticality=0.8,             
            powerup_distribution=0.5     
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
        
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
    
        coefficients = dict(
            meaningfulJumpVariance=2.0,    # Doubled - encourage varied jump challenges
            negativeSpace=1.5,             # Increased for better space usage
            pathPercentage=2.0,            # Doubled - heavily reward playable paths
            emptyPercentage=1.0,           # Kept moderate
            linearity=-0.2,                # Reduced penalty for non-linearity
            solvability=4.0,               # Much higher weight on solvability
            rhythm=2.0,                    # Strong emphasis on pacing
            verticality=2.0,               # Encourage vertical exploration
            powerup_distribution=1.5       # Better powerup placement
        )
    
        # Apply basic fitness calculation
        base_fitness = sum(map(lambda m: coefficients[m] * measurements[m], coefficients))
        
        # Enhanced penalties/rewards
        penalties = 0
        
        # Count various elements
        enemy_count = len(list(filter(lambda de: de[1] == "2_enemy", self.genome)))
        coin_count = len(list(filter(lambda de: de[1] == "3_coin", self.genome)))
        powerup_count = len(list(filter(lambda de: de[1] == "5_qblock", self.genome)))
        platform_count = len(list(filter(lambda de: de[1] == "1_platform", self.genome)))
        stairs_count = len(list(filter(lambda de: de[1] == "6_stairs", self.genome)))
        pipe_count = len(list(filter(lambda de: de[1] == "7_pipe", self.genome)))
        
        # Reward good distributions
        if 4 <= enemy_count <= 8:
            penalties += 3.0
        if 8 <= coin_count <= 15:
            penalties += 2.0
        if 2 <= powerup_count <= 4:
            penalties += 2.0
        if 6 <= platform_count <= 12:
            penalties += 3.0
        if 2 <= stairs_count <= 4:
            penalties += 2.0
        if 2 <= pipe_count <= 4:
            penalties += 2.0
            
        # Penalize excessive elements
        if enemy_count > 10:
            penalties -= (enemy_count - 10) * 0.5
        if stairs_count > 5:
            penalties -= (stairs_count - 5) * 1.0
        if pipe_count > 6:
            penalties -= (pipe_count - 6) * 0.5
            
        # Reward good level structure
        if platform_count > 0 and coin_count > 0 and powerup_count > 0:
            penalties += 4.0  # Basic completeness bonus
            
        # Spatial distribution bonus
        used_x_positions = set()
        for de in self.genome:
            x_pos = de[0]
            used_x_positions.add(x_pos // 20)  # Divide level into sections
        coverage = len(used_x_positions) / (width // 20)
        penalties += coverage * 3.0  # Reward using full level width

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
        # Create a basic platforming structure
        g = [
            # Starting platform
            (2, "1_platform", 4, 4, "X"),
            
            # Some strategically placed platforms
            (int(width/6), "1_platform", 3, 5, "X"),
            (int(width/3), "1_platform", 4, 6, "X"),
            (int(width/2), "1_platform", 3, 5, "X"),
            
            # A few coins for guidance
            (int(width/6) + 2, "3_coin", 4),
            (int(width/3) + 2, "3_coin", 5),
            
            # Essential power-ups
            (int(width/4), "5_qblock", 4, True),  # Question block with power-up
            
            # Some small gaps
            (int(width/5), "0_hole", 2),
            (int(width/2.5), "0_hole", 2),
            
            # A pipe
            (int(width/3.5), "7_pipe", 3)
        ]
        return Individual_DE(g)

    @classmethod
    def random_individual(_cls):
        # More controlled element count
        elt_count = random.randint(20, 50)  # Ensures enough elements for interesting levels
        
        # Define element probabilities
        elements = [
            # Format: (probability, creation_function)
            (0.25, lambda: (random.randint(1, width - 2), "1_platform", 
                           random.randint(3, 6), # width
                           random.randint(4, height - 4), # height
                           random.choice(["X", "B"]))), # platform type
            
            (0.15, lambda: (random.randint(1, width - 2), "3_coin", 
                           random.randint(3, height - 3))), # coins
            
            (0.15, lambda: (random.randint(1, width - 2), "5_qblock", 
                           random.randint(3, height - 3),
                           random.choice([True, False]))), # power-ups
            
            (0.15, lambda: (random.randint(1, width - 2), "4_block", 
                           random.randint(3, height - 3),
                           True)), # breakable blocks
            
            (0.10, lambda: (random.randint(1, width - 2), "0_hole", 
                           random.randint(2, 4))), # small gaps
            
            (0.08, lambda: (random.randint(1, width - 2), "2_enemy")), # enemies
            
            (0.07, lambda: (random.randint(1, width - 2), "7_pipe", 
                           random.randint(2, 4))), # pipes
            
            (0.05, lambda: (random.randint(1, width - 2), "6_stairs", 
                           random.randint(2, 4),
                           random.choice([-1, 1]))) # stairs
        ]
        
        g = []
        used_positions = set()
        
        # Generate elements
        for _ in range(elt_count):
            # Select element type based on probabilities
            total = sum(prob for prob, _ in elements)
            r = random.uniform(0, total)
            acc = 0
            
            for prob, create_fn in elements:
                acc += prob
                if r <= acc:
                    # Try to find unused position
                    for _ in range(10):  # Maximum attempts
                        element = create_fn()
                        x_pos = element[0]
                        if x_pos not in used_positions:
                            used_positions.add(x_pos)
                            g.append(element)
                            break
                    break

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
    best_fitness_history = []

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
        population = []
        for _ in range(pop_limit):
            r = random.random()
            if r < 0.6:  # 60% random individuals
                ind = Individual.random_individual()
                while len(ind.genome) < 20:  # Ensure minimum complexity
                    ind = Individual.random_individual()
                population.append(ind)
            elif r < 0.9:  # 30% empty individuals with basic structure
                base = Individual.empty_individual()
                # Add some random elements to the basic structure
                additional = Individual.random_individual()
                base.genome.extend(list(filter(lambda x: x[0] > width/3, additional.genome[:10])))
                population.append(base)
            else:  # 10% completely empty individuals for diversity
                population.append(Individual.empty_individual())
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
                    best_fitness_history.append(best.fitness())
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
