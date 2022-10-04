from collections import deque
import copy
from dataclasses import dataclass, field
import sys
import time
import heapq
import abc
from typing import Tuple


# 2 8 3\n1 6 4\n7 _ 5
class Node():

    def __init__(self, parent, depth: int, representation, empty_position) -> None:
        self.parent = parent
        self.depth = depth
        self.representation = representation
        self.empty_position = empty_position
        self.f = None


    def generate_children(self):
        children = []
        x, y = self.empty_position
        possible_moves = [[x+1, y], [x-1, y], [x, y+1], [x, y-1]]
        for p_x, p_y in possible_moves:
            if p_x >= 0 and p_x < 3 and p_y >= 0 and p_y < 3:
                new_children = copy.copy([copy.copy(x) for x in self.representation])
                temp = self.representation[p_x][p_y]
                new_children[p_x][p_y] = self.representation[x][y]
                new_children[x][y] = temp
                new_node = Node(self, self.depth+1, new_children, (p_x, p_y))
                children.append(new_node)

        return children

    def __str__(self) -> str:
        return "\n".join([" ".join(x) for x in self.representation]) + "\n"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, __o: object) -> bool:
        return self.representation == __o.representation

    def __hash__(self) -> int:
        return hash(''.join(y for x in self.representation for y in x))


@dataclass(order=True)
class PriorityNode():
    node: Node = field(compare=False)
    priority: int


class Puzzle8(abc.ABC):
    goal = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "_"]]

    def __init__(self) -> None:
        self.open_list = []
        self.closed_list = set()
        self.three = {}

    def f(self, node: Node):
        return self.heuristic(node) + self.cost(node)

    def cost(self, node: Node):
        return node.depth

    @abc.abstractmethod
    def heuristic(self, node: Node):
        ...

    def pprint(self, child, f):
        def fix_str(t):
            return [y for x in t for y in str(x).split("\n")]

        template = ["open list | closed list | current child"]
        template_size = max(len(self.open_list) * 4, len(self.closed_list) * 4, 4)

        fixed_open_list = fix_str([x.node for x in sorted(self.open_list)]) + [" - "] * (template_size - len(self.open_list))
        f_value_open_list = [str(x.priority) for x in sorted(self.open_list)]
        fixed_closed_list = fix_str(self.closed_list) + [" - "] * (template_size - len(self.closed_list))
        fixed_child = fix_str([child]) + [" - "] * (template_size - 3)

        targets = []

        for x in range(template_size):
            template.append("{:^8s}{:2s} {:^13s} {:^12s}{:2s}")
            targets.append(fixed_open_list[x])
            targets.append(" " if x % 4 or len(f_value_open_list) <= x // 4 else f_value_open_list[x // 4])
            targets.append(fixed_closed_list[x])
            targets.append(fixed_child[x])
            targets.append(" " if x else str(f))


        print("\n".join(template).format(*targets))

    def search(self, node: Node, max_iteration=1000, fast=True):
        fixed_node = PriorityNode(node, self.f(node))

        heapq.heappush(self.open_list, fixed_node)
        result = None
        i = 0

        while True:
            cur = heapq.heappop(self.open_list)
            if not fast:
                print(f"----------------- Got new child - ex ({i}) -----------------")
                self.pprint(cur.node, cur.priority)

            if cur.node.representation == self.goal:
                result = cur.node
                break

            if not fast:
                print(f"Getting new children:")

            for child in cur.node.generate_children():
                if child not in self.closed_list:
                    p_node = PriorityNode(child, self.f(child))
                    heapq.heappush(self.open_list, p_node)

                    if not fast:
                        print(p_node.priority, p_node.node, sep="\n")

            self.closed_list.add(cur.node)

            i += 1
            if i > max_iteration:
                print("Max iterations reached")
                break

        if result:
            path = deque()
            while result:
                path.appendleft(result)
                result = result.parent

            print(f"Steps: {len(path)}\nIterations: {i}\n")

            for child in path:
                print(child)


class Puzzle8CostUniform(Puzzle8):
    def heuristic(self, node: Node):
        return 0


class Puzzle8NTOP(Puzzle8):
    def heuristic(self, node: Node):
        f = 0
        for x in range(len(node.representation)):
            for y in range(len(node.representation[x])):
                if node.representation[x][y] != self.goal[x][y]:
                    f += 1
        return f


class Puzzle8MahattanDistance(Puzzle8):

    def find_distance(self, target: str, pos: Tuple[int, int]):
        for x in range(len(self.goal)):
            for y in range(len(self.goal)):
                if self.goal[x][y] == target:
                    return abs(((pos[0] + 1) * (pos[1] + 1)) - (x + 1) * (y + 1))

    def heuristic(self, node: Node):
        f = 0
        for x in range(len(node.representation)):
            for y in range(len(node.representation[x])):
                if node.representation[x][y] != self.goal[x][y]:
                    f += self.find_distance(node.representation[x][y], (x, y))
        return f


def main():
    initial_node = sys.argv[1]
    fast = sys.argv[2] == "true"
    max_it = int(sys.argv[3])
    # puzzle = Puzzle8CostUniform()
    # puzzle = Puzzle8NTOP()
    puzzle = Puzzle8MahattanDistance()

    pos = (0, 0)
    parsed_node = [[0] * 3, [0] * 3, [0] * 3]
    x, y = 0, 0
    for i, item in enumerate(initial_node.split(" ")):
        if not i % 3:
            x += 1
            y = 0

        parsed_node[x - 1][y] = item
        if item == "_":
            pos = (x - 1, y)
        y += 1

    start = Node(
        None,
        0,
        parsed_node,
        pos
    )

    puzzle.search(start, fast=fast, max_iteration=max_it)

if __name__ == "__main__":
    main()

# python3 main.py "4 1 3 7 _ 6 5 8 2" true 100000