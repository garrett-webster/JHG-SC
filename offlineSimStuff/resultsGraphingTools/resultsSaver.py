import os
import csv
import json

class ResultsSaver:
    HEADER = [ # default lil header guy
        "AgentType",
        "RandomAgents",
        "RoundType",
        "Scenario",
        "PeepConstant",
        "EnforceMajority",
        "AverageUtilityNonCats",
        "AverageUtilityCats",
        "AveragePopularityNonCats",
        "AveragePopularityCats",
        "UtilityLog",
        "PopularityLog"
    ]

    def __init__(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        self.file_name = os.path.join(output_dir, "simulation_results.csv")

        # Always overwrite the file and write a fresh header
        self.csv_file = open(self.file_name, "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(self.HEADER)

    def write_result_row(
        self,
        agent,
        random_agents,
        round_type,
        scenario,
        peep_constant,
        enforce_majority,
        average_utility_non_cats,
        average_utility_cats,
        average_popularity_non_cats,
        average_popularity_cats,
        utility_to_log,
        popularity_to_log,
    ):
        self.writer.writerow([
            agent,
            random_agents,
            json.dumps(round_type),  # safely store list
            scenario,
            peep_constant,
            enforce_majority,
            average_utility_non_cats,
            average_utility_cats,
            average_popularity_non_cats,
            average_popularity_cats,
            json.dumps(utility_to_log.tolist()),
            json.dumps(popularity_to_log.tolist()),
        ])

        # flush immediately
        self.csv_file.flush()
        os.fsync(self.csv_file.fileno())

    def close_file(self):
        self.csv_file.close()
