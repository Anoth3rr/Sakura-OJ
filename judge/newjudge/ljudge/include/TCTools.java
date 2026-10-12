import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class TCTools {
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
    System.out.print("{");
    for (int i = 0; i < x.length; ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      System.out.print(x[i]);
    }
    System.out.print("}");
    System.out.print("\n");
  }

  public static void Print(char[][] vv) {
    if (vv == null) {
      System.out.print("null\n");
      return;
    }
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

  public static void Print(double d) {
    if (Math.abs(d) < 0.0000099999) {
        System.out.println("0.00000");
    } else {
        System.out.println(new DecimalFormat("0.00000").format(d));
    }
  }

  public static void Print(int x) {
    System.out.println(x);
  }

  public static void Print(char c) {
    System.out.println(c);
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

  public static void Print(double A[]) {
    if (A == null) {
      System.out.print("null\n");
      return;
    }
    Print(A, A.length);
  }

  public static void Print(long A[]) {
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

  public static void Print(long A[], int num) {
    PrintInterval(A, num);
    System.out.print("\n");
  }

  public static void Print(double A[], int num) {
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
    System.out.print("{");
    for (int i = 0; i < num && i < A.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      System.out.print(A.get(i));
    }
    System.out.print("}");
  }

  public static void PrintInterval(int A[], int num) {
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

  public static void PrintInterval(long A[], int num) {
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

  public static void PrintInterval(double A[], int num) {
    System.out.print("{");
    for (int i = 0; i < num && i < A.length; ++i) {
      if (i == 0) {
	Print(A[i]);
      } else {
        System.out.print(", ");
        System.out.print(A[i]);
      }
    }
    System.out.print("}");
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

  public static void PrintAAInteger(ArrayList<ArrayList<Integer>> vv) {
    if (vv == null) {
      System.out.print("null\n");
      return;
    }

    System.out.print("{");
    for (int i = 0; i < vv.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      PrintAIntegerInternal(vv.get(i));
    }
    System.out.print("}\n");
  }

  public static void PrintAStrings(ArrayList<String[]> vv) {
    System.out.print("{");
    for (int i = 0; i < vv.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      PrintInterval(vv.get(i));
    }
    System.out.print("}\n");
  }

  public static void Print(int[][] vv) {
    if (vv == null) {
      System.out.print("null\n");
      return;
    }
    System.out.print("{");
    for (int i = 0; i < vv.length; ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      PrintInterval(vv[i], vv[i].length);
    }
    System.out.print("}\n");
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
    System.out.print("{");
    for (int i = 0; i < v.length; ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      PrintInterval(v[i]);
    }
    System.out.print("}");
  }

  public static void PrintAAString(ArrayList<ArrayList<String>> vvs) {
    if (vvs == null) {
      System.out.print("null\n");
      return;
    }
    System.out.print("{");
    for (int i = 0; i < vvs.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      PrintAStringInternal(vvs.get(i));
    }
    System.out.print("}\n");
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
    System.out.print("{");
    for (int i = 0; i < x.size(); ++i) {
      if (i != 0) {
        System.out.printf(",%d", x.get(i));
      } else {
        System.out.print(x.get(i));
      }
    }
    System.out.print("}");
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
    System.out.print("{");
    for (int i = 0; i < x.size(); ++i) {
      if (i != 0) {
        System.out.print(", ");
      }
      PrintInterval(x.get(i));
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
}
