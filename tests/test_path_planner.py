from __future__ import annotations

from wro.path_planner import GridPosition, HeuristicType, PathPlanner


def test_simple_path() -> None:
    planner = PathPlanner()
    a = planner.add_node(GridPosition(0, 0))
    b = planner.add_node(GridPosition(3, 4))
    planner.add_edge(a, b)
    path = planner.find_path(a, b)
    assert path == [GridPosition(0, 0), GridPosition(3, 4)]


def test_same_start_and_target() -> None:
    planner = PathPlanner()
    a = planner.add_node(GridPosition(0, 0))
    path = planner.find_path(a, a)
    assert path == [GridPosition(0, 0)]


def test_no_path_exists() -> None:
    planner = PathPlanner()
    a = planner.add_node(GridPosition(0, 0))
    b = planner.add_node(GridPosition(10, 10))
    path = planner.find_path(a, b)
    assert path is None


def test_blocked_node() -> None:
    planner = PathPlanner()
    a = planner.add_node(GridPosition(0, 0))
    b = planner.add_node(GridPosition(5, 0))
    c = planner.add_node(GridPosition(10, 0))
    planner.add_edge(a, b)
    planner.add_edge(b, c)
    planner.block_node(b)
    path = planner.find_path(a, c)
    assert path is None


def test_unblock_node() -> None:
    planner = PathPlanner()
    a = planner.add_node(GridPosition(0, 0))
    b = planner.add_node(GridPosition(5, 0))
    planner.add_edge(a, b)
    planner.block_node(b)
    assert planner.find_path(a, b) is None
    planner.unblock_node(b)
    path = planner.find_path(a, b)
    assert path == [GridPosition(0, 0), GridPosition(5, 0)]


def test_shortest_path_chosen() -> None:
    planner = PathPlanner()
    a = planner.add_node(GridPosition(0, 0))
    b = planner.add_node(GridPosition(100, 0))
    c = planner.add_node(GridPosition(1, 0))
    planner.add_edge(a, b)
    planner.add_edge(b, c)
    planner.add_edge(a, c)
    path = planner.find_path(a, c)
    assert path is not None
    assert len(path) == 2
    assert path[0] == GridPosition(0, 0)
    assert path[1] == GridPosition(1, 0)


def test_multi_hop_path() -> None:
    planner = PathPlanner()
    nodes = [planner.add_node(GridPosition(i * 10, 0)) for i in range(5)]
    for i in range(4):
        planner.add_edge(nodes[i], nodes[i + 1])
    path = planner.find_path(nodes[0], nodes[4])
    assert path is not None
    assert len(path) == 5


def test_invalid_node_indices() -> None:
    planner = PathPlanner()
    planner.add_node(GridPosition(0, 0))
    assert planner.find_path(0, 5) is None
    assert planner.find_path(-1, 0) is None


def test_self_loop_rejected() -> None:
    planner = PathPlanner()
    a = planner.add_node(GridPosition(0, 0))
    assert planner.add_edge(a, a) is False


def test_duplicate_edge_ignored() -> None:
    planner = PathPlanner()
    a = planner.add_node(GridPosition(0, 0))
    b = planner.add_node(GridPosition(5, 0))
    assert planner.add_edge(a, b) is True
    assert planner.add_edge(a, b) is True


def test_clear_map() -> None:
    planner = PathPlanner()
    a = planner.add_node(GridPosition(0, 0))
    b = planner.add_node(GridPosition(5, 0))
    planner.add_edge(a, b)
    planner.clear_map()
    assert planner.find_path(0, 1) is None


def test_manhattan_heuristic() -> None:
    planner = PathPlanner(heuristic=HeuristicType.MANHATTAN)
    a = planner.add_node(GridPosition(0, 0))
    b = planner.add_node(GridPosition(3, 4))
    planner.add_edge(a, b)
    path = planner.find_path(a, b)
    assert path is not None


def test_blocked_start() -> None:
    planner = PathPlanner()
    a = planner.add_node(GridPosition(0, 0))
    b = planner.add_node(GridPosition(5, 0))
    planner.add_edge(a, b)
    planner.block_node(a)
    assert planner.find_path(a, b) is None


def test_large_grid_path_returns_shortest() -> None:
    planner = PathPlanner()
    side = 25
    ids: dict[tuple[int, int], int] = {}
    for x in range(side):
        for y in range(side):
            ids[(x, y)] = planner.add_node(GridPosition(x, y))
    for x in range(side):
        for y in range(side):
            if x + 1 < side:
                planner.add_edge(ids[(x, y)], ids[(x + 1, y)])
            if y + 1 < side:
                planner.add_edge(ids[(x, y)], ids[(x, y + 1)])

    path = planner.find_path(ids[(0, 0)], ids[(side - 1, side - 1)])
    assert path is not None
    assert path[0] == GridPosition(0, 0)
    assert path[-1] == GridPosition(side - 1, side - 1)
    assert len(path) == 2 * side - 1
