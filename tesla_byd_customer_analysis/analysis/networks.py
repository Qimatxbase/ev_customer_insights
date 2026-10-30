"""Bigram network visualisation."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from .. import config


def save_bigram_networks(df: pd.DataFrame, top_n: int = 40) -> None:
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ModuleNotFoundError:
        return
    for group, subdf in df.groupby("comparison_type", dropna=False):
        counter: Counter[tuple[str, str]] = Counter()
        for text in subdf["clean_text"].fillna(""):
            tokens = str(text).split()
            counter.update(zip(tokens, tokens[1:]))
        graph = nx.Graph()
        for (a, b), weight in counter.most_common(top_n):
            graph.add_edge(a, b, weight=weight)
        if not graph.nodes:
            continue
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(graph, seed=config.RANDOM_SEED)
        nx.draw_networkx(graph, pos, with_labels=True, node_size=700, font_size=8, width=[graph[u][v]["weight"] for u, v in graph.edges])
        plt.axis("off")
        safe_group = str(group).lower().replace(" ", "_").replace("&", "and")
        plt.tight_layout()
        plt.savefig(config.FIGURE_DIR / f"bigram_network_{safe_group}.png", dpi=160)
        plt.close()

