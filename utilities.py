#!/usr/bin/env python3
#
#   hw5_utilities.py
#
#   Two classes to help the visualization and simulation.
#
#
#   VISUALIZATION:
#
#     visual = Visualization(walls)
#     visual.Show(prob)
#     visual.Show(prob, (row, col))
#
#     walls         NumPy 2D array defining both the grid size
#                   (rows/cols) and walls (being non-zero elements).
#     prob          NumPy 2D array of probabilities, values 0 to 1.
#
#   visual.Show() will visualize the probabilities.  The second form
#   will also mark the (row,col) position with an 'x'.
#
#
#   ROBOT SIMULATION:
#
#     robot = Robot(walls, row=0, col=0, probCmd=1.0, probProximal=[1.0])
#     robot.Command(drow, dcol)
#     True/False = robot.Sensor(drow, dcol)
#     (row, col) = robot.Position()
#
#     probCmd       Probability the command is executed (0 to 1).
#     probProximal  List of probabilities (0 to 1).  Each element is
#                   the probability that the proximity sensor will
#                   fire at a distance of (index+1 = 1,2,3,etc)
#     (drow, dcol)  Delta up/right/down/left: (-1,0) (0,1) (1,0) (0,-1)
#
#   Simulate a robot, to give us the sensor readings.  If the starting
#   row/col are not given, pick them randomly.  Note both the command
#   and the sensor may be configured to a random probability level.
#   The robot.Position() is intended for debugging and visualization
#   only, as it gives the actual position.
#
import matplotlib.pyplot as plt
import numpy as np
import random
from matplotlib import colors


#
#   Probailiity Grid Visualization
#
class Visualization():
    def __init__(self, walls, w):
        # Save the walls and determine the rows/cols:
        self.w = w
        self.walls = walls
        self.spots = np.sum(np.logical_not(walls))
        self.rows  = np.size(walls, axis=0)
        self.cols  = np.size(walls, axis=1)

        #Determine randomized rotation of sensors
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] #Up, down, left, right 
        self.permutations = [[0, 1, 2, 3], [3, 2, 0, 1], [1, 0, 3, 2], [2, 3, 1, 0]]
        self.orientation = random.randint(0, 3)


        # Clear the current, or create a new figure.
        plt.clf()

        # Create a new axes, enable the grid, and set axis limits.
        
        plt.axes()
        plt.grid(False)
        plt.gca().axis('off')
        plt.gca().set_aspect('equal')
        plt.gca().set_xlim(0, self.cols)
        plt.gca().set_ylim(self.rows, 0)

        self.colors = colors.ListedColormap(['#EDC9AF', 'k', 'g', 'r'])
        self.ocmap = walls.copy()
        self.cmap = walls.copy()
        self.bound_norm = colors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], self.colors.N)
        self.content = plt.gca().imshow(self.cmap, cmap = self.colors, norm = self.bound_norm,
                                        aspect='equal',
                                        interpolation='none',
                                        extent=[0, self.cols, self.rows, 0],
                                        zorder=0)

        # Add the row/col numbers.
        for row in range(0, self.rows, 2):
            plt.gca().text(         -0.3, 0.5+row, '%d'%row,
                           verticalalignment='center',
                           horizontalalignment='right')
        for row in range(1, self.rows, 2):
            plt.gca().text(self.cols+0.3, 0.5+row, '%d'%row,
                           verticalalignment='center',
                           horizontalalignment='left')
        for col in range(0, self.cols, 2):
            plt.gca().text(0.5+col,          -0.3, '%d'%col,
                           verticalalignment='bottom',
                           horizontalalignment='center')
        for col in range(1, self.cols, 2):
            plt.gca().text(0.5+col, self.rows+0.3, '%d'%col,
                           verticalalignment='top',
                           horizontalalignment='center')

        # Draw the grid, zorder 1 means draw after zorder 0 elements.
        for row in range(self.rows+1):
            plt.gca().axhline(row, lw=1, color='k', zorder=1)
            #plt.axvspan(row, row + 1, facecolor = 'r')
        for col in range(self.cols+1):
            plt.gca().axvline(col, lw=1, color='k', zorder=1)
            #plt.axhspan(col, col + 1, facecolor = 'r')

        # Clear the content and mark.  Then show with zeros.
        self.mark    = None
        self.Show()

    def Flush(self):
        # Show the plot.
        plt.pause(0.001)

    def Mark(self, row, col):
        # Check the row/col arguments.
        assert (row >= 0) and (row < self.rows), "Illegal row"
        assert (col >= 0) and (col < self.cols), "Illegal col"

        # Potentially remove the previous mark.
        if self.mark is not None:
            self.mark.remove()
            self.mark = None

        # Draw the mark.
        self.mark  = plt.gca().text(0.5+col, 0.5+row, 'x', color = 'green',
                                    verticalalignment='center',
                                    horizontalalignment='center',
                                    zorder=1)

    def Show(self, pos = None, sensor_vals = None):
        # Update the content.
        # Potentially add the mark
        if pos is not None:
            self.Mark(pos[0], pos[1])

        if sensor_vals is not None:
            self.content.remove()
            self.content = None
            self.cmap = np.array([[1.0*(c == 'x') for c in s] for s in self.w])
            for i, (ud, lr) in enumerate(self.directions):
                self.cmap[pos[0] + ud][pos[1] + lr] = sensor_vals[self.permutations[self.orientation][i]]
            self.content = plt.gca().imshow(self.cmap, cmap = self.colors, norm = self.bound_norm,
                                            aspect='equal',
                                        interpolation='none',
                                        extent=[0, self.cols, self.rows, 0],
                                        zorder=0)
        # Flush the figure.
        self.Flush()


