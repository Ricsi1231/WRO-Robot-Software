from __future__ import annotations

# ruff: noqa: E402
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wro.path_planner import GridPosition, HeuristicType, PathPlanner


def _format_path(path: list[GridPosition] | None) -> str:
    if path is None:
        return "no path"
    return " -> ".join(f"({position.x},{position.y})" for position in path)


def main() -> None:
    planner = PathPlanner(HeuristicType.EUCLIDEAN)
    start = planner.add_node(GridPosition(0, 0))
    middle = planner.add_node(GridPosition(1, 0))
    target = planner.add_node(GridPosition(2, 0))
    detour = planner.add_node(GridPosition(1, 1))

    planner.add_edge(start, middle)
    planner.add_edge(middle, target)
    planner.add_edge(start, detour)
    planner.add_edge(detour, target)

    print(f"normal={_format_path(planner.find_path(start, target))}")
    planner.block_node(middle)
    print(f"middle_blocked={_format_path(planner.find_path(start, target))}")
    planner.block_node(detour)
    print(f"all_routes_blocked={_format_path(planner.find_path(start, target))}")


if __name__ == "__main__":
    main()
