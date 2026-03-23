from stagHare.agents.agent import Agent
from stagHare.environment.state import State
import numpy as np
from typing import Tuple
from stagHare.utils.utils import HARE_NAME, POSSIBLE_DELTA_VALS, STAG_NAME
from stagHare.utils.a_star import AStar # this SHOULD do the trick.
from stagHare.utils.a_star import BFS # This SHOULD be faster. maybe.
# I have no idea if this will actually work the way that I want it to.

def findPathGreedy(state: State, p_curr_row, p_curr_col, goal_row, goal_col) -> Tuple[int, int]:
    prey_row, prey_col = goal_row, goal_col
    curr_row, curr_col = p_curr_row, p_curr_col

    if state.neighbors(prey_row, prey_col, curr_row, curr_col):
        return prey_row, prey_col

    prey_neighboring_positions, min_dist, goal = state.neighboring_positions(prey_row, prey_col), np.inf, None

    for row, col in prey_neighboring_positions:
        dist = state.n_movements(curr_row, curr_col, row, col)

        if dist < min_dist:
            goal, min_dist = (row, col), dist

    if goal is not None:
        row, col = goal
        d_row, d_col = state.delta_row(curr_row, row) % state.height, state.delta_col(curr_col, col) % state.width
        next_row, next_col = None, None

        if d_row > d_col:
            min_dist = np.inf

            for delta in POSSIBLE_DELTA_VALS:
                new_row, new_col = curr_row + delta, curr_col

                if state.is_available(new_row, new_col):
                    new_row, new_col = state.adjust_vals(new_row, new_col)
                    dist = state.n_movements(new_row, new_col, row, col)

                    if dist < min_dist:
                        next_row, next_col, min_dist = new_row, new_col, dist

        elif next_row is None or next_col is None:
            min_dist = np.inf

            for delta in POSSIBLE_DELTA_VALS:
                new_row, new_col = curr_row, curr_col + delta

                if state.is_available(new_row, new_col):
                    new_row, new_col = state.adjust_vals(new_row, new_col)
                    dist = state.n_movements(new_row, new_col, row, col)

                    if dist < min_dist:
                        next_row, next_col, min_dist = new_row, new_col, dist

        if next_row is not None and next_col is not None:
            return next_row, next_col

    return curr_row, curr_col # don't move at all. hope this works.


def findPathTeamAware(name, state, curr_row, curr_col, stag_row, stag_col) -> Tuple[int, int]:
    # if this bricks, it might be becuase we need the goal row and col to be idfferent than the stag row and col. room for thoughtg.
    stag_neighboring_positions = state.neighboring_positions(stag_row, stag_col)

    # If we are already neighbors with the stag, try to move to its current position in case it moves
    if state.neighbors(stag_row, stag_col, curr_row, curr_col):
        return stag_row, stag_col

    # Calculate the distance from each hunter to each available cell neighboring the stag
    neighbor_distances, name_ordering = {}, []

    for agent_name, curr_pos in state.agent_positions.items():
        # Ignore the prey
        if agent_name == STAG_NAME or agent_name == HARE_NAME:
            continue

        row, col = curr_pos

        # The hunter is already a neighbor of the stag
        if state.neighbors(stag_row, stag_col, row, col):
            continue

        distances = []

        for new_row, new_col in stag_neighboring_positions:
            dist = state.n_movements(row, col, new_row, new_col)
            distances.append((new_row, new_col, dist))

        # Sort by distance
        distances.sort(key=lambda x: x[-1])
        neighbor_distances[agent_name] = distances

        # Keep track of the worst shortest distance
        name_ordering.append((agent_name, distances[-1][-1]))

    # Order by the worst shortest distance
    name_ordering.sort(key=lambda x: x[-1])
    assigned, goal = set(), None

    # Make assignments - assign the goal when we reach ourselves so that we can plan a path
    for agent_name, _ in name_ordering:
        for row, col, _ in neighbor_distances[agent_name]:
            if (row, col) not in assigned:
                assigned.add((row, col))

                if agent_name == name: # well this sucks.
                    goal = (row, col)
                    break # inner break. this might help.

                break

    # If we can't move, stay at the current position
    if goal is None:
        return curr_row, curr_col

    goal_row, goal_col = goal

    # BFS is slightly faster but for consistency? we can still use A*. THere was a slight bug causing slowdowns on duplicate nodes.
    # BFS is WAAY faster on the 16x16 grid, so we are no longer using A*. might need to retrain the genetic model.
    return BFS.find_path(curr_row, curr_col, goal_row, goal_col, state)
    # return AStar.find_path(curr_row, curr_col, goal_row, goal_col, state)