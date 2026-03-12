from __future__ import annotations

from .types import PDDAG


def reachable_from(graph: PDDAG, src: str) -> set[str]:
    seen: set[str] = set()
    stack = [src]
    while stack:
        cur = stack.pop()
        for nxt in graph.edges[cur]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def predecessor_map(graph: PDDAG) -> dict[str, set[str]]:
    return {n: set(graph.reverse_edges[n]) for n in graph.nodes}


def successor_map(graph: PDDAG) -> dict[str, set[str]]:
    return {n: set(graph.edges[n]) for n in graph.nodes}


def preceq_map(graph: PDDAG) -> dict[str, set[str]]:
    out = {}
    for n in graph.nodes:
        out[n] = {n}.union(reachable_from_reverse(graph, n))
    return out


def reachable_from_reverse(graph: PDDAG, src: str) -> set[str]:
    seen: set[str] = set()
    stack = [src]
    while stack:
        cur = stack.pop()
        for nxt in graph.reverse_edges[cur]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen
