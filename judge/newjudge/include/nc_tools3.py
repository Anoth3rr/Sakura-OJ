# -*- coding: utf-8 -*-
import sys
import json
import traceback
import ncpy_link_module


class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None


class Interval:
    def __init__(self, a=0, b=0):
        self.start = a
        self.end = b


class Point:
    def __init__(self, a=0, b=0):
        self.x = a
        self.y = b


class TreeLinkNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None
        self.next = None


class RandomListNode:
    def __init__(self, x):
        self.label = x
        self.next = None
        self.random = None


class UndirectedGraphNode:
    def __init__(self, x):
        self.label = x
        self.neighbors = []


class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None


LEFT = 0
RIGHT = 1


class ncout:
    def write(self, output_stream):
        return


def IsBeginRange(c):
    return c == '{' or c == '[' or c == '('


def IsEndRange(c):
    return c == '' or c == ']' or c == ')' or c == '}'


# def GetArguments(line):
#     ret = []
#     if line == None:
#         return ret
#     inrange = 0
#     pre_index = 0
#     inmao = False
#     for i in range(len(line)):
#         if IsBeginRange(line[i]) and not inmao:
#             inrange = inrange + 1
#         elif IsEndRange(line[i]) and not inmao:
#             inrange = inrange - 1
#         elif line[i] == '"':
#             inmao = not inmao
#         elif line[i] == ',' and inrange == 0 and not inmao:
#             ret.append(line[pre_index:i])
#             pre_index = i + 1
#
#     ret.append(line[pre_index:])
#     return ret
#
#
# def GetRangeItems(string):
#     if string == None:
#         return []
#
#     begin = 0
#     while (not IsBeginRange(string[begin])) and begin < len(string):
#         begin = begin + 1
#     end = len(string)
#     while (not IsEndRange(string[end - 1])) and end > 1:
#         end = end - 1
#     string = string[begin + 1: end - 1]
#     return [] if len(string.strip()) == 0 else GetArguments(string)

# def GetArguments(line):
#     ret = []
#     if line == None:
#         return ret
#     inrange = 0
#     pre_index = 0
#     inmao = False
#     i = 0
#     for c in line:
#         if inmao == 0:
#             if c not in '{[(",)]}':
#                 i += 1
#                 continue
#             if c in '{[(':
#                 inrange = inrange - 1
#
#             elif c in '})]':
#                 inrange = inrange + 1
#             elif c == '"':
#                 inmao = 1 - inmao
#             elif c == ',' and inrange == 0:
#                 ret.append(line[pre_index:i])
#                 pre_index = i + 1
#         else:
#             if c == '"':
#                 inmao = 1 - inmao
#         i += 1
#     ret.append(line[pre_index:])
#     return ret

def GetArguments(line):
    line = line.strip()
    # ret = ncpy_link_module.GetArguments(line)
    return ncpy_link_module.GetArguments(line)


def GetRangeItems(string):
    # ret = ncpy_link_module.GetRangeItems(string)
    return ncpy_link_module.GetRangeItems(string)
    # if string == None:
    #     return []
    #
    # begin = 0
    # while (not string[begin] in '{[(') and begin < len(string):
    #     begin = begin + 1
    # end = len(string)
    # while (not string[end - 1] in '})]') and end > 1:
    #     end = end - 1
    # string = string[begin + 1: end - 1]
    # return [] if len(string.strip()) == 0 else GetArguments(string)


def GetInt(string):
    try:
        return 0 if string is None else int(string)
    except:
        return 0


def PrintIntInternal(x):
    # 为空或者不为整形
    if x is None or not isinstance(x, int):
        sys.stdout.write("null")
        return
    sys.stdout.write('%d' % x)


def GetLong(string):
    try:
        # python3 has no long
        return 0 if string is None else int(string)
    except:
        return 0


def PrintLongInternal(x):
    if x is None:
        sys.stdout.write("null")
        return
    sys.stdout.write('%ld' % x)


def GetFloat(string):
    try:
        return 0 if string is None else float(string)
    except:
        return 0


def PrintFloatInternal(x):
    if x is None or (not isinstance(x, float) and not isinstance(x, int)):
        sys.stdout.write("null")
        return
    if abs(x) < 0.000009999999:
        sys.stdout.write("0.00000")
    else:
        sys.stdout.write('%0.5f' % x)


def GetDouble(string):
    try:
        return 0 if string is None else float(string)
    except:
        return 0


def PrintDoubleInternal(x):
    PrintFloatInternal(x)


def GetString(string):
    # ret = ncpy_link_module.GetString(string)
    if string is None:
        return None
    else:
        string = string.strip()
    if len(string) == 0:
        return ""
    return ncpy_link_module.GetString(string)
    # if string == None:
    #     return None
    # else:
    #     string = string.strip()
    # if len(string) == 0:
    #     return ""
    # return string[1:-1] if string[0] == '"' and string[-1] == '"' else string


