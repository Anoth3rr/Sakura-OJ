using System.Collections.Generic;
using System;

public class TreeLinkNode
{
	public int val;
	public TreeLinkNode left;
	public TreeLinkNode right;
	public TreeLinkNode next;

	public TreeLinkNode (int x)
	{
		val = x;
	}
}

public class UndirectedGraphNode
{
	public int label;
	public IList<UndirectedGraphNode> neighbors;

	public UndirectedGraphNode (int x)
	{
		label = x;
		neighbors = new List<UndirectedGraphNode> ();
	}
}

public class RandomListNode
{
	public int label;
	public RandomListNode next, random;

	public RandomListNode (int x)
	{
		this.label = x;
	}
}

public class Interval
{
	public int start;
	public int end;

	public Interval ()
	{
		start = 0;
		end = 0;
	}

	public Interval (int s, int e)
	{
		start = s;
		end = e;
	}
}

public class TreeNode
{
	public int val;
	public TreeNode left;
	public TreeNode right;

	public TreeNode (int x)
	{
		val = x;
	}
}

public class Point
{
	public int x;
	public int y;

	public Point ()
	{
		x = 0;
		y = 0;
	}

	public Point (int a, int b)
	{
		x = a;
		y = b;
	}
}

public class ListNode
{
	public int val;
	public ListNode next;

	public ListNode (int x)
	{
		val = x;
	}
}

public class NCTools
{
	private static int LEFT = 0;
	private static int RIGHT = 1;

	private static bool IsBeginRange (char c)
	{
		return c == '{' || c == '[' || c == '(';
	}

	private static bool IsEndRange (char c)
	{
		return c == '}' || c == ']' || c == ')';
	}
	
	public static List<string> GetArguments (string line)
	{
		List<string> ret = new List<string> ();
		if (line == null) {
			return ret;
		}
		int inrange = 0;
		int pre_index = 0;
		bool inmao = false;
		for (int i = 0; i < line.Length; ++i) {
			if (IsBeginRange (line [i]) && !inmao) {
				++inrange;
			} else if (IsEndRange (line [i]) && !inmao) {
				--inrange;
			} else if (line [i] == '\"') {
				inmao = !inmao;
			} else if (line [i] == ',' && inrange == 0 && !inmao) {
				ret.Add (line.Substring (pre_index, i - pre_index));
				pre_index = i + 1;
			}
		}
		ret.Add (line.Substring (pre_index));
		return ret;
	}
	
	private static List<string> GetRangeItems (string str)
	{
		if (str == null) {
			return new List<string> ();
		}
		
		int begin = 0;
		while (!IsBeginRange(str[begin]) && begin < str.Length) {
			++begin;
		}
		int end = str.Length;
		while (!IsEndRange(str[end - 1]) && end > 1) {
			--end;
		}
		str = str.Substring (begin + 1, end - begin - 2);
		return str.Trim ().Length == 0 ? new List<string> () : GetArguments (str);
	}
	
	public static int GetInt (string str)
	{
	    try {
    		return str == null ? 0 : Int32.Parse (str.Trim ());
        } catch (Exception e) {
            return 0;
        }
	}

	private static void PrintInternal (int x)
	{
		System.Console.Write (x);
	}
	
	public static long GetLong (string str)
	{
	    try {
    		return str == null ? 0 : Int64.Parse (str.Trim ());
		} catch (Exception e) {
		    return 0;
		}
	}

	private static void PrintInternal (long x)
	{
		System.Console.Write (x);
	}
	
	public static float GetFloat (string str)
	{
	    try {
    		return str == null || str.Equals("") ? 0 : float.Parse (str.Trim ());
		} catch (Exception e) {
		    return 0;
		}
	}

	private static void PrintInternal (float d)
	{
		if (Math.Abs (d) < 0.000009999999) {
			System.Console.Write ("0.00000");
		} else {
			System.Console.Write (d.ToString ("0.00000"));
		}
	}
	
