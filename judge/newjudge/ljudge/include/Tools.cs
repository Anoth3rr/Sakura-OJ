using System.Collections.Generic;
using System;

public class TreeLinkNode
{
    public int val;
    public TreeLinkNode left;
    public TreeLinkNode right;
    public TreeLinkNode next;
    public TreeLinkNode(int x) { val = x; }
}

public class UndirectedGraphNode
{
    public int label;
    public IList<UndirectedGraphNode> neighbors;
    public UndirectedGraphNode(int x) { label = x; neighbors = new List<UndirectedGraphNode>(); }
}

public class RandomListNode
{
    public int label;
    public RandomListNode next, random;
    public RandomListNode(int x) { this.label = x; }
}

public class Interval
{
    public int start;
    public int end;
    public Interval() { start = 0; end = 0; }
    public Interval(int s, int e) { start = s; end = e; }
}

public class TreeNode
{
    public int val;
    public TreeNode left;
    public TreeNode right;
    public TreeNode(int x) { val = x; }
}

public class Point
{
    public int x;
    public int y;
    public Point() { x = 0; y = 0; }
    public Point(int a, int b) { x = a; y = b; }
}

public class ListNode
{
    public int val;
    public ListNode next;
    public ListNode(int x) { val = x; }
}

public class Tools
{
    private static string SubString(string str, int start, int end)
    {
        return SubString(str, start, end - start);
    }
    private static string SubString(string str, int start)
    {
        return SubString(str, start);
    }
    private static bool IsBeginRange(char c)
    {
        return c == '{' || c == '[' || c == '(';
    }

    private static bool IsEndRange(char c)
    {
        return c == '}' || c == ']' || c == ')';
    }

    private static bool IsValidRange(string str)
    {
        return IsBeginRange(str[0]) && IsEndRange(str[str.Length - 1]);
    }

    private static bool IsEmptyRange(string str)
    {
        return str == null || str.Equals("[]") || str.Equals("()") || str.Equals("{}");
    }

    public static List<string> GetArguments(string line, int arg_count)
    {
        List<string> ret = new List<string>();
        if (line == null)
        {
            return ret;
        }
        int inrange = 0;
        int pre_index = 0;
        bool inmao = false;
        for (int i = 0; i < line.Length; ++i)
        {
            if (IsBeginRange(line[i]))
            {
                ++inrange;
            }
            else if (IsEndRange(line[i]))
            {
                --inrange;
            }
            else if (line[i] == '\"')
            {
                inmao = !inmao;
            }
            else if (line[i] == ',' && inrange == 0 && !inmao)
            {
                ret.Add(SubString(line, pre_index, i));
                pre_index = i + 1;
            }
        }
        ret.Add(SubString(line, pre_index));
        return ret;
    }

    // [[1,2],[3,4],[5,6]]
    public static List<Interval> GetArrayListInterval(string str)
    {
        List<Interval> ret = new List<Interval>();
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret;
        }

