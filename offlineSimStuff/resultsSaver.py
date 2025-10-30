import os
import csv

class ResultsSaver:
    def __init__(self, output_dir):

        os.makedirs(output_dir, exist_ok=True)
        file_name = os.path.join(output_dir, "simulation_results.csv")

        file_exists = os.path.isfile(file_name)
        csv_file = open(file_name, "a", newline="")
        writer = csv.writer(csv_file)

        if not file_exists:
            writer.writerow([
                "AgentType",
                "RoundType",
                "Scenario",
                "PeepConstant",
                "EnforceMajority",
                "AverageUtilityNonCats",
                "AverageUtilityCats",
                "AveragePopularityNonCats",
                "AveragePopularityCats",
            ])

        self.writer = writer
        self.csv_file = csv_file

    def write_result_row(self,
                         agent,
                         round_type,
                         scenario,
                         peep_constant,
                         enforce_majority,
                         average_utility_non_cats,
                         average_utility_cats,
                         average_popularity_non_cats,
                         average_popularity_cats):

        self.writer.writerow([
            agent,
            str(round_type),
            scenario,
            peep_constant,
            enforce_majority,
            average_utility_non_cats,
            average_utility_cats,
            average_popularity_cats,
            average_popularity_non_cats,
        ])


        # flush to disc immediately, should be safer for longer runs.
        self.csv_file.flush()
        os.fsync(self.csv_file.fileno())

    def close_file(self):
        self.csv_file.close()