	public static double GetDouble (string str)
	{
	    try {
    		return str == null || str.Equals("") ? 0 : Double.Parse (str.Trim ());
		} catch (Exception e) {
		    return 0;
		}
	}

	private static void PrintInternal (double d)
	{
		if (Math.Abs (d) < 0.000009999999) {
			System.Console.Write ("0.00000");
		} else {
			System.Console.Write (d.ToString ("0.00000"));
		}
	}

	public static string GetString (string str)
	{
		if (str != null) {
			str = str.Trim ();
		}
		if (str == null || !str.StartsWith ("\"") || !str.EndsWith ("\"")) {
			return str == null ? "" : str;
		}
		return str.Substring (1, str.Length - 2);
	}

	private static void PrintInternal (string str)
	{
		if (str != null) {
			System.Console.Write ("\"{0}\"", str);
		} else {
			System.Console.Write ("null");
		}
	}

	public static char GetChar (string str)
	{
		return str == null || str.Trim ().Length == 0 ? '#' : str.Trim () [0];
	}

	private static void PrintInternal (char c)
	{
		System.Console.Write (c);
	}
	
	public static bool GetBool (string str)
	{
		return str == null ? false : bool.Parse (str);
	}

	private static void PrintInternal (bool b)
	{
		System.Console.Write (b ? "true" : "false");
	}

	public static Interval GetInterval (string str)
	{
		List<int> items = GetIntList (str);
		return items.Count == 2 ? new Interval (items [0], items [1]) : new Interval ();
	}

	private static void PrintInternal (Interval interval)
	{
		System.Console.Write ("[{0},{1}]", interval.start, interval.end);
	}
	
	public static Point GetPoint (string str)
	{
		List<int> items = GetIntList (str);
		return items.Count == 2 ? new Point (items [0], items [1]) : new Point ();
	}

	private static void PrintInternal (Point point)
	{
		System.Console.Write ("({0},{1})", point.x, point.y);
	}

	public static TreeNode GetTreeNode (string str)
	{
		List<string> items = GetRangeItems (str);
		if (items.Count == 0) {
			return null;
		}
		TreeNode [] tree_nodes = new TreeNode[items.Count + 1];
		int current = 0;
		/* 当前遍历节点位置 */
		int current_pos = LEFT;
		int index = 1;
		tree_nodes [0] = new TreeNode (GetInt (items [0]));
		for (int i = 1; i < items.Count; ++i) {
			if (items [i].Equals("#")) {
				if (tree_nodes [current] != null) {
					if (current_pos == LEFT) {
						current_pos = RIGHT;
					} else if (tree_nodes [current + 1] != null) {
						++current;
						current_pos = LEFT;
					}
				}
			} else {
				tree_nodes [index] = new TreeNode (GetInt (items [i]));
				if (current_pos == LEFT) {
					tree_nodes [current].left = tree_nodes [index];
					current_pos = RIGHT;
				} else {
					tree_nodes [current].right = tree_nodes [index];
					++current;
					current_pos = LEFT;
				}
				++index;
			}
		}
	
		return tree_nodes [0];
	}

	private static void PrintInternal (TreeNode root)
	{
		if (root == null) {
			System.Console.Write ("null");
			return;
		}
		System.Console.Write ("{");
		List<TreeNode> v = new List<TreeNode> ();
		if (root != null) {
			v.Add (root);
		}
		int c = 0;
		string none = "";
		while (c < v.Count) {
			if (c == 0) {
				System.Console.Write (v [c].val);
				v.Add (v [c].left);
				v.Add (v [c].right);
			} else {
				if (v [c] == null) {
					none = none + ",#";
				} else {
					System.Console.Write ("{0},{1}", none, v [c].val);
					none = "";
					v.Add (v [c].left);
					v.Add (v [c].right);
				}
			}
			++c;
		}
		System.Console.Write ("}");
	}
	
