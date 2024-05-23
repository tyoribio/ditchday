import numpy as np
import utilities

# Define constants
ROWS = 25
COLS = 49
WALL_PERC = 3
MAX_MOVES = 25
MAX_GUESSES = 3

def move_player(robot):
    # Get the command key to determine the direction.
    while True:
        key = input("Move one step up, down, left, or right: ")
        if   (key == 'q'):  return
        elif (key == 'w'):  (drow, dcol) = (-1,  0) ; break
        elif (key == 's'):  (drow, dcol) = ( 1,  0) ; break
        elif (key == 'a'):  (drow, dcol) = ( 0, -1) ; break
        elif (key == 'd'):  (drow, dcol) = ( 0,  1) ; break
        else: print("Invalid direction.")

    # Move the robot in the simulation.
    robot.Command(drow, dcol)

    return drow, dcol

def make_current_guess(visual, robot, sensor_readings, xs, ys):
    while True:
        curr_loc_guess = input("Change current guess location? (y/n) ")
        if curr_loc_guess == 'y':
            x_coord, y_coord = utilities.guess_location(visual)
            wall_check = robot.walls[y_coord][x_coord]
            if wall_check:
                print("You found a worm!")
                return xs, ys
            else:
                visual.Show((y_coord, x_coord), sensor_vals = sensor_readings)
            return x_coord, y_coord
        elif curr_loc_guess == 'n':
            return xs, ys
        else:
            print("Invalid option.")

def rotate_sensor(visual, robot, sensor_readings, xs, ys):
    while True:
        change_rotation = input("Rotate sensor? (y/n) ")
        finished_rotating = False
        if change_rotation == 'y':
            while True:
                num_rotations = input("How many counterclock 90-deg rotations? (1, 2 or 3) ")
                if int(num_rotations) in [1, 2, 3]:
                    visual = robot.Rotate(visual, int(num_rotations))
                    visual.Show((ys, xs), sensor_vals = sensor_readings)
                    finished_rotating = True
                    break
        elif change_rotation == 'n':
            break
        else:
            print("Invalid option.")

        if finished_rotating:
            break

def guess_starting_loc(visual, correct_x, correct_y, attempts):
    game_over = False
    delta = 0
    while True:
        start_location_guess = input("Guess starting location? (y/n) ")
        if start_location_guess == 'y':
            x_start, y_start = utilities.guess_location(visual)
            if x_start == correct_x and y_start == correct_y:
                print("Victory!")
                game_over = True
            else:
                print(f"Incorrect. Attempts remaining: {3 - (attempts + 1)}")
                if attempts + 1 == MAX_GUESSES:
                    game_over = True
                    print("Ornithopter crashed. Too many incorrect guesses. Dunes shifting.")
                delta += 1
            return game_over, delta
        elif start_location_guess == 'n':
            return game_over, delta
        else:
            print("Invalid option.")

def remove_close_walls(w, x, y):
    removed_w = [[char for char in w[i]] for i in range(len(w))]
    removed_w_final = []
    close_pts = [-2, -1, 0, 1, 2]
    for dx in close_pts:
        for dy in close_pts:
            new_x = x + dx
            new_y = y + dy
            if new_x > 1 and new_x < COLS - 2:
                if new_y > 1 and new_y < ROWS - 2:
                    removed_w[new_y][new_x] = " "

    for row_list in removed_w:
        row_items = ""
        for elem in row_list:
            row_items += elem
        removed_w_final.append(row_items)

    return removed_w_final

def main():
    # Determines when to stop code (player wins)
    victory = False

    # Create wall map and visuals
    w = utilities.generate_wall_map(ROWS, COLS, WALL_PERC)
    walls = np.array([[1.0*(c == 'x') for c in s] for s in w])
    
    # Initialize player and solution
    solution = utilities.generate_soln()
    robot = utilities.Robot(walls, row = solution[0], col = solution[1])
    correct_x, correct_y = robot.Position()

    # Reinitialize wall map to account for player's acutal position
    removed_w = remove_close_walls(w, correct_x, correct_y)
    new_walls = np.array([[1.0*(c == 'x') for c in s] for s in removed_w])
    visual = utilities.Visualization(new_walls, removed_w)
    
    # Intialize number of starting location guesses made and number of moves
    attempts = 0
    loops = 0

    # Set random starting guess
    ys, xs = utilities.generate_random_start(visual, correct_x, correct_y)
    visual.Show((ys, xs), sensor_vals = robot.Sense())

    while True:
        # Move player
        drow, dcol = move_player(robot)

        # Check if player got caught by sand worm
        if robot.crashed:
            print("Game over. Dunes shifting.")
            return
        
        #Sense and show
        sensor_readings = robot.Sense()
        
        # Check if guessed position is on the map
        if ys + drow < 0 or ys + drow > visual.rows:
            print("Sensors malfunctioned. Ornithopter crashed. Dunes shifting.")
            return
        
        if xs + dcol < 0 or xs + dcol > visual.cols:
            print("Sensors malfunctioned. Ornithopter crashed. Dunes shifting.")
            return
        
        # Show current guessed position and update
        visual.Show(pos = (ys + drow, xs + dcol), sensor_vals = sensor_readings)
        ys += drow
        xs += dcol

        while True:
            make_changes = input("Do you want to make changes/guesses? (y/n) ")
            if make_changes == "y":
                # Change guessed location if prompted
                xs, ys = make_current_guess(visual, robot, sensor_readings, xs, ys)

                # Rotate sensor if prompted
                rotate_sensor(visual, robot, sensor_readings, xs, ys)

                # Guess start location if prompted
                game_over, delta = guess_starting_loc(visual, correct_x, correct_y, attempts)
                attempts += delta

                break

            elif make_changes == "n":
                game_over = False
                break
            else:
                print("Invalid option.")

        if game_over:
            break  

        loops += 1
        if loops == MAX_MOVES:
            print("Ornithopter crashed. Too many moves. Dunes shifting.") 
            break
        else:
            print(f"Moves remaining: {MAX_MOVES - loops}")

    return victory


if __name__== "__main__":
    num_games = 1
    while True:
        outcome = main()
        if outcome:
            print(f"Won in {num_games} games.")
            break
        else:
            num_games += 1