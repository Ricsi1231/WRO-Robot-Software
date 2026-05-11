from __future__ import annotations

import enum
import heapq
import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class GridPosition:
    x: int
    y: int


class HeuristicType(enum.Enum):
    MANHATTAN = 0
    EUCLIDEAN = 1
    OCTAGONAL = 2


def _manhattan(a: GridPosition, b: GridPosition) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def _euclidean(a: GridPosition, b: GridPosition) -> int:
    dx = a.x - b.x
    dy = a.y - b.y
    return int(math.sqrt(dx * dx + dy * dy) + 0.5)


def _octagonal(a: GridPosition, b: GridPosition) -> int:
    dx = abs(a.x - b.x)
    dy = abs(a.y - b.y)
    return dx + dy - min(dx, dy)


@dataclass
class _WaypointEdge:
    target: int
    weight: int


@dataclass
class _Waypoint:
    position: GridPosition
    blocked: bool = False
    edges: list[_WaypointEdge] = field(default_factory=list)


@dataclass
class _SearchNode:
    g: int
    h: int
    waypoint_idx: int
    parent_idx: int

    @property
    def score(self) -> int:
        return self.g + self.h


NO_PARENT = -1


class PathPlanner:
    def __init__(self, heuristic: HeuristicType = HeuristicType.EUCLIDEAN) -> None:
        self._heuristic = heuristic
        self._waypoints: list[_Waypoint] = []

    def add_node(self, position: GridPosition) -> int:
        idx = len(self._waypoints)
        self._waypoints.append(_Waypoint(position=position))
        return idx

    def add_edge(self, from_idx: int, to_idx: int) -> bool:
        if not self._valid(from_idx) or not self._valid(to_idx):
            return False
        if from_idx == to_idx:
            return False
        for edge in self._waypoints[from_idx].edges:
            if edge.target == to_idx:
                return True
        weight = self._edge_weight(self._waypoints[from_idx].position, self._waypoints[to_idx].position)
        self._waypoints[from_idx].edges.append(_WaypointEdge(to_idx, weight))
        self._waypoints[to_idx].edges.append(_WaypointEdge(from_idx, weight))
        return True

    def block_node(self, node: int) -> None:
        if self._valid(node):
            self._waypoints[node].blocked = True

    def unblock_node(self, node: int) -> None:
        if self._valid(node):
            self._waypoints[node].blocked = False

    def clear_map(self) -> None:
        self._waypoints.clear()

    def find_path(self, start: int, target: int) -> list[GridPosition] | None:
        if not self._valid(start) or not self._valid(target):
            return None
        if self._waypoints[start].blocked or self._waypoints[target].blocked:
            return None
        if start == target:
            return [self._waypoints[start].position]

        target_pos = self._waypoints[target].position
        pool: list[_SearchNode] = []
        closed_set: set[int] = set()
        open_in_pool: dict[int, int] = {}
        heap: list[tuple[int, int, int]] = []
        counter = 0

        start_h = self._compute_h(self._waypoints[start].position, target_pos)
        pool.append(_SearchNode(g=0, h=start_h, waypoint_idx=start, parent_idx=NO_PARENT))
        open_in_pool[start] = 0
        heapq.heappush(heap, (start_h, counter, 0))
        counter += 1

        while heap:
            _, _, current_search_idx = heapq.heappop(heap)
            current_wp = pool[current_search_idx].waypoint_idx

            if current_wp in closed_set:
                continue
            if open_in_pool.get(current_wp) != current_search_idx:
                continue

            if current_wp == target:
                return self._reconstruct(pool, current_search_idx)

            closed_set.add(current_wp)
            open_in_pool.pop(current_wp, None)

            for edge in self._waypoints[current_wp].edges:
                neighbor = edge.target
                if self._waypoints[neighbor].blocked or neighbor in closed_set:
                    continue

                tentative_g = pool[current_search_idx].g + edge.weight
                existing_idx = open_in_pool.get(neighbor)
                if existing_idx is not None and tentative_g >= pool[existing_idx].g:
                    continue

                neighbor_h = self._compute_h(self._waypoints[neighbor].position, target_pos)
                new_idx = len(pool)
                pool.append(
                    _SearchNode(
                        g=tentative_g,
                        h=neighbor_h,
                        waypoint_idx=neighbor,
                        parent_idx=current_search_idx,
                    )
                )
                open_in_pool[neighbor] = new_idx
                heapq.heappush(heap, (tentative_g + neighbor_h, counter, new_idx))
                counter += 1

        return None

    def set_heuristic(self, heuristic: HeuristicType) -> None:
        self._heuristic = heuristic

    def _valid(self, idx: int) -> bool:
        return 0 <= idx < len(self._waypoints)

    def _compute_h(self, a: GridPosition, b: GridPosition) -> int:
        if self._heuristic == HeuristicType.MANHATTAN:
            return _manhattan(a, b)
        if self._heuristic == HeuristicType.OCTAGONAL:
            return _octagonal(a, b)
        return _euclidean(a, b)

    @staticmethod
    def _edge_weight(a: GridPosition, b: GridPosition) -> int:
        dx = a.x - b.x
        dy = a.y - b.y
        return int(math.sqrt(dx * dx + dy * dy) + 0.5)

    def _reconstruct(self, pool: list[_SearchNode], target_idx: int) -> list[GridPosition]:
        path: list[GridPosition] = []
        current = target_idx
        while current != NO_PARENT:
            path.append(self._waypoints[pool[current].waypoint_idx].position)
            current = pool[current].parent_idx
        path.reverse()
        return path
