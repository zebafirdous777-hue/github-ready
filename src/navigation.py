from collections import deque


def find_route(start, goal, obstacles, grid_size=5):
    def inside_grid(cell):
        x, y = cell
        return 0 <= x < grid_size and 0 <= y < grid_size

    if (
        not inside_grid(start)
        or not inside_grid(goal)
        or start in obstacles
        or goal in obstacles
    ):
        return None

    paths_to_check = deque([[start]])
    visited = {start}
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while paths_to_check:
        path = paths_to_check.popleft()
        x, y = path[-1]

        if (x, y) == goal:
            return path

        for move_x, move_y in moves:
            next_cell = (x + move_x, y + move_y)
            if (
                inside_grid(next_cell)
                and next_cell not in obstacles
                and next_cell not in visited
            ):
                visited.add(next_cell)
                paths_to_check.append(path + [next_cell])

    return None


def find_coverage_route(start, obstacles, grid_size=5):
    """Build a route that visits every open cell reachable from start.

    At each step, the closest unvisited cell is selected using shortest-path
    distance. This is a simple coverage heuristic, not a globally optimal tour.
    """
    if find_route(start, start, obstacles, grid_size) is None:
        return None

    reachable = {start}
    frontier = deque([start])
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while frontier:
        x, y = frontier.popleft()
        for dx, dy in moves:
            cell = (x + dx, y + dy)
            if (
                0 <= cell[0] < grid_size
                and 0 <= cell[1] < grid_size
                and cell not in obstacles
                and cell not in reachable
            ):
                reachable.add(cell)
                frontier.append(cell)

    route = [start]
    visited = {start}
    current = start
    while visited != reachable:
        remaining = reachable - visited
        target = min(
            remaining,
            key=lambda cell: (
                len(find_route(current, cell, obstacles, grid_size)),
                cell[1],
                cell[0],
            ),
        )
        segment = find_route(current, target, obstacles, grid_size)
        route.extend(segment[1:])
        visited.update(segment)
        current = target

    return route


if __name__ == "__main__":
    start = (0, 0)
    fire = (4, 3)
    obstacles = {(2, 0), (2, 1), (2, 2)}

    route = find_route(start, fire, obstacles)

    if route:
        print("Route to fire:")
        for position in route:
            print(position)
    else:
        print("No route to the fire was found.")
