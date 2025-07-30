import igraph as ig
import leidenalg
import numpy as np
from itertools import combinations


def returnCommunitiesGivenInfluenceFromLeiden(influence_matrix):
    list_influence = influence_matrix.tolist() # get the fetcher as a list
    g = ig.Graph.Weighted_Adjacency(
        influence_matrix.tolist(),
        mode=ig.ADJ_DIRECTED,
        attr="weight",
        loops=True, # I am actually curious about self relations
    )

    results = analyze_leiden(g, leiden_run, num_stability_runs=10)
    for r in results:
        print(r)
    partition = leiden_run(g)
    return partition


def leiden_run(g):
    return leidenalg.find_partition(g, leidenalg.ModularityVertexPartition)

def analyze_leiden(graph, leiden_runner, num_stability_runs=10):
    def internal_density(subgraph):
        v = len(subgraph.vs)
        if v < 2:
            return 0.0
        m = len(subgraph.es)
        max_edges = v * (v - 1) if graph.is_directed() else (v * (v - 1)) / 2
        return m / max_edges

    def conductance(graph, community):
        internal = 0
        external = 0
        for v in community:
            neighbors = graph.neighbors(v, mode="OUT" if graph.is_directed() else "ALL")
            for n in neighbors:
                if n in community:
                    internal += 1
                else:
                    external += 1
        internal = internal / 2 if not graph.is_directed() else internal
        total_degree = internal + external
        return external / total_degree if total_degree > 0 else 0.0

    def stability_scores(g, runner, runs=10):
        n = len(g.vs)
        co_matrix = np.zeros((n, n))
        last_partition = None

        for _ in range(runs):
            part = runner(g)
            last_partition = part
            for community in part:
                for i, j in combinations(community, 2):
                    co_matrix[i][j] += 1
                    co_matrix[j][i] += 1

        scores = []
        for community in last_partition:
            if len(community) < 2:
                scores.append(1.0)
            else:
                pair_vals = [co_matrix[i][j] / runs for i, j in combinations(community, 2)]
                scores.append(np.mean(pair_vals))
        return scores, last_partition

    stability, partition = stability_scores(graph, leiden_runner, num_stability_runs)

    results = []
    for i, community in enumerate(partition):
        subgraph = graph.subgraph(community)
        result = {
            "community_index": i,
            "size": len(community),
            "internal_density": internal_density(subgraph),
            "conductance": conductance(graph, community),
            "modularity_contribution": partition.quality(),  # whole partition quality
            "stability": stability[i],
            "members" : [com+1 for com in community],
        }
        results.append(result)

    return results