# -*- coding: UTF-8 -*-
import sys

class ncout:
    def write(self, output_stream):
        return

def IsBeginRange(c):
    return c == '{' or c == '[' or c == '('

def IsEndRange(c):
    return c == '' or c == ']' or c == ')' or c == '}'

def IsValidRange(str):
    return IsBeginRange(str[0]) and IsEndRange(str[len(str) - 1])

def IsEmptyRange(str):
    return str == None or str == "[]" or str == "()" or str == "{"

def SubString(str, start, end=0):
    return str[start:] if end == 0 else str[start:end]

def GetArguments(line, arg_count):
    ret = []
    if line == None:
        return ret
    
    inrange = 0
    pre_index = 0
    inmao = False
    for i in xrange(len(line)):
        if IsBeginRange(line[i]) and not inmao:
            inrange = inrange+1
        elif IsEndRange(line[i]) and not inmao:
            inrange = inrange - 1
        elif line[i] == '\"':
            inmao = not inmao
        elif line[i] == ',' and inrange == 0 and not inmao:
            ret.append(SubString(line, pre_index, i))
            pre_index = i + 1
    
    ret.append(SubString(line, pre_index))
    return ret

# "abc", abc
def GetString(str):
    if (str <> None):
        str = str.strip()
   
    if (str == None or (not str.startswith('"')) or (not str.endswith('"'))):
        return "" if str == None else str
   
    return SubString(str, 1, len(str) - 1)

# char
def GetChar(str):
    return '#' if str == None or len(str) == 0 else str[0]


# 1
def GetInt(str):
    return int(str.strip())


# 1
def GetLong(str):
    return long(str.strip())

# ["a", "b", "ccc"]
def GetStrings(str):
    str = None if str == None else str.strip()
    if (str == None or not IsValidRange(str) or IsEmptyRange(str)):
        return []
   
    str = SubString(str, 1, len(str) - 1)
    ret = []
    inrange = False
    pre_index = 0
    for i in xrange(len(str)):
        if (str[i] == '"'):
            inrange = not inrange
        elif (str[i] == ',' and not inrange):
            ret.append(GetString(SubString(str, pre_index, i)))
            pre_index = i + 1
       
   
    ret.append(GetString(SubString(str, pre_index)))
    return ret


# [1,2,-3]
def GetInts(str):
    return GetArrayListInt(str)


# [1,2,-3]
def GetDoubles(str):
    return GetArrayListDouble(str)


# [1,2,-3]
def GetLongs(str):
    return GetArrayListLong(str)


# [[1,2],[3,4]]
def GetIntss(str):
    str = None if str == None else str.strip()
    if (str == None or not IsValidRange(str) or IsEmptyRange(str)):
        return []
   
    str = SubString(str, 1, len(str) - 1)
    inrange = 0
    pre_index = 0
    count = 1
    for i in xrange(len(str)):
        if (IsBeginRange(str[i])):
            inrange = inrange + 1
        elif (IsEndRange(str[i])):
            inrange = inrange - 1
        elif (str[i] == ',' and inrange == 0):
            count = count + 1
       
   

    ret = []
    for i in xrange(len(str)):
        if (IsBeginRange(str[i])):
            inrange = inrange + 1
        elif (IsEndRange(str[i])):
            inrange = inrange - 1
        elif (str[i] == ',' and inrange == 0):
            ret.append(GetInts(SubString(str, pre_index, i)))
            pre_index = i + 1

    ret.append(GetInts(SubString(str, pre_index)))
    return ret

def PrintBoolean(b):
    if (b):
        print("true")
    else:
        print("false")
   


def PrintCharArray(x):
    if (x == None):
        sys.stdout.write("None\n")
        return
   
    sys.stdout.write("{")
    for i in xrange(len(x)):
        if (i <> 0):
            sys.stdout.write(", ")
       
        sys.stdout.write(x[i])
   
    sys.stdout.write("}")
    sys.stdout.write("\n")


def PrintCharArrayArray(vv):
    if (vv == None):
        sys.stdout.write("None\n")
        return
   
    sys.stdout.write("{")
    for i in xrange(len(vv)):
        if (i <> 0):
            sys.stdout.write(", ")
       
        v = vv[i]
        for j in xrange(len(v)):
            sys.stdout.write(v[j])
       
   
    sys.stdout.write("}\n")


def PrintDouble(d):
    if abs(d) < 0.0000099999:
        print '0.00000'
    else:
        print '%0.5f' % d


