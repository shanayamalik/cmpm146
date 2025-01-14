from heapq import heappop, heappush
from math import sqrt

def euclidean_distance(point1, point2):
    """Calculate the Euclidean distance between two points."""
    return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def find_path(source_point, destination_point, mesh):
    """
    Searches for a path from source_point to destination_point through the mesh using bidirectional A* search.

    Args:
        source_point: starting point of the pathfinder, given as an (x, y) tuple.
        destination_point: the ultimate goal the pathfinder must reach, also an (x, y) tuple.
        mesh: a dictionary representing the navigable space, containing:
            - 'boxes': a list of rectangular regions (nodes) defined by their bounds (x1, x2, y1, y2).
            - 'adj': a dictionary mapping each box to a list of its adjacent boxes (edges in the graph).

    Returns:
        A path (list of points) from source_point to destination_point if it exists.
        A list of boxes explored by the algorithm.
    """
    def find_box(point):
        """Find the box that contains the given point by checking if the point's coordinates fall within any box's bounds."""
        for box in mesh['boxes']:
            x1, x2, y1, y2 = box
            if x1 <= point[0] < x2 and y1 <= point[1] < y2:
                return box
        return None  # Return None if the point is outside all boxes.

    # Identify the start and end boxes that contain the source and destination points.
    start_box = find_box(source_point)
    end_box = find_box(destination_point)

    if not start_box or not end_box:
        print("Source or destination point is not within any box!")
        return [], []

    # Priority queues for bidirectional A* search, initialized with the start and end points.
    forward_queue = [(0, start_box, source_point)]  # (priority, current_box, current_point)
    backward_queue = [(0, end_box, destination_point)]

    # Distance tables to track the cost of reaching each box from the start and end points.
    forward_distances = {start_box: 0}
    backward_distances = {end_box: 0}

    # Predecessor tables to reconstruct the path once the two searches meet.
    forward_prev = {start_box: (None, source_point)}
    backward_prev = {end_box: (None, destination_point)}

    # A set to keep track of visited boxes.
    visited_boxes = set()

    def expand_search(queue, distances, prev, other_distances):
        """
        Expands the search from the current box in the given queue.

        Args:
            queue: the priority queue to expand.
            distances: the distance table for the current direction.
            prev: the predecessor table for the current direction.
            other_distances: the distance table for the opposite direction.

        Returns:
            The meeting box if the two searches meet, or None otherwise.
        """
        if not queue:
            return None

        # Pop the box with the lowest priority (shortest estimated distance to the goal).
        priority, current_box, current_point = heappop(queue)
        visited_boxes.add(current_box)  # Mark the current box as visited.

        # Check if this box has already been visited by the other search direction.
        if current_box in other_distances:
            return current_box

        # Expand each neighboring box.
        for neighbor in mesh['adj'].get(current_box, []):
            # Constrain the next point to be within the bounds of the neighbor box.
            next_point = (
                min(max(current_point[0], neighbor[0]), neighbor[1] - 1),
                min(max(current_point[1], neighbor[2]), neighbor[3] - 1)
            )
            # Calculate the total cost to reach the neighbor.
            cost = distances[current_box] + euclidean_distance(current_point, next_point)

            # Update the distance and predecessor tables if a shorter path is found.
            if neighbor not in distances or cost < distances[neighbor]:
                distances[neighbor] = cost
                prev[neighbor] = (current_box, next_point)
                # Calculate the priority using the cost and heuristic (estimated distance to the goal).
                heuristic = euclidean_distance(next_point, destination_point)
                heappush(queue, (cost + heuristic, neighbor, next_point))

        return None

    meeting_box = None  # This will store the box where the two searches meet.

    # Alternate between expanding the forward and backward searches.
    while forward_queue and backward_queue:
        meeting_box = expand_search(forward_queue, forward_distances, forward_prev, backward_distances)
        if meeting_box:
            break  # Stop if the searches meet.

        meeting_box = expand_search(backward_queue, backward_distances, backward_prev, forward_distances)
        if meeting_box:
            break  # Stop if the searches meet.

    if not meeting_box:
        print("No path found!")
        return [], list(visited_boxes)

    # Reconstruct the path from both directions once the meeting point is found.
    def reconstruct_path(forward_prev, backward_prev, meeting_box):
        """Reconstructs the path from the start to the destination by combining forward and backward paths."""
        path = []

        # Reconstruct the forward path from the start to the meeting point.
        box = meeting_box
        while box:
            prev_box, point = forward_prev[box]
            if point not in path:
                path.append(point)
            box = prev_box

        path.reverse()  # Reverse the forward path to get it in the correct order.

        # Reconstruct the backward path from the meeting point to the destination.
        box = meeting_box
        while box:
            prev_box, point = backward_prev[box]
            if point not in path:
                path.append(point)
            box = prev_box

        return path

    # Combine the forward and backward paths to form a complete path from source to destination.
    path = reconstruct_path(forward_prev, backward_prev, meeting_box)

    return path, list(visited_boxes)
