import pathfinding
import numpy as np
import sys


def metrics(levelStr):
    maxY = len(levelStr)
    maxX = len(levelStr[0])

    visited = set()
    curX = 2
    curY = 0
    solids = set(['X', 'Q', 'S', '?', 'B', 'b', '[', ']', 'T', '|', '<', '>', 'v', 'f', 'm'])

    def isSolid(tile):
        return tile in solids
    for yy in range(maxY - 2, -1, -1):
        if (levelStr[yy][curX] == '-' or levelStr[yy][curX] == '*') and isSolid(levelStr[yy + 1][curX]):
            curY = yy
            break

    jumps = [[(0, -1),
              (0, -2),
              (1, -3),
              (1, -4),
              (0, -4)],
             [(0, -1),
              (0, -2),
              (0, -3),
              (0, -4),
              (1, -4)],
             [(1, -1),
              (1, -2),
              (1, -3),
              (1, -4),
              (2, -4)],
             [(1, -1),
              (1, -2),
              (2, -2),
              (2, -3),
              (3, -3),
              (3, -4),
              (4, -4),
              (5, -3),
              (6, -3),
              (7, -3),
              (8, -2),
              (8, -1)],
             [(1, -1),
              (1, -2),
              (2, -2),
              (2, -3),
              (3, -3),
              (3, -4),
              (4, -4),
              (5, -4),
              (6, -3),
              (7, -3),
              (8, -2),
              (8, -1)]]
    jumpDiffs = []
    for jump in jumps:
        jumpDiff = [jump[0]]
        for ii in range(1, len(jump)):
            jumpDiff.append((jump[ii][0] - jump[ii - 1][0], jump[ii][1] - jump[ii - 1][1]))
        jumpDiffs.append(jumpDiff)
    jumps = jumpDiffs
    visited = set()

    def getNeighbors(pos):
        dist = pos[0]
        pos = pos[1]
        visited.add((pos[0], pos[1]))
        below = (pos[0], pos[1] + 1)
        neighbors = []
        if below[1] >= maxY:
            return []
        if pos[2] != -1:
            ii = pos[3] + 1
            jump = pos[2]
            if ii < len(jumps[jump]):
                if not (pos[0] + pos[4] * jumps[jump][ii][0] >= maxX or pos[0] + pos[4] * jumps[jump][ii][0] < 0 or pos[1] + jumps[jump][ii][1] < 0) and not isSolid(levelStr[pos[1] + jumps[jump][ii][1]][pos[0] + pos[4] * jumps[jump][ii][0]]):
                    neighbors.append([dist + 1, (pos[0] + pos[4] * jumps[jump][ii][0], pos[1] + jumps[jump][ii][1], jump, ii, pos[4])])

        if isSolid(levelStr[below[1]][below[0]]):
            if pos[0] + 1 < maxX and not isSolid(levelStr[pos[1]][pos[0] + 1]):
                neighbors.append([dist + 1, (pos[0] + 1, pos[1], -1)])
            if pos[0] - 1 >= 0 and not isSolid(levelStr[pos[1]][pos[0] - 1]):
                neighbors.append([dist + 1, (pos[0] - 1, pos[1], -1)])

            for jump in range(len(jumps)):
                ii = 0
                if not (pos[0] + jumps[jump][ii][0] >= maxX or pos[1] + jumps[jump][ii][1] < 0) and not isSolid(levelStr[pos[1] + jumps[jump][ii][1]][pos[0] + jumps[jump][ii][0]]):
                    neighbors.append([dist + ii + 1, (pos[0] + jumps[jump][ii][0], pos[1] + jumps[jump][ii][1], jump, ii, 1)])

                if not (pos[0] - jumps[jump][ii][0] < 0 or pos[1] + jumps[jump][ii][1] < 0) and not isSolid(levelStr[pos[1] + jumps[jump][ii][1]][pos[0] - jumps[jump][ii][0]]):
                    neighbors.append([dist + ii + 1, (pos[0] - jumps[jump][ii][0], pos[1] + jumps[jump][ii][1], jump, ii, -1)])

        else:
            neighbors.append([dist + 1, (pos[0], pos[1] + 1, -1)])
            if pos[1] + 1 < maxY:
                if pos[0] + 1 < maxX and not isSolid(levelStr[pos[1] + 1][pos[0] + 1]):
                    neighbors.append([dist + 1.4, (pos[0] + 1, pos[1] + 1, -1)])
                if pos[0] - 1 >= 0 and not isSolid(levelStr[pos[1] + 1][pos[0] - 1]):
                    neighbors.append([dist + 1.4, (pos[0] - 1, pos[1] + 1, -1)])
            if pos[1] + 2 < maxY:
                if pos[0] + 1 < maxX and not isSolid(levelStr[pos[1] + 2][pos[0] + 1]):
                    neighbors.append([dist + 2, (pos[0] + 1, pos[1] + 2, -1)])
                if pos[0] - 1 >= 0 and not isSolid(levelStr[pos[1] + 2][pos[0] - 1]):
                    neighbors.append([dist + 2, (pos[0] - 1, pos[1] + 2, -1)])
        return neighbors
    subOptimal = 0

    paths = pathfinding.dijkstras_shortest_path((curX, curY, -1), lambda pos: pos[0] == maxX - 2, getNeighbors, subOptimal)

    pathDict = {path[0]: [] for path in paths}

    for yy in range(maxY):
        s = ''
        for xx in range(maxX):
            if (xx, yy) in visited:
                s += '*'
            else:
                s += levelStr[yy][xx]

        # print s
    for path in paths:
        pathDict[path[0]].append([(p[0], p[1]) for p in path[1]])
    # print paths
    paths = pathDict
    pathStats = {}
    gaps = set()
    for xx in range(maxX):
        if levelStr[maxY - 1][xx] == '-':
            gaps.add(xx)
    for pathLength in paths:
        pathStats[pathLength] = {'jumps': [], 'meaningfulJumps': []}
        for path in paths[pathLength]:
            jumps = 0
            meaningfulJumps = 0
            onGround = True
            for p in path:
                if p[1] < 15 and isSolid(levelStr[p[1] + 1][p[0]]):
                    onGround = True
                elif onGround:
                    jumps += 1
                    onGround = False
                    for xx in range(5):
                        if p[0] + xx < maxX and p[0] + xx in gaps:
                            meaningfulJumps += 1
                            break
            pathStats[pathLength]['jumps'].append(jumps)
            pathStats[pathLength]['meaningfulJumps'].append(meaningfulJumps)
    totalJumps = 0
    totalMeaningfulJumps = 0
    pathcount = 0
    smallest = float('inf')

    for path in pathStats:
        if path < smallest:
            smallest = path
        for p in pathStats[path]['jumps']:
            totalJumps += p
            pathcount += 1
        for p in pathStats[path]['meaningfulJumps']:
            totalMeaningfulJumps += p
    jumpVariance = 0
    meaningfulJumpVariance = 0

    for path in pathStats:
        for p in pathStats[path]['jumps']:
            temp = p - float(totalJumps) / float(pathcount)
            jumpVariance += temp * temp

        for p in pathStats[path]['meaningfulJumps']:
            temp = p - float(totalMeaningfulJumps) / float(pathcount)
            meaningfulJumpVariance += temp * temp

    totalSize = maxX * maxY
    #negativeSpace = float(len(visited))/float(totalSize)
    enemies = 0
    pipes = 0
    empty = 0
    breakable = 0
    rewards = 0
    solid = 0
    powerups = 0
    for row in levelStr:
        enemies += row.count('E')
        empty += row.count('-') + row.count('E') + row.count('o') + row.count('*')
        pipes += row.count('|') + row.count('T')
        breakable += row.count('B')
        rewards += row.count('o') + row.count('?') + row.count('M')
        powerups += row.count('M')
        solid += row.count('X') + row.count('?') + row.count('|') + row.count('T') + row.count('M') + row.count('B')

    negativeSpace = float(len(visited)) / float(empty)
    pathPercentage = float(smallest) / float(empty)
    emptyPercentage = float(empty) / float(totalSize)
    decorationPercentage = (float(pipes) + float(breakable) + float(enemies) + float(rewards)) / float(totalSize)
    leniency = enemies - powerups * 0.5 - 0.5 * rewards + len(gaps)

    solidX = []
    solidY = []
    yy = 0
    for yy in range(maxY):
        xx = 0
        if yy > 0:
            for c in levelStr[yy]:
                if isSolid(c) and not isSolid(levelStr[yy - 1][xx]):
                    # solidPts.append([xx,yy])
                    solidX.append(xx)
                    solidY.append(yy)
                xx += 1
        yy += 1
    x = np.array(solidX)
    y = np.array(solidY)
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    linearity = np.abs(r_value)
    if len(paths) > 0:
        return {'length': maxX,
                'negativeSpace': negativeSpace,
                'pathPercentage': pathPercentage,
                'emptyPercentage': emptyPercentage,
                'decorationPercentage': decorationPercentage,
                'leniency': leniency,
                'meaningfulJumps': float(totalMeaningfulJumps) / float(pathcount),
                'jumps': float(totalJumps) / float(pathcount),
                'meaningfulJumpVariance': float(meaningfulJumpVariance) / float(pathcount),
                'jumpVariance': float(jumpVariance) / float(pathcount),
                'linearity': linearity,
                'solvability': 1.0,
                'rhythm': calculate_rhythm_metric(levelStr),
                'verticality': calculate_verticality(levelStr),
                'powerup_distribution': calculate_powerup_distribution(levelStr)}
    else:
        return {'length': maxX,
                'negativeSpace': negativeSpace,
                'pathPercentage': pathPercentage,
                'emptyPercentage': emptyPercentage,
                'decorationPercentage': decorationPercentage,
                'leniency': leniency,
                'meaningfulJumps': float(totalMeaningfulJumps) / float(pathcount),
                'jumps': float(totalJumps) / float(pathcount),
                'meaningfulJumpVariance': float(meaningfulJumpVariance) / float(pathcount),
                'jumpVariance': float(jumpVariance) / float(pathcount),
                'linearity': linearity,
                'solvability': 1.0,
                'rhythm': calculate_rhythm_metric(levelStr),
                'verticality': calculate_verticality(levelStr),
                'powerup_distribution': calculate_powerup_distribution(levelStr)}