	public static ListNode GetListNode (string str)
	{
		List<int> items = GetIntList (str);
		if (items.Count == 0) {
			return null;
		}
		ListNode head = new ListNode (items [0]);
		ListNode tail = head;
		for (int i = 1; i < items.Count; ++i) {
			tail.next = new ListNode (items [i]);
			tail = tail.next;
		}
		return head;
	}

	private static void PrintInternal (ListNode head)
	{
		if (head == null) {
			System.Console.Write ("null");
			return;
		}
		ListNode current = head;
		System.Console.Write ("{");
		while (current != null) {
			if (current == head) {
				System.Console.Write (current.val);
			} else {
				System.Console.Write (",{0}", current.val);
			}
			current = current.next;
		}
		System.Console.Write ("}");
	}
	
	
	// { -1, 8, 7, -3,4,4,-3,#,#,-1}
	// 分为两段，前部分为ListNode,后半部分如果random==null是#，否则就是random.val
	public static RandomListNode GetRandomListNode (string str)
	{
		List<string> items = GetRangeItems (str);
		if (items.Count < 2) {
			return null;
		}
	
		int count = items.Count / 2;
		// 记录前一半到节点
		RandomListNode[] list_nodes = new RandomListNode[count + 1];
	
		Dictionary<int, RandomListNode> nodes_map = new Dictionary<int, RandomListNode> ();
		RandomListNode head = new RandomListNode (GetInt (items [0]));
		nodes_map [head.label] = head;
		list_nodes [0] = head;
		RandomListNode tail = head;
		for (int i = 1; i < count; ++i) {
			RandomListNode cur = new RandomListNode (GetInt (items [i]));
			tail.next = cur;
			tail = cur;
			nodes_map [cur.label] = cur;
			list_nodes [i] = cur;
		}
	
		// 遍历后部分到随机节点
		for (int i = count; i < items.Count; ++i) {
			if (!items [i].Equals("#") && nodes_map.ContainsKey (GetInt (items [i]))) {
				list_nodes [i - count].random = nodes_map [GetInt (items [i])];
			}
		}
		return head;
	}

	private static void PrintInternal (RandomListNode head)
	{
		if (head == null) {
			System.Console.Write ("null");
			return;
		}
		RandomListNode current = head;
		System.Console.Write ("{");
		while (current != null) {
			if (current == head) {
				System.Console.Write (current.label);
			} else {
				System.Console.Write (",{0}", current.label);
			}
			current = current.next;
		}
		current = head;
		while (current != null) {
			if (current.random != null) {
				System.Console.Write (",{0}", current.random.label);
			} else {
				System.Console.Write (",#");
			}
			current = current.next;
		}
		System.Console.Write ("}");
	}
	/*二叉链接树序列化是通过按层遍历,#代表这这个节点为空节点,节点遍历以后再增加所有next节点数据,举个例子
 1.null
 / \
     2 .3.null
 /
 4.null
 5.null

 以上二叉树会被序列化为 {[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}
 对于{[1,2,3,#,#,4,#,#,5],[#,5,#,#,#]}构造出来的链接树节点2的next指向5节点*/
	public static TreeLinkNode GetTreeLinkNode (string str)
	{
		List<string> all_items = GetRangeItems (str);
		// 老版本只有{1,3,34}这种格式
		bool is_newversion = all_items.Count == 2 && all_items[0][0] == '[' && all_items[1][0] == '[';
		if (!is_newversion) {
		    all_items.Clear();
		    all_items.Add(str);
		    all_items.Add("[]");
		}
		if (all_items.Count < 2) {
			return null;
		}
		List<string> items = GetRangeItems (all_items [0]);
		if (items.Count == 0) {
			return null;
		}

		TreeLinkNode [] tree_nodes = new TreeLinkNode[items.Count + 1];
		Dictionary<int, TreeLinkNode> map_nodes = new Dictionary<int, TreeLinkNode> ();
		int current = 0;
		/* 当前遍历节点位置 */
		int current_pos = LEFT;
		int index = 1;
		tree_nodes [0] = new TreeLinkNode (GetInt (items [0]));
		for (int i = 1; i < items.Count; ++i) {
			if (items [i].Equals("#")) {
				if (tree_nodes [current] != null) {
					if (current_pos == LEFT) {
						current_pos = RIGHT;
					} else if (tree_nodes [current + 1] != null) {
						++current;
						current_pos = LEFT;
					}
				}
			} else {
				int label = GetInt (items [i]);
				tree_nodes [index] = new TreeLinkNode (label);
				map_nodes [label] = tree_nodes [index];
				if (current_pos == LEFT) {
					tree_nodes [current].left = tree_nodes [index];
					current_pos = RIGHT;
				} else {
					tree_nodes [current].right = tree_nodes [index];
					++current;
					current_pos = LEFT;
				}
				++index;
			}
		}

		// 连接next指针
		items = GetRangeItems (all_items [1]);
		for (int i = 0; i < items.Count; ++i) {
			if (!items [i].Equals("#") && map_nodes.ContainsKey (GetInt (items [i]))) {
				tree_nodes [i].next = tree_nodes [GetInt (items [i])];
			}
		}

		return tree_nodes [0];
	}