def PrintStringInternal(string):
    if string == None:
        sys.stdout.write("null")
    else:
        sys.stdout.write('"%s"' % string)


def GetChar(string):
    return '#' if string is None or len(string.strip()) == 0 else string.strip()[0]


def PrintCharInternal(c):
    sys.stdout.write(c)


def GetBool(string):
    return False if string is None else string.strip().lower() == 'true'


def PrintBoolInternal(b):
    if b is None:
        sys.stdout.write("null")
    elif b:
        sys.stdout.write("true")
    else:
        sys.stdout.write("false")


def GetInterval(string):
    items = json.loads(string)
    if len(items) == 2:
        return Interval(items[0], items[1])
    else:
        return Interval(0, 0)


def PrintIntervalInternal(interval):
    if interval is None:
        sys.stdout.write("[]")
        return
    sys.stdout.write("[%d,%d]" % (interval.start, interval.end))


def GetPoint(string, isReplace=False):
    if not isReplace:
        string = string.replace('(', '[')
        string = string.replace(')', ']')
    items = json.loads(string)
    if len(items) == 2:
        return Point(items[0], items[1])
    else:
        return Point(0, 0)


def PrintPointInternal(point):
    if point is None:
        sys.stdout.write("()")
        return
    sys.stdout.write("(%d,%d)" % (point.x, point.y))


def GetTreeNode(string, isReplace=False):
    string = string.strip()
    string = string[1:-1]
    if not string:
        return None
    if not isReplace:
        string = string.replace('#', 'null')
    items = [s.strip() for s in string.split(',')]
    # items = GetRangeItems(string)
    if len(items) == 0:
        return None

    tree_nodes = [None] * (len(items) + 1)
    current = 0
    # 当前遍历节点位置
    current_pos = LEFT
    index = 1
    tree_nodes[0] = TreeNode(GetInt(items[0]))
    for i in range(1, len(items)):
        if (items[i].strip() == "null"):
            if (tree_nodes[current] != None):
                if current_pos == LEFT:
                    current_pos = RIGHT
                elif tree_nodes[current + 1] != None:
                    current = current + 1
                    current_pos = LEFT
        else:
            tree_nodes[index] = TreeNode(GetInt(items[i]))
            if current_pos == LEFT:
                tree_nodes[current].left = tree_nodes[index]
                current_pos = RIGHT
            else:
                tree_nodes[current].right = tree_nodes[index]
                current = current + 1
                current_pos = LEFT
            index = index + 1

    return tree_nodes[0]


def PrintTreeNodeInternal(root):
    if root == None:
        sys.stdout.write("{}")
        return
    sys.stdout.write("{")
    v = [root]
    c = 0
    none = ""
    while c < len(v):
        if c == 0:
            sys.stdout.write("%d" % v[c].val)
            v.append(v[c].left)
            v.append(v[c].right)
        else:
            if v[c] == None:
                none = none + ",#"
            else:
                sys.stdout.write("%s,%d" % (none, v[c].val))
                none = ""
                v.append(v[c].left)
                v.append(v[c].right)
        c = c + 1
    sys.stdout.write("}")


def GetListNode(string, isReplace=False):
    if not isReplace:
        string = string.replace('{', '[')
        string = string.replace('}', ']')
    items = json.loads(string)
    # dummyRoot = ListNode(0)
    # ptr = dummyRoot
    # for number in items:
    #     ptr.next = ListNode(number)
    #     ptr = ptr.next
    #
    # ptr = dummyRoot.next
    # return ptr

    if len(items) == 0:
        return None
    head = ListNode(items[0])
    tail = head
    for i in range(1, len(items)):
        tail.next = ListNode(items[i])
        tail = tail.next
    return head


def PrintListNodeInternal(head):
    if head == None:
        sys.stdout.write("{}")
        return
    current = head
    sys.stdout.write("{")
    while current != None:
        if current == head:
            sys.stdout.write("%d" % current.val)
        else:
            sys.stdout.write(",%d" % current.val)
        current = current.next
    sys.stdout.write("}")


