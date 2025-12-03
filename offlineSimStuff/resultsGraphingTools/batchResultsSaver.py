import os
import json
import pandas as pd

class BatchResultsSaver:
    """
    Efficient CSV writer that batches rows in memory and flushes to disk every N writes.
    """
    def __init__(self, output_dir, flush_interval=50):
        os.makedirs(output_dir, exist_ok=True)
        self.file_name = os.path.join(output_dir, "simulation_results.csv")
        self.flush_interval = flush_interval
        self.buffer = []

        # Create CSV with header if not exists
        if not os.path.isfile(self.file_name):
            pd.DataFrame(columns=[
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
            ]).to_csv(self.file_name, index=False)

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
        """Add a single result to the in-memory buffer."""
        self.buffer.append({
            "AgentType": agent,
            "RoundType": json.dumps(round_type),
            "Scenario": scenario,
            "PeepConstant": peep_constant,
            "EnforceMajority": enforce_majority,
            "AverageUtilityNonCats": average_utility_non_cats,
            "AverageUtilityCats": average_utility_cats,
            "AveragePopularityNonCats": average_popularity_non_cats,
            "AveragePopularityCats": average_popularity_cats,
            "UtilityLog": json.dumps(utility_to_log.tolist()),
            "PopularityLog": json.dumps(popularity_to_log.tolist()),
        })

        if len(self.buffer) >= self.flush_interval:
            self._flush_buffer()

    def _flush_buffer(self):
        """Write buffered rows to CSV and clear memory."""
        if not self.buffer:
            return
        df = pd.DataFrame(self.buffer)
        df.to_csv(self.file_name, mode="a", index=False, header=False)
        self.buffer.clear()

    def close(self):
        """Flush remaining rows before shutdown."""
        self._flush_buffer()
