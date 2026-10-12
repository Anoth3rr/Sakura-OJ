import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Tools {
  private static boolean IsBeginRange(char c) {
    return c == '{' || c == '[' || c == '(';
  }

  private static boolean IsEndRange(char c) {
    return c == '}' || c == ']' || c == ')';
  }

  private static boolean IsValidRange(String str) {
    return IsBeginRange(str.charAt(0)) && IsEndRange(str.charAt(str.length() - 1));
  }

  private static boolean IsEmptyRange(String str) {
    return str == null || str.equals("[]") || str.equals("()") || str.equals("{}");
  }

  public static ArrayList<String> GetArguments(String line, int arg_count) {
    ArrayList<String> ret = new ArrayList<String>();
    if (line == null) {
      return ret;
    }
    int inrange = 0;
    int pre_index = 0;
    boolean inmao = false;
    for (int i = 0; i < line.length(); ++i) {
      if (IsBeginRange(line.charAt(i))) {
        ++inrange;
      } else if (IsEndRange(line.charAt(i))) {
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

  // [[1,2],[3,4],[5,6]]
  public static ArrayList<Interval> GetArrayListInterval(String str) {
    ArrayList<Interval> ret = new ArrayList<Interval>();
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = str.substring(1, str.length() - 1);
    int inrange = 0;
    int pre_index = 0;
    for (int i = 0; i < str.length(); ++i) {
      if (IsBeginRange(str.charAt(i))) {
        ++inrange;
      } else if (IsEndRange(str.charAt(i))) {
        --inrange;
      } else if (str.charAt(i) == ',' && inrange == 0) {
        ret.add(GetInterval(str.substring(pre_index, i)));
        pre_index = i + 1;
      }
    }
    ret.add(GetInterval(str.substring(pre_index)));
    return ret;
  }

  // "abc", abc
  public static String GetString(String str) {
    if (str != null) {
      str = str.trim();
    }
    if (str == null || !str.startsWith("\"") || !str.endsWith("\"")) {
      return str == null ? "" : str;
    }
    return str.substring(1, str.length() - 1);
  }

  // char
  public static char GetChar(String str) {
    return str == null || str.length() == 0 ? '#' : str.charAt(0);
  }

  // 1
  public static int GetInt(String str) {
    return Integer.parseInt(str.trim());
  }

  // 1
  public static long GetLong(String str) {
    return Long.parseLong(str.trim());
  }

  // [1,3] (1,3)
  public static Interval GetInterval(String str) {
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str)) {
      return null;
    }
    str = str.substring(1, str.length() - 1);
    String[] v = str.split(",", -1);
    if (v.length != 2) {
      return null;
    }
    return new Interval(GetInt(v[0]), GetInt(v[1]));
  }

  // ["a","b","ccc"]
  public static String[] GetStrings(String str) {
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return new String[0];
    }

    str = str.substring(1, str.length() - 1);
    ArrayList<String> ret = new ArrayList<String>();
    boolean inrange = false;
    int pre_index = 0;
    for (int i = 0; i < str.length(); ++i) {
      if (str.charAt(i) == '"') {
        inrange = !inrange;
      } else if (str.charAt(i) == ',' && !inrange) {
        ret.add(GetString(str.substring(pre_index, i)));
        pre_index = i + 1;
      }
    }
    ret.add(GetString(str.substring(pre_index)));
    return ret.toArray(new String[ret.size()]);
  }

  // [1,2,-3]
  public static int[] GetInts(String str) {
    ArrayList<Integer> ret = GetArrayListInt(str);
    int[] z = new int[ret.size()];
    for (int i = 0; i < ret.size(); ++i) {
      z[i] = ret.get(i);
    }
    return z;
  }

  // [1,2,-3]
  public static double[] GetDoubles(String str) {
    ArrayList<Double> ret = GetArrayListDouble(str);
    double[] z = new double[ret.size()];
    for (int i = 0; i < ret.size(); ++i) {
      z[i] = ret.get(i);
    }
    return z;
  }

  // [1,2,-3]
  public static long[] GetLongs(String str) {
    ArrayList<Long> ret = GetArrayListLong(str);
    long[] z = new long[ret.size()];
    for (int i = 0; i < ret.size(); ++i) {
      z[i] = ret.get(i);
    }
    return z;
  }

  // [[1,2],[3,4]]
  public static int[][] GetIntss(String str) {
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return new int[0][0];
    }

    str = str.substring(1, str.length() - 1);
    int inrange = 0;
    int pre_index = 0;
    int count = 1;
    for (int i = 0; i < str.length(); ++i) {
      if (IsBeginRange(str.charAt(i))) {
        ++inrange;
      } else if (IsEndRange(str.charAt(i))) {
        --inrange;
      } else if (str.charAt(i) == ',' && inrange == 0) {
        ++count;
      }
    }

    int[][] ret = new int[count][];
    count = 0;
    for (int i = 0; i < str.length(); ++i) {
      if (IsBeginRange(str.charAt(i))) {
        ++inrange;
      } else if (IsEndRange(str.charAt(i))) {
        --inrange;
      } else if (str.charAt(i) == ',' && inrange == 0) {
        ret[count] = GetInts(str.substring(pre_index, i));
        ++count;
        pre_index = i + 1;
      }
    }
    ret[count] = GetInts(str.substring(pre_index));
    return ret;
  }

  public static TreeNode GetTreeNode(String str) {
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return null;
    }
    List<TreeNode> treeNodes = new ArrayList<TreeNode>();

    int current = 0;
    boolean isLeft = true;

    str = str.substring(1, str.length() - 1);
    String[] values = str.split(",", -1);
    for (String value : values) {
      value = value.trim();
      if (value.isEmpty()) {
        continue;
      } else if (value.equals("#")) {
        if (treeNodes.get(current) != null) {
          if (isLeft) {
            isLeft = false;
          } else if (treeNodes.size() > current + 1) {
            ++current;
            isLeft = true;
          }
        }
        continue;
      }

      TreeNode newNode = null;
      try {
        newNode = new TreeNode(GetInt(value));
        treeNodes.add(newNode);
      } catch (Exception e) {
        continue;
      }

      /* 第一个节点 */
      if (treeNodes.size() == 1) {
        current = 0;
        isLeft = true;
      } else {
        if (isLeft) {
          treeNodes.get(current).left = newNode;
          isLeft = false;
        } else {
          treeNodes.get(current).right = newNode;
          ++current;
          isLeft = true;
        }
      }
    }
    return treeNodes.size() > 0 ? treeNodes.get(0) : null;
  }

  public static void Print(boolean b) {
    if (b) {
      System.out.println("true");
    } else {
      System.out.println("false");
    }
  }

  public static void Print(char[] x) {
    if (x == null) {
      System.out.print("null\n");
      return;
    }
    System.out.print("[");
    for (int i = 0; i < x.length; ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      System.out.print(x[i]);
    }
    System.out.print("]");
    System.out.print("\n");
  }

  public static void Print(char[][] vv) {
    if (vv == null) {
      System.out.print("null\n");
      return;
    }
    System.out.print("[");
    for (int i = 0; i < vv.length; ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      char[] v = vv[i];
      for (int j = 0; j < v.length; ++j) {
        System.out.print(v[j]);
      }
    }
    System.out.print("]\n");
  }

  public static void Print(double d) {
    System.out.println(new DecimalFormat("0.00000").format(d));
  }

  public static void Print(int x) {
    System.out.println(x);
  }
  
  public static void Print(long x) {
    System.out.println(x);
  }

  public static void Print(int A[]) {
    if (A == null) {
      System.out.print("null\n");
      return;
    }
    Print(A, A.length);
  }

  public static void Print(int A[], int num) {
    PrintInterval(A, num);
    System.out.print("\n");
  }

  public static void Print(List<Integer> array) {
    PrintInterval(array, array.size());
    System.out.print("\n");
  }

  public static void PrintInterval(List<Integer> A, int num) {
    if (A == null) {
      System.out.print("null");
      return;
    }
    System.out.print("[");
    for (int i = 0; i < num && i < A.size(); ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      System.out.print(A.get(i));
    }
    System.out.print("]");
  }

  public static void PrintInterval(int A[], int num) {
    System.out.print("[");
    for (int i = 0; i < num && i < A.length; ++i) {
      if (i == 0) {
        System.out.print(A[i]);
      } else {
        System.out.print(",");
        System.out.print(A[i]);
      }
    }
    System.out.print("]");
  }

  public static void Print(ListNode head) {
    PrintListNode(head);
    System.out.print("\n");
  }

  public static void Print(RandomListNode head) {
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
    System.out.print("}\n");
  }

  public static void PrintInterval(String str) {
    if (str != null) {
      System.out.printf("\"%s\"", str);
    } else {
      System.out.print("null");
    }
  }

  public static void Print(String str) {
    PrintInterval(str);
    System.out.print("\n");
  }

  public static void Print(TreeLinkNode root) {
    System.out.print("{");
    ArrayList<TreeLinkNode> v = new ArrayList<TreeLinkNode>();
    if (root != null) {
      v.add(root);
    }
    int c = 0;
    String none = "";
    while (c < v.size()) {
      if (c == 0) {
        System.out.printf("%d,#", v.get(c).val);
        v.add(v.get(c).left);
        v.add(v.get(c).right);
      } else {
        if (v.get(c) != null) {
          if (v.get(c).next != null) {
            System.out.printf("%s,%d", none, v.get(c).val);
          } else {
            System.out.printf("%s,%d,#", none, v.get(c).val);
          }

          none = "";
          v.add(v.get(c).left);
          v.add(v.get(c).right);
        }
      }
      ++c;
    }
    System.out.print("}\n");
  }

  public static void Print(TreeNode root) {
    PrintTreeNode(root);
    System.out.print("\n");
  }

  public static void Print(UndirectedGraphNode root) {
    System.out.print("{");
    if (root != null) {
      Set<UndirectedGraphNode> nodes_set = new HashSet<UndirectedGraphNode>();
      Map<Integer, UndirectedGraphNode> nodesMap = new HashMap<Integer, UndirectedGraphNode>();
      ArrayList<UndirectedGraphNode> nodes = new ArrayList<UndirectedGraphNode>();
      nodes.add(root);
      nodes_set.add(root);
      nodesMap.put(root.label, root);
      for (int i = 0; i < nodes.size(); ++i) {
        for (int j = 0; j < nodes.get(i).neighbors.size(); ++j) {
          UndirectedGraphNode n_node = nodes.get(i).neighbors.get(j);
          if (!nodes_set.contains(n_node)) {
            nodes_set.add(n_node);
            nodes.add(n_node);
            nodesMap.put(n_node.label, n_node);
          }
        }
      }

      boolean first = true;
      // 根据label从小到大打印
      ArrayList<Integer> keys = new ArrayList<Integer>(nodesMap.keySet());
      Collections.sort(keys);
      for (Integer key : keys) {
        UndirectedGraphNode node = nodesMap.get(key);
        if (first) {
          first = false;
          System.out.print(node.label);
        } else {
          System.out.printf("#%d", node.label);
        }
        for (int j = 0; j < node.neighbors.size(); ++j) {
          System.out.printf(",%d", node.neighbors.get(j).label);
        }
      }

    }
    System.out.print("}\n");
  }

  public static void PrintAAInteger(ArrayList<ArrayList<Integer>> vv) {
    if (vv == null) {
      System.out.print("null\n");
      return;
    }

    System.out.print("[");
    for (int i = 0; i < vv.size(); ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      PrintAIntegerInternal(vv.get(i));
    }
    System.out.print("]\n");
  }

  public static void PrintAStrings(ArrayList<String[]> vv) {
    System.out.print("[");
    for (int i = 0; i < vv.size(); ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      PrintInterval(vv.get(i));
    }
    System.out.print("]\n");
  }

  public static void Print(int[][] vv) {
    if (vv == null) {
      System.out.print("null\n");
      return;
    }
    System.out.print("[");
    for (int i = 0; i < vv.length; ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      PrintInterval(vv[i], vv[i].length);
    }
    System.out.print("]\n");
  }

  public static void Print(String[] v) {
    if (v == null) {
      System.out.print("null\n");
      return;
    }
    PrintInterval(v);
    System.out.print("\n");
  }

  private static void PrintInterval(String[] v) {
    System.out.print("[");
    for (int i = 0; i < v.length; ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      PrintInterval(v[i]);
    }
    System.out.print("]");
  }

  public static void PrintAAString(ArrayList<ArrayList<String>> vvs) {
    if (vvs == null) {
      System.out.print("null\n");
      return;
    }
    System.out.print("[");
    for (int i = 0; i < vvs.size(); ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      PrintAStringInternal(vvs.get(i));
    }
    System.out.print("]\n");
  }

  public static void PrintAInteger(ArrayList<Integer> x) {
    if (x == null) {
      System.out.print("null\n");
      return;
    }
    PrintAIntegerInternal(x);
    System.out.print("\n");
  }

  private static void PrintAIntegerInternal(ArrayList<Integer> x) {
    if (x == null) {
      System.out.print("null\n");
      return;
    }
    System.out.print("[");
    for (int i = 0; i < x.size(); ++i) {
      if (i != 0) {
        System.out.printf(",%d", x.get(i));
      } else {
        System.out.print(x.get(i));
      }
    }
    System.out.print("]");
  }

  public static void PrintAInterval(ArrayList<Interval> x) {
    if (x == null) {
      System.out.print("null\n");
      return;
    }
    System.out.print("[");
    for (int i = 0; i < x.size(); ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      System.out.printf("[%d,%d]", x.get(i).start, x.get(i).end);
    }
    System.out.print("]\n");
  }

  public static void PrintAListNode(ArrayList<ListNode> v) {
    if (v == null) {
      System.out.print("null\n");
      return;
    }
    PrintAListNode(v, v.size());
  }

  public static void PrintAListNode(ArrayList<ListNode> A, int num) {
    System.out.print("[");
    for (int i = 0; i < A.size() && i < num; ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      Print(A.get(i));
    }
    System.out.print("]\n");
  }

  public static void PrintAString(ArrayList<String> x) {
    if (x == null) {
      System.out.print("null\n");
      return;
    }
    PrintAStringInternal(x);
    System.out.print("\n");
  }

  public static void PrintAStringInternal(ArrayList<String> x) {
    if (x == null) {
      System.out.print("null\n");
      return;
    }
    System.out.print("[");
    for (int i = 0; i < x.size(); ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      PrintInterval(x.get(i));
    }
    System.out.print("]");
  }

  public static void PrintATreeNode(ArrayList<TreeNode> v) {
    if (v == null) {
      System.out.print("null\n");
      return;
    }
    System.out.print("[");
    for (int i = 0; i < v.size(); ++i) {
      if (i != 0) {
        System.out.print(",");
      }
      PrintTreeNode(v.get(i));
    }
    System.out.print("]\n");
  }

  public static void PrintListNode(ListNode head) {
    ListNode current = head;
    System.out.print("{");
    while (current != null) {
      if (current == head) {
        System.out.print(current.val);
      } else {
        System.out.printf(",%d", current.val);
      }
      current = current.next;
    }
    System.out.print("}");
  }

  public static void PrintTreeNode(TreeNode root) {
    System.out.print("{");
    ArrayList<TreeNode> v = new ArrayList<TreeNode>();
    if (root != null) {
      v.add(root);
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
          System.out.printf("%s,%d", none, v.get(c).val);
          none = "";
          v.add(v.get(c).left);
          v.add(v.get(c).right);
        }
      }
      ++c;
    }
    System.out.print("}");
  }

  // [aa,bb,cc]
  public static char[][] GetCharss(String str) {
    ArrayList<String> vs = GetArrayListString(str);
    char[][] ret = new char[vs.size()][];
    for (int i = 0; i < vs.size(); ++i) {
      ret[i] = new char[vs.get(i).length()];
      for (int j = 0; j < vs.get(i).length(); ++j) {
        ret[i][j] = vs.get(i).charAt(j);
      }
    }
    return ret;
  }

  // [ [ 1 , 2 ] ,[ 3 , 4 , -6 ] ]
  public static ArrayList<ArrayList<Integer>> GetAArrayListInt(String str) {
    ArrayList<ArrayList<Integer>> ret = new ArrayList<ArrayList<Integer>>();
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = str.substring(1, str.length() - 1);
    int inrange = 0;
    int pre_index = 0;
    for (int i = 0; i < str.length(); ++i) {
      if (IsBeginRange(str.charAt(i))) {
        ++inrange;
      } else if (IsEndRange(str.charAt(i))) {
        --inrange;
      } else if (str.charAt(i) == ',' && inrange == 0) {
        ret.add(GetArrayListInt(str.substring(pre_index, i)));
        pre_index = i + 1;
      }
    }
    ret.add(GetArrayListInt(str.substring(pre_index)));
    return ret;
  }

  // [[z,ed,kk],[ab,dd,zz]]
  public static ArrayList<ArrayList<String>> GetAArrayListString(String str) {
    ArrayList<ArrayList<String>> ret = new ArrayList<ArrayList<String>>();
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = str.substring(1, str.length() - 1);
    int inrange = 0;
    int pre_index = 0;
    for (int i = 0; i < str.length(); ++i) {
      if (IsBeginRange(str.charAt(i))) {
        ++inrange;
      } else if (IsEndRange(str.charAt(i))) {
        --inrange;
      } else if (str.charAt(i) == ',' && inrange == 0) {
        ret.add(GetArrayListString(str.substring(pre_index, i)));
        pre_index = i + 1;
      }
    }
    ret.add(GetArrayListString(str.substring(pre_index)));
    return ret;
  }

  // 支持[1,2,3,-4,5]
  // [,,] . 空
  // [] . 空
  public static ArrayList<Integer> GetArrayListInt(String str) {
    ArrayList<Integer> ret = new ArrayList<Integer>();
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = str.substring(1, str.length() - 1);
    String[] values = str.split(",", -1);
    for (String value : values) {
      ret.add(GetInt(value));
    }
    return ret;
  }

  // 支持[1,2,3,-4,5]
  // [,,] . 空
  // [] . 空
  public static ArrayList<Long> GetArrayListLong(String str) {
    ArrayList<Long> ret = new ArrayList<Long>();
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = str.substring(1, str.length() - 1);
    String[] values = str.split(",", -1);
    for (String value : values) {
      ret.add(GetLong(value));
    }
    return ret;
  }

  // 支持[1,2,3,-4,5]
  // [,,] . 空
  // [] . 空
  public static ArrayList<Double> GetArrayListDouble(String str) {
    ArrayList<Double> ret = new ArrayList<Double>();
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = str.substring(1, str.length() - 1);
    String[] values = str.split(",", -1);
    for (String value : values) {
      ret.add(GetDouble(value));
    }
    return ret;
  }

  // [{1,2,3},{1,2}]
  public static ArrayList<ListNode> GetArrayListListNode(String str) {
    ArrayList<ListNode> ret = new ArrayList<ListNode>();
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }
    str = str.substring(1, str.length() - 1);

    int inrange = 0;
    int pre_index = 0;
    for (int i = 0; i < str.length(); ++i) {
      if (IsBeginRange(str.charAt(i))) {
        ++inrange;
      } else if (IsEndRange(str.charAt(i))) {
        --inrange;
      } else if (str.charAt(i) == ',' && inrange == 0) {
        ret.add(GetListNode(str.substring(pre_index, i)));
        pre_index = i + 1;
      }
    }
    ret.add(GetListNode(str.substring(pre_index)));
    return ret;
  }

  // [(1,2),(1,3)]
  public static Point[] GetPoints(String str) {
    ArrayList<Point> ret = new ArrayList<Point>();
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return (Point[]) ret.toArray(new Point[ret.size()]);
    }

    str = str.substring(1, str.length() - 1);
    int inrange = 0;
    int pre_index = 0;
    for (int i = 0; i < str.length(); ++i) {
      if (IsBeginRange(str.charAt(i))) {
        ++inrange;
      } else if (IsEndRange(str.charAt(i))) {
        --inrange;
      } else if (str.charAt(i) == ',' && inrange == 0) {
        Interval interval = GetInterval(str.substring(pre_index, i));
        ret.add(new Point(interval.start, interval.end));
        pre_index = i + 1;
      }
    }
    Interval interval = GetInterval(str.substring(pre_index));
    ret.add(new Point(interval.start, interval.end));
    return (Point[]) ret.toArray(new Point[ret.size()]);
  }

  // [abc,def,,kk],["a","bdd","cc"]
  public static ArrayList<String> GetArrayListString(String str) {
    ArrayList<String> ret = new ArrayList<String>();
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = str.substring(1, str.length() - 1);
    String[] values = str.split(",", -1);
    for (String value : values) {
      ret.add(GetString(value));
    }
    return ret;
  }

  public static double GetDouble(String str) {
    return Double.parseDouble(str);
  }

  // {1,2,3}
  public static ListNode GetListNode(String str) {
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return null;
    }
    str = str.substring(1, str.length() - 1);
    ListNode head = null;
    ListNode current = null;
    String[] values = str.split(",", -1);
    for (String value : values) {
      if (current == null && head == null) {
        head = new ListNode(GetInt(value));
        current = head;
      } else {
        current.next = new ListNode(GetInt(value));
        current = current.next;
      }
    }
    return head;
  }

  // { -1, 8, 7, -3,4,4,-3,#,#,-1}
  // 分为两段，前部分为ListNode,后半部分如果random==null是#，否则就是random.val
  public static RandomListNode GetRandomListNode(String str) {
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return null;
    }
    str = str.substring(1, str.length() - 1);
    RandomListNode head = null;
    RandomListNode current = null;
    Map<Integer, RandomListNode> nodesMap = new HashMap<Integer, RandomListNode>();
    // 先统计总共有多少个元素
    String[] values = str.split(",", -1);
    for (int i = 0; i < values.length / 2; ++i) {
      if (head == null && current == null) {
        head = new RandomListNode(GetInt(values[i]));
        current = head;
      } else {
        current.next = new RandomListNode(GetInt(values[i]));
        current = current.next;
      }
      nodesMap.put(current.label, current);
    }

    current = head;
    for (int i = values.length / 2; i < values.length; ++i) {
      if (!values[i].equals("#")) {
        current.random = nodesMap.get(GetInt(values[i]));
      }
      current = current.next;
    }
    return head;
  }

  // ["aaa","dd","fff","","dfd"]
  public static HashSet<String> GetHashSetString(String str) {
    HashSet<String> ret = new HashSet<String>();
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = str.substring(1, str.length() - 1);
    boolean inrange = false;
    int pre_index = 0;
    for (int i = 0; i < str.length(); ++i) {
      if (str.charAt(i) == '"') {
        inrange = !inrange;
      } else if (str.charAt(i) == ',' && !inrange) {
        ret.add(GetString(str.substring(pre_index, i)));
        pre_index = i + 1;
      }
    }
    ret.add(GetString(str.substring(pre_index)));
    return ret;
  }

  public static TreeLinkNode GetTreeLinkNode(String str) {
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return null;
    }

    List<TreeLinkNode> treeNodes = new ArrayList<TreeLinkNode>();
    str = str.substring(1, str.length() - 1);
    int current = 0;
    boolean isLeft = true;

    String[] values = str.split(",", -1);
    for (String value : values) {
      value = value.trim();
      if (value.isEmpty()) {
        continue;
      } else if (value.equals("#")) {
        if (treeNodes.get(current) != null) {
          if (isLeft) {
            isLeft = false;
          } else if (treeNodes.size() > current + 1) {
            ++current;
            isLeft = true;
          }
        }
        continue;
      }

      TreeLinkNode newNode = null;
      try {
        newNode = new TreeLinkNode(GetInt(value));
        treeNodes.add(newNode);
      } catch (Exception e) {
        continue;
      }

      /* 第一个节点 */
      if (treeNodes.size() == 1) {
        current = 0;
        isLeft = true;
      } else {
        if (isLeft) {
          treeNodes.get(current).left = newNode;
          isLeft = false;
        } else {
          treeNodes.get(current).right = newNode;
          ++current;
          isLeft = true;
        }
      }
    }
    return treeNodes.size() > 0 ? treeNodes.get(0) : null;
  }

  public static UndirectedGraphNode GetUndirectedGraphNode(String str) {
    UndirectedGraphNode ret = null;
    str = str == null ? null : str.trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }
    str = str.substring(1, str.length() - 1);
    String[] nodeStrs = str.split("#");

    Map<Integer, UndirectedGraphNode> nodesMap = new HashMap<Integer, UndirectedGraphNode>();

    // 把所有的点构造出来
    for (int i = 0; i < nodeStrs.length; ++i) {
      String[] v = nodeStrs[i].split(",");
      if (v.length < 1) {
        continue;
      }
      if (!nodesMap.containsKey(v[0])) {
        UndirectedGraphNode node = new UndirectedGraphNode(GetInt(v[0]));
        nodesMap.put(node.label, node);
        if (ret == null) {
          ret = node;
        }
      }
    }

    // 把各个边连接起来
    for (int i = 0; i < nodeStrs.length; ++i) {
      String[] v = nodeStrs[i].split(",");
      if (v.length < 1) {
        continue;
      }
      UndirectedGraphNode node = nodesMap.get(GetInt(v[0]));
      for (int j = 1; j < v.length; ++j) {
        node.neighbors.add(nodesMap.get(GetInt(v[j])));
      }
    }
    return ret;
  }

  public static Interval Print(Interval interval) {
    System.out.printf("[%d,%d]\n", interval.start, interval.end);
    return interval;
  }

  public static Interval TCPrint(Interval interval) {
    System.out.printf("{%d, %d}\n", interval.start, interval.end);
    return interval;
  }

  public static void TCPrint(boolean b) {
    if (b) {
      System.out.println("true");
    } else {
      System.out.println("false");
    }
  }

  public static void TCPrint(char[] x) {
    System.out.print("{");
    for (int i = 0; i < x.length; ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      System.out.print(x[i]);
    }
    System.out.print("}\n");
  }

  public static void TCPrint(char[][] vv) {
    System.out.print("{");
    for (int i = 0; i < vv.length; ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      char[] v = vv[i];
      for (int j = 0; j < v.length; ++j) {
        System.out.print(v[j]);
      }
    }
    System.out.print("}\n");
  }

  public static void TCPrint(double d) {
    System.out.println(new DecimalFormat("0.00000").format(d));
  }

  public static void TCPrint(int x) {
    System.out.println(x);
  }
  
  public static void TCPrint(long x) {
    System.out.println(x);
  }
  
  public static void TCPrint(int A[]) {
    TCPrint(A, A.length);
  }

  public static void TCPrint(int A[], int num) {
    TCPrintInterval(A, num);
    System.out.print("\n");
  }

  public static void TCPrint(List<Integer> array) {
    TCPrintInterval(array, array.size());
    System.out.print("\n");
  }

  public static void TCPrintInterval(List<Integer> A, int num) {
    System.out.print("{");
    for (int i = 0; i < num && i < A.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      System.out.print(A.get(i));
    }
    System.out.print("}");
  }

  public static void TCPrintInterval(long A[], int num) {
    System.out.print("{");
    for (int i = 0; i < num && i < A.length; ++i) {
      if (i == 0) {
        System.out.print(A[i]);
      } else {
        System.out.print(", ");
        System.out.print(A[i]);
      }
    }
    System.out.print("}");
  }

  public static void TCPrintInterval(double A[], int num) {
    System.out.print("{");
    for (int i = 0; i < num && i < A.length; ++i) {
      if (i == 0) {
        TCPrint(A[i]);
      } else {
        System.out.print(", ");
        TCPrint(A[i]);
      }
    }
    System.out.print("}");
  }

  public static void TCPrintInterval(int A[], int num) {
    System.out.print("{");
    for (int i = 0; i < num && i < A.length; ++i) {
      if (i == 0) {
        System.out.print(A[i]);
      } else {
        System.out.print(", ");
        System.out.print(A[i]);
      }
    }
    System.out.print("}");
  }

  public static void TCPrint(String str) {
    TCPrintInterval(str);
    System.out.print("\n");
  }

  public static void TCPrintAAInteger(ArrayList<ArrayList<Integer>> vv) {
    System.out.print("{");
    for (int i = 0; i < vv.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      TCPrintAIntegerInternal(vv.get(i));
    }
    System.out.print("}\n");
  }

  public static void TCPrintAStrings(ArrayList<String[]> vv) {
    System.out.print("{");
    for (int i = 0; i < vv.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      TCPrintInterval(vv.get(i));
    }
    System.out.print("}\n");
  }

  public static void TCPrint(int[][] vv) {
    System.out.print("{");
    for (int i = 0; i < vv.length; ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      TCPrintInterval(vv[i], vv[i].length);
    }
    System.out.print("}\n");
  }

  public static void TCPrint(String[] v) {
    TCPrintInterval(v);
    System.out.print("\n");
  }

  public static void TCPrint(long[] vs) {
    TCPrintInterval(vs, vs.length);
    System.out.print("\n");
  }

  public static void TCPrint(double[] vs) {
    TCPrintInterval(vs, vs.length);
    System.out.print("\n");
  }

  public static void TCPrintInterval(String str) {
    if (str != null) {
      System.out.printf("\"%s\"", str);
    } else {
      System.out.print("null");
    }
  }

  private static void TCPrintInterval(String[] v) {
    System.out.print("{");
    for (int i = 0; i < v.length; ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      TCPrintInterval(v[i]);
    }
    System.out.print("}");
  }

  public static void TCPrintAAString(ArrayList<ArrayList<String>> vvs) {
    System.out.print("{");
    for (int i = 0; i < vvs.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      TCPrintAStringInternal(vvs.get(i));
    }
    System.out.print("}\n");
  }

  public static void TCPrintAInteger(ArrayList<Integer> x) {
    TCPrintAIntegerInternal(x);
    System.out.print("\n");
  }

  private static void TCPrintAIntegerInternal(ArrayList<Integer> x) {
    System.out.print("{");
    for (int i = 0; i < x.size(); ++i) {
      if (i != 0) {
        System.out.printf(", %d", x.get(i));
      } else {
        System.out.print(x.get(i));
      }
    }
    System.out.print("}");
  }

  public static void TCPrintAInterval(ArrayList<Interval> x) {
    System.out.print("{");
    for (int i = 0; i < x.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      System.out.printf("{%d, %d}", x.get(i).start, x.get(i).end);
    }
    System.out.print("}\n");
  }

  public static void TCPrintAString(ArrayList<String> x) {
    TCPrintAStringInternal(x);
    System.out.print("\n");
  }

  public static void TCPrintAStringInternal(ArrayList<String> x) {
    System.out.print("{");
    for (int i = 0; i < x.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      TCPrintInterval(x.get(i));
    }
    System.out.print("}");
  }
}
