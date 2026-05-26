//
// Created by Sean Smith on 5/26/2026.
//


#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include "types.h"
#include "utils.h"

namespace jhg {
    class State {
        public:
        State(int height, int width, const std::vector<std::string>& agent_names);

        // position and movement queries
        std::unordered_map<std::string, std::vector<Position>> available_actions() const;
        std::vector<Position> neighboring_positions(int curr_row, int curr_col, bool filter_availability = true) const;
        bool is_available(int row, int col) const;
        int n_movements(int curr_row, int curr_col, int new_row, int new_col) const;
        bool neighbors(int row1, int col1, int row2, int col2) const;

        // game state stuff
        void update_intent(const std::unordered_map<std::string, bool>& hunting_hare_map);
        std::vector<double> process_actions(const std::unordered_map<std::string, Position>& action_map);

        bool hare_captured() const;
        bool stag_captured() const;

        std::vector<double> vector_representation(const std::string& hunter_name) const;
        std::vector<std::vector<int>> return_as_array() const; // or a flat vector, non flat will be easier for me to think about.

        void reset_positions();

        // some simple getters
        int round_num() const {return m_round_num;}
        int height() const {return m_height;}
        int width() const {return m_width;}

        private:
        int m_height;
        int m_width;
        int m_round_num;

        std::vector<std::vector<int>> m_grid;
        std::unordered_map<std::string, Position> m_agent_positions;
        std::vector<std::string> m_agent_names;
        std::unordered_map<std::string, bool> m_hunting_hare_map; // empty means not set.

        // now for the internal helpers
        Position adjust_vals(int row, int col) const;
        bool hunter_ready_to_kill(int row, int col, bool hare) const;
        int delta_row(int curr_row, int new_row) const;
        int delta_col(int curr_col, int new_col) const;

    };
}