def calculate_rhythm_metric(levelStr):
    """Measures the rhythmic spacing of challenges"""
    maxY = len(levelStr)
    maxX = len(levelStr[0])
    challenge_positions = []
    for x in range(maxX):
        for y in range(maxY):
            if levelStr[y][x] in ['E', '-'] or \
               (y < maxY-1 and levelStr[y][x] in ['?', 'M', 'B'] and levelStr[y+1][x] == '-'):
                challenge_positions.append(x)
    
    if len(challenge_positions) < 2:
        return 0
        
    spacings = [challenge_positions[i+1] - challenge_positions[i] 
               for i in range(len(challenge_positions)-1)]
    
    avg_spacing = sum(spacings) / len(spacings)
    variance = sum((s - avg_spacing) ** 2 for s in spacings) / len(spacings)
    
    ideal_variance = 16
    return 1.0 / (1.0 + abs(variance - ideal_variance))

def calculate_verticality(levelStr):
    """Measures how much vertical exploration is encouraged"""
    maxY = len(levelStr)
    maxX = len(levelStr[0])
    height_utilization = [0] * maxX
    for x in range(maxX):
        solid_found = False
        max_height = 0
        for y in range(maxY-2, -1, -1):
            if levelStr[y][x] in ['X', '?', 'M', 'B', '|', 'T']:
                if not solid_found:
                    solid_found = True
                max_height = maxY - y
        height_utilization[x] = max_height if solid_found else 0
    
    valid_heights = [h for h in height_utilization if h > 0]
    if not valid_heights:
        return 0
    avg_height = sum(valid_heights) / len(valid_heights)
    height_variety = sum(1 for h in valid_heights if abs(h - avg_height) > 2)
    
    return min(1.0, height_variety / (maxX * 0.3))

def calculate_powerup_distribution(levelStr):
    """Evaluates the distribution of powerups and their accessibility"""
    maxY = len(levelStr)
    maxX = len(levelStr[0])
    powerup_positions = []
    for x in range(maxX):
        for y in range(maxY):
            if levelStr[y][x] == 'M':
                powerup_positions.append((x, y))
    
    if not powerup_positions:
        return 0
        
    x_positions = sorted([p[0] for p in powerup_positions])
    if len(x_positions) < 2:
        spacing_score = 1.0
    else:
        spacings = [x_positions[i+1] - x_positions[i] for i in range(len(x_positions)-1)]
        avg_spacing = sum(spacings) / len(spacings)
        ideal_spacing = maxX * 0.25
        spacing_score = 1.0 / (1.0 + abs(avg_spacing - ideal_spacing))
    
    return spacing_score

if __name__ == "__main__":
    name = sys.argv[1]
    with open(name, 'r') as openFile:
        lines = openFile.readlines()
    print(len(lines), len(lines[0]))
    print(metrics(lines))
