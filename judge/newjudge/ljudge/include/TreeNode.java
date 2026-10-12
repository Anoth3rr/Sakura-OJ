
/*
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
 */
public class TreeNode {
    int val = 0;
    TreeNode left = null;
    TreeNode right = null;

    public TreeNode(int val) {
        this.val = val;

    }

}