	private static void PrintInternal (TreeLinkNode root)
	{
		if (root == null) {
			System.Console.Write ("null");
			return;
		}
		System.Console.Write ("{[");
		List<TreeLinkNode> v = new List<TreeLinkNode> ();
		List<TreeLinkNode> label_node_v = new List<TreeLinkNode> ();
		if (root != null) {
			v.Add (root);
			label_node_v.Add (root);
		}
		int c = 0;
		string none = "";
		while (c < v.Count) {
			if (c == 0) {
				System.Console.Write (v [c].val);
				v.Add (v [c].left);
				v.Add (v [c].right);
			} else {
				if (v [c] == null) {
					none = none + ",#";
				} else {
					label_node_v.Add (v [c]);
					System.Console.Write ("{0},{1}", none, v [c].val);
					none = "";
					v.Add (v [c].left);
					v.Add (v [c].right);
				}
			}
			++c;
		}
		v.Clear ();
		System.Console.Write ("],[");
		for (int i = 0; i < label_node_v.Count; ++i) {
			if (i != 0) {
				System.Console.Write (",");
			}
			if (label_node_v [i].next != null) {
				System.Console.Write (label_node_v [i].next.val);
			} else {
				System.Console.Write ("#");
			}
		}
		System.Console.Write ("]}");
	}
	
	
/**
 无向图里每个节点都有一个唯一的数字ID,每个节点的序列化通过[]保存,每个节点第一个元素后跟随的是这个节点连接的其他节点,以下图
 1
 /  \
     /    \
    0 --- 2
 / \
         \_/
 序列化后为{[0,1,2],[1,2],[2,2]}*/
	public static UndirectedGraphNode GetUndirectedGraphNode (string str)
	{
		List<List<int>> points = GetIntListList (str);

		UndirectedGraphNode ret = null;
		Dictionary<int, UndirectedGraphNode> nodes_map = new Dictionary<int, UndirectedGraphNode> ();
	
		// 把所有的点构造出来
		for (int i = 0; i < points.Count; ++i) {
			List<int> v = points [i];
			if (v.Count == 0) {
				continue;
			}
			if (!nodes_map.ContainsKey (v [0])) {
				UndirectedGraphNode node = new UndirectedGraphNode (v [0]);
				nodes_map [v [0]] = node;
				if (ret == null) {
					ret = node;
				}
			}
		}
	
		// 把各个边连接起来
		for (int i = 0; i < points.Count; ++i) {
			List<int> v = points [i];
			if (v.Count == 0) {
				continue;
			}
			UndirectedGraphNode node = nodes_map [v [0]];
			for (int j = 1; j < v.Count; ++j) {
				node.neighbors.Add (nodes_map [v [j]]);
			}
		}
		return ret;
	}
	