def PrintInt(x):
    print(x)


def PrintLong(x):
    print(x)


def PrintIntArray(A):
    if (A == None):
        sys.stdout.write("None\n")
        return
   
    PrintIntervalListInt(A, len(A))
    sys.stdout.write("\n")


def Print(A, num):
    PrintInterval(A, num)
    sys.stdout.write("\n")


def PrintIntList(array):
    PrintInterval(array, len(len(array)))
    sys.stdout.write("\n")


def PrintIntervalListInt(A, num):
    if (A == None):
        sys.stdout.write("None")
        return
   
    sys.stdout.write("{")
    for i in xrange(min(num, len(A))):
        if (i <> 0):
            sys.stdout.write(", ")
        sys.stdout.write(str(A[i]))
   
    sys.stdout.write("}")


def PrintIntervalIntArray(A, num):
    sys.stdout.write("{")
    for i in xrange(min(num, len(A))):
        if (i == 0):
            sys.stdout.write(A[i])
        else:
            sys.stdout.write(", ")
            sys.stdout.write(A[i])
    sys.stdout.write("}")




def PrintIntervalString(str):
    if (str <> None):
        sys.stdout.write("\"")
        sys.stdout.write(str)
        sys.stdout.write("\"")
    else:
        sys.stdout.write("None")
   


def PrintString(str):
    PrintIntervalString(str)
    sys.stdout.write("\n")

def PrintAAInteger(vv):
    if (vv == None):
        sys.stdout.write("None\n")
        return
   

    sys.stdout.write("{")
    for i in xrange(len(vv)):
        if (i <> 0):
            sys.stdout.write(", ")
       
        PrintAIntegerInternal(vv[i])
   
    sys.stdout.write("}\n")

# ArrayList<String[]>
def PrintAStrings(vv):
    sys.stdout.write("{")
    for i in xrange(len(vv)):
        if (i <> 0):
            sys.stdout.write(", ")
       
        PrintIntervalStringArray(vv[i])
   
    sys.stdout.write("}\n")


def PrintIntArrayArray(vv):
    if (vv == None):
        sys.stdout.write("None\n")
        return
   
    sys.stdout.write("{")
    for i in xrange(len(vv)):
        if (i <> 0):
            sys.stdout.write(", ")
       
        PrintIntervalIntArray(vv[i], len(vv[i]))
   
    sys.stdout.write("}\n")


def PrintStringArray(v):
    if (v == None):
        sys.stdout.write("None\n")
        return
   
    PrintIntervalStringArray(v)
    sys.stdout.write("\n")


def PrintIntervalStringArray(v):
    sys.stdout.write("{")
    for i in xrange(len(v)):
        if (i <> 0):
            sys.stdout.write(", ")
       
        PrintIntervalString(v[i])
   
    sys.stdout.write("}")

#ArrayList<ArrayList<String>>
def PrintAAString(vvs):
    if (vvs == None):
        sys.stdout.write("None\n")
        return
   
    sys.stdout.write("{")
    for i in xrange(len(vvs)):
        if (i <> 0):
            sys.stdout.write(", ")
       
        PrintAStringInternal(vvs[i])
   
    sys.stdout.write("}\n")

#ArrayList<Integer>
def PrintAInteger(x):
    if (x == None):
        sys.stdout.write("None\n")
        return
   
    PrintAIntegerInternal(x)
    sys.stdout.write("\n")

# ArrayList<Integer>
def PrintAIntegerInternal( x):
    if (x == None):
        sys.stdout.write("None\n")
        return
   
    sys.stdout.write("{")
    for i in xrange(len(x)):
        if (i <> 0):
            sys.stdout.writef(",%d", x[i])
        else:
            sys.stdout.write(x[i])
       
   
    sys.stdout.write("}")

# ArrayList<Interval>
def PrintAInterval(x):
    if (x == None):
        sys.stdout.write("None\n")
        return
   
    sys.stdout.write("{")
    for i in xrange(len(x)):
        if (i <> 0):
            sys.stdout.write(", ")
       
        sys.stdout.writef("[%d,%d]", x[i][0], x[i][1])
   
    sys.stdout.write("}\n")

# ArrayList<String>
def PrintAString(x):
    if (x == None):
        sys.stdout.write("None\n")
        return
   
    PrintAStringInternal(x)
    sys.stdout.write("\n")

#ArrayList<String>
def PrintAStringInternal(x):
    if (x == None):
        sys.stdout.write("None\n")
        return
   
    sys.stdout.write("{")
    for i in xrange(len(x)):
        if (i <> 0):
            sys.stdout.write(", ")
       
        PrintInterval(x[i])
   
    sys.stdout.write("}")

