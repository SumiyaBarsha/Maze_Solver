def heuristic(cell, goal):
    # Manhattan distance heuristic
    return abs(cell.r - goal.r) + abs(cell.c - goal.c)

def alpha_beta_pruning(cell, goal, grid, depth, alpha, beta, minimizingPlayer, visited):
    if cell == goal:
        return 0, [cell]
    if depth == 0:
        return heuristic(cell, goal), [cell]

    visited.add(cell)

    if minimizingPlayer:
        minEval = float('inf')
        bestPath = []
        for neighbor in cell.create_neighbors(grid):
            if not neighbor.visited:
                continue
            if neighbor not in visited:
                if (cell.walls[0] == False and neighbor == grid[cell.r-1][cell.c]) or \
                   (cell.walls[1] == False and neighbor == grid[cell.r][cell.c+1]) or \
                   (cell.walls[2] == False and neighbor == grid[cell.r+1][cell.c]) or \
                   (cell.walls[3] == False and neighbor == grid[cell.r][cell.c-1]):
                    eval, path = alpha_beta_pruning(neighbor, goal, grid, depth - 1, alpha, beta, False, visited)
                    if eval < minEval:
                        minEval = eval
                        bestPath = [cell] + path
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        visited.remove(cell)
        return minEval, bestPath
    else:
        maxEval = float('-inf')
        bestPath = []
        for neighbor in cell.create_neighbors(grid):
            if not neighbor.visited:
                continue
            if neighbor not in visited:
                if (cell.walls[0] == False and neighbor == grid[cell.r-1][cell.c]) or \
                   (cell.walls[1] == False and neighbor == grid[cell.r][cell.c+1]) or \
                   (cell.walls[2] == False and neighbor == grid[cell.r+1][cell.c]) or \
                   (cell.walls[3] == False and neighbor == grid[cell.r][cell.c-1]):
                    eval, path = alpha_beta_pruning(neighbor, goal, grid, depth - 1, alpha, beta, True, visited)
                    if eval > maxEval:
                        maxEval = eval
                        bestPath = [cell] + path
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        visited.remove(cell)
        return maxEval, bestPath

def evaluate(cell, goal):
    return -(abs(cell.r - goal.r) + abs(cell.c - goal.c))


def find_best_move(current, goal, grid, depth, alpha, beta, maximizing_player, visited_cells):
    if current == goal or depth == 0:
        return evaluate(current, goal), [current]

    best_path = []
    neighbors = current.create_neighbors(grid)
    if maximizing_player:
        max_eval = float('-inf')
        for neighbor in neighbors:
            if neighbor not in visited_cells and not current.walls[current.create_neighbors(grid).index(neighbor)]:
                visited_cells.add(neighbor)
                evaluation, path = find_best_move(neighbor, goal, grid, depth - 1, alpha, beta, False, visited_cells)
                visited_cells.remove(neighbor)
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_path = [current] + path
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
        return max_eval, best_path
    else:
        min_eval = float('inf')
        for neighbor in neighbors:
            if neighbor not in visited_cells and not current.walls[current.create_neighbors(grid).index(neighbor)]:
                visited_cells.add(neighbor)
                evaluation, path = find_best_move(neighbor, goal, grid, depth - 1, alpha, beta, True, visited_cells)
                visited_cells.remove(neighbor)
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_path = [current] + path
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
        return min_eval, best_path

