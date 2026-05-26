//
// Created by Sean Smith on 5/26/2026.
//

#pragma once

#include <string>
#include <vector>

namespace jhg {
    constexpr int AVAILABLE = -1;

    inline const std::string HARE_NAME = "hare";
    inline const std::string STAG_NAME = "stag";

    inline const std::string VERTICAL = "vertical";
    inline const std::string HORIZONTAL = "horizontal";

    inline const std::vector<std::string> POSSIBLE_MOVEMENTS = {VERTICAL, HORIZONTAL};
    inline const std::vector<int> POSSIBLE_DELTA_VALS = {-1, 0, 1};

    constexpr int MAX_MOVEMENT_UNITS = 1;

    constexpr int LEFT = 0;
    constexpr int RIGHT = 1;
    constexpr int UP = 2;
    constexpr int DOWN = 3;
    constexpr int NONE = 4;

    constexpr int HARE_REWARD = 10;
    constexpr int STAG_REWARD = 60;

    constexpr int N_REQUIRED_TO_CAPTURE_HARE = 1;
    constexpr int N_REQUIRED_TO_CAPTURE_STAG = 3;
    constexpr int N_HUNTERS = 3;


}