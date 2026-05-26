//
// Created by Sean Smith on 5/26/2026.
//


#pragma once
#include <cmath>

namespace jhg {

    struct Position {
        int row;
        int col;

        // Default constructor — initializes to (0, 0)
        Position() : row(0), col(0) {}

        // Constructor with values
        Position(int r, int c) : row(r), col(c) {}

        // Equality comparison — needed for containers like std::unordered_map
        bool operator==(const Position& other) const {
            return row == other.row && col == other.col;
        }

        // Inequality — good practice to define both
        bool operator!=(const Position& other) const {
            return !(*this == other);
        }
    };

} // namespace jhg