# { -1, 8, 7, -3,4,4,-3,#,#,-1}
# 分为两段，前部分为ListNode,后半部分如果random==None是#，否则就是random.val
def GetRandomListNode(string):
    items = GetRangeItems(string)
    if len(items) < 2:
        return None
    count = int(len(items) / 2)
    # 记录前一半到节点
    list_nodes = [None] * (count + 1)

    nodes_map = {}
    head = RandomListNode(GetInt(items[0]))
    nodes_map[head.label] = head
    list_nodes[0] = head
    tail = head
    for i in range(1, count):
        cur = RandomListNode(GetInt(items[i]))
        tail.next = cur
        tail = cur
        nodes_map[cur.label] = cur
        list_nodes[i] = cur

    # 遍历后部分到随机节点
    for i in range(count, len(items)):
        if (items[i].strip() != "#" and GetInt(items[i])) in nodes_map:
            list_nodes[i - count].random = nodes_map[GetInt(items[i])]
    return head


def PrintRandomListNodeInternal(head):
    if head == None:
        sys.stdout.write("{}")
        return
    current = head
    sys.stdout.write("{")
    while current != None:
        if current == head:
            sys.stdout.write("%d" % current.label)
        else:
            sys.stdout.write(",%d" % current.label)
        current = current.next

    current = head
    while current != None:
        if current.random != None:
            sys.stdout.write(",%d" % current.random.label)
        else:
            sys.stdout.write(",#")
        current = current.next
    sys.stdout.write("}")


'''
二叉链接树序列化是通过按层遍历,#代表这这个节点为空节点,节点遍历以后再增加所有next节点数据,举个例子
   1->None
  / \
 2 -> 3->None
      /
     4 ->None   
     \
      5->None

 以上二叉树会被序列化为 {[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}
 对于{[1,2,3,#,#,4,#,#,5],[#,5,#,#,#]}构造出来的链接树节点2的next指向5节点*/
 '''


def GetTreeLinkNode(string):
    all_items = GetRangeItems(string)
    # 老版本只有{1,3,34}这种格式
    is_newversion = len(all_items) == 2 and all_items[0][0] == '[' and all_items[1][0] == '['
    if not is_newversion:
        all_items = [string, "[]"]
    if len(all_items) < 2:
        return None
    items = GetRangeItems(all_items[0])
    if len(items) == 0:
        return None

    tree_nodes = [None] * (len(items) + 1)
    map_nodes = {}
    current = 0
    # 当前遍历节点位置
    current_pos = LEFT
    index = 1
    tree_nodes[0] = TreeLinkNode(GetInt(items[0]))
    for i in range(1, len(items)):
        if items[i].strip() == "#":
            if tree_nodes[current] != None:
                if current_pos == LEFT:
                    current_pos = RIGHT
                elif tree_nodes[current + 1] != None:
                    current = current + 1
                    current_pos = LEFT
        else:
            label = GetInt(items[i])
            tree_nodes[index] = TreeLinkNode(label)
            map_nodes[label] = tree_nodes[index]
            if current_pos == LEFT:
                tree_nodes[current].left = tree_nodes[index]
                current_pos = RIGHT
            else:
                tree_nodes[current].right = tree_nodes[index]
                current = current + 1
                current_pos = LEFT
            index = index + 1

    # 连接next指针
    items = GetRangeItems(all_items[1])
    for i in range(0, len(items)):
        if items[i].strip() != "#" and GetInt(items[i]) in map_nodes:
            tree_nodes[i].next = tree_nodes[GetInt(items[i])]

    return tree_nodes[0]


def PrintTreeLinkNodeInternal(root):
    if root == None:
        sys.stdout.write("{}")
        return
    sys.stdout.write("{[")
    v = []
    label_node_v = []
    if root != None:
        v.append(root)
        label_node_v.append(root)
    c = 0
    none = ""
    while c < len(v):
        if c == 0:
            sys.stdout.write("%d" % v[c].val)
            v.append(v[c].left)
            v.append(v[c].right)
        else:
            if v[c] == None:
                none = none + ",#"
            else:
                label_node_v.append(v[c])
                sys.stdout.write("%s,%d" % (none, v[c].val))
                none = ""
                v.append(v[c].left)
                v.append(v[c].right)
        c = c + 1
    v = []
    sys.stdout.write("],[")
    for i in range(0, len(label_node_v)):
        if i != 0:
            sys.stdout.write(",")
        if label_node_v[i].next != None:
            sys.stdout.write("%d" % label_node_v[i].next.val)
        else:
            sys.stdout.write("#")
    sys.stdout.write("]}")


'''
无向图里每个节点都有一个唯一的数字ID,每个节点的序列化通过[]保存,每个节点第一个元素后跟随的是这个节点连接的其他节点,以下图
       1 
     /  \
     /  \
    0 --- 2
         / \
         \_/
 序列化后为{[0,1,2],[1,2],[2,2]}
 '''


