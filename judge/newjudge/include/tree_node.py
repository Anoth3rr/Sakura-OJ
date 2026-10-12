"""
The serialization of a binary tree follows a level order traversal, where '#'
signifies a path terminator where no node exists below.

Here's an example:

  1
 / \
2   3
   /
  4
   \
    5

The above binary tree is serialized as "1,2,3,#,#,4,#,#,5".
"""

class TreeNode(object):
    val = 0
    left = right = None

    def __init__(self, val):
        self.val = val

    @classmethod
    def generate_tree_node(cls, tree_str):
        if not tree_str:
            return

        tree_nodes = []

        current = 0
        is_left = True

        values = tree_str.split(',')
        for value in values:
            value = value.strip()
            if not value:
                continue
            if value == '#':
                if tree_nodes[current]:
                    if is_left:
                        is_left = False
                    elif len(tree_nodes) > current + 1:
                        current += 1
                        is_left = True
                continue

            try:
                new_node = TreeNode(int(value))
                tree_nodes.append(new_node)
            except:
                continue

            if len(tree_nodes) == 1:
                current = 0
                is_left = True
            else:
                if is_left:
                    tree_nodes[current].left = new_node
                    is_left = False
                else:
                    tree_nodes[current].right = new_node
                    current += 1
                    is_left = True

        return len(tree_nodes) and tree_nodes[0] or None