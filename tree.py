class Tree:
    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data

    def print_tree(self):
        print(self.data)
        if self.left is not None:
            print('LEFT')
            self.left.print_tree()
        if self.right is not None:
            print('RIGHT')
            self.right.print_tree()

    def get_codes_dict(self, codes_dict, path):
        if self.left is not None:
            if self.left.data != '_NewLine' and self.left.data != '_Space' and self.left.data != '_EOT' and len(self.left.data) > 1:
                self.left.get_codes_dict(codes_dict, path + [0])
            else:
                codes_dict[self.left.data] = ''.join(str(x) for x in path + [0])
        if self.right is not None:
            if self.right.data != '_NewLine' and self.right.data != '_Space' and self.right.data != '_EOT' and len(self.right.data) > 1:
                self.right.get_codes_dict(codes_dict, path + [1])
            else:
                codes_dict[self.right.data] = ''.join(str(x) for x in path + [1])
        return codes_dict

    def add_to_tree(self, path, data):
        if len(path) == 1:
            if path[0] == 0:
                self.left = Tree(data)
            else:
                self.right = Tree(data)
        elif path[0] == 0:
            path.pop(0)
            self.left.add_to_tree(path, data)
        else:
            path.pop(0)
            self.right.add_to_tree(path, data)
