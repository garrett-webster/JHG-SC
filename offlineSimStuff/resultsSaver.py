import os
import csv
import json

class ResultsSaver:
    def __init__(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        self.file_name = os.path.join(output_dir, "simulation_results.csv")

        file_exists = os.path.isfile(self.file_name)
        self.csv_file = open(self.file_name, "a", newline="", encoding="utf-8")
        self.writer = csv.writer(self.csv_file)

        if not file_exists:
            self.writer.writerow([
                "AgentType",
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
            ])

    def write_result_row(
        self,
        agent,
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
