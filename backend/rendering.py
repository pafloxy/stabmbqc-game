"""Rendering helpers: circuit and graph images.

This module provides functions to generate PNG images for:
- Quantum circuits (CZ gates, rotations, measurements)
- Interaction graphs

For now, these are stubs. The full implementation can use:
- Qiskit for circuit diagrams
- matplotlib/networkx for graph visualizations
- Stim's built-in diagram features
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Dict, Any

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


def render_circuit_png(
    spec: Dict[str, Any],
    out_path: Path,
    title: Optional[str] = None
) -> Optional[Path]:
    """
    Render a circuit diagram and save as PNG.
    
    Args:
        spec: Circuit specification with keys:
            - n_qubits: int
            - alice_qubits: List[int]
            - bob_qubits: List[int]
            - cz_edges: List[List[int]] (pairs)
            - rotations: List[Dict] (optional)
            - measurements: List[Dict] (optional)
        out_path: Path to save the PNG
        title: Optional title for the diagram
    
    Returns:
        Path to the saved file, or None if rendering failed
    """
    if not MATPLOTLIB_AVAILABLE:
        print(f"  [STUB] Would render circuit to {out_path}")
        return None
    
    n_qubits = spec.get("n_qubits", 3)
    alice_qubits = spec.get("alice_qubits", [])
    bob_qubits = spec.get("bob_qubits", [])
    cz_edges = spec.get("cz_edges", [])
    rotations = spec.get("rotations", [])
    
    fig, ax = plt.subplots(figsize=(8, n_qubits * 0.8 + 1))
    
    # Draw qubit lines
    wire_length = 6
    for q in range(n_qubits):
        y = n_qubits - q - 1
        color = "#33ff33" if q in alice_qubits else "#ffcc00" if q in bob_qubits else "#888888"
        ax.plot([0, wire_length], [y, y], color=color, linewidth=2, zorder=1)
        
        # Label
        label = f"q{q}"
        if q in alice_qubits:
            label += " (A)"
        elif q in bob_qubits:
            label += " (B)"
        ax.text(-0.3, y, label, ha='right', va='center', fontsize=10, color=color)
    
    # Draw CZ gates
    x_pos = 1.5
    for edge in cz_edges:
        if len(edge) >= 2:
            q1, q2 = edge[0], edge[1]
            y1, y2 = n_qubits - q1 - 1, n_qubits - q2 - 1
            
            # Vertical line
            ax.plot([x_pos, x_pos], [min(y1, y2), max(y1, y2)], 
                   color="#33ff33", linewidth=2, zorder=2)
            
            # Dots at qubits
            ax.scatter([x_pos, x_pos], [y1, y2], s=100, color="#33ff33", zorder=3)
            
            x_pos += 1
    
    # Draw rotations
    for rot in rotations:
        gate = rot.get("gate", "R")
        q = rot.get("q", 0)
        theta = rot.get("theta", "θ")
        y = n_qubits - q - 1
        
        rect = mpatches.FancyBboxPatch(
            (x_pos - 0.3, y - 0.3), 0.6, 0.6,
            boxstyle="round,pad=0.05",
            facecolor="#0a0a0a",
            edgecolor="#33ff33",
            linewidth=2,
            zorder=4
        )
        ax.add_patch(rect)
        ax.text(x_pos, y, f"{gate}", ha='center', va='center', 
               fontsize=9, color="#33ff33", zorder=5)
        x_pos += 1
    
    # Style
    ax.set_xlim(-1, wire_length + 0.5)
    ax.set_ylim(-0.5, n_qubits - 0.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#0a0a0a')
    fig.patch.set_facecolor('#0a0a0a')
    
    if title:
        ax.set_title(title, color="#33ff33", fontsize=12, pad=10)
    
    # Save
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight', 
                facecolor='#0a0a0a', edgecolor='none')
    plt.close(fig)
    
    return out_path


def render_graph_png(
    spec: Dict[str, Any],
    out_path: Path,
    title: Optional[str] = None
) -> Optional[Path]:
    """
    Render an interaction graph and save as PNG.
    
    Args:
        spec: Graph specification with keys:
            - n_qubits: int
            - alice_qubits: List[int]
            - bob_qubits: List[int]
            - cz_edges: List[List[int]] (pairs)
        out_path: Path to save the PNG
        title: Optional title for the diagram
    
    Returns:
        Path to the saved file, or None if rendering failed
    """
    if not MATPLOTLIB_AVAILABLE or not NETWORKX_AVAILABLE:
        print(f"  [STUB] Would render graph to {out_path}")
        return None
    
    n_qubits = spec.get("n_qubits", 3)
    alice_qubits = set(spec.get("alice_qubits", []))
    bob_qubits = set(spec.get("bob_qubits", []))
    cz_edges = spec.get("cz_edges", [])
    
    # Build graph
    G = nx.Graph()
    G.add_nodes_from(range(n_qubits))
    for edge in cz_edges:
        if len(edge) >= 2:
            G.add_edge(edge[0], edge[1])
    
    # Colors
    node_colors = []
    for q in range(n_qubits):
        if q in alice_qubits:
            node_colors.append("#33ff33")
        elif q in bob_qubits:
            node_colors.append("#ffcc00")
        else:
            node_colors.append("#888888")
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Layout
    if len(bob_qubits) > 0:
        # Bipartite-ish layout
        pos = {}
        alice_list = sorted(alice_qubits)
        bob_list = sorted(bob_qubits)
        
        for i, q in enumerate(alice_list):
            pos[q] = (0, -i)
        for i, q in enumerate(bob_list):
            pos[q] = (2, -i)
        # Other qubits
        other = [q for q in range(n_qubits) if q not in alice_qubits and q not in bob_qubits]
        for i, q in enumerate(other):
            pos[q] = (1, -i - len(alice_list))
    else:
        pos = nx.spring_layout(G, seed=42)
    
    # Draw
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color="#33ff33", width=2, ax=ax)
    nx.draw_networkx_labels(G, pos, font_color="#0a0a0a", font_size=10, ax=ax)
    
    ax.set_facecolor('#0a0a0a')
    fig.patch.set_facecolor('#0a0a0a')
    ax.axis('off')
    
    if title:
        ax.set_title(title, color="#33ff33", fontsize=12, pad=10)
    
    # Legend
    alice_patch = mpatches.Patch(color="#33ff33", label="Alice")
    bob_patch = mpatches.Patch(color="#ffcc00", label="Bob")
    ax.legend(handles=[alice_patch, bob_patch], loc='upper right',
              facecolor='#0a0a0a', edgecolor='#33ff33', labelcolor='#33ff33')
    
    # Save
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight',
                facecolor='#0a0a0a', edgecolor='none')
    plt.close(fig)
    
    return out_path


def render_campaign_assets(campaign: Any, assets_dir: Path) -> List[Path]:
    """
    Render all assets for a campaign.
    
    Args:
        campaign: A Campaign object
        assets_dir: Base directory for assets
    
    Returns:
        List of paths to rendered files
    """
    rendered: List[Path] = []
    
    for round_data in campaign.rounds:
        if not round_data.qc_spec:
            continue
        
        spec = {
            "n_qubits": round_data.qc_spec.n_qubits,
            "alice_qubits": round_data.qc_spec.alice_qubits,
            "bob_qubits": round_data.qc_spec.bob_qubits,
            "cz_edges": round_data.qc_spec.cz_edges,
            "rotations": round_data.qc_spec.rotations,
        }
        
        # Render circuit
        if round_data.assets and round_data.assets.circuit_image:
            circuit_path = assets_dir / round_data.assets.circuit_image
            result = render_circuit_png(spec, circuit_path, f"Round {round_data.id}")
            if result:
                rendered.append(result)
        
        # Render graph
        if round_data.assets and round_data.assets.graph_image:
            graph_path = assets_dir / round_data.assets.graph_image
            result = render_graph_png(spec, graph_path, f"Round {round_data.id}")
            if result:
                rendered.append(result)
    
    return rendered