#
#  Robot (Emulate the actual robot)
#
#    probCmd is the probability that the command is actually executed
#
#    probProximal is a list of probabilities.  Each element
#    corresponds to the probability that the proximity sensor will
#    fire at a distance of (index+1).
#
class Robot():
    def __init__(self, walls, row = 0, col = 0):
        # Check the row/col arguments.
        assert (row >= 0) and (row < np.size(walls, axis=0)), "Illegal row"
        assert (col >= 0) and (col < np.size(walls, axis=1)), "Illegal col"

        # Report.
        if walls[row, col]:
            location = "(random location)"
        else:
            location = "(at %d, %d)" % (row, col)
        #print(f"Starting robot at {location}")

        # Save the walls, the initial location, and the probabilities.
        self.walls        = walls
        self.row          = row
        self.col          = col

        # Pick a valid starting location (if not already given).
        while self.walls[self.row, self.col]:
            self.row = random.randrange(0, np.size(walls, axis=0))
            self.col = random.randrange(0, np.size(walls, axis=1))
        self.crashed = False

    def Command(self, drow, dcol):
        # Check the delta.
        assert ((abs(drow+dcol) == 1) and (abs(drow-dcol) == 1)), "Bad delta"
        
        # Try to move the robot the given delta.
        row = self.row + drow
        col = self.col + dcol
        if (not self.walls[row, col]):
            self.row = row
            self.col = col
        else:
            self.crashed = True

    def Position(self):
        return (self.col, self.row)

    def Sense(self):
        neighbors = [(self.row - 1, self.col), (self.row + 1, self.col),
                     (self.row, self.col - 1), (self.row, self.col + 1)]
        sensor_names = ["Up", "Down", "Left", "Right"]
        sensor_vals = []
        for i, (row, col) in enumerate(neighbors):
            if self.walls[row][col]:
                #print(f"{sensor_names[i]} Sensor detects a wall")
                sensor_vals.append(3)
            else:
                #print(f"{sensor_names[i]} Sensor detects no wall")
                sensor_vals.append(2)
 
        return sensor_vals
    
    def Rotate(self, visual, val):
        for _ in range(val):
            if visual.orientation == 3:
                visual.orientation = 0
            else:
                visual.orientation += 1

        return visual
    
def generate_soln():
    return (12, 16)

