# Create the ConnectX environment with debugging enabled
env = make("connectx", debug=True)

# Render the environment
env.render()

def cell_swarm(obs, conf):
    def evaluate_cell(cell):
        """Evaluate qualities of the cell."""
        cell = get_patterns(cell)
        cell = calculate_points(cell)
        for i in range(1, conf.rows):
            cell = explore_cell_above(cell, i)
        return cell

    def get_patterns(cell):
        """Get swarm and opponent's patterns of each axis of the cell."""
        ne = get_pattern(cell["x"], lambda z: z + 1, cell["y"], lambda z: z - 1, conf.inarow)
        sw = get_pattern(cell["x"], lambda z: z - 1, cell["y"], lambda z: z + 1, conf.inarow)[::-1]
        cell["swarm_patterns"]["NE_SW"] = sw + [{"mark": swarm_mark}] + ne
        cell["opp_patterns"]["NE_SW"] = sw + [{"mark": opp_mark}] + ne
        e = get_pattern(cell["x"], lambda z: z + 1, cell["y"], lambda z: z, conf.inarow)
        w = get_pattern(cell["x"], lambda z: z - 1, cell["y"], lambda z: z, conf.inarow)[::-1]
        cell["swarm_patterns"]["E_W"] = w + [{"mark": swarm_mark}] + e
        cell["opp_patterns"]["E_W"] = w + [{"mark": opp_mark}] + e
        se = get_pattern(cell["x"], lambda z: z + 1, cell["y"], lambda z: z + 1, conf.inarow)
        nw = get_pattern(cell["x"], lambda z: z - 1, cell["y"], lambda z: z - 1, conf.inarow)[::-1]
        cell["swarm_patterns"]["SE_NW"] = nw + [{"mark": swarm_mark}] + se
        cell["opp_patterns"]["SE_NW"] = nw + [{"mark": opp_mark}] + se
        s = get_pattern(cell["x"], lambda z: z, cell["y"], lambda z: z + 1, conf.inarow)
        n = get_pattern(cell["x"], lambda z: z, cell["y"], lambda z: z - 1, conf.inarow)[::-1]
        cell["swarm_patterns"]["S_N"] = n + [{"mark": swarm_mark}] + s
        cell["opp_patterns"]["S_N"] = n + [{"mark": opp_mark}] + s
        return cell

    def get_pattern(x, x_fun, y, y_fun, cells_remained):
        """Get pattern of marks in direction."""
        pattern = []
        x = x_fun(x)
        y = y_fun(y)
        if y >= 0 and y < conf.rows and x >= 0 and x < conf.columns:
            pattern.append({
                "mark": swarm[x][y]["mark"]
            })
            cells_remained -= 1
            if cells_remained > 1:
                pattern.extend(get_pattern(x, x_fun, y, y_fun, cells_remained))
        return pattern

    def calculate_points(cell):
        """Calculate amounts of swarm's and opponent's correct patterns and add them to cell's points."""
        for i in range(conf.inarow - 2):
            inarow = conf.inarow - i
            swarm_points = 0
            opp_points = 0
            swarm_points = evaluate_pattern(swarm_points, cell["swarm_patterns"]["E_W"], swarm_mark, inarow)
            swarm_points = evaluate_pattern(swarm_points, cell["swarm_patterns"]["NE_SW"], swarm_mark, inarow)
            swarm_points = evaluate_pattern(swarm_points, cell["swarm_patterns"]["SE_NW"], swarm_mark, inarow)
            swarm_points = evaluate_pattern(swarm_points, cell["swarm_patterns"]["S_N"], swarm_mark, inarow)
            opp_points = evaluate_pattern(opp_points, cell["opp_patterns"]["E_W"], opp_mark, inarow)
            opp_points = evaluate_pattern(opp_points, cell["opp_patterns"]["NE_SW"], opp_mark, inarow)
            opp_points = evaluate_pattern(opp_points, cell["opp_patterns"]["SE_NW"], opp_mark, inarow)
            opp_points = evaluate_pattern(opp_points, cell["opp_patterns"]["S_N"], opp_mark, inarow)
            if i > 0:
                if swarm_points > opp_points:
                    cell["points"].append(swarm_points)
                    cell["points"].append(opp_points)
                else:
                    cell["points"].append(opp_points)
                    cell["points"].append(swarm_points)
            else:
                cell["points"].append(swarm_points)
                cell["points"].append(opp_points)
        return cell

    def evaluate_pattern(points, pattern, mark, inarow):
        """Get amount of points if pattern has required amounts of marks and zeros."""
        for i in range(len(pattern) - (conf.inarow - 1)):
            marks = 0
            zeros = 0
            for j in range(conf.inarow):
                if pattern[i + j]["mark"] == mark:
                    marks += 1
                elif pattern[i + j]["mark"] == 0:
                    zeros += 1
            if marks >= inarow and (marks + zeros) == conf.inarow:
                return points + 1
        return points

    def explore_cell_above(cell, i):
        """Add positive or negative points from cell above (if it exists) to points of current cell."""
        if (cell["y"] - i) >= 0:
            cell_above = swarm[cell["x"]][cell["y"] - i]
            cell_above = get_patterns(cell_above)
            cell_above = calculate_points(cell_above)
            n = -1 if i & 1 else 1
            if i == 1:
                cell["points"][2:2] = [n * cell_above["points"][1], n * cell_above["points"][0]]
                if abs(cell["points"][4]) < 2 and abs(cell["points"][4]) < cell_above["points"][2]:
                    cell["points"][4:4] = [n * cell_above["points"][2]]
                    if abs(cell["points"][5]) < 2 and abs(cell["points"][5]) < cell_above["points"][3]:
                        cell["points"][5:5] = [n * cell_above["points"][3]]
                    else:
                        cell["points"][7:7] = [n * cell_above["points"][3]]
                else:
                    cell["points"][6:6] = [n * cell_above["points"][2], n * cell_above["points"][3]]
            else:
                cell["points"].extend(map(lambda z: z * n, cell_above["points"]))
        else:
            cell["points"].extend([0, 0, 0, 0])
        return cell

    def choose_best_cell(best_cell, current_cell):
        """Compare two cells and return the best one."""
        if best_cell is not None:
            for i in range(len(best_cell["points"])):
                if best_cell["points"][i] < current_cell["points"][i]:
                    best_cell = current_cell
                    break
                if best_cell["points"][i] > current_cell["points"][i]:
                    break
                if best_cell["points"][i] > 0:
                    if best_cell["distance_to_center"] > current_cell["distance_to_center"]:
                        best_cell = current_cell
                        break
                    if best_cell["distance_to_center"] < current_cell["distance_to_center"]:
                        break
        else:
            best_cell = current_cell
        return best_cell

    swarm_mark = obs.mark
    opp_mark = 2 if swarm_mark == 1 else 1
    swarm_center_horizontal = conf.columns // 2
    swarm_center_vertical = conf.rows // 2
    swarm = [[{
        "x": column,
        "y": row,
        "mark": obs.board[conf.columns * row + column],
        "swarm_patterns": {},
        "opp_patterns": {},
        "distance_to_center": abs(row - swarm_center_vertical) + abs(column - swarm_center_horizontal),
        "points": []
    } for row in range(conf.rows)] for column in range(conf.columns)]

    best_cell = None
    x = swarm_center_horizontal
    shift = 0

    while x >= 0 and x < conf.columns:
        y = conf.rows - 1
        while y >= 0 and swarm[x][y]["mark"] != 0:
            y -= 1
        if y >= 0:
            current_cell = evaluate_cell(swarm[x][y])
            best_cell = choose_best_cell(best_cell, current_cell)
        if shift >= 0:
            shift += 1
        shift *= -1
        x = swarm_center_horizontal + shift

    return best_cell["x"]
env.reset()
env.run([cell_swarm, cell_swarm])
env.render(mode="ipython", width=500, height=450)

trainer = env.train([None, "negamax"])
observation = trainer.reset()

while not env.done:
    my_action = cell_swarm(observation, env.configuration)
    observation, reward, done, info = trainer.step(my_action)

env.render()

def mean_reward(rewards):
    return "{0} episodes: won {1}, lost {2}, draw {3}".format(
        len(rewards),
        sum(1 if r[0] > 0 else 0 for r in rewards),
        sum(1 if r[1] > 0 else 0 for r in rewards),
        sum(r[0] == r[1] for r in rewards)
    )
env.play([cell_swarm, None], width=500, height=450)

import os
import inspect

def write_agent_to_file(function, file):
    with open(file, "a" if os.path.exists(file) else "w") as f:
        f.write(inspect.getsource(function))
        print(function, "written to", file)

write_agent_to_file(cell_swarm, "submission.py")


out = sys.stdout
submission = utils.read_file("/kaggle/working/submission.py")
agent = utils.get_last_callable(submission)
sys.stdout = out
env = make("connectx", debug=True)
env.run([agent, agent])