	private static void PrintInternal (UndirectedGraphNode root)
	{
		if (root == null) {
			System.Console.Write ("null");
			return;
		}
		System.Console.Write ("{");
		if (root != null) {
			HashSet<UndirectedGraphNode> nodes_set = new HashSet<UndirectedGraphNode> ();
			Dictionary<int, UndirectedGraphNode> nodes_map = new Dictionary<int, UndirectedGraphNode> ();
			List<UndirectedGraphNode> nodes = new List<UndirectedGraphNode> ();
			nodes.Add (root);
			nodes_set.Add (root);
			nodes_map [root.label] = root;
			for (int i = 0; i < nodes.Count; ++i) {
				for (int j = 0; j < nodes[i].neighbors.Count; ++j) {
					UndirectedGraphNode n_node = nodes [i].neighbors [j];
					if (!nodes_set.Contains (n_node)) {
						nodes_set.Add (n_node);
						nodes.Add (n_node);
						nodes_map [n_node.label] = n_node;
					}
				}
			}
	
			// 根据label从小到大打印
			foreach (UndirectedGraphNode node in nodes_map.Values) {
				if (node != nodes [0]) {// 不是第一个节点
					System.Console.Write (",[{0}", node.label);
				} else {
					System.Console.Write ("[{0}", node.label);
				}
				for (int j = 0; j < node.neighbors.Count; ++j) {
					System.Console.Write (",{0}", node.neighbors [j].label);
				}
				System.Console.Write ("]");
			}
		}
		System.Console.Write ("}");
	}

