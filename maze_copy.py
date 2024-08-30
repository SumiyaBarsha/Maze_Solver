import pygame
import random
from collections import deque
from random import randint
from ga import *
import const
from const import WHITE,BLACK,PURPLE,BLUE,OLIVE,FPS
#import calc_score
from fuzzy_new import get_membership_blocks_accessed,get_membership_time_elapsed,rule_evaluation,defuzzify

# pygame.init()

# Constants
WIDTH, HEIGHT = const.WIDTH, const.HEIGHT
CELL_SIZE = const.CELL_SIZE
PADDING = const.PADDING  
MAX_moves = const.MAX_moves

nrows = HEIGHT // CELL_SIZE
ncols = WIDTH // CELL_SIZE  
print(nrows,ncols)
nempty = nrows//2

# Setup the display
win = pygame.display.set_mode((WIDTH+200, HEIGHT))
pygame.display.set_caption("Maze Solver")

# Load images
cat_img = pygame.image.load("G:/AMaze-Game/cat.png")
fish_img = pygame.image.load("G:/AMaze-Game/fish.png")
robot_img = pygame.image.load("G:/AMaze-Game/robot.png")
treasure_img = pygame.image.load("G:/AMaze-Game/treasure-chest.png")
cat_img = pygame.transform.scale(cat_img, (CELL_SIZE - PADDING, CELL_SIZE - PADDING))
robot_img = pygame.transform.scale(robot_img, (CELL_SIZE - PADDING, CELL_SIZE - PADDING))
fish_img = pygame.transform.scale(fish_img, (CELL_SIZE - PADDING, CELL_SIZE - PADDING))
treasure_img = pygame.transform.scale(treasure_img, (CELL_SIZE - PADDING, CELL_SIZE - PADDING))

# Button rectangles
regen_button_rect = pygame.Rect(WIDTH + 200 - 180, 50, 160, 40)
show_button_rect = pygame.Rect(WIDTH + 200 - 180, 100, 160, 40)
result_button_rect = pygame.Rect(WIDTH + 200 - 180, 150, 160, 40)
toggle_footprints_button_rect = pygame.Rect(WIDTH + 200 - 180, 200, 160, 40)
ga_button_rect = pygame.Rect(WIDTH + 200 - 180, 250, 160, 40)
minimax_button_rect = pygame.Rect(WIDTH + 200 - 180, 300, 160, 40)

