from heapq import heappop, heappush
from math import sqrt

def euclidean_distance(point1, point2):
    """Calculate the Euclidean distance between two points."""
    return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def find_path(source_point, destination_point, mesh):
    """
    Searches for a path from source_point to destination_point through the mesh using bidirectional A* search.

    Args:
        source_point: starting point of the pathfinder
        destination_point: the ultimate goal the pathfinder must reach
        mesh: pathway constraints the path adheres to

    Returns:
        A path (list of points) from source_point to destination_point if exists
        A list of boxes explored by the algorithm
    """
    def find_box(point):
        """Find the box that contains the given point."""
        for box in mesh['boxes']:
            x1, x2, y1, y2 = box
            if x1 <= point[0] < x2 and y1 <= point[1] < y2:
                return box
        return None

    start_box = find_box(source_point)
    end_box = find_box(destination_point)

    if not start_box or not end_box:
        print("Source or destination point is not within any box!")
        return [], []

    # Priority queue for A* search
    queue = [(0, start_box, source_point, [])]  # (priority, current_box, current_point, path_so_far)
    visited_boxes = set()
    distances = {start_box: 0}

    while queue:
        priority, current_box, current_point, path_so_far = heappop(queue)

        # Add the current box to visited
        visited_boxes.add(current_box)

        # If we reach the destination box, construct the path
        if current_box == end_box:
            # Add the final segment to the path
            path_so_far.append(destination_point)
            return path_so_far, list(visited_boxes)

        # Expand neighbors
        for neighbor in mesh['adj'].get(current_box, []):
            # Constrain the next point to be within the bounds of the neighbor box
            next_point = (
                min(max(current_point[0], neighbor[0]), neighbor[1] - 1),
                min(max(current_point[1], neighbor[2]), neighbor[3] - 1)
            )
            # Calculate cost and heuristic
            cost = distances[current_box] + euclidean_distance(current_point, next_point)
            heuristic = euclidean_distance(next_point, destination_point)

            if neighbor not in distances or cost < distances[neighbor]:
                distances[neighbor] = cost
                # Add the direct path from the source or previous point
                new_path = path_so_far + [next_point]
                heappush(queue, (cost + heuristic, neighbor, next_point, new_path))

    print("No path found!")
    return [], list(visited_boxes)
