from typing import Optional, Union

import matplotlib as mpl
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import networkx as nx


def prepare_drawing(G, groups: list, random_seed: int = 42, **kwargs) -> tuple[dict, list, list]:
    left_nodes, right_nodes = [], []
    for node in G.nodes():
        if node in groups:
            left_nodes.append(node)
        else:
            right_nodes.append(node)
    pos = nx.drawing.layout.spring_layout(G, seed=random_seed, **kwargs)
    return pos, left_nodes, right_nodes


def make_legend(_dict, size: int, loc: str):
    patches = list()
    for name, color in _dict.items():
        patches.append(
            mlines.Line2D(
                [],
                [],
                color=color,
                marker="o",
                linestyle="None",
                markersize=size,
                label=name,
            )
        )
    plt.legend(handles=patches, loc=loc)


def draw_nodes(
    G,
    pos,
    ax,
    node_list: list,
    size_dict: dict,
    add_labels: bool,
    label_dict: dict,
    color: Union[str, list] = "C0",
    node_size_reduction_factor=1,
    node_alpha=0.5,
    font_size=5,
    font_color="k",
    style=None,
    zorder=None,
):
    sizes = [size_dict[node] / node_size_reduction_factor for node in node_list]
    node_collection = nx.draw_networkx_nodes(
        G, pos, nodelist=node_list, alpha=node_alpha, node_size=sizes, node_color=color, ax=ax
    )

    if zorder:
        node_collection.set_zorder(zorder)

    if add_labels:
        labels = {node: label_dict.get(node, "") for node in node_list}
        texts = nx.draw_networkx_labels(
            G, pos, labels=labels, font_size=font_size, font_color=font_color, ax=ax
        )

    if style is not None and add_labels:
        for _, text_obj in texts.items():  # type: ignore
            text_obj.set_style(style)


def draw_graph(
    G,
    pos,
    nodes_draw_list: list[list],
    nodes_labels_list: list[dict],
    nodes_sizes_list: list[dict],
    nodes_font_colors: list = ["#CEECFF", "#FFD0FD"],
    figsize: tuple = (7, 7),
    ax: Optional[plt.Axes] = None,
    add_labels: bool = False,
    dark_mode: bool = True,
    dpi: int = 140,
    node_colors: dict = None,
    node_alpha: float = 0.6,
    edge_alpha: float = 0.15,
    node_size_reduction_factor=1,
    edge_linewidth_reduction_factor=1,
    curved_edges: bool = True,
    legend_labels: dict = None,
    legend_size: int = 5,
    legend_loc: str = "best",
    **kwargs,
):
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
        no_ax_input = True
    else:
        no_ax_input = False
    # plt.figure(figsize=figsize, dpi=dpi)
    if dark_mode:
        plt.style.use("cyberpunk")
        edge_color = "#A47FFF"
        face_color = "#13042B"
    else:
        plt.style.use("seaborn-darkgrid")
        edge_color = "k"
        face_color = "w"

    for idx, (nodes_draw, nodes_labels, node_font_color, node_sizes) in enumerate(
        zip(nodes_draw_list, nodes_labels_list, nodes_font_colors, nodes_sizes_list)
    ):
        if node_colors is not None:
            default_color = "grey"
            _node_colors = [node_colors.get(node, default_color) for node in nodes_draw]
        else:
            _node_colors = f"C{idx}"
        draw_nodes(
            G,
            pos,
            ax=ax,
            node_list=nodes_draw,
            size_dict=node_sizes,
            add_labels=add_labels,
            color=_node_colors,
            label_dict=nodes_labels,
            node_alpha=node_alpha,
            font_color=node_font_color,
            node_size_reduction_factor=node_size_reduction_factor,
            **kwargs,
        )

    node_size_dict = dict(nodes_sizes_list[0], **nodes_sizes_list[1])
    node_size = [node_size_dict[node] / node_size_reduction_factor for node in G.nodes()]

    if curved_edges:
        # see http://stackoverflow.com/a/65213187/3240855
        G_for_edge_drawing = G.copy()
        additional_edge_args = {
            "connectionstyle": "arc3, rad=0.1",
            "arrows": True,
            "arrowstyle": "-",  # "-" instead of "->" to avoid arrowheads
            "node_size": node_size,  # because drawing arrows considers node sizes
        }
    else:
        G_for_edge_drawing = G.to_undirected()
        additional_edge_args = {}

    for node1 in nodes_draw_list[0]:
        for node2 in nodes_draw_list[1]:
            if G.has_edge(node1, node2):
                weight = G[node1][node2]["weight"]
                linewidth = weight / edge_linewidth_reduction_factor

                color = edge_color
                if node_colors is not None:
                    if node1 in node_colors:
                        color = node_colors[node1]
                    elif node2 in node_colors:
                        color = node_colors[node2]

                nx.draw_networkx_edges(
                    G_for_edge_drawing,
                    pos,
                    edge_color=color,
                    edgelist=[(node1, node2)],
                    alpha=edge_alpha,
                    width=linewidth,
                    ax=ax,
                    **additional_edge_args,
                )
    # Don't draw marker edges for nodes
    for p in ax.collections:
        if type(p) == mpl.collections.PathCollection:
            p.set_edgecolors("None")

    if dark_mode:
        ax.set_facecolor(face_color)
    if legend_labels is not None and no_ax_input:
        make_legend(legend_labels, loc=legend_loc, size=legend_size)
    ax.axis("off")
    plt.tight_layout()
    if no_ax_input:
        plt.gcf().set_facecolor(face_color)
        plt.show()
    else:
        return face_color


def draw_graph_filtered(
    G,
    pos,
    nodes_list: list,
    nodes_sizes_list: list[dict],
    min_sizes: list[int],
    min_sizes_labels: list[int],
    nodes_labels_list: Optional[list[dict]] = None,
    **kwargs,
):
    nodes_draw_list = []
    _nodes_labels_list = []
    for idx, (_nodes, _sizes, _min_size, _min_size_label) in enumerate(
        zip(nodes_list, nodes_sizes_list, min_sizes, min_sizes_labels)
    ):
        nodes_draw_list.append([__node for __node in _nodes if _sizes[__node] >= _min_size])
        if nodes_labels_list is not None and nodes_labels_list[idx] is not None:
            _nodes_labels_list.append(nodes_labels_list[idx])
        else:
            _nodes_labels_list.append(
                {__node: __node for __node in _nodes if _sizes[__node] >= _min_size_label}
            )
    return draw_graph(
        G,
        pos,
        nodes_draw_list=nodes_draw_list,
        nodes_labels_list=_nodes_labels_list,
        nodes_sizes_list=nodes_sizes_list,
        **kwargs,
    )


def main():
    return ()


if __name__ == "__main__":
    main()
