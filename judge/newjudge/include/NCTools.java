import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

public class NCTools {
    public static void main(String[] argv) {
        String line = "1 , [ 1 , 2 ],[[1],[2],[3,4,-5]],[ 1 , 2 ],[[1],[2],[3,4,5]],"; // int
        line = line
                + "true , [ false , true ],[[false],[false],[false,true,true]],[ true , false ],[[false],[true],[true,true,true]],"; // bool
        line = line
                + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [ 1 , 2 ],[[1],[2],[3,4,5]],"; // float
        line = line
                + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [],[ 1 , 2 ],[[1],[2],[3,4,5]],"; // double
        line = line
                + " \"a\", [\"\",\"x[[[[,,,,[}}}}\"], [[acd, efg], [acd, \"efg\"]],";// string
        line = line + " a, [x, y ], [[a, b],[], [c, d]],";// char
        line = line
                + " 1000000000, [3000000000, 2000000000 ], [[3000000000, 2000000000 ],[13000000000, 22000000000 ]],";// long
        line = line
                + "{1,3,4},[{2, 4, 5},{5,6,7,89,11},{ }],[[{2, 4, 5},{5,6,7,89,11},{}],[{2, 4, 5},{5,6,7,89,11}]],"; // ListNode
        line = line
                + "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]],"; // Interval
        line = line
                + "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]],"; // Point
        line = line
                + "{1,2,3,#,#,4,#,#,5},[{1,2,3,#,#,4,#,#,5}],[[{1,2,3,#,#,4,#,#,5}],[{1,2,3,#,#,4,#,#,5},{1,2,3,#,#,4,#,#,5}]],"; // TreeNode
        line = line
                + "{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]},[{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}],[[],[{[],[]}], [{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}]],"; // TreeLinkNode
        line = line
                + "{ -1, 8, 7,  -3,4,4,-3,#,#,-1}, [{ -1, 8, 7,  -3,4,4,-3,#,#,-1}], [[{}],[{ -1, 8, 7,  -3,4,4,-3,#,#,-1}]],"; // RandomListNode
        line = line
                + "{[0,1,2],[1,2],[2,2]}, [{[0,1,2],[1,2],[2,2]}], [[], [{[0,1,2],[1,2],[2,2]},{[0,1,2],[1,2],[2,2]}]]"; //

        ArrayList<String> parameters = NCTools.GetArguments(line);
        // NCTools.Print(parameters);
        int i = 0;
        NCTools.PrintInt(NCTools.GetInt(parameters.get(i++)));
        NCTools.PrintIntList(NCTools.GetInts(parameters.get(i++)));
        NCTools.PrintIntListList(NCTools.GetIntss(parameters.get(i++)));
        NCTools.PrintIntList(NCTools.GetIntList(parameters.get(i++)));
        NCTools.PrintIntListList(NCTools.GetIntListList(parameters.get(i++)));

        NCTools.PrintBoolean(NCTools.GetBoolean(parameters.get(i++)));
        NCTools.PrintBooleanList(NCTools.GetBooleans(parameters.get(i++)));
        NCTools.PrintBooleanListList(NCTools.GetBooleanss(parameters.get(i++)));
        NCTools.PrintBooleanList(NCTools.GetBooleanList(parameters.get(i++)));
        NCTools.PrintBooleanListList(NCTools.GetBooleanListList(parameters
                .get(i++)));

        NCTools.PrintFloat(NCTools.GetFloat(parameters.get(i++)));
        NCTools.PrintFloatList(NCTools.GetFloats(parameters.get(i++)));
        NCTools.PrintFloatListList(NCTools.GetFloatss(parameters.get(i++)));
        NCTools.PrintFloatList(NCTools.GetFloatList(parameters.get(i++)));
        NCTools.PrintFloatListList(NCTools.GetFloatListList(parameters.get(i++)));

        NCTools.PrintDouble(NCTools.GetDouble(parameters.get(i++)));
        NCTools.PrintDoubleList(NCTools.GetDoubles(parameters.get(i++)));
        NCTools.PrintDoubleListList(NCTools.GetDoubless(parameters.get(i++)));
        NCTools.PrintDoubleList(NCTools.GetDoubles(parameters.get(i++)));
        NCTools.PrintDoubleList(NCTools.GetDoubleList(parameters.get(i++)));
        NCTools.PrintDoubleListList(NCTools.GetDoubleListList(parameters
                .get(i++)));

        NCTools.PrintString(NCTools.GetString(parameters.get(i++)));
        NCTools.PrintStringList(NCTools.GetStringList(parameters.get(i)));
        NCTools.PrintStringList(NCTools.GetStrings(parameters.get(i++)));
        NCTools.PrintStringListList(NCTools.GetStringListList(parameters.get(i)));
        NCTools.PrintStringListList(NCTools.GetStringss(parameters.get(i++)));

        NCTools.PrintChar(NCTools.GetChar(parameters.get(i++)));
        NCTools.PrintCharList(NCTools.GetChars(parameters.get(i++)));
        NCTools.PrintCharListList(NCTools.GetCharss(parameters.get(i++)));

        NCTools.PrintLong(NCTools.GetLong(parameters.get(i++)));
        NCTools.PrintLongList(NCTools.GetLongList(parameters.get(i)));
        NCTools.PrintLongList(NCTools.GetLongs(parameters.get(i++)));
        NCTools.PrintLongListList(NCTools.GetLongListList(parameters.get(i)));
        NCTools.PrintLongListList(NCTools.GetLongss(parameters.get(i++)));

        NCTools.PrintListNode(NCTools.GetListNode(parameters.get(i++)));
        NCTools.PrintListNodeList(NCTools.GetListNodeList(parameters.get(i)));
        NCTools.PrintListNodeList(NCTools.GetListNodes(parameters.get(i++)));
        NCTools.PrintListNodeListList(NCTools.GetListNodeListList(parameters
                .get(i)));
        NCTools.PrintListNodeListList(NCTools.GetListNodess(parameters.get(i++)));

        NCTools.PrintInterval(NCTools.GetInterval(parameters.get(i++)));
        NCTools.PrintIntervalList(NCTools.GetIntervalList(parameters.get(i)));
        NCTools.PrintIntervalList(NCTools.GetIntervals(parameters.get(i++)));
        NCTools.PrintIntervalListList(NCTools.GetIntervalListList(parameters
                .get(i)));
        NCTools.PrintIntervalListList(NCTools.GetIntervalss(parameters.get(i++)));

        NCTools.PrintPoint(NCTools.GetPoint(parameters.get(i++)));
        NCTools.PrintPointList(NCTools.GetPointList(parameters.get(i)));
        NCTools.PrintPointList(NCTools.GetPoints(parameters.get(i++)));
        NCTools.PrintPointListList(NCTools.GetPointListList(parameters.get(i)));
        NCTools.PrintPointListList(NCTools.GetPointss(parameters.get(i++)));

        NCTools.PrintTreeNode(NCTools.GetTreeNode(parameters.get(i++)));
        NCTools.PrintTreeNodeList(NCTools.GetTreeNodeList(parameters.get(i)));
        NCTools.PrintTreeNodeList(NCTools.GetTreeNodes(parameters.get(i++)));
        NCTools.PrintTreeNodeListList(NCTools.GetTreeNodeListList(parameters
                .get(i)));
        NCTools.PrintTreeNodeListList(NCTools.GetTreeNodess(parameters.get(i++)));

        NCTools.PrintTreeLinkNode(NCTools.GetTreeLinkNode(parameters.get(i++)));
        NCTools.PrintTreeLinkNodeList(NCTools.GetTreeLinkNodeList(parameters
                .get(i)));
        NCTools.PrintTreeLinkNodeList(NCTools.GetTreeLinkNodes(parameters
                .get(i++)));
        NCTools.PrintTreeLinkNodeListList(NCTools
                .GetTreeLinkNodeListList(parameters.get(i)));
        NCTools.PrintTreeLinkNodeListList(NCTools.GetTreeLinkNodess(parameters
                .get(i++)));

        NCTools.PrintRandomListNode(NCTools.GetRandomListNode(parameters
                .get(i++)));
        NCTools.PrintRandomListNodeList(NCTools
                .GetRandomListNodeList(parameters.get(i)));
        NCTools.PrintRandomListNodeList(NCTools.GetRandomListNodes(parameters
                .get(i++)));
        NCTools.PrintRandomListNodeListList(NCTools
                .GetRandomListNodeListList(parameters.get(i)));
        NCTools.PrintRandomListNodeListList(NCTools
                .GetRandomListNodess(parameters.get(i++)));
    }