def generate_wall_map(rows, cols, wall_perc):
    blank_map = [[" " for _ in range(cols)] for _ in range(rows)]
    final_map = []
    endpts = []

    #All boarders are walls, generate random wall endpoints
    for i in range(rows):
        for j in range(cols):
            if i == 0 or i == rows - 1 or j == 0 or j == cols - 1:
                blank_map[i][j] = 'x'
            else:
                rand_int = np.random.randint(0, 100)
                if rand_int < wall_perc:
                    blank_map[i][j] = 'x'
                    endpts.append((i, j))

    endpt_pairs = []
    finished_pts = []
    finished = False
    start_index = 3


    # Map each endpt to the (start_index)th closest point
    while len(finished_pts) < len(endpts) - len(endpts) % 2:
        for endpt in endpts:
            point_used = False
            if len(finished_pts) != 0:
                for pt in finished_pts:
                    if pt[0] == endpt[0] and pt[1] == endpt[1]:
                        point_used = True
            if point_used:
                continue

            def sorting_function(pt):
                dx = endpt[0] - pt[0]
                dy = endpt[1] - pt[1]
                return np.sqrt(dx ** 2 + dy ** 2)
            
            pts = endpts.copy()
            closest_pt_list = sorted(pts, key = sorting_function)
            
            index = start_index
            while True:
                try:
                    closest_pt = closest_pt_list[index]
                    point_used = False
                    for pt in finished_pts:
                        if pt[0] == closest_pt[0] and pt[1] == closest_pt[1]:
                            point_used = True
                    if not point_used:
                        endpt_pairs.append([endpt, closest_pt])
                        finished_pts.append(endpt)
                        finished_pts.append(closest_pt)
                        break
                    else:
                        index += 1
                except IndexError:
                    finished = True
                    break
        if finished:
            break

    connecting_pts_dict = {i : [] for i in range(len(endpt_pairs))}

    # Connect the pairs of endpoints
    for (i, pair) in enumerate(endpt_pairs):
        start = pair[0]
        end = pair[1]

        cur = start
        while True:
            dx = end[0] - cur[0]
            dy = end[1] - cur[1]
            if dx == 0 and dy == 0:
                break
            new_x = cur[0] + np.random.randint(0, 2) * np.sign(dx)
            new_y = cur[1] + np.random.randint(0, 2) * np.sign(dy)
            blank_map[new_x][new_y] = "x"
            cur = (new_x, new_y)
            connecting_pts_dict[i].append(cur)
            

    def find_k_neighbors(k):
        neighbor_points = []
        for i in range(rows):
            for j in range(cols):
                if i == 0 or i == rows - 1 or j == 0 or j == cols - 1:
                    continue
                elif blank_map[i][j] != 'x':
                    x_neighbors = 0
                    for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if blank_map[i + dx][j + dy] == "x":
                            x_neighbors += 1
                    if x_neighbors >= k:
                        neighbor_points.append((i, j))
        
        for pair in neighbor_points:
            blank_map[pair[0]][pair[1]] = 'x'

    find_k_neighbors(3)
    find_k_neighbors(4)

    for row_list in blank_map:
        row_items = ""
        for elem in row_list:
            row_items += elem
        final_map.append(row_items)

    return final_map

def guess_location(visual):
    while True:
        guess_x = input("Guess x-coordinate: ")
        guess_y = input("Guess y-coordinate: ")

        try:
            x_coord, y_coord = int(guess_x), int(guess_y)
            if y_coord < 0 or y_coord > visual.rows - 1:
                print("Y-Coordinate is out of bounds!")
                continue
            if x_coord < 0 or x_coord > visual.cols - 1:
                print("X-Coordinate is out of bounds!")
                continue

        except ValueError:
            print("Both inputs must be integers.")
            continue
        break

    return x_coord, y_coord

def generate_random_start(visual, actual_x, actual_y):
    while True:
        xs = np.random.randint(2, visual.cols - 3)
        ys = np.random.randint(2, visual.rows - 3)

        if not visual.walls[ys][xs]:
            if xs != actual_x and ys != actual_y:
                print(f"First guess: ({ys}, {xs})")
                return (ys, xs)
        
        