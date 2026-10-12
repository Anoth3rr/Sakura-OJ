using System.Collections.Generic;
using System;

class TCTools
{
    private static string SubString(string str, int start, int end)
    {
        return str.Substring(start, end - start);
    }
    private static string SubString(string str, int start)
    {
        return str.Substring(start);
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
            if (IsBeginRange(line[i]) && !inmao)
            {
                ++inrange;
            }
            else if (IsEndRange(line[i]) && !inmao)
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
        return System.Int32.Parse(str.Trim());
    }

    // 1
    public static long GetLong(string str)
    {
        return System.Int64.Parse(str.Trim());
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
        List<System.Int32> ret = GetListInt(str);
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
        List<Double> ret = GetListDouble(str);
        double[] z = new double[ret.Count];
        for (int i = 0; i < ret.Count; ++i)
        {
            z[i] = ret[i];
        }
        return z;
    }

    // [1,2,-3]
    public static long[] GetLongs(string str)
    {
        List<Int64> ret = GetListLong(str);
        long[] z = new long[ret.Count];
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

    public static void Print(bool b)
    {
        if (b)
        {
            System.Console.WriteLine("true");
        }
        else
        {
            System.Console.WriteLine("false");
        }
    }

    public static void Print(char[] x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("{");
        for (int i = 0; i < x.Length; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(", ");
            }
            System.Console.Write(x[i]);
        }
        System.Console.Write("}");
        System.Console.Write("\n");
    }

    public static void Print(char[][] vv)
    {
        if (vv == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("{");
        for (int i = 0; i < vv.Length; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(", ");
            }
            char[] v = vv[i];
            for (int j = 0; j < v.Length; ++j)
            {
                System.Console.Write(v[j]);
            }
        }
        System.Console.Write("}\n");
    }

    public static void Print(double d)
    {
        if (Math.Abs(d) < 0.000009999999)
        {
            System.Console.WriteLine("0.00000");
        }
        else
        {
            System.Console.WriteLine(d.ToString("0.00000"));
        }
    }

    public static void Print(int x)
    {
        System.Console.WriteLine(x);
    }

    public static void Print(char c)
    {
        System.Console.WriteLine(c);
    }

    public static void Print(long x)
    {
        System.Console.WriteLine(x);
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

    public static void Print(long[] A)
    {
        if (A == null)
        {
            System.Console.Write("null\n");
            return;
        }
        Print(A, A.Length);
    }

    public static void Print(double[] A)
    {
        if (A == null)
        {
            System.Console.Write("null\n");
            return;
        }
        Print(A, A.Length);
    }

    public static void Print(long[] A, int num)
    {
        PrintInterval(A, num);
        System.Console.Write("\n");
    }

    public static void Print(double[] A, int num)
    {
        PrintInterval(A, num);
        System.Console.Write("\n");
    }

    public static void PrintInterval(List<System.Int32> A, int num)
    {
        if (A == null)
        {
            System.Console.Write("null");
            return;
        }
        System.Console.Write("{");
        for (int i = 0; i < num && i < A.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(", ");
            }
            System.Console.Write(A[i]);
        }
        System.Console.Write("}");
    }

    public static void PrintInterval(int[] A, int num)
    {
        System.Console.Write("{");
        for (int i = 0; i < num && i < A.Length; ++i)
        {
            if (i == 0)
            {
                System.Console.Write(A[i]);
            }
            else
            {
                System.Console.Write(", ");
                System.Console.Write(A[i]);
            }
        }
        System.Console.Write("}");
    }

    public static void PrintInterval(long[] A, int num)
    {
        System.Console.Write("{");
        for (int i = 0; i < num && i < A.Length; ++i)
        {
            if (i == 0)
            {
                System.Console.Write(A[i]);
            }
            else
            {
                System.Console.Write(", ");
                System.Console.Write(A[i]);
            }
        }
        System.Console.Write("}");
    }

    public static void PrintInterval(double[] A, int num)
    {
        System.Console.Write("{");
        for (int i = 0; i < num && i < A.Length; ++i)
        {
            if (i == 0)
            {
                Print(A[i]);
            }
            else
            {
                System.Console.Write(", ");
                System.Console.Write(A[i]);
            }
        }
        System.Console.Write("}");
    }


