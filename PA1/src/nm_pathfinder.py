# python3 nm_interactive.py ../input/homer.gif ../input/homer.gif.mesh.pickle 2from heapq import heappop, heappushfrom math import sqrtdef euclidean_distance(point1, point2):    """Calculate the Euclidean distance between two points."""    return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)def find_path(source_point, destination_point, mesh):    """    Searches for a path from source_point to destination_point through    the mesh using bidirectional A* search.    Args:        source_point: starting point of the pathfinder        destination_point: the ultimate goal the pathfinder must reach        mesh: pathway constraints the path adheres to    Returns:        A path (list of points) from source_point to destination_point if exists        A list of boxes explored by the algorithm    """    # Helper function to identify the box containing a given point    def find_box(point):        for box in mesh['boxes']:            x1, x2, y1, y2 = box            if x1 <= point[0] < x2 and y1 <= point[1] < y2:                return box        print(f"Point {point} is not in any box!")        return None    # Debugging: Print mesh information    print("Mesh Info:")    print(f"Boxes: {mesh['boxes']}")    print(f"Adjacency: {mesh['adj']}")    start_box = find_box(source_point)    end_box = find_box(destination_point)    if not start_box or not end_box:        print("No valid start or end box found!")        return [], []    # Priority queues for forward and backward search    forward_queue = [(0, start_box, source_point)]    backward_queue = [(0, end_box, destination_point)]    # Distances and predecessors for both directions    forward_dist = {start_box: 0}    backward_dist = {end_box: 0}    forward_prev = {start_box: source_point}    backward_prev = {end_box: destination_point}    visited_boxes = set()    def expand_search(queue, dist, prev, other_dist):        if not queue:            return None        priority, current_box, current_point = heappop(queue)        visited_boxes.add(current_box)        if current_box in other_dist:            print(f"Meeting box found: {current_box}")            return current_box        for neighbor in mesh['adj'].get(current_box, []):            if neighbor not in mesh['boxes']:                print(f"Invalid neighbor: {neighbor}")                continue            next_point = (                min(max(current_point[0], neighbor[0]), neighbor[1] - 1),                min(max(current_point[1], neighbor[2]), neighbor[3] - 1)            )            cost = euclidean_distance(current_point, next_point)            new_dist = dist[current_box] + cost            if neighbor not in dist or new_dist < dist[neighbor]:                dist[neighbor] = new_dist                prev[neighbor] = next_point                heuristic = euclidean_distance(next_point, destination_point)                heappush(queue, (new_dist + heuristic, neighbor, next_point))        return None    meeting_box = None    while forward_queue and backward_queue:        meeting_box = expand_search(forward_queue, forward_dist, forward_prev, backward_dist)        if meeting_box:            break        meeting_box = expand_search(backward_queue, backward_dist, backward_prev, forward_dist)        if meeting_box:            break    if not meeting_box:        print("No path exists!")        return [], list(visited_boxes)    # Reconstruct path    path = []    # Forward path    box = meeting_box    while box in forward_prev:        path.append(forward_prev[box])        box = next((b for b in forward_prev if forward_prev[b] == forward_prev[box] and b != box), None)    path.reverse()    # Backward path    box = meeting_box    while box in backward_prev:        if backward_prev[box] not in path:            path.append(backward_prev[box])        box = next((b for b in backward_prev if backward_prev[b] == backward_prev[box] and b != box), None)    return path, list(visited_boxes)