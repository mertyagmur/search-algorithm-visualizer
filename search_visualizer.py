import pygame
import time
import math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)

pygame.init()

# Set up the game window
window_width, window_height = 900, 800
window = pygame.display.set_mode((window_width, window_height))

# Define box properties
box_size = 30
num_boxes = window_width // box_size

START = "start"
TARGET = "target"
OBSTACLE = "obstacle"
PATH = "path"
TRAVELED = "traveled"

class Box:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.type = None
        self.parent = None
        self.g_cost = 0
        self.h_cost = 0

    def draw(self):
        x = self.col * box_size
        y = self.row * box_size

        if self.type == START:
            color = GREEN
        elif self.type == TARGET:
            color = RED
        elif self.type == OBSTACLE:
            color = GRAY
        elif self.type == PATH:
            color = BLUE
        elif self.type == TRAVELED:
            color = LIGHT_BLUE
        else:
            color = WHITE

        pygame.draw.rect(window, color, (x, y, box_size, box_size))
        pygame.draw.rect(window, BLACK, (x, y, box_size, box_size), 1)  # Add box borders

    def calculate_g_cost(self, start_box):
        """
        Calculates real cost with Euclidean Distance.
        Time Complexity: O(n)
        Space Complexity: O(1)
        """
        return math.sqrt((self.row - start_box.row) ** 2 + (self.col - start_box.col) ** 2)

    def calculate_h_cost(self, target_box):
        """
        Calculates heuristic cost with Manhattan Distance.
        Time Complexity: O(n)
        Space Complexity: O(1)
        """
        return abs(self.row - target_box.row) + abs(self.col - target_box.col)

    def calculate_f_cost(self):
        """
        Calculates total cost.
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        return self.g_cost + self.h_cost

    def update_costs(self, start_box, target_box):
        """
        Updates the cost attributes of a box.
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.g_cost = self.calculate_g_cost(start_box)
        self.h_cost = self.calculate_h_cost(target_box)

# Create grid of boxes
boxes = [[Box(row, col) for col in range(num_boxes)] for row in range(num_boxes)]

# Initialize start position as None
start_box = None
target_box = None

# Breadth-first search algorithm
def breadth_first_search():
    queue = [start_box]
    visited = set([start_box])
    target_reached = False
    operations = 0

    while queue:
        operations += 1
        box = queue.pop(0)

        if box == target_box:
            # Found the target box, construct the path
            path = []
            while box != start_box:
                path.append(box)
                box = box.parent
            path.append(start_box)
            path.reverse()

            # Mark the boxes on the path as PATH type
            for path_box in path:
                path_box.type = PATH

            target_reached = True
            break

        neighbors = get_valid_neighbors(box.row, box.col)
        for neighbor_row, neighbor_col in neighbors:
            neighbor_box = boxes[neighbor_row][neighbor_col]
            if neighbor_box not in visited:
                queue.append(neighbor_box)
                visited.add(neighbor_box)
                neighbor_box.parent = box
                neighbor_box.type = TRAVELED

        # Update the window after each traversal
        window.fill(WHITE)
        for row in boxes:
            for box in row:
                box.draw()
        pygame.display.flip()

        # Add a small delay to visualize the traversal steps
        pygame.time.wait(10)

    if not target_reached:
        return False

    print("Breadth-first search:")
    print("Number of operations:", operations)

    return True

# A* search algorithm
def astar_search():
    queue = [start_box]
    visited = set()
    target_reached = False
    operations = 0

    while queue:
        operations += 1
        current_box = min(queue, key=lambda box: box.calculate_f_cost())

        if current_box == target_box:
            # Found the target box, construct the path
            path = []
            while current_box != start_box:
                path.append(current_box)
                current_box = current_box.parent
            path.append(start_box)
            path.reverse()

            # Mark the boxes on the path as PATH type
            for path_box in path:
                path_box.type = PATH

            target_reached = True
            break

        queue.remove(current_box)
        visited.add(current_box)

        neighbors = get_valid_neighbors(current_box.row, current_box.col)
        for neighbor_row, neighbor_col in neighbors:
            neighbor_box = boxes[neighbor_row][neighbor_col]
            if neighbor_box in visited:
                continue

            tentative_g_cost = current_box.g_cost + neighbor_box.calculate_g_cost(current_box)

            if neighbor_box not in queue:
                queue.append(neighbor_box)
            elif tentative_g_cost >= neighbor_box.g_cost:
                continue

            neighbor_box.parent = current_box
            neighbor_box.g_cost = tentative_g_cost
            neighbor_box.h_cost = neighbor_box.calculate_h_cost(target_box)

        # Update the window after each traversal
        window.fill(WHITE)
        for row in boxes:
            for box in row:
                box.draw()
        pygame.display.flip()

        # Add a small delay to visualize the traversal steps
        pygame.time.wait(10)

        # Mark the current box as traversed
        current_box.type = TRAVELED

    if not target_reached:
        return False

    print("A* search:")
    print("Number of operations:", operations)

    return True


# Helper function to get valid neighbors
def get_valid_neighbors(row, col):
    neighbors = []
    # Check the neighbor boxes in the vertical and horizontal directions
    if row > 0 and boxes[row-1][col].type != OBSTACLE:  # Up
        neighbors.append((row-1, col))
    if row < num_boxes-1 and boxes[row+1][col].type != OBSTACLE:  # Down
        neighbors.append((row+1, col))
    if col > 0 and boxes[row][col-1].type != OBSTACLE:  # Left
        neighbors.append((row, col-1))
    if col < num_boxes-1 and boxes[row][col+1].type != OBSTACLE:  # Right
        neighbors.append((row, col+1))
    return neighbors

# Game loop
running = True
dragging = False
algorithm = None  # Selected algorithm

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:  # Left click
                pos = pygame.mouse.get_pos()
                col = pos[0] // box_size
                row = pos[1] // box_size

                if start_box is None:
                    start_box = boxes[row][col]
                    start_box.type = START
                elif start_box.type == START:
                    dragging = True
                    boxes[row][col].type = OBSTACLE

            elif pygame.mouse.get_pressed()[2]:  # Right click
                if target_box is None:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // box_size
                    row = pos[1] // box_size

                    if start_box is not None and start_box.type == START:
                        target_box = boxes[row][col]
                        target_box.type = TARGET

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                pos = pygame.mouse.get_pos()
                col = pos[0] // box_size
                row = pos[1] // box_size

                if start_box is not None and start_box.type == START:
                    boxes[row][col].type = OBSTACLE

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:  # 'b' key for selecting Breadth-first Search
                algorithm = "BFS"
            elif event.key == pygame.K_a:  # 'a' key for selecting A* Search
                algorithm = "A*"
            elif event.key == pygame.K_r:  # 'r' key for resetting the game
                start_box = None
                target_box = None
                algorithm = None
                for row in boxes:
                    for box in row:
                        box.type = None

            elif event.key == pygame.K_RETURN:  # 'Enter' key to start the selected algorithm
                if algorithm == "BFS" and start_box is not None and target_box is not None:
                    breadth_first_search()
                elif algorithm == "A*" and start_box is not None and target_box is not None:
                    for row in boxes:
                        for box in row:
                            box.update_costs(start_box, target_box)
                    astar_search()

    # Update the window
    window.fill(WHITE)
    for row in boxes:
        for box in row:
            box.draw()
    pygame.display.flip()

# Quit the game
pygame.quit()