# [aa,bb,cc]
def GetCharss(str):
    vs = GetArrayListString(str)
    ret = []
    for i in xrange(len(vs)):
        ret.append([])
        for j in xrange(len(vs[i])):
            ret[i].append(vs[i][j])
    return ret


# [ [ 1 , 2 ] ,[ 3 , 4 , -6 ] ]
def GetAArrayListInt(str):
    ret = []
    str = None if str == None else str.strip()
    if (str == None or not IsValidRange(str) or IsEmptyRange(str)):
        return ret

    str = SubString(str, 1, len(str) - 1)
    inrange = 0
    pre_index = 0
    for i in xrange(len(str)):
        if (IsBeginRange(str[i])):
            inrange = inrange + 1
        elif (IsEndRange(str[i])):
            inrange = inrange - 1
        elif (str[i] == ',' and inrange == 0):
            ret.append(GetArrayListInt(SubString(str, pre_index, i)))
            pre_index = i + 1
       
   
    ret.append(GetArrayListInt(SubString(str, pre_index)))
    return ret


# [[z,ed,kk],[ab,dd,zz]]
def GetAArrayListString(str):
    ret = []
    str = None if str == None else str.strip()
    if (str == None or not IsValidRange(str) or IsEmptyRange(str)):
        return ret
   

    str = SubString(str, 1, len(str) - 1)
    inrange = 0
    pre_index = 0
    for i in xrange(len(str)):
        if (IsBeginRange(str[i])):
            inrange = inrange + 1
        elif (IsEndRange(str[i])):
            inrange = inrange - 1
        elif (str[i] == ',' and inrange == 0):
            ret.append(GetArrayListString(SubString(str, pre_index, i)))
            pre_index = i + 1
       
   
    ret.append(GetArrayListString(SubString(str, pre_index)))
    return ret


# 支持[1,2,3,-4,5]
# [,,] . 空
# [] . 空
def GetArrayListInt(str):
    ret = []
    str = None if str == None else str.strip()
    if (str == None or not IsValidRange(str) or IsEmptyRange(str)):
        return ret
   

    str = SubString(str, 1, len(str) - 1)
    values = str.split(", ", -1)
    for value in values:
        ret.append(GetInt(value))
   
    return ret


# 支持[1,2,3,-4,5]
# [,,] . 空
# [] . 空
def GetArrayListLong(str):
    ret = []
    str = None if str == None else str.strip()
    if (str == None or not IsValidRange(str) or IsEmptyRange(str)):
        return ret
   
    str = SubString(str, 1, len(str) - 1)
    values = str.split(", ", -1)
    for value in values:
        ret.append(GetLong(value))
   
    return ret


# 支持[1,2,3,-4,5]
# [,,] . 空
# [] . 空
def GetArrayListDouble(str):
    ret = []
    str = None if str == None else str.strip()
    if (str == None or not IsValidRange(str) or IsEmptyRange(str)):
        return ret
   

    str = SubString(str, 1, len(str) - 1)
    values = str.split(", ", -1)
    for value in values:
        ret.append(GetDouble(value))
   
    return ret


# [abc,def,,kk],["a", "bdd", "cc"]
def GetArrayListString(str):
    ret = []
    str = None if str == None else str.strip()
    if (str == None or not IsValidRange(str) or IsEmptyRange(str)):
        return ret
   
    str = SubString(str, 1, len(str) - 1)
    values = str.split(", ", -1)
    for value in values:
        ret.append(GetString(value))
   
    return ret


def GetDouble(str):
    return float(str.strip())


# ["aaa", "dd", "fff", "", "dfd"]
def GetHashSetString(str):
    ret = []
    str = None if str == None else str.strip()
    if (str == None or not IsValidRange(str) or IsEmptyRange(str)):
        return ret
   
    str = SubString(str, 1, len(str) - 1)
    inrange = False
    pre_index = 0
    for i in xrange(len(str)):
        if (str[i] == '"'):
            inrange = True if not inrange else False
        elif (str[i] == ',' and not inrange):
            ret.append(GetString(SubString(str, pre_index, i)))
            pre_index = i + 1
       
   
    ret.append(GetString(SubString(str, pre_index)))
    return set(ret)


def PrintInterval(interval):
    sys.stdout.writef("[%d,%d]\n", interval[0], interval[1])
    return interval