def GetUndirectedGraphNode(string):
    points = GetIntListList(string)

    ret = None
    nodes_map = {}

    # 把所有的点构造出来
    for i in range(0, len(points)):
        v = points[i]
        if len(v) == 0:
            continue
        if not nodes_map.has_key(v[0]):
            node = UndirectedGraphNode(v[0])
            nodes_map[v[0]] = node
            if ret == None:
                ret = node

    # 把各个边连接起来
    for i in range(0, len(points)):
        v = points[i]
        if len(v) == 0:
            continue
        node = nodes_map[v[0]]
        for j in range(1, len(v)):
            node.neighbors.append(nodes_map[v[j]])
    return ret


def PrintUndirectedGraphNodeInternal(root):
    if root == None:
        sys.stdout.write("{}")
        return
    sys.stdout.write("{")
    if root != None:
        nodes_set = {}
        nodes_map = {}
        nodes = []
        nodes.append(root)
        nodes_set.append(root)
        nodes_map[root.label] = root
        for i in range(0, len(nodes)):
            for j in range(0, len(nodes[i].neighbors)):
                n_node = nodes[i].neighbors[j]
                if not nodes_set.has_key(n_node):
                    nodes_set[n_node] = True
                    nodes.append(n_node)
                    nodes_map[n_node.label] = n_node

        # 根据label从小到大打印
        for node in nodes_map.values():
            if node != nodes[0]:  # 不是第一个节点
                sys.stdout.write(",[{0}", node.label)
            else:
                sys.stdout.write("[{0}", node.label)
            for j in range(0, len(node.neighbors)):
                sys.stdout.write(",{0}", node.neighbors[j].label)
            sys.stdout.write("]")
    sys.stdout.write("}")


def GetIntSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetInt(item))
    return set(ret)


def GetIntList(string):
    return json.loads(string)


def GetInts(string):
    return json.loads(string)


def GetIntListList(string):
    return json.loads(string)


def GetIntss(string):
    return json.loads(string)


def PrintIntListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintIntInternal(x[i])
    sys.stdout.write(']')


def PrintInt(x):
    PrintIntInternal(x)
    sys.stdout.write('\n')


def PrintIntList(x):
    PrintIntListInternal(x)
    sys.stdout.write('\n')


def PrintIntListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintIntListInternal(x[i])
    sys.stdout.write("]\n")


def PrintInts(x):
    PrintIntList(x)


def PrintIntss(x):
    PrintIntListList(x)


def GetLongSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetLong(item))
    return set(ret)


def GetLongList(string):
    return json.loads(string)


def GetLongs(string):
    return json.loads(string)


def GetLongListList(string):
    return json.loads(string)


def GetLongss(string):
    return json.loads(string)


def PrintLongListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintLongInternal(x[i])
    sys.stdout.write(']')


def PrintLong(x):
    PrintLongInternal(x)
    sys.stdout.write('\n')


def PrintLongList(x):
    PrintLongListInternal(x)
    sys.stdout.write('\n')


def PrintLongListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintLongListInternal(x[i])
    sys.stdout.write("]\n")


def PrintLongs(x):
    PrintLongList(x)


def PrintLongss(x):
    PrintLongListList(x)


def GetFloatSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetFloat(item))
    return set(ret)


def GetFloatList(string):
    return json.loads(string)


def GetFloats(string):
    return json.loads(string)


def GetFloatListList(string):
    return json.loads(string)


def GetFloatss(string):
    return json.loads(string)


def PrintFloatListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintFloatInternal(x[i])
    sys.stdout.write(']')


def PrintFloat(x):
    PrintFloatInternal(x)
    sys.stdout.write('\n')


def PrintFloatList(x):
    PrintFloatListInternal(x)
    sys.stdout.write('\n')


def PrintFloatListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintFloatListInternal(x[i])
    sys.stdout.write("]\n")


def PrintFloats(x):
    PrintFloatList(x)


def PrintFloatss(x):
    PrintFloatListList(x)


def GetDoubleSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetDouble(item))
    return set(ret)


def GetDoubleList(string):
    return json.loads(string)


def GetDoubles(string):
    return json.loads(string)


def GetDoubleListList(string):
    return json.loads(string)


def GetDoubless(string):
    return json.loads(string)


def PrintDoubleListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintDoubleInternal(x[i])
    sys.stdout.write(']')


def PrintDouble(x):
    PrintDoubleInternal(x)
    sys.stdout.write('\n')


def PrintDoubleList(x):
    PrintDoubleListInternal(x)
    sys.stdout.write('\n')


def PrintDoubleListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintDoubleListInternal(x[i])
    sys.stdout.write("]\n")


def PrintDoubles(x):
    PrintDoubleList(x)


def PrintDoubless(x):
    PrintDoubleListList(x)


def GetCharSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetChar(item))
    return set(ret)


def GetCharList(string):
    # items = GetRangeItems(string)
    # ret = []
    # for item in items:
    #     ret.append(GetChar(item))
    return ncpy_link_module.GetCharList(string)


