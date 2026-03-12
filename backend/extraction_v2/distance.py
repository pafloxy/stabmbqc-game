from __future__ import annotations

from collections import defaultdict, deque

from .types import DistanceLayers, PDDAG


def compute_distance_and_layers(graph: PDDAG, extracted: set[str]) -> DistanceLayers:
    dist = {n: -1 for n in graph.nodes}
    q = deque()
    for n in extracted:
        if n in graph.nodes:
            dist[n] = 0
            q.append(n)
    while q:
        cur = q.popleft()
        for pred in graph.reverse_edges[cur]:
            if dist[pred] == -1 or dist[pred] > dist[cur] + 1:
                dist[pred] = dist[cur] + 1
                q.append(pred)
    layers = defaultdict(list)
    for n, d in dist.items():
        layers[d].append(n)
    for v in layers.values():
        v.sort(key=lambda nid: graph.nodes[nid].original_index)
    return DistanceLayers(d_m=dist, layers=dict(layers))
