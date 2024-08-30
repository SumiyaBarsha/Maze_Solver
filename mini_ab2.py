import pygame
from collections import deque

def heuristic(a, b):
    return abs(a.r - b.r) + abs(a.c - b.c)

def alpha_beta_search(grid, start, goal, depth, alpha, beta, maximizing_player, visited):
    if depth == 0 or start == goal:
        return heuristic(start, goal)

    neighbors = get_neighbors(grid, start)
    
    if maximizing_player:
        max_eval = float('-inf')
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                eval = alpha_beta_search(grid, neighbor, goal, depth - 1, alpha, beta, False, visited)
                visited.remove(neighbor)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float('inf')
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                eval = alpha_beta_search(grid, neighbor, goal, depth - 1, alpha, beta, True, visited)
                visited.remove(neighbor)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

def get_neighbors(grid, cell):
    neighbors = []
    r, c = cell.r, cell.c
    if r > 0 and not grid[r][c].walls[0]:  # Up
        neighbors.append(grid[r-1][c])
    if r < len(grid) - 1 and not grid[r][c].walls[2]:  # Down
        neighbors.append(grid[r+1][c])
    if c > 0 and not grid[r][c].walls[3]:  # Left
        neighbors.append(grid[r][c-1])
    if c < len(grid[0]) - 1 and not grid[r][c].walls[1]:  # Right
        neighbors.append(grid[r][c+1])
    return neighbors

def minimax_ab(current, goal, grid, depth, alpha, beta, maximizing_player, visited):
    if depth == 0 or current == goal:
        return heuristic(current, goal), [current]

    neighbors = get_neighbors(grid, current)
    best_path = []

    if maximizing_player:
        max_eval = float('-inf')
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                eval, path = minimax_ab(neighbor, goal, grid, depth - 1, alpha, beta, False, visited)
                visited.remove(neighbor)
                if eval > max_eval:
                    max_eval = eval
                    best_path = [current] + path
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval, best_path
    else:
        min_eval = float('inf')
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                eval, path = minimax_ab(neighbor, goal, grid, depth - 1, alpha, beta, True, visited)
                visited.remove(neighbor)
                if eval < min_eval:
                    min_eval = eval
                    best_path = [current] + path
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval, best_path

def find_best_move(current, goal, grid, depth, visited):
    _, path = minimax_ab(current, goal, grid, depth, float('-inf'), float('inf'), True, visited)
    return path[1] if len(path) > 1 else None, path