    private static int LEFT = 0;
    private static int RIGHT = 1;

    private static boolean IsBeginRange(char c) {
        return c == '{' || c == '[' || c == '(';
    }

    private static boolean IsEndRange(char c) {
        return c == '}' || c == ']' || c == ')';
    }

    public static ArrayList<String> GetArguments(String line) {
        ArrayList<String> ret = new ArrayList<String>();
        if (line == null) {
            return ret;
        }
        int inrange = 0;
        int pre_index = 0;
        boolean inmao = false;
        for (int i = 0; i < line.length(); ++i) {
            if (IsBeginRange(line.charAt(i)) && !inmao) {
                ++inrange;
            } else if (IsEndRange(line.charAt(i)) && !inmao) {
                --inrange;
            } else if (line.charAt(i) == '\"') {
                inmao = !inmao;
            } else if (line.charAt(i) == ',' && inrange == 0 && !inmao) {
                ret.add(line.substring(pre_index, i));
                pre_index = i + 1;
            }
        }
        ret.add(line.substring(pre_index));
        return ret;
    }

    private static ArrayList<String> GetRangeItems(String str) {
        if (str == null) {
            return new ArrayList<String>();
        }

        int begin = 0;
        while (!IsBeginRange(str.charAt(begin)) && begin < str.length()) {
            ++begin;
        }
        int end = str.length();
        while (!IsEndRange(str.charAt(end - 1)) && end > 1) {
            --end;
        }
        str = str.substring(begin + 1, end - 1);
        return str.trim().length() == 0 ? new ArrayList<String>()
                : GetArguments(str);
    }

    public static int GetInt(String str) {
        try {
            return str == null ? 0 : Integer.parseInt(str.trim());
        } catch (Exception e) {
            return 0;
        }
    }

    public static void PrintInternal(int x) {
        System.out.print(x);
    }

    public static long GetLong(String str) {
        try {
            return str == null ? 0 : Long.parseLong(str.trim());
        } catch (Exception e) {
            return 0;
        }
    }

    public static void PrintInternal(long x) {
        System.out.print(x);
    }

    public static float GetFloat(String str) {
        try {
            return str == null || str.equals("") ? 0 : Float.parseFloat(str.trim());
        } catch (Exception e) {
            return 0.0f;
        }
    }

    public static void PrintInternal(float d) {
        if (Math.abs(d) < 0.0000099999) {
            System.out.print("0.00000");
        } else {
            System.out.print(new DecimalFormat("0.00000").format(d));
        }
    }

    public static double GetDouble(String str) {
        try {
            return str == null || str.equals("") ? 0 : Double.parseDouble(str
                .trim());
        } catch (Exception e) {
            return 0.0;
        }
    }

    public static void PrintInternal(double d) {
        if (Math.abs(d) < 0.0000099999) {
            System.out.print("0.00000");
        } else {
            System.out.print(new DecimalFormat("0.00000").format(d));
        }
    }

    public static String GetString(String str) {
        if (str != null) {
            str = str.trim();
        }
        if (str == null || !str.startsWith("\"") || !str.endsWith("\"")) {
            return str == null ? "" : str;
        }
        return str.substring(1, str.length() - 1);
    }

    public static void PrintInternal(String str) {
        if (str != null) {
            System.out.printf("\"%s\"", str);
        } else {
            System.out.print("null");
        }
    }

    public static char GetChar(String str) {
        return str == null || str.trim().length() == 0 ? '#' : str.trim()
                .charAt(0);
    }

    public static void PrintInternal(char c) {

        System.out.print(c);
    }

    public static boolean GetBoolean(String str) {
        return str == null ? false : str.trim().toLowerCase().equals("true");
    }

    public static void PrintInternal(boolean b) {
        System.out.print(b ? "true" : "false");
    }

    public static Interval GetInterval(String str) {
        int[] items = GetInts(str);
        return items.length == 2 ? new Interval(items[0], items[1])
                : new Interval(0, 0);
    }

    public static void PrintInternal(Interval interval) {
        System.out.printf("[%d,%d]", interval.start, interval.end);
    }

    public static Point GetPoint(String str) {
        int[] items = GetInts(str);
        return items.length == 2 ? new Point(items[0], items[1]) : new Point(0,
                0);
    }

    public static void PrintInternal(Point point) {
        System.out.printf("(%d,%d)", point.x, point.y);
    }

