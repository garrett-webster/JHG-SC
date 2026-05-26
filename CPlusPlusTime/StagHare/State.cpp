//
// Created by Sean Smith on 5/26/2026.
//

#include "State.h"
#include <algorithm>  // put this at the top of your .cpp file


namespace jhg {

// --- Constructor ---
State::State(int height, int width, const std::vector<std::string>& agent_names)
    : m_height(height)
    , m_width(width)
    , m_round_num(0)
    , m_grid(height, std::vector<int>(width, AVAILABLE))
    , m_agent_names(agent_names)
{
    // Random starting positions go here
}

// --- Position / movement queries ---
std::unordered_map<std::string, std::vector<Position>>
State::available_actions() const {
    // TODO
    std::unordered_map<std::string, std::vector<Position>> possible_actions_map;

    for (const auto& [agent_name, curr_pos] : m_agent_positions) {
        // agent name is a const std::string&
        // curr pos is a const Position&
        // used exaclty how you think they should be used
        int curr_row = curr_pos.row;
        int curr_col = curr_pos.col;

        int new_row;
        int new_col;

        for (auto movement : POSSIBLE_MOVEMENTS) {
            for (auto delta : POSSIBLE_DELTA_VALS) {
                if (movement == VERTICAL) {
                    new_row = curr_row + delta;
                    new_col = curr_col;
                }
                else {
                    new_row = curr_row;
                    new_col = curr_col + delta;
                }

                auto [row, col] = adjust_vals(new_row, new_col);
                std::vector<Position>& possible_positions = possible_actions_map[agent_name];

                if (std::find(possible_positions.begin(), possible_positions.end(),
                    Position(new_row, new_col)) == possible_positions.end()) {
                    possible_positions.emplace_back(new_row, new_col);
               }

                possible_actions_map[agent_name] = possible_positions;
            }
        }
        return possible_actions_map;
    }

    return {};
}

std::vector<Position>
State::neighboring_positions(int curr_row, int curr_col,
                              bool filter_availability) const {
    // TODO
    auto positions = std::vector<Position>();

    int new_row;
    int new_col;

    for (auto movement : POSSIBLE_MOVEMENTS) {
        for (auto delta : POSSIBLE_DELTA_VALS) {
            if (movement == VERTICAL) {
                new_row = curr_row + delta;
                new_col = curr_col;
            }
            else {
                new_row = curr_row;
                new_col = curr_col + delta;
            }

            if (not filter_availability || is_available(new_row, new_col)) {
                auto [row, col] = adjust_vals(new_row, new_col);
                positions.emplace_back(row, col);
            }
        }
    }
    return positions;
}

bool State::is_available(int row, int col) const {
    auto [adj_row, adj_col] = adjust_vals(row, col);
    return m_grid[adj_row][adj_col] == AVAILABLE;
}

int State::n_movements(int curr_row, int curr_col,
                       int new_row, int new_col) const {
    // TODO
    return 0;
}

bool State::neighbors(int row1, int col1, int row2, int col2) const {
    // TODO
    return false;
}

// --- Game state ---
void State::update_intent(const std::unordered_map<std::string, bool>& hunting_hare_map) {
    // TODO
}

std::vector<double>
State::process_actions(const std::unordered_map<std::string, Position>& action_map) {
    // TODO
    return {};
}

bool State::hare_captured() const {
    // TODO
    return false;
}

bool State::stag_captured() const {
    // TODO
    return false;
}

std::vector<double>
State::vector_representation(const std::string& hunter_name) const {
    // TODO
    return {};
}

std::vector<std::vector<int>> State::return_as_array() const {
    // TODO
    return {};
}

void State::reset_positions() {
    // TODO
}

// --- Internal helpers ---
Position State::adjust_vals(int row, int col) const {
    int row_val = row;
    int col_val = col;

    if (row_val < 0) {
        row = m_height - 1;
    }

    else if (row_val >= m_height) {
        row = 0;
    }

    if (col_val < 0) {
        col = m_width - 1;
    }
    else if (col_val >= m_width) {
        col = 0;
    }

    return {row, col};
}

bool State::hunter_ready_to_kill(int row_val, int col_val, bool hare) const {
    // TODO
    auto [row, col] = adjust_vals(row_val, col_val);
    auto [hare_row, hare_col] = m_agent_positions[HARE_NAME];
    auto [stag_row, stag_col] = m_agent_positions[STAG_NAME];

    

    return false;
}

int State::delta_row(int curr_row, int new_row) const {
    // TODO
    int move_down = (m_height - curr_row) + new_row;
    int move_up = curr_row + (m_height - new_row);
    int move_regular = std::abs(curr_row - move_down);

    return std::min({move_regular, move_up, move_regular});
}

int State::delta_col(int curr_col, int new_col) const {
    // TODO
    int move_left = (m_width - curr_col) + new_col;
    int move_right = curr_col + (m_width - new_col);
    int move_regular = std::abs(curr_col - move_left);
    return std::min({move_left, move_right, move_regular});
}

} // namespace jhg