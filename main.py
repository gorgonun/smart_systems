import copy


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
                new_children = copy.copy(self.representation)
                temp = self.representation[p_x][p_y]
                new_children[p_x][p_y] = self.representation[x][y]
                new_children[x][y] = temp
                children.append(Node(self, self.depth+1, new_children, (p_x, p_y)))




class Puzzle8():
    goal = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "_"]]

    def __init__(self) -> None:
        self.open_list = []
        self.closed_list = []

    def get_start_node(self, node_repr: str):
        return Node(
            None,
            0,
            [x.split(" ") for x in node_repr.split("\n")]
        )

    def f(self, node: Node):
        return self.h(node) + node.depth

    def h(self, node: Node):
        f = 0
        for x in len(node.representation):
            for y in len(x):
                if node.representation[x][y] != self.goal[x][y]:
                    f += 1
        return f

    def search(self, node: Node):
        node.f = self.f()

        self.open_list.append(node)

        while True:
            cur = self.open_list[0]
            if not self.h(cur):
                break

            for child in node.generate_children():
                child.f = self.f(child)
                self.open_list.append(child)

            self.closed_list.append(cur)
            del self.open_list[0]

        result = self.open_list[0]
        while result:
            print(result.representation)
            result = result.parent