    public static TreeNode GetTreeNode(String str) {
        ArrayList<String> items = GetRangeItems(str);
        if (items.isEmpty()) {
            return null;
        }
        TreeNode[] tree_nodes = new TreeNode[items.size() + 1];
        int current = 0;
        /* 当前遍历节点位置 */
        int current_pos = LEFT;
        int index = 1;
        tree_nodes[0] = new TreeNode(GetInt(items.get(0)));
        for (int i = 1; i < items.size(); ++i) {
            if (items.get(i).trim().equals("#")) {
                if (tree_nodes[current] != null) {
                    if (current_pos == LEFT) {
                        current_pos = RIGHT;
                    } else if (tree_nodes[current + 1] != null) {
                        ++current;
                        current_pos = LEFT;
                    }
                }
            } else {
                tree_nodes[index] = new TreeNode(GetInt(items.get(i)));
                if (current_pos == LEFT) {
                    tree_nodes[current].left = tree_nodes[index];
                    current_pos = RIGHT;
                } else {
                    tree_nodes[current].right = tree_nodes[index];
                    ++current;
                    current_pos = LEFT;
                }
                ++index;
            }
        }

        return tree_nodes[0];
    }

    // public static String getTreeNodePrintString(TreeNode root) {
    //     if (root == null) {
    //         return "{}";
    //     }
    //     StringBuilder temp = new StringBuilder("{");
    //     ArrayList<TreeNode> v = new ArrayList<TreeNode>();
    //     if (root != null) {
    //         v.add(root);
    //     }
    //     int c = 0;
    //     StringBuilder none = new StringBuilder();
    //     while (c < v.size()) {
    //         if (c == 0) {
    //             temp.append(v.get(c).val);
    //             v.add(v.get(c).left);
    //             v.add(v.get(c).right);
    //         } else {
    //             if (v.get(c) == null) {
    //                 none.append(",#");
    //             } else {
    //                 temp.append(none).append(",").append(v.get(c).val);
    //                 none = new StringBuilder();
    //                 v.add(v.get(c).left);
    //                 v.add(v.get(c).right);
    //             }
    //         }
    //         ++c;
    //     }
    //     temp.append("}");
    //     return temp.toString();
    // }

    // public static void PrintInternal(TreeNode root) {
    //     System.out.print(getTreeNodePrintString(root));
    // }

    public static ListNode GetListNode(String str) {
        int[] items = GetInts(str);
        if (items.length == 0) {
            return null;
        }
        ListNode head = new ListNode(items[0]);
        ListNode tail = head;
        for (int i = 1; i < items.length; ++i) {
            tail.next = new ListNode(items[i]);
            tail = tail.next;
        }
        return head;
    }

//    public static String getListNodePrintString(ListNode head) {
//         if (head == null) {
//             return "{}";
//         }
//         ListNode current = head;
//         StringBuilder stringBuilder = new StringBuilder("{");
//         while (current != null) {
//             if (current == head) {
//                 stringBuilder.append(current.val);
//             } else {
//                 stringBuilder.append(",").append(current.val);
//             }
//             current = current.next;
//         }
//         stringBuilder.append("}");
//         return stringBuilder.toString();
//     }

//     public static void PrintInternal(ListNode head) {
//         System.out.print(getListNodePrintString(head));
//     }

    // { -1, 8, 7, -3,4,4,-3,#,#,-1}
    // 分为两段，前部分为ListNode,后半部分如果random==null是#，否则就是random.val
    public static RandomListNode GetRandomListNode(String str) {
        ArrayList<String> items = GetRangeItems(str);
        if (items.size() < 2) {
            return null;
        }

        int count = items.size() / 2;
        // 记录前一半到节点
        RandomListNode[] list_nodes = new RandomListNode[count + 1];

        Map<Integer, RandomListNode> nodes_map = new HashMap<Integer, RandomListNode>();
        RandomListNode head = new RandomListNode(GetInt(items.get(0)));
        nodes_map.put(head.label, head);
        list_nodes[0] = head;
        RandomListNode tail = head;
        for (int i = 1; i < count; ++i) {
            RandomListNode cur = new RandomListNode(GetInt(items.get(i)));
            tail.next = cur;
            tail = cur;
            nodes_map.put(cur.label, cur);
            list_nodes[i] = cur;
        }

        // 遍历后部分到随机节点
        for (int i = count; i < items.size(); ++i) {
            if (!items.get(i).trim().equals("#")
                    && nodes_map.containsKey(GetInt(items.get(i)))) {
                list_nodes[i - count].random = nodes_map.get(GetInt(items
                        .get(i)));
            }
        }
        return head;
    }

    public static void PrintInternal(RandomListNode head) {
        if (head == null) {
            System.out.print("{}");
            return;
        }
        RandomListNode current = head;
        System.out.print("{");
        while (current != null) {
            if (current == head) {
                System.out.print(current.label);
            } else {
                System.out.printf(",%d", current.label);
            }
            current = current.next;
        }
        current = head;
        while (current != null) {
            if (current.random != null) {
                System.out.printf(",%d", current.random.label);
            } else {
                System.out.print(",#");
            }
            current = current.next;
        }
        System.out.print("}");
    }

    /*
     * 二叉链接树序列化是通过按层遍历,#代表这这个节点为空节点,节点遍历以后再增加所有next节点数据,举个例子 1.null / \ 2
     * .3.null / 4.null 5.null
     * 
     * 以上二叉树会被序列化为 {[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}
     * 对于{[1,2,3,#,#,4,#,#,5],[#,5,#,#,#]}构造出来的链接树节点2的next指向5节点
     */
    public static TreeLinkNode GetTreeLinkNode(String str) {
        ArrayList<String> all_items = GetRangeItems(str);
		// 老版本只有{1,3,34}这种格式
		boolean is_newversion = all_items.size() == 2 && all_items.get(0).charAt(0) == '[' && all_items.get(1).charAt(0) == '[';
		if (!is_newversion) {
		    all_items.clear();
		    all_items.add(str);
		    all_items.add("[]");
		}
        if (all_items.size() < 2) {
            return null;
        }
        ArrayList<String> items = GetRangeItems(all_items.get(0));
        if (items.size() == 0) {
            return null;
        }

        TreeLinkNode[] tree_nodes = new TreeLinkNode[items.size() + 1];
        Map<Integer, TreeLinkNode> map_nodes = new HashMap<Integer, TreeLinkNode>();
        int current = 0;
        /* 当前遍历节点位置 */
        int current_pos = LEFT;
        int index = 1;
        tree_nodes[0] = new TreeLinkNode(GetInt(items.get(0)));
        for (int i = 1; i < items.size(); ++i) {
            if (items.get(i).trim().equals("#")) {
                if (tree_nodes[current] != null) {
                    if (current_pos == LEFT) {
                        current_pos = RIGHT;
                    } else if (tree_nodes[current + 1] != null) {
                        ++current;
                        current_pos = LEFT;
                    }
                }
            } else {
                int label = GetInt(items.get(i));
                tree_nodes[index] = new TreeLinkNode(label);
                map_nodes.put(label, tree_nodes[index]);
                if (current_pos == LEFT) {
                    tree_nodes[current].left = tree_nodes[index];
                    current_pos = RIGHT;
                } else {
                    tree_nodes[current].right = tree_nodes[index];
                    ++current;
                    current_pos = LEFT;
                }
                ++index;
            }
        }

        // 连接next指针
        items = GetRangeItems(all_items.get(1));
        for (int i = 0; i < items.size(); ++i) {
            if (!items.get(i).trim().equals("#")
                    && map_nodes.containsKey(GetInt(items.get(i)))) {
                tree_nodes[i].next = tree_nodes[GetInt(items.get(i))];
            }
        }

        return tree_nodes[0];
    }