        str = SubString(str, 1, str.Length - 1);
        int inrange = 0;
        int pre_index = 0;
        for (int i = 0; i < str.Length; ++i)
        {
            if (IsBeginRange(str[i]))
            {
                ++inrange;
            }
            else if (IsEndRange(str[i]))
            {
                --inrange;
            }
            else if (str[i] == ',' && inrange == 0)
            {
                ret.Add(GetInterval(SubString(str, pre_index, i)));
                pre_index = i + 1;
            }
        }
        ret.Add(GetInterval(SubString(str, pre_index)));
        return ret;
    }

    // "abc", abc
    public static string GetString(string str)
    {
        if (str != null)
        {
            str = str.Trim();
        }
        if (str == null || !str.StartsWith("\"") || !str.EndsWith("\""))
        {
            return str == null ? "" : str;
        }
        return SubString(str, 1, str.Length - 1);
    }

    // char
    public static char GetChar(string str)
    {
        return str == null || str.Length == 0 ? '#' : str[0];
    }

    // 1
    public static int GetInt(string str)
    {
        return Int32.Parse(str.Trim());
    }

    // 1
    public static Int64 GetLong(string str)
    {
        return Int64.Parse(str.Trim());
    }

    // [1,3] (1,3)
    public static Interval GetInterval(string str)
    {
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str))
        {
            return null;
        }
        str = SubString(str, 1, str.Length - 1);
        string[] v = str.Split(',');
        if (v.Length != 2)
        {
            return null;
        }
        return new Interval(GetInt(v[0]), GetInt(v[1]));
    }

    // ["a","b","ccc"]
    public static string[] GetStrings(string str)
    {
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return new string[0];
        }

        str = SubString(str, 1, str.Length - 1);
        List<string> ret = new List<string>();
        bool inrange = false;
        int pre_index = 0;
        for (int i = 0; i < str.Length; ++i)
        {
            if (str[i] == '"')
            {
                inrange = !inrange;
            }
            else if (str[i] == ',' && !inrange)
            {
                ret.Add(GetString(SubString(str, pre_index, i)));
                pre_index = i + 1;
            }
        }
        ret.Add(GetString(SubString(str, pre_index)));
        return ret.ToArray();
    }

    // [1,2,-3]
    public static int[] GetInts(string str)
    {
        List<Int32> ret = GetArrayListInt(str);
        int[] z = new int[ret.Count];
        for (int i = 0; i < ret.Count; ++i)
        {
            z[i] = ret[i];
        }
        return z;
    }

    // [1,2,-3]
    public static double[] GetDoubles(string str)
    {
        List<Double> ret = GetArrayListDouble(str);
        double[] z = new double[ret.Count];
        for (int i = 0; i < ret.Count; ++i)
        {
            z[i] = ret[i];
        }
        return z;
    }

    // [1,2,-3]
    public static Int64[] GetLongs(string str)
    {
        List<Int64> ret = GetArrayListLong(str);
        Int64[] z = new Int64[ret.Count];
        for (int i = 0; i < ret.Count; ++i)
        {
            z[i] = ret[i];
        }
        return z;
    }

    // [[1,2],[3,4]]
    public static int[][] GetIntss(string str)
    {
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return new int[0][];
        }

        str = SubString(str, 1, str.Length - 1);
        int inrange = 0;
        int pre_index = 0;
        int count = 1;
        for (int i = 0; i < str.Length; ++i)
        {
            if (IsBeginRange(str[i]))
            {
                ++inrange;
            }
            else if (IsEndRange(str[i]))
            {
                --inrange;
            }
            else if (str[i] == ',' && inrange == 0)
            {
                ++count;
            }
        }

        int[][] ret = new int[count][];
        count = 0;
        for (int i = 0; i < str.Length; ++i)
        {
            if (IsBeginRange(str[i]))
            {
                ++inrange;
            }
            else if (IsEndRange(str[i]))
            {
                --inrange;
            }
            else if (str[i] == ',' && inrange == 0)
            {
                ret[count] = GetInts(SubString(str, pre_index, i));
                ++count;
                pre_index = i + 1;
            }
        }
        ret[count] = GetInts(SubString(str, pre_index));
        return ret;
    }

    public static TreeNode GetTreeNode(string str)
    {
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return null;
        }
        List<TreeNode> treeNodes = new List<TreeNode>();

        int current = 0;
        bool isLeft = true;

        str = SubString(str, 1, str.Length - 1);
        string[] values = str.Split(',');
        for (int i = 0; i < values.Length; ++i)
        {
            string value = values[i].Trim();
            if (value.Length == 0)
            {
                continue;
            }
            else if (value.Equals("#"))
            {
                if (treeNodes[current] != null)
                {
                    if (isLeft)
                    {
                        isLeft = false;
                    }
                    else if (treeNodes.Count > current + 1)
                    {
                        ++current;
                        isLeft = true;
                    }
                }
                continue;
            }

            TreeNode newNode = null;
            try
            {
                newNode = new TreeNode(GetInt(value));
                treeNodes.Add(newNode);
            }
            catch (Exception e)
            {
                continue;
            }

            /* 第一个节点 */
            if (treeNodes.Count == 1)
            {
                current = 0;
                isLeft = true;
            }
            else
            {
                if (isLeft)
                {
                    treeNodes[current].left = newNode;
                    isLeft = false;
                }
                else
                {
                    treeNodes[current].right = newNode;
                    ++current;
                    isLeft = true;
                }
            }
        }
        return treeNodes.Count > 0 ? treeNodes[0] : null;
    }

    public static void Print(bool b)
    {
        if (b)
        {
            System.Console.Write("true");
        }
        else
        {
            System.Console.Write("false");
        }
    }

    public static void Print(char[] x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("[");
        for (int i = 0; i < x.Length; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            System.Console.Write(x[i]);
        }
        System.Console.Write("]");
        System.Console.Write("\n");
    }

    public static void Print(char[][] vv)
    {
        if (vv == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("[");
        for (int i = 0; i < vv.Length; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            char[] v = vv[i];
            for (int j = 0; j < v.Length; ++j)
            {
                System.Console.Write(v[j]);
            }
        }
        System.Console.Write("]\n");
    }

    public static void Print(double d)
    {
        System.Console.Write(d.ToString("0.00000"));
    }

    public static void Print(int x)
    {
        System.Console.Write(x);
    }

    public static void Print(Int64 x)
    {
        System.Console.Write(x);
    }

    public static void Print(int[] A)
    {
        if (A == null)
        {
            System.Console.Write("null\n");
            return;
        }
        Print(A, A.Length);
    }

    public static void Print(int[] A, int num)
    {
        PrintInterval(A, num);
        System.Console.Write("\n");
    }

    public static void Print(List<Int32> array)
    {
        PrintInterval(array, array.Count);
        System.Console.Write("\n");
    }

    public static void PrintInterval(List<Int32> A, int num)
    {
        if (A == null)
        {
            System.Console.Write("null");
            return;
        }
        System.Console.Write("[");
        for (int i = 0; i < num && i < A.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            System.Console.Write(A[i]);
        }
        System.Console.Write("]");
    }

    public static void PrintInterval(int[] A, int num)
    {
        System.Console.Write("[");
        for (int i = 0; i < num && i < A.Length; ++i)
        {
            if (i == 0)
            {
                System.Console.Write(A[i]);
            }
            else
            {
                System.Console.Write(",");
                System.Console.Write(A[i]);
            }
        }
        System.Console.Write("]");
    }

    public static void Print(ListNode head)
    {
        PrintListNode(head);
        System.Console.Write("\n");
    }

    public static void Print(RandomListNode head)
    {
        RandomListNode current = head;
        System.Console.Write("{");
        while (current != null)
        {
            if (current == head)
            {
                System.Console.Write(current.label);
            }
            else
            {
                System.Console.WriteLine(",%d", current.label);
            }
            current = current.next;
        }
        current = head;
        while (current != null)
        {
            if (current.random != null)
            {
                System.Console.WriteLine(",%d", current.random.label);
            }
            else
            {
                System.Console.Write(",#");
            }
            current = current.next;
        }
        System.Console.Write("}\n");
    }

    public static void PrintInterval(string str)
    {
        if (str != null)
        {
            System.Console.WriteLine("\"%s\"", str);
        }
        else
        {
            System.Console.Write("null");
        }
    }

    public static void Print(string str)
    {
        PrintInterval(str);
        System.Console.Write("\n");
    }

    public static void Print(TreeLinkNode root)
    {
        System.Console.Write("{");
        List<TreeLinkNode> v = new List<TreeLinkNode>();
        if (root != null)
        {
            v.Add(root);
        }
        int c = 0;
        string none = "";
        while (c < v.Count)
        {
            if (c == 0)
            {
                System.Console.WriteLine("%d,#", v[c].val);
                v.Add(v[c].left);
                v.Add(v[c].right);
            }
            else
            {
                if (v[c] != null)
                {
                    if (v[c].next != null)
                    {
                        System.Console.WriteLine("%s,%d", none, v[c].val);
                    }
                    else
                    {
                        System.Console.WriteLine("%s,%d,#", none, v[c].val);
                    }

                    none = "";
                    v.Add(v[c].left);
                    v.Add(v[c].right);
                }
            }
            ++c;
        }
        System.Console.Write("}\n");
    }

    public static void Print(TreeNode root)
    {
        PrintTreeNode(root);
        System.Console.Write("\n");
    }

    public static void Print(UndirectedGraphNode root)
    {
        System.Console.Write("{");
        if (root != null)
        {

            HashSet<UndirectedGraphNode> nodes_set = new HashSet<UndirectedGraphNode>();
            Dictionary<Int32, UndirectedGraphNode> nodesMap = new Dictionary<Int32, UndirectedGraphNode>();
            List<UndirectedGraphNode> nodes = new List<UndirectedGraphNode>();
            nodes.Add(root);
            nodes_set.Add(root);
            nodesMap[root.label] = root;
            for (int i = 0; i < nodes.Count; ++i)
            {
                for (int j = 0; j < nodes[i].neighbors.Count; ++j)
                {
                    UndirectedGraphNode n_node = nodes[i].neighbors[j];
                    if (!nodes_set.Contains(n_node))
                    {
                        nodes_set.Add(n_node);
                        nodes.Add(n_node);
                        nodesMap[n_node.label] = n_node;
                    }
                }
            }

            bool first = true;
            // 根据label从小到大打印
            List<Int32> keys = new List<Int32>(nodesMap.Keys);
            keys.Sort();
            foreach (Int32 key in keys)
            {
                UndirectedGraphNode node = nodesMap[key];
                if (first)
                {
                    first = false;
                    System.Console.Write(node.label);
                }
                else
                {
                    System.Console.WriteLine("#%d", node.label);
                }
                for (int j = 0; j < node.neighbors.Count; ++j)
                {
                    System.Console.WriteLine(",%d", node.neighbors[j].label);
                }
            }

        }
        System.Console.Write("}\n");
    }

    public static void PrintAAInteger(List<List<Int32>> vv)
    {
        if (vv == null)
        {
            System.Console.Write("null\n");
            return;
        }

        System.Console.Write("[");
        for (int i = 0; i < vv.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            PrintAIntegerInternal(vv[i]);
        }
        System.Console.Write("]\n");
    }

    public static void PrintAStrings(List<string[]> vv)
    {
        System.Console.Write("[");
        for (int i = 0; i < vv.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            PrintInterval(vv[i]);
        }
        System.Console.Write("]\n");
    }

    public static void Print(int[][] vv)
    {
        if (vv == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("[");
        for (int i = 0; i < vv.Length; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            PrintInterval(vv[i], vv[i].Length);
        }
        System.Console.Write("]\n");
    }

    public static void Print(string[] v)
    {
        if (v == null)
        {
            System.Console.Write("null\n");
            return;
        }
        PrintInterval(v);
        System.Console.Write("\n");
    }

    private static void PrintInterval(string[] v)
    {
        System.Console.Write("[");
        for (int i = 0; i < v.Length; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            PrintInterval(v[i]);
        }
        System.Console.Write("]");
    }

    public static void PrintAAString(List<List<string>> vvs)
    {
        if (vvs == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("[");
        for (int i = 0; i < vvs.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            PrintAStringInternal(vvs[i]);
        }
        System.Console.Write("]\n");
    }

    public static void PrintAInteger(List<Int32> x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        PrintAIntegerInternal(x);
        System.Console.Write("\n");
    }

    private static void PrintAIntegerInternal(List<Int32> x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("[");
        for (int i = 0; i < x.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.WriteLine(",%d", x[i]);
            }
            else
            {
                System.Console.Write(x[i]);
            }
        }
        System.Console.Write("]");
    }

    public static void PrintAInterval(List<Interval> x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("[");
        for (int i = 0; i < x.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            System.Console.WriteLine("[%d,%d]", x[i].start, x[i].end);
        }
        System.Console.Write("]\n");
    }

    public static void PrintAListNode(List<ListNode> v)
    {
        if (v == null)
        {
            System.Console.Write("null\n");
            return;
        }
        PrintAListNode(v, v.Count);
    }

    public static void PrintAListNode(List<ListNode> A, int num)
    {
        System.Console.Write("[");
        for (int i = 0; i < A.Count && i < num; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            Print(A[i]);
        }
        System.Console.Write("]\n");
    }

    public static void PrintAString(List<string> x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        PrintAStringInternal(x);
        System.Console.Write("\n");
    }

    public static void PrintAStringInternal(List<string> x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("[");
        for (int i = 0; i < x.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            PrintInterval(x[i]);
        }
        System.Console.Write("]");
    }

    public static void PrintATreeNode(List<TreeNode> v)
    {
        if (v == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("[");
        for (int i = 0; i < v.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",");
            }
            PrintTreeNode(v[i]);
        }
        System.Console.Write("]\n");
    }

    public static void PrintListNode(ListNode head)
    {
        ListNode current = head;
        System.Console.Write("{");
        while (current != null)
        {
            if (current == head)
            {
                System.Console.Write(current.val);
            }
            else
            {
                System.Console.WriteLine(",%d", current.val);
            }
            current = current.next;
        }
        System.Console.Write("}");
    }

    public static void PrintTreeNode(TreeNode root)
    {
        System.Console.Write("{");
        List<TreeNode> v = new List<TreeNode>();
        if (root != null)
        {
            v.Add(root);
        }
        int c = 0;
        string none = "";
        while (c < v.Count)
        {
            if (c == 0)
            {
                System.Console.Write(v[c].val);
                v.Add(v[c].left);
                v.Add(v[c].right);
            }
            else
            {
                if (v[c] == null)
                {
                    none = none + ",#";
                }
                else
                {
                    System.Console.WriteLine("%s,%d", none, v[c].val);
                    none = "";
                    v.Add(v[c].left);
                    v.Add(v[c].right);
                }
            }
            ++c;
        }
        System.Console.Write("}");
    }

    // [aa,bb,cc]
    public static char[][] GetCharss(string str)
    {
        List<string> vs = GetArrayListString(str);
        char[][] ret = new char[vs.Count][];
        for (int i = 0; i < vs.Count; ++i)
        {
            ret[i] = new char[vs[i].Length];
            for (int j = 0; j < vs[i].Length; ++j)
            {
                ret[i][j] = vs[i][j];
            }
        }
        return ret;
    }

    // [ [ 1 , 2 ] ,[ 3 , 4 , -6 ] ]
    public static List<List<Int32>> GetAArrayListInt(string str)
    {
        List<List<Int32>> ret = new List<List<Int32>>();
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret;
        }

        str = SubString(str, 1, str.Length - 1);
        int inrange = 0;
        int pre_index = 0;
        for (int i = 0; i < str.Length; ++i)
        {
            if (IsBeginRange(str[i]))
            {
                ++inrange;
            }
            else if (IsEndRange(str[i]))
            {
                --inrange;
            }
            else if (str[i] == ',' && inrange == 0)
            {
                ret.Add(GetArrayListInt(SubString(str, pre_index, i)));
                pre_index = i + 1;
            }
        }
        ret.Add(GetArrayListInt(SubString(str, pre_index)));
        return ret;
    }

    // [[z,ed,kk],[ab,dd,zz]]
    public static List<List<string>> GetAArrayListString(string str)
    {
        List<List<string>> ret = new List<List<string>>();
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret;
        }

        str = SubString(str, 1, str.Length - 1);
        int inrange = 0;
        int pre_index = 0;
        for (int i = 0; i < str.Length; ++i)
        {
            if (IsBeginRange(str[i]))
            {
                ++inrange;
            }
            else if (IsEndRange(str[i]))
            {
                --inrange;
            }
            else if (str[i] == ',' && inrange == 0)
            {
                ret.Add(GetArrayListString(SubString(str, pre_index, i)));
                pre_index = i + 1;
            }
        }
        ret.Add(GetArrayListString(SubString(str, pre_index)));
        return ret;
    }

    // 支持[1,2,3,-4,5]
    // [,,] . 空
    // [] . 空
    public static List<Int32> GetArrayListInt(string str)
    {
        List<Int32> ret = new List<Int32>();
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret;
        }

        str = SubString(str, 1, str.Length - 1);
        string[] values = str.Split(',');
        foreach (string value in values)
        {
            ret.Add(GetInt(value));
        }
        return ret;
    }

    // 支持[1,2,3,-4,5]
    // [,,] . 空
    // [] . 空
    public static List<Int64> GetArrayListLong(string str)
    {
        List<Int64> ret = new List<Int64>();
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret;
        }

        str = SubString(str, 1, str.Length - 1);
        string[] values = str.Split(',');
        foreach (string value in values)
        {
            ret.Add(GetLong(value));
        }
        return ret;
    }

    // 支持[1,2,3,-4,5]
    // [,,] . 空
    // [] . 空
    public static List<Double> GetArrayListDouble(string str)
    {
        List<Double> ret = new List<Double>();
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret;
        }

        str = SubString(str, 1, str.Length - 1);
        string[] values = str.Split(',');
        foreach (string value in values)
        {
            ret.Add(GetDouble(value));
        }
        return ret;
    }

    // [{1,2,3},{1,2}]
    public static List<ListNode> GetArrayListListNode(string str)
    {
        List<ListNode> ret = new List<ListNode>();
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret;
        }
        str = SubString(str, 1, str.Length - 1);

        int inrange = 0;
        int pre_index = 0;
        for (int i = 0; i < str.Length; ++i)
        {
            if (IsBeginRange(str[i]))
            {
                ++inrange;
            }
            else if (IsEndRange(str[i]))
            {
                --inrange;
            }
            else if (str[i] == ',' && inrange == 0)
            {
                ret.Add(GetListNode(SubString(str, pre_index, i)));
                pre_index = i + 1;
            }
        }
        ret.Add(GetListNode(SubString(str, pre_index)));
        return ret;
    }

    // [(1,2),(1,3)]
    public static Point[] GetPoints(string str)
    {
        List<Point> ret = new List<Point>();
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret.ToArray();
        }

        str = SubString(str, 1, str.Length - 1);
        int inrange = 0;
        int pre_index = 0;
        for (int i = 0; i < str.Length; ++i)
        {
            if (IsBeginRange(str[i]))
            {
                ++inrange;
            }
            else if (IsEndRange(str[i]))
            {
                --inrange;
            }
            else if (str[i] == ',' && inrange == 0)
            {
                Interval interval = GetInterval(SubString(str, pre_index, i));
                ret.Add(new Point(interval.start, interval.end));
                pre_index = i + 1;
            }
        }
        Interval inv = GetInterval(SubString(str, pre_index));
        ret.Add(new Point(inv.start, inv.end));
        return ret.ToArray();
    }

    // [abc,def,,kk],["a","bdd","cc"]
    public static List<string> GetArrayListString(string str)
    {
        List<string> ret = new List<string>();
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret;
        }

        str = SubString(str, 1, str.Length - 1);
        string[] values = str.Split(',');
        foreach (string value in values)
        {
            ret.Add(GetString(value));
        }
        return ret;
    }

    public static double GetDouble(string str)
    {
        return Double.Parse(str);
    }

    // {1,2,3}
    public static ListNode GetListNode(string str)
    {
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return null;
        }
        str = SubString(str, 1, str.Length - 1);
        ListNode head = null;
        ListNode current = null;
        string[] values = str.Split(',');
        foreach (string value in values)
        {
            if (current == null && head == null)
            {
                head = new ListNode(GetInt(value));
                current = head;
            }
            else
            {
                current.next = new ListNode(GetInt(value));
                current = current.next;
            }
        }
        return head;
    }

    // { -1, 8, 7, -3,4,4,-3,#,#,-1}
    // 分为两段，前部分为ListNode,后半部分如果random==null是#，否则就是random.val
    public static RandomListNode GetRandomListNode(string str)
    {
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return null;
        }
        str = SubString(str, 1, str.Length - 1);
        RandomListNode head = null;
        RandomListNode current = null;
        Dictionary<Int32, RandomListNode> nodesMap = new Dictionary<Int32, RandomListNode>();
        // 先统计总共有多少个元素
        string[] values = str.Split(',');
        for (int i = 0; i < values.Length / 2; ++i)
        {
            if (head == null && current == null)
            {
                head = new RandomListNode(GetInt(values[i]));
                current = head;
            }
            else
            {
                current.next = new RandomListNode(GetInt(values[i]));
                current = current.next;
            }
            nodesMap[current.label] = current;
        }

        current = head;
        for (int i = values.Length / 2; i < values.Length; ++i)
        {
            if (!values[i].Equals("#"))
            {
                current.random = nodesMap[GetInt(values[i])];
            }
            current = current.next;
        }
        return head;
    }

    // ["aaa","dd","fff","","dfd"]
    public static HashSet<string> GetHashSetString(string str)
    {
        HashSet<string> ret = new HashSet<string>();
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret;
        }

        str = SubString(str, 1, str.Length - 1);
        bool inrange = false;
        int pre_index = 0;
        for (int i = 0; i < str.Length; ++i)
        {
            if (str[i] == '"')
            {
                inrange = !inrange;
            }
            else if (str[i] == ',' && !inrange)
            {
                ret.Add(GetString(SubString(str, pre_index, i)));
                pre_index = i + 1;
            }
        }
        ret.Add(GetString(SubString(str, pre_index)));
        return ret;
    }

    public static TreeLinkNode GetTreeLinkNode(string str)
    {
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return null;
        }

        List<TreeLinkNode> treeNodes = new List<TreeLinkNode>();
        str = SubString(str, 1, str.Length - 1);
        int current = 0;
        bool isLeft = true;

        string[] values = str.Split(',');
        for (int i = 0; i < values.Length; ++i)
        {
            string
                value = values[i];
            if (value.Length == 0)
            {
                continue;
            }
            else if (value.Equals("#"))
            {
                if (treeNodes[current] != null)
                {
                    if (isLeft)
                    {
                        isLeft = false;
                    }
                    else if (treeNodes.Count > current + 1)
                    {
                        ++current;
                        isLeft = true;
                    }
                }
                continue;
            }

            TreeLinkNode newNode = null;
            try
            {
                newNode = new TreeLinkNode(GetInt(value));
                treeNodes.Add(newNode);
            }
            catch (Exception e)
            {
                continue;
            }

            /* 第一个节点 */
            if (treeNodes.Count == 1)
            {
                current = 0;
                isLeft = true;
            }
            else
            {
                if (isLeft)
                {
                    treeNodes[current].left = newNode;
                    isLeft = false;
                }
                else
                {
                    treeNodes[current].right = newNode;
                    ++current;
                    isLeft = true;
                }
            }
        }
        return treeNodes.Count > 0 ? treeNodes[0] : null;
    }

    public static UndirectedGraphNode GetUndirectedGraphNode(string str)
    {
        UndirectedGraphNode ret = null;
        str = str == null ? null : str.Trim();
        if (str == null || !IsValidRange(str) || IsEmptyRange(str))
        {
            return ret;
        }
        str = SubString(str, 1, str.Length - 1);
        string[] nodeStrs = str.Split('#');

        Dictionary<Int32, UndirectedGraphNode> nodesMap = new Dictionary<Int32, UndirectedGraphNode>();

        // 把所有的点构造出来
        for (int i = 0; i < nodeStrs.Length; ++i)
        {
            string[] v = nodeStrs[i].Split(',');
            if (v.Length < 1)
            {
                continue;
            }
            if (!nodesMap.ContainsKey(GetInt(v[0])))
            {
                UndirectedGraphNode node = new UndirectedGraphNode(GetInt(v[0]));
                nodesMap[node.label] = node;
                if (ret == null)
                {
                    ret = node;
                }
            }
        }

        // 把各个边连接起来
        for (int i = 0; i < nodeStrs.Length; ++i)
        {
            string[] v = nodeStrs[i].Split(',');
            if (v.Length < 1)
            {
                continue;
            }
            UndirectedGraphNode node = nodesMap[GetInt(v[0])];
            for (int j = 1; j < v.Length; ++j)
            {
                node.neighbors.Add(nodesMap[GetInt(v[j])]);
            }
        }
        return ret;
    }

    public static Interval Print(Interval interval)
    {
        System.Console.WriteLine("[%d,%d]\n", interval.start, interval.end);
        return interval;
    }
}