class Cell:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.walls = [True, True, True, True]  # Top Right Bottom Left
        self.visited = False
        self.path_visited = False
        self.part_of_result_path = False
        self.parent = None

    def draw(self, win, show_footprints):
        x = self.c * CELL_SIZE
        y = self.r * CELL_SIZE

        if self.visited:
            pygame.draw.rect(win, BLACK, (x + PADDING, y + PADDING, CELL_SIZE - PADDING*2, CELL_SIZE - PADDING*2))

        if show_footprints and self.path_visited:
            pygame.draw.rect(win, PURPLE, (x + PADDING, y + PADDING, CELL_SIZE - PADDING*2, CELL_SIZE - PADDING*2))

        if self.part_of_result_path:
            pygame.draw.rect(win, BLUE, (x + PADDING, y + PADDING, CELL_SIZE - PADDING*2, CELL_SIZE - PADDING*2))

        if self.walls[0]:
            pygame.draw.line(win, WHITE, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls[1]:
            pygame.draw.line(win, WHITE, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls[2]:
            pygame.draw.line(win, WHITE, (x + CELL_SIZE, y + CELL_SIZE), (x, y + CELL_SIZE), 2)
        if self.walls[3]:
            pygame.draw.line(win, WHITE, (x, y + CELL_SIZE), (x, y), 2)

    def create_neighbors(self, grid):
        neighbors = []
        if self.r > 0:
            neighbors.append(grid[self.r - 1][self.c])
        if self.c < ncols - 1:
            neighbors.append(grid[self.r][self.c + 1])
        if self.r < nrows - 1:
            neighbors.append(grid[self.r + 1][self.c])
        if self.c > 0:
            neighbors.append(grid[self.r][self.c - 1])
        return neighbors
    
def remove_walls(current, next):
    dx = current.c - next.c
    dy = current.r - next.r
    if dx == 1:  # Next is left of current
        current.walls[3] = False
        next.walls[1] = False
    elif dx == -1:  # Next is right of current
        current.walls[1] = False
        next.walls[3] = False
    if dy == 1:  # Next is above current
        current.walls[0] = False
        next.walls[2] = False
    elif dy == -1:  # Next is below current
        current.walls[2] = False
        next.walls[0] = False

def random_remove_walls(grid, start, goal, num_walls):
    path = bfs(grid, start, goal)
    if not path:
        return  # No path found

    # Set to keep track of cells already modified to avoid redundant work
    modified_cells = set()

    for _ in range(num_walls):
        # Randomly decide whether to remove walls from the path or the entire grid
        if random.random() < 0.5 and len(path) > 1:
            # Choose a random cell along the path (except the last one)
            idx = random.randint(0, len(path) - 2)
            current = path[idx]
        else:
            # Choose a random cell from the grid
            r = random.randint(0, nrows - 1)
            c = random.randint(0, ncols - 1)
            current = grid[r][c]

        # Ensure we are not modifying the same cell multiple times
        if current in modified_cells:
            continue

        # Mark the cell as modified
        modified_cells.add(current)

        # Remove all walls from the current cell
        for neighbor in current.create_neighbors(grid):
            remove_walls(current, neighbor)

        # Recalculate the path after removing walls to ensure it still leads to the goal
        path = bfs(grid, start, goal)
        if not path:
            break



def generate_maze(grid):
    stack = []
    current = grid[0][0]
    while True:
        current.visited = True
        neighbors = [cell for cell in current.create_neighbors(grid) if not cell.visited]
        if neighbors:
            next_cell = random.choice(neighbors)
            stack.append(current)
            remove_walls(current, next_cell)
            current = next_cell
        elif stack:
            current = stack.pop()
        else:
            break

def step_maze_generation(grid, stack, current):
    current.visited = True
    neighbors = [cell for cell in current.create_neighbors(grid) if not cell.visited]
    if neighbors:
        next_cell = random.choice(neighbors)
        stack.append(current)
        remove_walls(current, next_cell)
        current = next_cell
    elif stack:
        current = stack.pop()
    return current, stack

def draw_grid(win, grid, show_footprints):
    for row in grid:
        for cell in row:
            cell.draw(win, show_footprints)

def draw_buttons(win):
    pygame.draw.rect(win, OLIVE, regen_button_rect)
    pygame.draw.rect(win, OLIVE, show_button_rect)
    pygame.draw.rect(win, OLIVE, result_button_rect)
    pygame.draw.rect(win, OLIVE, toggle_footprints_button_rect)
    pygame.draw.rect(win, OLIVE, ga_button_rect)
    pygame.draw.rect(win, OLIVE, minimax_button_rect)
    font = pygame.font.Font(None, 36)
    regen_text = font.render('Regenerate', True, WHITE)
    show_text = font.render('Show Gen', True, WHITE)
    result_text = font.render('Result', True, WHITE)
    toggle_footprints_text = font.render('Footprints', True, WHITE)
    ga_text = font.render('Run GA', True, WHITE)
    minimax_text = font.render('Run MinMax', True, WHITE)
    win.blit(regen_text, (regen_button_rect.x + 10, regen_button_rect.y + 5))
    win.blit(show_text, (show_button_rect.x + 10, show_button_rect.y + 5))
    win.blit(result_text, (result_button_rect.x + 10, result_button_rect.y + 5))
    win.blit(toggle_footprints_text, (toggle_footprints_button_rect.x + 10, toggle_footprints_button_rect.y + 5))
    win.blit(ga_text, (ga_button_rect.x + 10, ga_button_rect.y + 5))
    win.blit(minimax_text, (minimax_button_rect.x + 10, minimax_button_rect.y + 5))

def bfs(grid, start, goal):
    queue = deque([(start, [])])
    visited = set()
    while queue:
        current, path = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        path = path + [current]
        if current == goal:
            return path
        neighbors = current.create_neighbors(grid)
        for neighbor in neighbors:
            if not neighbor.visited:
                continue
            if neighbor not in visited:
                if (current.walls[0] == False and neighbor == grid[current.r-1][current.c]) or \
                   (current.walls[1] == False and neighbor == grid[current.r][current.c+1]) or \
                   (current.walls[2] == False and neighbor == grid[current.r+1][current.c]) or \
                   (current.walls[3] == False and neighbor == grid[current.r][current.c-1]):
                    queue.append((neighbor, path))
    return path

def calculate_score_fuzzy(blocks_accessed, optimal_path_length, time_elapsed, level):
    if level == 'easy':
        time_elapsed_membership = get_membership_time_elapsed(time_elapsed,optimal_path_length,level)
        blocks_accessed_membership = get_membership_blocks_accessed(blocks_accessed,optimal_path_length,level)
        
    elif level == 'medium':
        time_elapsed_membership = get_membership_time_elapsed(time_elapsed,optimal_path_length,level)
        blocks_accessed_membership = get_membership_blocks_accessed(blocks_accessed,optimal_path_length,level)
       
    elif level == 'hard':
        time_elapsed_membership = get_membership_time_elapsed(time_elapsed,optimal_path_length,level)
        blocks_accessed_membership = get_membership_blocks_accessed(blocks_accessed,optimal_path_length,level)
    else:
        raise ValueError("Invalid level")

    low, medium, high = rule_evaluation(blocks_accessed_membership,time_elapsed_membership)
    score = defuzzify(low, medium, high)
    # Determine score category
    if score < 34:
        category = "Low"
    elif score >35 and score < 67:
        category = "Medium"
    else:
        category = "High"
    return score,category

def minimax(grid, start, goal, depth, alpha, beta, is_maximizing):
    if depth == 0 or start == goal:
        return -len(bfs(grid, start, goal))  # Heuristic: negative path length

    neighbors = start.create_neighbors(grid)
    if is_maximizing:
        max_eval = float('-inf')
        for neighbor in neighbors:
            if (start.walls[0] == False and neighbor == grid[start.r - 1][start.c]) or \
               (start.walls[1] == False and neighbor == grid[start.r][start.c + 1]) or \
               (start.walls[2] == False and neighbor == grid[start.r + 1][start.c]) or \
               (start.walls[3] == False and neighbor == grid[start.r][start.c - 1]):
                eval = minimax(grid, neighbor, goal, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float('inf')
        for neighbor in neighbors:
            if (start.walls[0] == False and neighbor == grid[start.r - 1][start.c]) or \
               (start.walls[1] == False and neighbor == grid[start.r][start.c + 1]) or \
               (start.walls[2] == False and neighbor == grid[start.r + 1][start.c]) or \
               (start.walls[3] == False and neighbor == grid[start.r][start.c - 1]):
                eval = minimax(grid, neighbor, goal, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

def get_best_move(grid, start, goal, depth, visited_states):
    best_move = None
    max_eval = float('-inf')
    for neighbor in start.create_neighbors(grid):
        if (start.walls[0] == False and neighbor == grid[start.r - 1][start.c]) or \
           (start.walls[1] == False and neighbor == grid[start.r][start.c + 1]) or \
           (start.walls[2] == False and neighbor == grid[start.r + 1][start.c]) or \
           (start.walls[3] == False and neighbor == grid[start.r][start.c - 1]):
            eval = minimax(grid, neighbor, goal, depth, float('-inf'), float('inf'), False)
            if neighbor not in visited_states:  # Avoid revisiting the same state
                eval = minimax(grid, neighbor, goal, depth, float('-inf'), float('inf'), False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = neighbor
    return best_move


def main(difficulty_level):
    clock = pygame.time.Clock()
    grid = [[Cell(r, c) for c in range(ncols)] for r in range(nrows)]
    generate_maze(grid)
    nempty = nrows//2
    random_remove_walls(grid, grid[0][0], grid[nrows - 1][ncols - 1], nempty)
    print(nempty)
    current = grid[0][0]

    current_cat = grid[0][0]
    current_robot = grid[0][ncols - 1]
    goal_mini = grid[nrows // 2][ncols // 2]

    goal = grid[nrows - 1][ncols - 1]
    stack = []
    generating = False
    show_footprints = True
    cat_turn = True
    minimax_running = False


    ga_running = False
    ga_start_time = 0
    ga_best_fitness = 0
    ga_generations = 0
    ga_best_path = []

    extra_blocks_accessed_count = 0
    start_time = pygame.time.get_ticks()
    block_count = 0
    agent_block_count = 1
    levels = {1: 'easy', 2: 'medium', 3: 'hard'}
    level = levels[difficulty_level]
    category = None


    running = True
    while running:
        clock.tick(FPS)
        win.fill(BLACK)

        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) / 1000  # Convert to seconds
        if level == 'easy':
            optimal_time = len(bfs(grid,grid[0][0],goal))*0.6
            timeout_threshold = optimal_time*10.0
        elif level == 'medium':
            optimal_time = len(bfs(grid,grid[0][0],goal))*0.5
            timeout_threshold = optimal_time*2.0
        elif level == 'hard':
            optimal_time = len(bfs(grid,grid[0][0],goal))*0.48
            timeout_threshold = optimal_time*0.8 + optimal_time
        else:
            raise ValueError("Invalid level")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if regen_button_rect.collidepoint(event.pos):
                    grid = [[Cell(r, c) for c in range(ncols)] for r in range(nrows)]
                    generate_maze(grid) 
                    random_remove_walls(grid, grid[0][0], grid[nrows - 1][ncols - 1], nempty)
                    current = grid[0][0]
                    goal = grid[nrows - 1][ncols - 1]
                    stack = []
                    generating = False
                    ga_running = False
                    minimax_running = False
                elif show_button_rect.collidepoint(event.pos):
                    grid = [[Cell(r, c) for c in range(ncols)] for r in range(nrows)]
                    current = grid[0][0]
                    goal = grid[nrows - 1][ncols - 1]
                    stack = []
                    generating = True
                    ga_running = False
                    minimax_running = False
                elif result_button_rect.collidepoint(event.pos):
                    path = bfs(grid, grid[0][0], goal)
                    block_count = len(path)
                    print("Count: ",block_count)
                    if path:
                        for cell in path:
                            cell.part_of_result_path = True
                    ga_running = False
                    minimax_running = False
                elif toggle_footprints_button_rect.collidepoint(event.pos):
                    show_footprints = not show_footprints
                    minimax_running = False
                elif ga_button_rect.collidepoint(event.pos):
                    ga_running = True
                    ga_start_time = pygame.time.get_ticks()
                    ga_best_fitness = 0
                    ga_generations = 0
                    ga_best_path = []
                    minimax_running = False
                elif minimax_button_rect.collidepoint(event.pos):
                    ga_running = False
                    minimax_running = True
                    current_cat = grid[0][0]
                    current_robot = grid[0][ncols - 1]
                    cat_turn = True
                    visited_states = set()
                    visited_states.add(current_robot)
           

            elif event.type == pygame.KEYDOWN:
                prev_r, prev_c = current.r, current.c
                if not generating:
                    if event.key == pygame.K_UP and not current.walls[0]:
                        current.path_visited = True
                        current = grid[current.r - 1][current.c]
                        agent_block_count+=1
                    elif event.key == pygame.K_DOWN and not current.walls[2]:
                        current.path_visited = True
                        current = grid[current.r + 1][current.c]
                        agent_block_count+=1
                    elif event.key == pygame.K_LEFT and not current.walls[3]:
                        current.path_visited = True
                        current = grid[current.r][current.c - 1]
                        agent_block_count+=1
                    elif event.key == pygame.K_RIGHT and not current.walls[1]:
                        current.path_visited = True
                        current = grid[current.r][current.c + 1]
                        agent_block_count+=1

                    if (prev_r, prev_c) != (current.r, current.c):
                        extra_blocks_accessed_count += 1
                    
                if minimax_running and not generating:
                    if cat_turn:
                        prev_cat = current_cat
                        if event.key == pygame.K_UP and not current_cat.walls[0]:
                            current_cat = grid[current_cat.r - 1][current_cat.c]
                        elif event.key == pygame.K_DOWN and not current_cat.walls[2]:
                            current_cat = grid[current_cat.r + 1][current_cat.c]
                        elif event.key == pygame.K_LEFT and not current_cat.walls[3]:
                            current_cat = grid[current_cat.r][current_cat.c - 1]
                        elif event.key == pygame.K_RIGHT and not current_cat.walls[1]:
                            current_cat = grid[current_cat.r][current_cat.c + 1]
                        
                        if current_cat != prev_cat:
                            cat_turn = False

        if not cat_turn and minimax_running and not generating:
            prev_robot = current_robot
            best_move = get_best_move(grid, current_robot, goal_mini, 3, visited_states)
            if best_move and best_move != prev_robot:
                current_robot = best_move
                visited_states.add(current_robot)
                cat_turn = True

        if generating:
            current, stack = step_maze_generation(grid, stack, current)
            if not stack and all(cell.visited for row in grid for cell in row):
                generating = False

        if ga_running:
            current_time = pygame.time.get_ticks()
            if current_time - ga_start_time >= 1200:
                ga_start_time = current_time
                ga_generations += 1
                best_path = run_genetic_algorithm(grid, grid[0][0], goal, nrows, ncols, pop_size=1000, max_moves=MAX_moves, num_generations=1, mutation_rate=0.01)
                current = grid[0][0]
                for move in best_path:
                    current.path_visited = True
                    if move == 'U' and not current.walls[0] and current.r > 0:
                        current = grid[current.r - 1][current.c]
                    elif move == 'D' and not current.walls[2] and current.r < nrows - 1:
                        current = grid[current.r + 1][current.c]
                    elif move == 'L' and not current.walls[3] and current.c > 0:
                        current = grid[current.r][current.c - 1]
                    elif move == 'R' and not current.walls[1] and current.c < ncols - 1:
                        current = grid[current.r][current.c + 1]
                    if current == goal:
                        break
                fitness = evaluate_individual(grid, best_path, grid[0][0], goal, nrows, ncols)
                if fitness > ga_best_fitness:
                    ga_best_fitness = fitness
                    ga_best_path = best_path
                print(f"Generation: {ga_generations}, Fitness: {ga_best_fitness}")


        draw_grid(win, grid, show_footprints)
        draw_buttons(win)
        if minimax_running:
            win.blit(treasure_img, (goal_mini.c * CELL_SIZE + PADDING, goal_mini.r * CELL_SIZE + PADDING))
            win.blit(cat_img, (current_cat.c * CELL_SIZE + PADDING, current_cat.r * CELL_SIZE + PADDING))
            win.blit(robot_img, (current_robot.c * CELL_SIZE + PADDING, current_robot.r * CELL_SIZE + PADDING))
        else:
            win.blit(cat_img, (current.c * CELL_SIZE + PADDING, current.r * CELL_SIZE + PADDING))
            win.blit(fish_img, (goal.c * CELL_SIZE + PADDING, goal.r * CELL_SIZE + PADDING))
        
        

        # Draw remaining time
        font = pygame.font.Font(None, 26)
        elapsed_time_text = font.render(f"Time Count: {elapsed_time:.2f}s", True, WHITE)
        win.blit(elapsed_time_text, (regen_button_rect.x, regen_button_rect.y - 40))

        pygame.display.flip()
        

        if elapsed_time > timeout_threshold:
            print("Timeout!")
            timeout_message(win)
            running = False
        
        if current_cat == goal_mini:
            print("Cat wins!")
            running = False
        elif current_robot == goal_mini:
            print("Robot wins!")
            running = False

        if current == goal and not generating:
            print("You won!")
            winning_message(win)
            end_time = pygame.time.get_ticks()
            time_elapsed = (end_time - start_time) / 1000  # Convert to seconds
            print(f'Time Elapsed: {time_elapsed}')
            path = bfs(grid, grid[0][0], goal)
            block_count = len(path)  
            score,category = calculate_score_fuzzy(extra_blocks_accessed_count, block_count, time_elapsed, level)
            # score = calc_score.calculate_score(extra_blocks_accessed_count, len(shortest_path), time_elapsed, level)
            #score = round(score)
            print(f'Block_count: {block_count}')
            print(f'Agent_block_count: {agent_block_count}')
            print(f'Score: {score} ({category})')
            running = False
    
def winning_message(win):
    font = pygame.font.Font(None, 72)
    text = font.render("You Won!!!", True, (0, 255, 0))
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.update()
    pygame.time.wait(3000)  # Display message for 3 seconds

def timeout_message(win):
    font = pygame.font.Font(None, 72)
    text = font.render("Timeout!!!", True, (255, 0, 0))
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.update()
    pygame.time.wait(3000)  # Display message for 3 seconds

if __name__ == "__main__":
    import sys
    difficulty_level = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    main(difficulty_level)