    public static void PrintInternal(TreeLinkNode root) {
        if (root == null) {
            System.out.print("{}");
            return;
        }
        System.out.print("{[");
        ArrayList<TreeLinkNode> v = new ArrayList<TreeLinkNode>();
        ArrayList<TreeLinkNode> label_node_v = new ArrayList<TreeLinkNode>();
        if (root != null) {
            v.add(root);
            label_node_v.add(root);
        }
        int c = 0;
        String none = "";
        while (c < v.size()) {
            if (c == 0) {
                System.out.print(v.get(c).val);
                v.add(v.get(c).left);
                v.add(v.get(c).right);
            } else {
                if (v.get(c) == null) {
                    none = none + ",#";
                } else {
                    label_node_v.add(v.get(c));
                    System.out.printf("%s,%d", none, v.get(c).val);
                    none = "";
                    v.add(v.get(c).left);
                    v.add(v.get(c).right);
                }
            }
            ++c;
        }
        v.clear();
        System.out.print("],[");
        for (int i = 0; i < label_node_v.size(); ++i) {
            if (i != 0) {
                System.out.print(",");
            }
            if (label_node_v.get(i).next != null) {
                System.out.print(label_node_v.get(i).next.val);
            } else {
                System.out.print("#");
            }
        }
        System.out.print("]}");
    }

    /**
     * 无向图里每个节点都有一个唯一的数字ID,每个节点的序列化通过[]保存,每个节点第一个元素后跟随的是这个节点连接的其他节点,以下图 1 / \ /
     * \ 0 --- 2 / \ \_/ 序列化后为{[0,1,2],[1,2],[2,2]}
     */
    public static UndirectedGraphNode GetUndirectedGraphNode(String str) {
        int[][] points = GetIntss(str);

        UndirectedGraphNode ret = null;
        Map<Integer, UndirectedGraphNode> nodes_map = new HashMap<Integer, UndirectedGraphNode>();

        // 把所有的点构造出来
        for (int i = 0; i < points.length; ++i) {
            int[] v = points[i];
            if (v.length == 0) {
                continue;
            }
            if (!nodes_map.containsKey(v[0])) {
                UndirectedGraphNode node = new UndirectedGraphNode(v[0]);
                nodes_map.put(v[0], node);
                if (ret == null) {
                    ret = node;
                }
            }
        }

        // 把各个边连接起来
        for (int i = 0; i < points.length; ++i) {
            int[] v = points[i];
            if (v.length == 0) {
                continue;
            }
            UndirectedGraphNode node = nodes_map.get(v[0]);
            for (int j = 1; j < v.length; ++j) {
                node.neighbors.add(nodes_map.get(v[j]));
            }
        }
        return ret;
    }

    public static void PrintInternal(UndirectedGraphNode root) {
        if (root == null) {
            System.out.print("{}");
            return;
        }
        System.out.print("{");
        if (root != null) {
            HashSet<UndirectedGraphNode> nodes_set = new HashSet<UndirectedGraphNode>();
            Map<Integer, UndirectedGraphNode> nodes_map = new HashMap<Integer, UndirectedGraphNode>();
            ArrayList<UndirectedGraphNode> nodes = new ArrayList<UndirectedGraphNode>();
            nodes.add(root);
            nodes_set.add(root);
            nodes_map.put(root.label, root);
            for (int i = 0; i < nodes.size(); ++i) {
                for (int j = 0; j < nodes.get(i).neighbors.size(); ++j) {
                    UndirectedGraphNode n_node = nodes.get(i).neighbors.get(j);
                    if (!nodes_set.contains(n_node)) {
                        nodes_set.add(n_node);
                        nodes.add(n_node);
                        nodes_map.put(n_node.label, n_node);
                    }
                }
            }

            // 根据label从小到大打印
            for (UndirectedGraphNode node : nodes_map.values()) {
                if (node != nodes.get(0)) {// 不是第一个节点
                    System.out.printf(",[%d", node.label);
                } else {
                    System.out.printf("[%d", node.label);
                }
                for (int j = 0; j < node.neighbors.size(); ++j) {
                    System.out.printf(",%d", node.neighbors.get(j).label);
                }
                System.out.print("]");
            }
        }
        System.out.print("}");
    }