def GetChars(string):
    return GetCharList(string)


def GetCharListList(string):
    # items = GetRangeItems(string)
    # ret = []
    # for item in items:
    #     ret.append(GetCharList(item))
    return ncpy_link_module.GetCharListList(string)


def GetCharss(string):
    return GetCharListList(string)


def PrintCharListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintCharInternal(x[i])
    sys.stdout.write(']')


def PrintChar(x):
    PrintCharInternal(x)
    sys.stdout.write('\n')


def PrintCharList(x):
    PrintCharListInternal(x)
    sys.stdout.write('\n')


def PrintCharListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintCharListInternal(x[i])
    sys.stdout.write("]\n")


def PrintChars(x):
    PrintCharList(x)


def PrintCharss(x):
    PrintCharListList(x)


def GetBoolSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetBool(item))
    return set(ret)


def GetBoolList(string):
    return json.loads(string)


def GetBools(string):
    return json.loads(string)


def GetBoolListList(string):
    return json.loads(string)


def GetBoolss(string):
    return json.loads(string)


def PrintBoolListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintBoolInternal(x[i])
    sys.stdout.write(']')


def PrintBool(x):
    PrintBoolInternal(x)
    sys.stdout.write('\n')


def PrintBoolList(x):
    PrintBoolListInternal(x)
    sys.stdout.write('\n')


def PrintBoolListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintBoolListInternal(x[i])
    sys.stdout.write("]\n")


def PrintBools(x):
    PrintBoolList(x)


def PrintBoolss(x):
    PrintBoolListList(x)


def GetStringSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetString(item))
    return set(ret)


def GetStringList(string):
    # ret = ncpy_link_module.GetStringList(string)
    # items = GetRangeItems(string)
    # ret = []
    # for item in items:
    #     ret.append(GetString(item))
    return ncpy_link_module.GetStringList(string)


def GetStrings(string):
    return GetStringList(string)


def GetStringListList(string):
    # ret = ncpy_link_module.GetStringListList(string)

    # items = GetRangeItems(string)
    # ret = []
    # for item in items:
    #     ret.append(GetStringList(item))
    return ncpy_link_module.GetStringListList(string)


def GetStringss(string):
    return GetStringListList(string)


def PrintStringListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintStringInternal(x[i])
    sys.stdout.write(']')


def PrintString(x):
    PrintStringInternal(x)
    sys.stdout.write('\n')


def PrintStringList(x):
    PrintStringListInternal(x)
    sys.stdout.write('\n')


def PrintStringListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintStringListInternal(x[i])
    sys.stdout.write("]\n")


def PrintStrings(x):
    PrintStringList(x)


def PrintStringss(x):
    PrintStringListList(x)


def GetIntervalSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetInterval(item))
    return set(ret)


def GetIntervalList(string):
    items = json.loads(string)
    ret = []
    for item in items:
        ret.append(GetInterval(json.dumps(item)))
    return ret


def GetIntervals(string):
    return GetIntervalList(string)


def GetIntervalListList(string):
    items = json.loads(string)
    ret = []
    for item in items:
        ret.append(GetIntervalList(json.dumps(item)))
    return ret


def GetIntervalss(string):
    return GetIntervalListList(string)


def PrintIntervalListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintIntervalInternal(x[i])
    sys.stdout.write(']')


def PrintInterval(x):
    PrintIntervalInternal(x)
    sys.stdout.write('\n')


def PrintIntervalList(x):
    PrintIntervalListInternal(x)
    sys.stdout.write('\n')


def PrintIntervalListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintIntervalListInternal(x[i])
    sys.stdout.write("]\n")


def PrintIntervals(x):
    PrintIntervalList(x)


def PrintIntervalss(x):
    PrintIntervalListList(x)


def GetPointSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetPoint(item))
    return set(ret)


def GetPointList(string, isReplace=False):
    if not isReplace:
        string = string.replace('(', '[')
        string = string.replace(')', ']')
    items = json.loads(string)
    # items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetPoint(json.dumps(item), isReplace=True))
    return ret


def GetPoints(string):
    return GetPointList(string)


def GetPointListList(string):
    string = string.replace('(', '[')
    string = string.replace(')', ']')
    # items = GetRangeItems(string)
    items = json.loads(string)
    ret = []
    for item in items:
        ret.append(GetPointList(json.dumps(item), isReplace=True))
    return ret


def GetPointss(string):
    return GetPointListList(string)


def PrintPointListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintPointInternal(x[i])
    sys.stdout.write(']')


def PrintPoint(x):
    PrintPointInternal(x)
    sys.stdout.write('\n')


def PrintPointList(x):
    PrintPointListInternal(x)
    sys.stdout.write('\n')


def PrintPointListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintPointListInternal(x[i])
    sys.stdout.write("]\n")


def PrintPoints(x):
    PrintPointList(x)


def PrintPointss(x):
    PrintPointListList(x)


def GetUndirectedGraphNodeSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetUndirectedGraphNode(item))
    return set(ret)


def GetUndirectedGraphNodeList(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetUndirectedGraphNode(item))
    return ret


def GetUndirectedGraphNodes(string):
    return GetUndirectedGraphNodeList(string)


def GetUndirectedGraphNodeListList(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetUndirectedGraphNodeList(item))
    return ret


def GetUndirectedGraphNodess(string):
    return GetUndirectedGraphNodeListList(string)


def PrintUndirectedGraphNodeListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintUndirectedGraphNodeInternal(x[i])
    sys.stdout.write(']')


def PrintUndirectedGraphNode(x):
    PrintUndirectedGraphNodeInternal(x)
    sys.stdout.write('\n')


def PrintUndirectedGraphNodeList(x):
    PrintUndirectedGraphNodeListInternal(x)
    sys.stdout.write('\n')


def PrintUndirectedGraphNodeListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintUndirectedGraphNodeListInternal(x[i])
    sys.stdout.write("]\n")


def PrintUndirectedGraphNodes(x):
    PrintUndirectedGraphNodeList(x)


def PrintUndirectedGraphNodess(x):
    PrintUndirectedGraphNodeListList(x)


def GetListNodeSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetListNode(item))
    return set(ret)


def GetListNodeList(string, isReplace=False):
    if not isReplace:
        string = string.replace('{', '[')
        string = string.replace('}', ']')
    listNodeArrays = json.loads(string)
    # items = GetRangeItems(string)
    ret = []
    for listNodeArray in listNodeArrays:
        ret.append(GetListNode(json.dumps(listNodeArray), isReplace=True))
    return ret


def GetListNodes(string):
    return GetListNodeList(string)


def GetListNodeListList(string):
    string = string.replace('{', '[')
    string = string.replace('}', ']')
    listNodeArrayArrays = json.loads(string)
    # items = GetRangeItems(string)
    ret = []
    for listNodeArrayArray in listNodeArrayArrays:
        ret.append(GetListNodeList(json.dumps(listNodeArrayArray), isReplace=True))
    return ret


def GetListNodess(string):
    return GetListNodeListList(string)


def PrintListNodeListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintListNodeInternal(x[i])
    sys.stdout.write(']')


def PrintListNode(x):
    PrintListNodeInternal(x)
    sys.stdout.write('\n')


def PrintListNodeList(x):
    PrintListNodeListInternal(x)
    sys.stdout.write('\n')


def PrintListNodeListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintListNodeListInternal(x[i])
    sys.stdout.write("]\n")


def PrintListNodes(x):
    PrintListNodeList(x)


def PrintListNodess(x):
    PrintListNodeListList(x)


def GetRandomListNodeSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetRandomListNode(item))
    return set(ret)


def GetRandomListNodeList(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetRandomListNode(item))
    return ret


def GetRandomListNodes(string):
    return GetRandomListNodeList(string)


def GetRandomListNodeListList(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetRandomListNodeList(item))
    return ret


def GetRandomListNodess(string):
    return GetRandomListNodeListList(string)


def PrintRandomListNodeListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintRandomListNodeInternal(x[i])
    sys.stdout.write(']')


def PrintRandomListNode(x):
    PrintRandomListNodeInternal(x)
    sys.stdout.write('\n')


def PrintRandomListNodeList(x):
    PrintRandomListNodeListInternal(x)
    sys.stdout.write('\n')


def PrintRandomListNodeListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintRandomListNodeListInternal(x[i])
    sys.stdout.write("]\n")


def PrintRandomListNodes(x):
    PrintRandomListNodeList(x)


def PrintRandomListNodess(x):
    PrintRandomListNodeListList(x)


def GetTreeNodeSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetTreeNode(item))
    return set(ret)


def GetTreeNodeList(string, isReplace=False):
    if not isReplace:
        string = string.replace('{', '[')
        string = string.replace('}', ']')
        string = string.replace('#', 'null')
    items = json.loads(string)
    # items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetTreeNode(json.dumps(item), isReplace=True))
    return ret


def GetTreeNodes(string):
    return GetTreeNodeList(string)


def GetTreeNodeListList(string):
    string = string.replace('{', '[')
    string = string.replace('}', ']')
    string = string.replace('#', 'null')
    # items = GetRangeItems(string)
    items = json.loads(string)
    ret = []
    for item in items:
        ret.append(GetTreeNodeList(json.dumps(item), isReplace=True))
    return ret