	public static HashSet<int> GetIntSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<int> ret = new HashSet<int> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetInt (items [i]));
		}
		return ret;
	}

	public static List<int> GetIntList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<int> ret = new List<int> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetInt (items [i]));
		}
		return ret;
	}

	public static int[] GetInts (string str)
	{
		List<string> items = GetRangeItems (str);
		int[] ret = new int[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetInt (items [i]);
		}
		return ret;
	}

	public static List<List<int>> GetIntListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<int>> ret = new List<List<int>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetIntList (items [i]));
		}
		return ret;
	}

	public static int[][] GetIntss (string str)
	{
		List<string> items = GetRangeItems (str);
		int[][] ret = new int[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetInts (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<int> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (int x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<int> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<int>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (int[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (int[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (int[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<long> GetLongSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<long> ret = new HashSet<long> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetLong (items [i]));
		}
		return ret;
	}

	public static List<long> GetLongList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<long> ret = new List<long> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetLong (items [i]));
		}
		return ret;
	}

	public static long[] GetLongs (string str)
	{
		List<string> items = GetRangeItems (str);
		long[] ret = new long[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetLong (items [i]);
		}
		return ret;
	}

	public static List<List<long>> GetLongListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<long>> ret = new List<List<long>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetLongList (items [i]));
		}
		return ret;
	}

	public static long[][] GetLongss (string str)
	{
		List<string> items = GetRangeItems (str);
		long[][] ret = new long[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetLongs (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<long> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (long x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<long> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<long>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (long[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (long[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (long[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<float> GetFloatSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<float> ret = new HashSet<float> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetFloat (items [i]));
		}
		return ret;
	}

	public static List<float> GetFloatList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<float> ret = new List<float> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetFloat (items [i]));
		}
		return ret;
	}

	public static float[] GetFloats (string str)
	{
		List<string> items = GetRangeItems (str);
		float[] ret = new float[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetFloat (items [i]);
		}
		return ret;
	}

	public static List<List<float>> GetFloatListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<float>> ret = new List<List<float>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetFloatList (items [i]));
		}
		return ret;
	}

	public static float[][] GetFloatss (string str)
	{
		List<string> items = GetRangeItems (str);
		float[][] ret = new float[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetFloats (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<float> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (float x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<float> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<float>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (float[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (float[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (float[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<double> GetDoubleSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<double> ret = new HashSet<double> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetDouble (items [i]));
		}
		return ret;
	}

	public static List<double> GetDoubleList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<double> ret = new List<double> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetDouble (items [i]));
		}
		return ret;
	}

	public static double[] GetDoubles (string str)
	{
		List<string> items = GetRangeItems (str);
		double[] ret = new double[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetDouble (items [i]);
		}
		return ret;
	}

	public static List<List<double>> GetDoubleListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<double>> ret = new List<List<double>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetDoubleList (items [i]));
		}
		return ret;
	}

	public static double[][] GetDoubless (string str)
	{
		List<string> items = GetRangeItems (str);
		double[][] ret = new double[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetDoubles (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<double> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (double x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<double> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<double>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (double[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (double[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (double[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<char> GetCharSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<char> ret = new HashSet<char> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetChar (items [i]));
		}
		return ret;
	}

	public static List<char> GetCharList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<char> ret = new List<char> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetChar (items [i]));
		}
		return ret;
	}

	public static char[] GetChars (string str)
	{
	    str = GetString(str);
		char[] ret = new char[str.Length];
		for (int i = 0; i < str.Length; ++i) {
			ret [i] = str[i];
		}
		return ret;
	}

	public static List<List<char>> GetCharListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<char>> ret = new List<List<char>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetCharList (items [i]));
		}
		return ret;
	}

	public static char[][] GetCharss (string str)
	{
		List<string> items = GetRangeItems (str);
		char[][] ret = new char[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetChars (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<char> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (char x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<char> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<char>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (char[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (char[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (char[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<bool> GetBoolSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<bool> ret = new HashSet<bool> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetBool (items [i]));
		}
		return ret;
	}

	public static List<bool> GetBoolList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<bool> ret = new List<bool> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetBool (items [i]));
		}
		return ret;
	}

	public static bool[] GetBools (string str)
	{
		List<string> items = GetRangeItems (str);
		bool[] ret = new bool[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetBool (items [i]);
		}
		return ret;
	}

	public static List<List<bool>> GetBoolListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<bool>> ret = new List<List<bool>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetBoolList (items [i]));
		}
		return ret;
	}

	public static bool[][] GetBoolss (string str)
	{
		List<string> items = GetRangeItems (str);
		bool[][] ret = new bool[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetBools (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<bool> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (bool x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<bool> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<bool>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (bool[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (bool[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (bool[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<string> GetStringSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<string> ret = new HashSet<string> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetString (items [i]));
		}
		return ret;
	}

	public static List<string> GetStringList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<string> ret = new List<string> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetString (items [i]));
		}
		return ret;
	}

	public static string[] GetStrings (string str)
	{
		List<string> items = GetRangeItems (str);
		string[] ret = new string[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetString (items [i]);
		}
		return ret;
	}

	public static List<List<string>> GetStringListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<string>> ret = new List<List<string>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetStringList (items [i]));
		}
		return ret;
	}

	public static string[][] GetStringss (string str)
	{
		List<string> items = GetRangeItems (str);
		string[][] ret = new string[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetStrings (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<string> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (string x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<string> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<string>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (string[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (string[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (string[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<Interval> GetIntervalSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<Interval> ret = new HashSet<Interval> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetInterval (items [i]));
		}
		return ret;
	}

	public static List<Interval> GetIntervalList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<Interval> ret = new List<Interval> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetInterval (items [i]));
		}
		return ret;
	}

	public static Interval[] GetIntervals (string str)
	{
		List<string> items = GetRangeItems (str);
		Interval[] ret = new Interval[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetInterval (items [i]);
		}
		return ret;
	}

	public static List<List<Interval>> GetIntervalListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<Interval>> ret = new List<List<Interval>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetIntervalList (items [i]));
		}
		return ret;
	}

	public static Interval[][] GetIntervalss (string str)
	{
		List<string> items = GetRangeItems (str);
		Interval[][] ret = new Interval[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetIntervals (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<Interval> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (Interval x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<Interval> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<Interval>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (Interval[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (Interval[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (Interval[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<Point> GetPointSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<Point> ret = new HashSet<Point> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetPoint (items [i]));
		}
		return ret;
	}

	public static List<Point> GetPointList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<Point> ret = new List<Point> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetPoint (items [i]));
		}
		return ret;
	}

	public static Point[] GetPoints (string str)
	{
		List<string> items = GetRangeItems (str);
		Point[] ret = new Point[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetPoint (items [i]);
		}
		return ret;
	}

	public static List<List<Point>> GetPointListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<Point>> ret = new List<List<Point>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetPointList (items [i]));
		}
		return ret;
	}

	public static Point[][] GetPointss (string str)
	{
		List<string> items = GetRangeItems (str);
		Point[][] ret = new Point[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetPoints (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<Point> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (Point x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<Point> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<Point>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (Point[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (Point[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (Point[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<UndirectedGraphNode> GetUndirectedGraphNodeSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<UndirectedGraphNode> ret = new HashSet<UndirectedGraphNode> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetUndirectedGraphNode (items [i]));
		}
		return ret;
	}

	public static List<UndirectedGraphNode> GetUndirectedGraphNodeList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<UndirectedGraphNode> ret = new List<UndirectedGraphNode> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetUndirectedGraphNode (items [i]));
		}
		return ret;
	}

	public static UndirectedGraphNode[] GetUndirectedGraphNodes (string str)
	{
		List<string> items = GetRangeItems (str);
		UndirectedGraphNode[] ret = new UndirectedGraphNode[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetUndirectedGraphNode (items [i]);
		}
		return ret;
	}

	public static List<List<UndirectedGraphNode>> GetUndirectedGraphNodeListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<UndirectedGraphNode>> ret = new List<List<UndirectedGraphNode>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetUndirectedGraphNodeList (items [i]));
		}
		return ret;
	}

	public static UndirectedGraphNode[][] GetUndirectedGraphNodess (string str)
	{
		List<string> items = GetRangeItems (str);
		UndirectedGraphNode[][] ret = new UndirectedGraphNode[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetUndirectedGraphNodes (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<UndirectedGraphNode> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (UndirectedGraphNode x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<UndirectedGraphNode> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<UndirectedGraphNode>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (UndirectedGraphNode[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (UndirectedGraphNode[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (UndirectedGraphNode[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<ListNode> GetListNodeSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<ListNode> ret = new HashSet<ListNode> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetListNode (items [i]));
		}
		return ret;
	}

	public static List<ListNode> GetListNodeList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<ListNode> ret = new List<ListNode> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetListNode (items [i]));
		}
		return ret;
	}

	public static ListNode[] GetListNodes (string str)
	{
		List<string> items = GetRangeItems (str);
		ListNode[] ret = new ListNode[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetListNode (items [i]);
		}
		return ret;
	}

	public static List<List<ListNode>> GetListNodeListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<ListNode>> ret = new List<List<ListNode>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetListNodeList (items [i]));
		}
		return ret;
	}

	public static ListNode[][] GetListNodess (string str)
	{
		List<string> items = GetRangeItems (str);
		ListNode[][] ret = new ListNode[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetListNodes (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<ListNode> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (ListNode x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<ListNode> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<ListNode>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (ListNode[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (ListNode[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (ListNode[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<RandomListNode> GetRandomListNodeSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<RandomListNode> ret = new HashSet<RandomListNode> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetRandomListNode (items [i]));
		}
		return ret;
	}

	public static List<RandomListNode> GetRandomListNodeList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<RandomListNode> ret = new List<RandomListNode> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetRandomListNode (items [i]));
		}
		return ret;
	}

	public static RandomListNode[] GetRandomListNodes (string str)
	{
		List<string> items = GetRangeItems (str);
		RandomListNode[] ret = new RandomListNode[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetRandomListNode (items [i]);
		}
		return ret;
	}

	public static List<List<RandomListNode>> GetRandomListNodeListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<RandomListNode>> ret = new List<List<RandomListNode>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetRandomListNodeList (items [i]));
		}
		return ret;
	}

	public static RandomListNode[][] GetRandomListNodess (string str)
	{
		List<string> items = GetRangeItems (str);
		RandomListNode[][] ret = new RandomListNode[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetRandomListNodes (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<RandomListNode> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (RandomListNode x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<RandomListNode> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<RandomListNode>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (RandomListNode[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (RandomListNode[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (RandomListNode[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<TreeNode> GetTreeNodeSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<TreeNode> ret = new HashSet<TreeNode> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetTreeNode (items [i]));
		}
		return ret;
	}

	public static List<TreeNode> GetTreeNodeList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<TreeNode> ret = new List<TreeNode> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetTreeNode (items [i]));
		}
		return ret;
	}

	public static TreeNode[] GetTreeNodes (string str)
	{
		List<string> items = GetRangeItems (str);
		TreeNode[] ret = new TreeNode[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetTreeNode (items [i]);
		}
		return ret;
	}

	public static List<List<TreeNode>> GetTreeNodeListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<TreeNode>> ret = new List<List<TreeNode>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetTreeNodeList (items [i]));
		}
		return ret;
	}

	public static TreeNode[][] GetTreeNodess (string str)
	{
		List<string> items = GetRangeItems (str);
		TreeNode[][] ret = new TreeNode[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetTreeNodes (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<TreeNode> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (TreeNode x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<TreeNode> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<TreeNode>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (TreeNode[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (TreeNode[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (TreeNode[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	public static HashSet<TreeLinkNode> GetTreeLinkNodeSet (string str)
	{
		List<string> items = GetRangeItems (str);
		HashSet<TreeLinkNode> ret = new HashSet<TreeLinkNode> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetTreeLinkNode (items [i]));
		}
		return ret;
	}

	public static List<TreeLinkNode> GetTreeLinkNodeList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<TreeLinkNode> ret = new List<TreeLinkNode> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetTreeLinkNode (items [i]));
		}
		return ret;
	}

	public static TreeLinkNode[] GetTreeLinkNodes (string str)
	{
		List<string> items = GetRangeItems (str);
		TreeLinkNode[] ret = new TreeLinkNode[items.Count];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetTreeLinkNode (items [i]);
		}
		return ret;
	}

	public static List<List<TreeLinkNode>> GetTreeLinkNodeListList (string str)
	{
		List<string> items = GetRangeItems (str);
		List<List<TreeLinkNode>> ret = new List<List<TreeLinkNode>> ();
		for (int i = 0; i < items.Count; ++i) {
			ret.Add (GetTreeLinkNodeList (items [i]));
		}
		return ret;
	}

	public static TreeLinkNode[][] GetTreeLinkNodess (string str)
	{
		List<string> items = GetRangeItems (str);
		TreeLinkNode[][] ret = new TreeLinkNode[items.Count][];
		for (int i = 0; i < items.Count; ++i) {
			ret [i] = GetTreeLinkNodes (items [i]);
		}
		return ret;
	}

	private static void PrintInternal (List<TreeLinkNode> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (TreeLinkNode x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<TreeLinkNode> x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (List<List<TreeLinkNode>> x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Count; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

	private static void PrintInternal (TreeLinkNode[] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write (']');
	}

	public static void Print (TreeLinkNode[] x)
	{
		PrintInternal (x);
		Console.Out.Write ('\n');
	}

	public static void Print (TreeLinkNode[][] x)
	{
		Console.Out.Write ('[');
		for (int i = 0; i < x.Length; ++i) {
			if (i != 0) {
				Console.Out.Write (',');
			}
			PrintInternal (x [i]);
		}
		Console.Out.Write ("]\n");
	}

}