    public static void PrintInterval(string str)
    {
        if (str != null)
        {
            System.Console.Write("\"{0}\"", str);
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

    public static void PrintAAInt32(List<List<System.Int32>> vv)
    {
        if (vv == null)
        {
            System.Console.Write("null\n");
            return;
        }

        System.Console.Write("{");
        for (int i = 0; i < vv.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(", ");
            }
            PrintAInt32Internal(vv[i]);
        }
        System.Console.Write("}\n");
    }

    public static void Print(int[][] vv)
    {
        if (vv == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("{");
        for (int i = 0; i < vv.Length; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(", ");
            }
            PrintInterval(vv[i], vv[i].Length);
        }
        System.Console.Write("}\n");
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
        System.Console.Write("{");
        for (int i = 0; i < v.Length; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(", ");
            }
            PrintInterval(v[i]);
        }
        System.Console.Write("}");
    }

    public static void PrintAAstring(List<List<string>> vvs)
    {
        if (vvs == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("{");
        for (int i = 0; i < vvs.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(", ");
            }
            PrintAstringInternal(vvs[i]);
        }
        System.Console.Write("}\n");
    }

    public static void PrintAInt32(List<System.Int32> x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        PrintAInt32Internal(x);
        System.Console.Write("\n");
    }

    private static void PrintAInt32Internal(List<System.Int32> x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("{");
        for (int i = 0; i < x.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(",%d", x[i]);
            }
            else
            {
                System.Console.Write(x[i]);
            }
        }
        System.Console.Write("}");
    }


    public static void PrintAstring(List<string> x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        PrintAstringInternal(x);
        System.Console.Write("\n");
    }

    public static void PrintAstringInternal(List<string> x)
    {
        if (x == null)
        {
            System.Console.Write("null\n");
            return;
        }
        System.Console.Write("{");
        for (int i = 0; i < x.Count; ++i)
        {
            if (i != 0)
            {
                System.Console.Write(", ");
            }
            PrintInterval(x[i]);
        }
        System.Console.Write("}");
    }

    // [aa,bb,cc]
    public static char[][] GetCharss(string str)
    {
        List<string> vs = GetListString(str);
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
    public static List<List<System.Int32>> GetAListInt(string str)
    {
        List<List<System.Int32>> ret = new List<List<System.Int32>>();
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
                ret.Add(GetListInt(SubString(str, pre_index, i)));
                pre_index = i + 1;
            }
        }
        ret.Add(GetListInt(SubString(str, pre_index)));
        return ret;
    }

    // [[z,ed,kk],[ab,dd,zz]]
    public static List<List<string>> GetAListstring(string str)
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
                ret.Add(GetListString(SubString(str, pre_index, i)));
                pre_index = i + 1;
            }
        }
        ret.Add(GetListString(SubString(str, pre_index)));
        return ret;
    }

    // 支持[1,2,3,-4,5]
    // [,,] . 空
    // [] . 空
    public static List<System.Int32> GetListInt(string str) {
    List<System.Int32> ret = new List<System.Int32>();
    str = str == null ? null : str.Trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = SubString(str, 1, str.Length - 1);
    string[] values = str.Split(',');
    foreach (string value in values) {
      ret.Add(GetInt(value));
    }
    return ret;
  }

    // 支持[1,2,3,-4,5]
    // [,,] . 空
    // [] . 空
    public static List<Int64> GetListLong(string str) {
    List<Int64> ret = new List<Int64>();
    str = str == null ? null : str.Trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = SubString(str, 1, str.Length - 1);
    string[] values = str.Split(',');
    foreach (string value in values) {
      ret.Add(GetLong(value));
    }
    return ret;
  }

    // 支持[1,2,3,-4,5]
    // [,,] . 空
    // [] . 空
    public static List<Double> GetListDouble(string str) {
    List<Double> ret = new List<Double>();
    str = str == null ? null : str.Trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
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


    // [abc,def,,kk],["a","bdd","cc"]
    public static List<string> GetListString(string str) {
    List<string> ret = new List<string>();
    str = str == null ? null : str.Trim();
    if (str == null || !IsValidRange(str) || IsEmptyRange(str)) {
      return ret;
    }

    str = SubString(str, 1, str.Length - 1);
    string[] values = str.Split(',');
    foreach (string value in values) {
      ret.Add(GetString(value));
    }
    return ret;
  }

    public static double GetDouble(string str)
    {
        return Double.Parse(str);
    }


    // ["aaa","dd","fff","","dfd"]
    public static HashSet<string> GetHashSetstring(string str)
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
}