def GetTreeNodess(string):
    return GetTreeNodeListList(string)


def PrintTreeNodeListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintTreeNodeInternal(x[i])
    sys.stdout.write(']')


def PrintTreeNode(x):
    PrintTreeNodeInternal(x)
    sys.stdout.write('\n')


def PrintTreeNodeList(x):
    PrintTreeNodeListInternal(x)
    sys.stdout.write('\n')


def PrintTreeNodeListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintTreeNodeListInternal(x[i])
    sys.stdout.write("]\n")


def PrintTreeNodes(x):
    PrintTreeNodeList(x)


def PrintTreeNodess(x):
    PrintTreeNodeListList(x)


def GetTreeLinkNodeSet(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetTreeLinkNode(item))
    return set(ret)


def GetTreeLinkNodeList(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetTreeLinkNode(item))
    return ret


def GetTreeLinkNodes(string):
    return GetTreeLinkNodeList(string)


def GetTreeLinkNodeListList(string):
    items = GetRangeItems(string)
    ret = []
    for item in items:
        ret.append(GetTreeLinkNodeList(item))
    return ret


def GetTreeLinkNodess(string):
    return GetTreeLinkNodeListList(string)


def PrintTreeLinkNodeListInternal(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintTreeLinkNodeInternal(x[i])
    sys.stdout.write(']')


def PrintTreeLinkNode(x):
    PrintTreeLinkNodeInternal(x)
    sys.stdout.write('\n')


def PrintTreeLinkNodeList(x):
    PrintTreeLinkNodeListInternal(x)
    sys.stdout.write('\n')


def PrintTreeLinkNodeListList(x):
    sys.stdout.write('[')
    if x is not None:
        for i in range(0, len(x)):
            if i != 0:
                sys.stdout.write(',')
            PrintTreeLinkNodeListInternal(x[i])
    sys.stdout.write("]\n")


def PrintTreeLinkNodes(x):
    PrintTreeLinkNodeList(x)


def PrintTreeLinkNodess(x):
    PrintTreeLinkNodeListList(x)


if __name__ == "__main__":
    line = ""
    line = line + "1 , [ 1 , 2 ],[[1],[2],[3,4,-5]],[ 1 , 2 ],[[1],[2],[3,4,5]],"  # int
    line = line + "true , [ false , true ],[[false],[false],[false,true,true]],[ true , false ],[[false],[true],[true,true,true]],"  # bool
    line = line + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [ 1 , 2 ],[[1],[2],[3,4,5]],"  # float
    line = line + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [],[ 1 , 2 ],[[1],[2],[3,4,5]],"  # double
    line = line + " \"a\", [\"\",\"x[[[[,,,,[}}}}\"], [[acd, efg], [acd, \"efg\"]],"  # string
    line = line + " a, [x, y ], [[a, b],[], [c, d]],"  # char
    line = line + " 1000000000, [3000000000, 2000000000 ], [[3000000000, 2000000000 ],[13000000000, 22000000000 ]],"  # long
    line = line + "{1,3,4},[{2,4,5},{5,6,7,89,11},{}],[[{2,4,5},{5,6,7,89,11},{}],[{2,4,5},{5,6,7,89,11}]],"  # ListNode
    line = line + "[1,3],[[2,5],[5,11]],[[[2,5],[5,6]],[[4,5],[89,11]]],"  # Interval
    line = line + "(1,3),[(2,5),(5,11)],[[(2,5),(5,6)],[(4,5),(89,11)]],"  # Point
    line = line + "{1,2,3,#,#,4,#,#,5},[{1,2,3,#,#,4,#,#,5}],[[{1,2,3,#,#,4,#,#,5}],[{1,2,3,#,#,4,#,#,5},{1,2,3,#,#,4,#,#,5}]],"  # TreeNode
    line = line + "{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]},[{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}],[[],[{[],[]}], [{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}]],"  # TreeLinkNode
    line = line + "{ -1, 8, 7,  -3,4,4,-3,#,#,-1}, [{ -1, 8, 7,  -3,4,4,-3,#,#,-1}], [[{}],[{ -1, 8, 7,  -3,4,4,-3,#,#,-1}]],"  # RandomListNode
    line = line + "{[0,1,2],[1,2],[2,2]}, [{[0,1,2],[1,2],[2,2]}], [[], [{[0,1,2],[1,2],[2,2]},{[0,1,2],[1,2],[2,2]}]]"  #

    parameters = GetArguments(line)
    i = 0
    PrintInt(GetInt(parameters[i]))
    i = i + 1
    PrintInts(GetInts(parameters[i]))
    i = i + 1
    PrintIntss(GetIntss(parameters[i]))
    i = i + 1
    PrintIntList(GetIntList(parameters[i]))
    i = i + 1
    PrintIntListList(GetIntListList(parameters[i]))
    i = i + 1

    PrintBool(GetBool(parameters[i]))
    i = i + 1
    PrintBools(GetBools(parameters[i]))
    i = i + 1
    PrintBoolss(GetBoolss(parameters[i]))
    i = i + 1
    PrintBoolList(GetBoolList(parameters[i]))
    i = i + 1
    PrintBoolListList(GetBoolListList(parameters[i]))
    i = i + 1

    PrintFloat(GetFloat(parameters[i]))
    i = i + 1
    PrintFloats(GetFloats(parameters[i]))
    i = i + 1
    PrintFloatss(GetFloatss(parameters[i]))
    i = i + 1
    PrintFloatList(GetFloatList(parameters[i]))
    i = i + 1
    PrintFloatListList(GetFloatListList(parameters[i]))
    i = i + 1

    PrintDouble(GetDouble(parameters[i]))
    i = i + 1
    PrintDoubles(GetDoubles(parameters[i]))
    i = i + 1
    PrintDoubless(GetDoubless(parameters[i]))
    i = i + 1
    PrintDoubles(GetDoubles(parameters[i]))
    i = i + 1
    PrintDoubleList(GetDoubleList(parameters[i]))
    i = i + 1
    PrintDoubleListList(GetDoubleListList(parameters[i]))
    i = i + 1

    PrintString(GetString(parameters[i]))
    i = i + 1
    PrintStringList(GetStringList(parameters[i]))
    PrintStrings(GetStrings(parameters[i]))
    i = i + 1
    PrintStringListList(GetStringListList(parameters[i]))
    PrintStringss(GetStringss(parameters[i]))
    i = i + 1

    PrintChar(GetChar(parameters[i]))
    i = i + 1
    PrintChars(GetChars(parameters[i]))
    i = i + 1
    PrintCharss(GetCharss(parameters[i]))
    i = i + 1

    PrintLong(GetLong(parameters[i]))
    i = i + 1
    PrintLongList(GetLongList(parameters[i]))
    PrintLongs(GetLongs(parameters[i]))
    i = i + 1
    PrintLongListList(GetLongListList(parameters[i]))
    PrintLongss(GetLongss(parameters[i]))
    i = i + 1

    PrintListNode(GetListNode(parameters[i]))
    i = i + 1
    PrintListNodeList(GetListNodeList(parameters[i]))
    PrintListNodes(GetListNodes(parameters[i]))
    i = i + 1
    PrintListNodeListList(GetListNodeListList(parameters[i]))
    PrintListNodess(GetListNodess(parameters[i]))
    i = i + 1

    PrintInterval(GetInterval(parameters[i]))
    i = i + 1
    PrintIntervalList(GetIntervalList(parameters[i]))
    PrintIntervals(GetIntervals(parameters[i]))
    i = i + 1
    PrintIntervalListList(GetIntervalListList(parameters[i]))
    PrintIntervalss(GetIntervalss(parameters[i]))
    i = i + 1

    PrintPoint(GetPoint(parameters[i]))
    i = i + 1
    PrintPointList(GetPointList(parameters[i]))
    PrintPoints(GetPoints(parameters[i]))
    i = i + 1
    PrintPointListList(GetPointListList(parameters[i]))
    PrintPointss(GetPointss(parameters[i]))
    i = i + 1

    PrintTreeNode(GetTreeNode(parameters[i]))
    i = i + 1
    PrintTreeNodeList(GetTreeNodeList(parameters[i]))
    PrintTreeNodes(GetTreeNodes(parameters[i]))
    i = i + 1
    PrintTreeNodeListList(GetTreeNodeListList(parameters[i]))
    PrintTreeNodess(GetTreeNodess(parameters[i]))
    i = i + 1

    PrintTreeLinkNode(GetTreeLinkNode(parameters[i]))
    i = i + 1
    PrintTreeLinkNodeList(GetTreeLinkNodeList(parameters[i]))
    PrintTreeLinkNodes(GetTreeLinkNodes(parameters[i]))
    i = i + 1
    PrintTreeLinkNodeListList(GetTreeLinkNodeListList(parameters[i]))
    PrintTreeLinkNodess(GetTreeLinkNodess(parameters[i]))
    i = i + 1

    PrintRandomListNode(GetRandomListNode(parameters[i]))
    i = i + 1
    PrintRandomListNodeList(GetRandomListNodeList(parameters[i]))
    PrintRandomListNodes(GetRandomListNodes(parameters[i]))
    i = i + 1
    PrintRandomListNodeListList(GetRandomListNodeListList(parameters[i]))
    PrintRandomListNodess(GetRandomListNodess(parameters[i]))
    i = i + 1
