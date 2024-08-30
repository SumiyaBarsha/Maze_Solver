import random

# Define the grid size and goal position
grid_size = 10
goal_position = (grid_size // 2, grid_size // 2)

# Initial positions for cat and robot
cat_position = (0, 0)
robot_position = (9, 9)

def print_grid(cat_position, robot_position, goal_position):
    for i in range(grid_size):
        for j in range(grid_size):
            if (i, j) == cat_position:
                print("C", end=" ")
            elif (i, j) == robot_position:
                print("R", end=" ")
            elif (i, j) == goal_position:
                print("G", end=" ")
            else:
                print(".", end=" ")
        print()
    print()

def is_goal(position):
    return position == goal_position

def get_neighbors(position):
    x, y = position
    neighbors = []
    if x > 0: neighbors.append((x-1, y))
    if x < grid_size-1: neighbors.append((x+1, y))
    if y > 0: neighbors.append((x, y-1))
    if y < grid_size-1: neighbors.append((x, y+1))
    return neighbors

def evaluate(position):
    x, y = position
    gx, gy = goal_position
    return abs(gx - x) + abs(gy - y)

def minimax(current, depth, alpha, beta, maximizing, visited):
    if depth == 0 or is_goal(current):
        return evaluate(current)
    
    if current in visited:
        return float('-inf') if maximizing else float('inf')
    
    visited.add(current)
    
    if maximizing:
        max_eval = float('-inf')
        for neighbor in get_neighbors(current):
            eval = minimax(neighbor, depth - 1, alpha, beta, False, visited)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        visited.remove(current)
        return max_eval
    else:
        min_eval = float('inf')
        for neighbor in get_neighbors(current):
            eval = minimax(neighbor, depth - 1, alpha, beta, True, visited)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        visited.remove(current)
        return min_eval

def get_best_move(position, depth, maximizing):
    best_move = None
    best_value = float('-inf') if maximizing else float('inf')
    for neighbor in get_neighbors(position):
        visited = set()
        value = minimax(neighbor, depth - 1, float('-inf'), float('inf'), not maximizing, visited)
        if (maximizing and value > best_value) or (not maximizing and value < best_value):
            best_value = value
            best_move = neighbor
    return best_move

# Main game loop
turn = "cat"
depth = 5  # Set the depth for Minimax search
print_grid(cat_position, robot_position, goal_position)
while True:
    if turn == "cat":
        # Get user input for cat move
        move = input("Enter move for cat (W/A/S/D): ").upper()
        if move == "W" and cat_position[0] > 0:
            cat_position = (cat_position[0] - 1, cat_position[1])
        elif move == "A" and cat_position[1] > 0:
            cat_position = (cat_position[0], cat_position[1] - 1)
        elif move == "S" and cat_position[0] < grid_size - 1:
            cat_position = (cat_position[0] + 1, cat_position[1])
        elif move == "D" and cat_position[1] < grid_size - 1:
            cat_position = (cat_position[0], cat_position[1] + 1)
        else:
            print("Invalid move!")
            continue
        if is_goal(cat_position):
            print("Cat wins!")
            break
        turn = "robot"
    else:
        # AI move for robot using Minimax
        robot_position = get_best_move(robot_position, depth, True)
        if is_goal(robot_position):
            print("Robot wins!")
            break
        turn = "cat"
    print_grid(cat_position, robot_position, goal_position)