    public static HashSet<Integer> GetIntSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<Integer> ret = new HashSet<Integer>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetInt(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<Integer> GetIntList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<Integer> ret = new ArrayList<Integer>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetInt(items.get(i)));
        }
        return ret;
    }

    public static int[] GetInts(String str) {
        ArrayList<String> items = GetRangeItems(str);
        int[] ret = new int[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetInt(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<Integer>> GetIntListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<Integer>> ret = new ArrayList<ArrayList<Integer>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetIntList(items.get(i)));
        }
        return ret;
    }

    public static int[][] GetIntss(String str) {
        ArrayList<String> items = GetRangeItems(str);
        int[][] ret = new int[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetInts(items.get(i));
        }
        return ret;
    }

    public static void PrintInt(int x) {
        System.out.println(x);
    }

    public static String getIntListPrintString(ArrayList<Integer> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(",");
            }
            stringBuilder.append(x.get(i));
        }
        stringBuilder.append("]");
        return stringBuilder.toString();
    }

    public static void PrintIntList(ArrayList<Integer> x) {
        System.out.println(getIntListPrintString(x));
    }

    public static void PrintIntListList(ArrayList<ArrayList<Integer>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(",");
            }
            stringBuilder.append(getIntListPrintString(x.get(i)));
        }
        stringBuilder.append("]");
        System.out.println(stringBuilder.toString());
    }

    public static String getIntsPrintString(int[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(",");
            }
            stringBuilder.append(x[i]);
        }
        stringBuilder.append("]");
        return stringBuilder.toString();
    }

    public static void PrintIntList(int[] x) {
        System.out.println(getIntsPrintString(x));
    }

    public static void PrintIntListList(int[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getIntsPrintString(x[i]));
        }
        stringBuilder.append("]");
        System.out.println(stringBuilder.toString());
    }

    public static HashSet<Long> GetLongSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<Long> ret = new HashSet<Long>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetLong(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<Long> GetLongList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<Long> ret = new ArrayList<Long>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetLong(items.get(i)));
        }
        return ret;
    }

    public static long[] GetLongs(String str) {
        ArrayList<String> items = GetRangeItems(str);
        long[] ret = new long[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetLong(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<Long>> GetLongListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<Long>> ret = new ArrayList<ArrayList<Long>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetLongList(items.get(i)));
        }
        return ret;
    }

    public static long[][] GetLongss(String str) {
        ArrayList<String> items = GetRangeItems(str);
        long[][] ret = new long[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetLongs(items.get(i));
        }
        return ret;
    }

    public static void PrintLong(long x) {
        System.out.println(x);
    }

    public static String getLongListPrintString(ArrayList<Long> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(x.get(i));
        }
        stringBuilder.append("]");
        return stringBuilder.toString();
    }

    public static void PrintLongList(ArrayList<Long> x) {
        System.out.println(getLongListPrintString(x));
    }

    public static void PrintLongListList(ArrayList<ArrayList<Long>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");

        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getLongListPrintString(x.get(i)));
        }
        stringBuilder.append("]");
        System.out.println(stringBuilder.toString());
    }

    public static String getLongsPrintString(long[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(x[i]);
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintLongList(long[] x) {
        System.out.println(getLongsPrintString(x));
    }

    public static void PrintLongListList(long[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getLongsPrintString(x[i]));
        }
        stringBuilder.append("]");
        System.out.println(stringBuilder.toString());
    }

    public static HashSet<Float> GetFloatSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<Float> ret = new HashSet<Float>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetFloat(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<Float> GetFloatList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<Float> ret = new ArrayList<Float>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetFloat(items.get(i)));
        }
        return ret;
    }

    public static float[] GetFloats(String str) {
        ArrayList<String> items = GetRangeItems(str);
        float[] ret = new float[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetFloat(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<Float>> GetFloatListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<Float>> ret = new ArrayList<ArrayList<Float>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetFloatList(items.get(i)));
        }
        return ret;
    }

    public static float[][] GetFloatss(String str) {
        ArrayList<String> items = GetRangeItems(str);
        float[][] ret = new float[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetFloats(items.get(i));
        }
        return ret;
    }

   public static String getFloatPrintString(float x) {
        if (Math.abs(x) < 0.0000099999) {
            return "0.00000";
        } else {
            return new DecimalFormat("0.00000").format(x);
        }
    }

    public static void PrintFloat(float x) {
        System.out.println(getFloatPrintString(x));
    }

    public static String getFloatListPrintString(ArrayList<Float> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getFloatPrintString(x.get(i)));

        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintFloatList(ArrayList<Float> x) {
        System.out.println(getFloatListPrintString(x));
    }

    public static void PrintFloatListList(ArrayList<ArrayList<Float>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getFloatListPrintString(x.get(i)));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }



    public static String getFloatsPrintString(float[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getFloatPrintString(x[i]));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }


    public static void PrintFloatList(float[] x) {
        System.out.println(getFloatsPrintString(x));
    }

    public static void PrintFloatListList(float[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getFloatsPrintString(x[i]));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }


    public static HashSet<Double> GetDoubleSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<Double> ret = new HashSet<Double>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetDouble(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<Double> GetDoubleList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<Double> ret = new ArrayList<Double>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetDouble(items.get(i)));
        }
        return ret;
    }

    public static double[] GetDoubles(String str) {
        ArrayList<String> items = GetRangeItems(str);
        double[] ret = new double[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetDouble(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<Double>> GetDoubleListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<Double>> ret = new ArrayList<ArrayList<Double>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetDoubleList(items.get(i)));
        }
        return ret;
    }

    public static double[][] GetDoubless(String str) {
        ArrayList<String> items = GetRangeItems(str);
        double[][] ret = new double[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetDoubles(items.get(i));
        }
        return ret;
    }

    public static String getDoublePrintString(double x) {
        if (Math.abs(x) < 0.0000099999) {
            return "0.00000";
        } else {
            return new DecimalFormat("0.00000").format(x);
        }
    }

    public static void PrintDouble(double x) {
        System.out.println(getDoublePrintString(x));
    }

    public static String getDoubleListPrintString(ArrayList<Double> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getDoublePrintString(x.get(i)));

        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintDoubleList(ArrayList<Double> x) {
        System.out.println(getDoubleListPrintString(x));
    }

    public static void PrintDoubleListList(ArrayList<ArrayList<Double>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getDoubleListPrintString(x.get(i)));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }

    public static String getDoublesPrintString(double[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getDoublePrintString(x[i]));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintDoubleList(double[] x) {
        System.out.println(getDoublesPrintString(x));
    }

    public static void PrintDoubleListList(double[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getDoublesPrintString(x[i]));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }

    public static HashSet<Character> GetCharSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<Character> ret = new HashSet<Character>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetChar(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<Character> GetCharList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<Character> ret = new ArrayList<Character>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetChar(items.get(i)));
        }
        return ret;
    }

    public static char[] GetChars(String str) {
        ArrayList<String> items = GetRangeItems(str);
        char[] ret = new char[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetChar(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<Character>> GetCharListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<Character>> ret = new ArrayList<ArrayList<Character>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetCharList(items.get(i)));
        }
        return ret;
    }

    public static char[][] GetCharss(String str) {
        ArrayList<String> items = GetRangeItems(str);
        char[][] ret = new char[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetChars(items.get(i));
        }
        return ret;
    }

    public static void PrintChar(char x) {
        System.out.println(x);
    }

    public static String getCharListPrintString(ArrayList<Character> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(x.get(i));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintCharList(ArrayList<Character> x) {
        System.out.println(getCharListPrintString(x));
    }

    public static void PrintCharListList(ArrayList<ArrayList<Character>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getCharListPrintString(x.get(i)));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }


    public static String getCharsPrintString(char[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(x[i]);
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }


    public static void PrintCharList(char[] x) {
        System.out.println(getCharsPrintString(x));
    }

    public static void PrintCharListList(char[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getCharsPrintString(x[i]));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }


    public static HashSet<Boolean> GetBooleanSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<Boolean> ret = new HashSet<Boolean>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetBoolean(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<Boolean> GetBooleanList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<Boolean> ret = new ArrayList<Boolean>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetBoolean(items.get(i)));
        }
        return ret;
    }

    public static boolean[] GetBooleans(String str) {
        ArrayList<String> items = GetRangeItems(str);
        boolean[] ret = new boolean[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetBoolean(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<Boolean>> GetBooleanListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<Boolean>> ret = new ArrayList<ArrayList<Boolean>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetBooleanList(items.get(i)));
        }
        return ret;
    }

    public static boolean[][] GetBooleanss(String str) {
        ArrayList<String> items = GetRangeItems(str);
        boolean[][] ret = new boolean[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetBooleans(items.get(i));
        }
        return ret;
    }

    public static void PrintBoolean(boolean x) {
        System.out.println(x ? "true" : "false");
    }

    public static String getBooleanListPrintString(ArrayList<Boolean> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(x.get(i));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintBooleanList(ArrayList<Boolean> x) {
        System.out.println(getBooleanListPrintString(x));
    }

    public static void PrintBooleanListList(ArrayList<ArrayList<Boolean>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getBooleanListPrintString(x.get(i)));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }

    public static String getBooleansPrintString(boolean[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(x[i]);
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintBooleanList(boolean[] x) {
        System.out.println(getBooleansPrintString(x));
    }

    public static void PrintBooleanListList(boolean[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getBooleansPrintString(x[i]));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }


    public static HashSet<String> GetStringSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<String> ret = new HashSet<String>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetString(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<String> GetStringList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<String> ret = new ArrayList<String>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetString(items.get(i)));
        }
        return ret;
    }

    public static String[] GetStrings(String str) {
        ArrayList<String> items = GetRangeItems(str);
        String[] ret = new String[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetString(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<String>> GetStringListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<String>> ret = new ArrayList<ArrayList<String>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetStringList(items.get(i)));
        }
        return ret;
    }

    public static String[][] GetStringss(String str) {
        ArrayList<String> items = GetRangeItems(str);
        String[][] ret = new String[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetStrings(items.get(i));
        }
        return ret;
    }

      public static String getStringPrint(String str) {
        if (str != null) {
            return "\"" + str + "\"";
        } else {
            return "null";
        }
    }
    
    public static String getStringListPrint(ArrayList<String> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getStringPrint(x.get(i)));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintString(String x) {
        System.out.println(getStringPrint(x));
    }

    public static void PrintStringList(ArrayList<String> x) {
        System.out.println(getStringListPrint(x));
    }

    public static void PrintStringListList(ArrayList<ArrayList<String>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getStringListPrint(x.get(i)));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }


     public static String getStringsPrint(String[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getStringPrint(x[i]));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }


    public static void PrintStringList(String[] x) {
        System.out.println(getStringsPrint(x));
    }

    public static void PrintStringListList(String[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getStringsPrint(x[i]));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }

    public static HashSet<Interval> GetIntervalSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<Interval> ret = new HashSet<Interval>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetInterval(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<Interval> GetIntervalList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<Interval> ret = new ArrayList<Interval>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetInterval(items.get(i)));
        }
        return ret;
    }

    public static Interval[] GetIntervals(String str) {
        ArrayList<String> items = GetRangeItems(str);
        Interval[] ret = new Interval[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetInterval(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<Interval>> GetIntervalListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<Interval>> ret = new ArrayList<ArrayList<Interval>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetIntervalList(items.get(i)));
        }
        return ret;
    }

    public static Interval[][] GetIntervalss(String str) {
        ArrayList<String> items = GetRangeItems(str);
        Interval[][] ret = new Interval[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetIntervals(items.get(i));
        }
        return ret;
    }

    public static String getIntervalPrintString(Interval interval) {
        return "[" + interval.start + "," + interval.end + "]";
    }

    public static void PrintInterval(Interval x) {
        System.out.println(getIntervalPrintString(x));
    }

    public static String getIntervalListPrintString(ArrayList<Interval> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getIntervalPrintString(x.get(i)));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintIntervalList(ArrayList<Interval> x) {
        System.out.println(getIntervalListPrintString(x));
    }

    public static void PrintIntervalListList(ArrayList<ArrayList<Interval>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getIntervalListPrintString(x.get(i)));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }
    

    public static String getIntervalsPrintString(Interval[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getIntervalPrintString(x[i]));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }


    public static void PrintIntervalList(Interval[] x) {
        System.out.println(getIntervalsPrintString(x));
    }

    public static void PrintIntervalListList(Interval[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getIntervalsPrintString(x[i]));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }

    public static HashSet<Point> GetPointSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<Point> ret = new HashSet<Point>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetPoint(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<Point> GetPointList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<Point> ret = new ArrayList<Point>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetPoint(items.get(i)));
        }
        return ret;
    }

    public static Point[] GetPoints(String str) {
        ArrayList<String> items = GetRangeItems(str);
        Point[] ret = new Point[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetPoint(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<Point>> GetPointListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<Point>> ret = new ArrayList<ArrayList<Point>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetPointList(items.get(i)));
        }
        return ret;
    }

    public static Point[][] GetPointss(String str) {
        ArrayList<String> items = GetRangeItems(str);
        Point[][] ret = new Point[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetPoints(items.get(i));
        }
        return ret;
    }

     public static String getPointPrintString(Point point) {
        return "(" + point.x + "," + point.y + ")";
    }

    public static void PrintPoint(Point x) {
        System.out.println(getPointPrintString(x));
    }

    public static String getPointListPrintString(ArrayList<Point> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getPointPrintString(x.get(i)));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintPointList(ArrayList<Point> x) {
        System.out.println(getPointListPrintString(x));
    }

    public static void PrintPointListList(ArrayList<ArrayList<Point>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getPointListPrintString(x.get(i)));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }


    public static String getPointsPrintString(Point[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getPointPrintString(x[i]));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }


    public static void PrintPointList(Point[] x) {
        System.out.println(getPointsPrintString(x));
    }

    public static void PrintPointListList(Point[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getPointsPrintString(x[i]));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }


    public static HashSet<UndirectedGraphNode> GetUndirectedGraphNodeSet(
            String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<UndirectedGraphNode> ret = new HashSet<UndirectedGraphNode>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetUndirectedGraphNode(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<UndirectedGraphNode> GetUndirectedGraphNodeList(
            String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<UndirectedGraphNode> ret = new ArrayList<UndirectedGraphNode>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetUndirectedGraphNode(items.get(i)));
        }
        return ret;
    }

    public static UndirectedGraphNode[] GetUndirectedGraphNodes(String str) {
        ArrayList<String> items = GetRangeItems(str);
        UndirectedGraphNode[] ret = new UndirectedGraphNode[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetUndirectedGraphNode(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<UndirectedGraphNode>> GetUndirectedGraphNodeListList(
            String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<UndirectedGraphNode>> ret = new ArrayList<ArrayList<UndirectedGraphNode>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetUndirectedGraphNodeList(items.get(i)));
        }
        return ret;
    }

    public static UndirectedGraphNode[][] GetUndirectedGraphNodess(String str) {
        ArrayList<String> items = GetRangeItems(str);
        UndirectedGraphNode[][] ret = new UndirectedGraphNode[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetUndirectedGraphNodes(items.get(i));
        }
        return ret;
    }

    private static void PrintUndirectedGraphNodeListInternal(
            ArrayList<UndirectedGraphNode> x) {
        System.out.print('[');
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintInternal(x.get(i));
        }
        System.out.print(']');
    }

    public static void PrintUndirectedGraphNode(UndirectedGraphNode x) {
        PrintInternal(x);
        System.out.print('\n');
    }

    public static void PrintUndirectedGraphNodeList(
            ArrayList<UndirectedGraphNode> x) {
        PrintUndirectedGraphNodeListInternal(x);
        System.out.print('\n');
    }

    public static void PrintUndirectedGraphNodeListList(
            ArrayList<ArrayList<UndirectedGraphNode>> x) {
        System.out.print('[');
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintUndirectedGraphNodeListInternal(x.get(i));
        }
        System.out.print("]\n");
    }

    private static void PrintUndirectedGraphNodeListInternal(
            UndirectedGraphNode[] x) {
        System.out.print('[');
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintInternal(x[i]);
        }
        System.out.print(']');
    }

    public static void PrintUndirectedGraphNodeList(UndirectedGraphNode[] x) {
        PrintUndirectedGraphNodeListInternal(x);
        System.out.print('\n');
    }

    public static void PrintUndirectedGraphNodeListList(
            UndirectedGraphNode[][] x) {
        System.out.print('[');
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintUndirectedGraphNodeListInternal(x[i]);
        }
        System.out.print("]\n");
    }

    public static HashSet<ListNode> GetListNodeSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<ListNode> ret = new HashSet<ListNode>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetListNode(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<ListNode> GetListNodeList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ListNode> ret = new ArrayList<ListNode>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetListNode(items.get(i)));
        }
        return ret;
    }

    public static ListNode[] GetListNodes(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ListNode[] ret = new ListNode[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetListNode(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<ListNode>> GetListNodeListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<ListNode>> ret = new ArrayList<ArrayList<ListNode>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetListNodeList(items.get(i)));
        }
        return ret;
    }

    public static ListNode[][] GetListNodess(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ListNode[][] ret = new ListNode[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetListNodes(items.get(i));
        }
        return ret;
    }

     public static String getListNodePrintString(ListNode head) {
        if (head == null) {
            return "{}";
        }
        ListNode current = head;
        StringBuilder stringBuilder = new StringBuilder("{");
        while (current != null) {
            if (current == head) {
                stringBuilder.append(current.val);
            } else {
                stringBuilder.append(",").append(current.val);
            }
            current = current.next;
        }
        stringBuilder.append("}");
        return stringBuilder.toString();
    }

    public static String getListNodeListPrintString(ArrayList<ListNode> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getListNodePrintString(x.get(i)));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }


    public static void PrintListNode(ListNode x) {
        System.out.println(getListNodePrintString(x));
    }

    public static void PrintListNodeList(ArrayList<ListNode> x) {
        System.out.println(getListNodeListPrintString(x));
    }

    public static void PrintListNodeListList(ArrayList<ArrayList<ListNode>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getListNodeListPrintString(x.get(i)));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }


    public static String getListNodesPrintString(ListNode[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getListNodePrintString(x[i]));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintListNodeList(ListNode[] x) {
        System.out.println(getListNodesPrintString(x));
    }

    public static void PrintListNodeListList(ListNode[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getListNodesPrintString(x[i]));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }


    public static HashSet<RandomListNode> GetRandomListNodeSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<RandomListNode> ret = new HashSet<RandomListNode>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetRandomListNode(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<RandomListNode> GetRandomListNodeList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<RandomListNode> ret = new ArrayList<RandomListNode>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetRandomListNode(items.get(i)));
        }
        return ret;
    }

    public static RandomListNode[] GetRandomListNodes(String str) {
        ArrayList<String> items = GetRangeItems(str);
        RandomListNode[] ret = new RandomListNode[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetRandomListNode(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<RandomListNode>> GetRandomListNodeListList(
            String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<RandomListNode>> ret = new ArrayList<ArrayList<RandomListNode>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetRandomListNodeList(items.get(i)));
        }
        return ret;
    }

    public static RandomListNode[][] GetRandomListNodess(String str) {
        ArrayList<String> items = GetRangeItems(str);
        RandomListNode[][] ret = new RandomListNode[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetRandomListNodes(items.get(i));
        }
        return ret;
    }

    private static void PrintRandomListNodeListInternal(
            ArrayList<RandomListNode> x) {
        System.out.print('[');
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintInternal(x.get(i));
        }
        System.out.print(']');
    }

    public static void PrintRandomListNode(RandomListNode x) {
        PrintInternal(x);
        System.out.print('\n');
    }

    public static void PrintRandomListNodeList(ArrayList<RandomListNode> x) {
        PrintRandomListNodeListInternal(x);
        System.out.print('\n');
    }

    public static void PrintRandomListNodeListList(
            ArrayList<ArrayList<RandomListNode>> x) {
        System.out.print('[');
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintRandomListNodeListInternal(x.get(i));
        }
        System.out.print("]\n");
    }

    private static void PrintRandomListNodeListInternal(RandomListNode[] x) {
        System.out.print('[');
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintInternal(x[i]);
        }
        System.out.print(']');
    }

    public static void PrintRandomListNodeList(RandomListNode[] x) {
        PrintRandomListNodeListInternal(x);
        System.out.print('\n');
    }

    public static void PrintRandomListNodeListList(RandomListNode[][] x) {
        System.out.print('[');
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintRandomListNodeListInternal(x[i]);
        }
        System.out.print("]\n");
    }

    public static HashSet<TreeNode> GetTreeNodeSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<TreeNode> ret = new HashSet<TreeNode>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetTreeNode(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<TreeNode> GetTreeNodeList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<TreeNode> ret = new ArrayList<TreeNode>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetTreeNode(items.get(i)));
        }
        return ret;
    }

    public static TreeNode[] GetTreeNodes(String str) {
        ArrayList<String> items = GetRangeItems(str);
        TreeNode[] ret = new TreeNode[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetTreeNode(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<TreeNode>> GetTreeNodeListList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<TreeNode>> ret = new ArrayList<ArrayList<TreeNode>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetTreeNodeList(items.get(i)));
        }
        return ret;
    }

    public static TreeNode[][] GetTreeNodess(String str) {
        ArrayList<String> items = GetRangeItems(str);
        TreeNode[][] ret = new TreeNode[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetTreeNodes(items.get(i));
        }
        return ret;
    }

   public static String getTreeNodePrintString(TreeNode root) {
        if (root == null) {
            return "{}";
        }
        StringBuilder temp = new StringBuilder("{");
        ArrayList<TreeNode> v = new ArrayList<TreeNode>();
        if (root != null) {
            v.add(root);
        }
        int c = 0;
        StringBuilder none = new StringBuilder();
        while (c < v.size()) {
            if (c == 0) {
                temp.append(v.get(c).val);
                v.add(v.get(c).left);
                v.add(v.get(c).right);
            } else {
                if (v.get(c) == null) {
                    none.append(",#");
                } else {
                    temp.append(none).append(",").append(v.get(c).val);
                    none = new StringBuilder();
                    v.add(v.get(c).left);
                    v.add(v.get(c).right);
                }
            }
            ++c;
        }
        temp.append("}");
        return temp.toString();
    }

    public static String getTreeNodeListPrintString(ArrayList<TreeNode> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getTreeNodePrintString(x.get(i)));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }

    public static void PrintTreeNode(TreeNode x) {
        System.out.println(getTreeNodePrintString(x));
    }

    public static void PrintTreeNodeList(ArrayList<TreeNode> x) {
        System.out.println(getTreeNodeListPrintString(x));
    }

    public static void PrintTreeNodeListList(ArrayList<ArrayList<TreeNode>> x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getTreeNodeListPrintString(x.get(i)));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }

    public static String getTreeNodesPrintString(TreeNode[] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getTreeNodePrintString(x[i]));
        }
        stringBuilder.append(']');
        return stringBuilder.toString();
    }


    public static void PrintTreeNodeList(TreeNode[] x) {
        System.out.println(getTreeNodesPrintString(x));
    }

    public static void PrintTreeNodeListList(TreeNode[][] x) {
        StringBuilder stringBuilder = new StringBuilder("[");
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                stringBuilder.append(',');
            }
            stringBuilder.append(getTreeNodesPrintString(x[i]));
        }
        stringBuilder.append(']');
        System.out.println(stringBuilder.toString());
    }

    public static HashSet<TreeLinkNode> GetTreeLinkNodeSet(String str) {
        ArrayList<String> items = GetRangeItems(str);
        HashSet<TreeLinkNode> ret = new HashSet<TreeLinkNode>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetTreeLinkNode(items.get(i)));
        }
        return ret;
    }

    public static ArrayList<TreeLinkNode> GetTreeLinkNodeList(String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<TreeLinkNode> ret = new ArrayList<TreeLinkNode>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetTreeLinkNode(items.get(i)));
        }
        return ret;
    }

    public static TreeLinkNode[] GetTreeLinkNodes(String str) {
        ArrayList<String> items = GetRangeItems(str);
        TreeLinkNode[] ret = new TreeLinkNode[items.size()];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetTreeLinkNode(items.get(i));
        }
        return ret;
    }

    public static ArrayList<ArrayList<TreeLinkNode>> GetTreeLinkNodeListList(
            String str) {
        ArrayList<String> items = GetRangeItems(str);
        ArrayList<ArrayList<TreeLinkNode>> ret = new ArrayList<ArrayList<TreeLinkNode>>();
        for (int i = 0; i < items.size(); ++i) {
            ret.add(GetTreeLinkNodeList(items.get(i)));
        }
        return ret;
    }

    public static TreeLinkNode[][] GetTreeLinkNodess(String str) {
        ArrayList<String> items = GetRangeItems(str);
        TreeLinkNode[][] ret = new TreeLinkNode[items.size()][];
        for (int i = 0; i < items.size(); ++i) {
            ret[i] = GetTreeLinkNodes(items.get(i));
        }
        return ret;
    }

    private static void PrintTreeLinkNodeListInternal(ArrayList<TreeLinkNode> x) {
        System.out.print('[');
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintInternal(x.get(i));
        }
        System.out.print(']');
    }

    public static void PrintTreeLinkNode(TreeLinkNode x) {
        PrintInternal(x);
        System.out.print('\n');
    }

    public static void PrintTreeLinkNodeList(ArrayList<TreeLinkNode> x) {
        PrintTreeLinkNodeListInternal(x);
        System.out.print('\n');
    }

    public static void PrintTreeLinkNodeListList(
            ArrayList<ArrayList<TreeLinkNode>> x) {
        System.out.print('[');
        for (int i = 0; i < x.size(); ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintTreeLinkNodeListInternal(x.get(i));
        }
        System.out.print("]\n");
    }

    private static void PrintTreeLinkNodeListInternal(TreeLinkNode[] x) {
        System.out.print('[');
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintInternal(x[i]);
        }
        System.out.print(']');
    }

    public static void PrintTreeLinkNodeList(TreeLinkNode[] x) {
        PrintTreeLinkNodeListInternal(x);
        System.out.print('\n');
    }

    public static void PrintTreeLinkNodeListList(TreeLinkNode[][] x) {
        System.out.print('[');
        for (int i = 0; i < x.length; ++i) {
            if (i != 0) {
                System.out.print(',');
            }
            PrintTreeLinkNodeListInternal(x[i]);
        }
        System.out.print("]\n");
    }

}
