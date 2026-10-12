# -*- coding utf-8 -*-
require "set"

# ===== DEFINE
class TreeNode
  attr_accessor :val, :left, :right

  def initialize(val, left = nil, right = nil)
    @val, @left, @right = val, left, right
  end
end

class Interval
  attr_accessor :start, :end

  def initialize(a = 0, b = 0)
    @start, @end = a, b
  end
end

class Point
  attr_accessor :x, :y

  def initialize(x = 0, y = 0)
    @x, @y = x, y
  end
end

class TreeLinkNode
  attr_accessor :val, :left, :right, :next

  def initialize(val, left = nil, right = nil, _next = nil)
    @val, @left, @right, @next = val, left, right, _next
  end
end

class RandomListNode
  attr_accessor :label, :next, :random

  def initialize(label = nil, _next = nil, random = nil)
    @label, @next, @random = label, _next, random
  end
end

class UndirectedGraphNode
  attr_accessor :val, :neighbors

  def initialize(val = 0, neighbors = nil)
    @val = val
    @neighbors = neighbors != nil ? [] : neighbors
  end
end

class ListNode
  attr_accessor :val, :next

  def initialize(val = 0, _next = nil)
    @val, @next = val, _next
  end
end

class NCTools 
  LEFT = 0
  RIGHT = 1

  def self.IsBeginRange(c)
    c == "{" or c == "[" or c == "("
  end

  def self.IsEndRange(c)
    c == "" or c == "]" or c == ")" or c == "}"
  end

  def self.GetArguments(line)
    ret = []
    return ret if line == nil
    inrange = 0
    pre_index = 0
    inmao = false
    (0...line.length).each do |i|
      if self.IsBeginRange(line[i]) and not inmao
        inrange = inrange + 1
      elsif self.IsEndRange(line[i]) and not inmao
        inrange = inrange - 1
      elsif line[i] == "\""
        inmao = !inmao
      elsif line[i] == "," and inrange == 0 and not inmao
        ret.append(line[pre_index...i])
        pre_index = i + 1
      end
    end
    ret.append(line[pre_index..-1])
    ret
  end

  def self.GetRangeItems(string)
    return [] if string == nil

    bg = 0
    while (not self.IsBeginRange(string[bg])) and bg < string.length do
      bg = bg + 1
    end
    ed = string.length
    while (not self.IsEndRange(string[ed - 1])) and ed > 1 do
      ed = ed - 1
    end
    string = string[bg + 1...ed - 1]
    string.strip.length == 0 ? [] :  self.GetArguments(string)
  end

  # ===== DEFAULT

  # INT
  def self.GetInt(s)
    s.to_i
  end

  def self.PrintIntInternal(s)
    print(s)
  end

  # LONG
  def self.GetLong(s)
    s.to_i
  end

  def self.PrintLongInternal(s)
    print(s)
  end

  # FLOAT
  def self.GetFloat(s)
    s.to_f
  end

  def self.PrintFloatInternal(s)
    print(s.abs < 0.000009999999 ? "0.00000" : ("%0.05f" % s))
  end

  def self.GetDouble(s)
    s.to_f
  end

  def self.PrintDoubleInternal(s)
    print(s.abs < 0.000009999999 ? "0.00000" :  ("%0.05f" % s))
  end

  def self.GetString(s)
    return nil if s == nil
    s&.strip!
    return "" if s.length == 0
    (s.length != 0 && s[0] == "\"" && s[-1] == "\"") ? s[1...-1] : s
  end

  def self.PrintStringInternal(s)
    if s == nil
      print("null")
    else
      print("\""+s+"\"")
    end
  end

  def self.GetChar(s)
    (s != nil && s.length != 0) ? s.strip[0]:  "#"
  end

  def self.PrintCharInternal(s)
    print(s)
  end

  def self.GetBool(s)
    s && s.strip.downcase == "true"
  end

  def self.PrintBoolInternal(s)
    print(!!s)
  end

  def self.GetInterval(s)
    items = self.GetIntList(s)
    items.length == 2 ? Interval.new(items[0], items[1]) : Interval.new(0, 0)
  end

  def self.PrintIntervalInternal(s)
    print("[#{s.start},#{s.end}]")
  end

  def self.GetPoint(s)
    items = self.GetIntList(s)
    items.length == 2 ? Point.new(items[0], items[1]) : Point.new(0, 0)
  end

  def self.PrintPointInternal(s)
    print("(#{s.x},#{s.y})")
  end


  def self.GetTreeNode(s)
    items = self.GetRangeItems(s)
    return nil if items.length == 0
    tree_nodes = [nil] * (items.length + 1)
    current = 0
    current_pos = LEFT
    index = 1
    tree_nodes[0] = TreeNode.new(self.GetInt(items[0]))
    (1...items.length).each{|i|
      if items[i].strip == "#"
        if tree_nodes[current] != nil
          if current_pos == LEFT
            current_pos = RIGHT
          elsif tree_nodes[current + 1]  != nil
            current = current + 1
            current_pos = LEFT
          end
        end
      else
        tree_nodes[index] = TreeNode.new(self.GetInt(items[i]))
        if current_pos == LEFT
          tree_nodes[current].left = tree_nodes[index]
          current_pos = RIGHT
        else
          tree_nodes[current].right = tree_nodes[index]
          current = current + 1
          current_pos = LEFT
        end
        index = index + 1
      end
    }
    tree_nodes[0]
  end

  def self.PrintTreeNodeInternal(root)
    if root == nil
      print("{}")
      return
    end

    print("{")
    v = [root]
    c = 0
    none = ""
    while c < v.length
      if c == 0
        print(v[c].val)
        v.append(v [c].left)
        v.append(v [c].right)
      else
        if v [c] == nil
          none = none + ",#"
        else
          print("#{none},#{v[c].val}")
          none = ""
          v.append(v [c].left)
          v.append(v [c].right)
        end
      end
      c = c + 1
    end
    print("}")
  end


  def self.GetListNode(s)
    items = self.GetIntList(s)
    head = ListNode.new(0)
    tail = head
    items.each { |i|
      tail.next = ListNode.new(i)
      tail = tail.next
    }
    head.next
  end

  def self.PrintListNodeInternal(s)
    print("{")
    cur = s
    while cur != nil do
      print(",") if cur != s
      print(cur.val)
      cur = cur.next
    end
    print("}")
  end


  def self.GetRandomListNode(string)
    items = self.GetRangeItems(string)
    return nil if items.length < 2
    count = items.length / 2
    # 记录前一半到节点
    list_nodes = [nil] * (count + 1)
    nodes_map = {}
    head = RandomListNode.new(self.GetInt(items [0]))
    nodes_map[head.label] = head
    list_nodes[0] = head
    tail = head
    (1...count).each do |i|
      cur = RandomListNode.new(self.GetInt(items[i]))
      tail.next = cur
      tail = cur
      nodes_map[cur.label] = cur
      list_nodes[i] = cur
    end

    # 遍历后部分到随机节点
    (count...items.length).each do |i|
      if items[i].strip != "#" and nodes_map.key?(self.GetInt(items[i]))
        list_nodes[i - count].random = nodes_map[self.GetInt(items[i])]
      end
    end
    head
  end

  def self.PrintRandomListNodeInternal(head)
    print("{")
    current = head
    while current != nil
      print(",") if current != head
      print(current.label)
      current = current.next
    end

    current = head
    while current != nil
      if current.random != nil
        print(",%d" % current.random.label)
      else
        print(",#")
      end
      current = current.next
    end
    print("}")
  end

  """
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
  """
  def self.GetTreeLinkNode (string)
    all_items = self.GetRangeItems(string)
    is_newversion = (all_items.length == 2 and all_items[0][0] == "[" and all_items[1][0] == "[")

    all_items = [string, "[]"] unless is_newversion
    return nil if all_items.length < 2
    items = self.GetRangeItems(all_items[0])
    return nil if items.length == 0

    tree_nodes = [nil] * (items.length + 1)
    map_nodes = {}
    current = 0
    #当前遍历节点位置
    current_pos = LEFT
    index = 1
    tree_nodes[0] = TreeLinkNode.new(self.GetInt(items [0]))
    (1...items.length).each { |i|
      if items[i].strip == "#"
        if tree_nodes[current] != nil
          if current_pos == LEFT
            current_pos = RIGHT
          elsif tree_nodes[current + 1] != nil
            current = current + 1
            current_pos = LEFT
          end
        end
      else
        label = self.GetInt(items[i])
        tree_nodes[index] = TreeLinkNode.new(label)
        map_nodes[label] = tree_nodes[index]
        if current_pos == LEFT
          tree_nodes[current].left = tree_nodes[index]
          current_pos = RIGHT
        else
          tree_nodes[current].right = tree_nodes[index]
          current = current + 1
          current_pos = LEFT
        end
        index = index + 1
      end
    }

    # 连接next指针
    items = self.GetRangeItems(all_items[1])
    (0...items.length).each { |i|
      if items[i].strip != "#" and map_nodes.key?(self.GetInt(items [i]))
        tree_nodes[i].next = tree_nodes[self.GetInt(items [i])]
      end
    }
    tree_nodes[0]
  end

  def self.PrintTreeLinkNodeInternal(root)
    if root == nil
      print("{}")
      return
    end
    print("{[")
    v = []
    label_node_v = []
    v.append(root) if root != nil
    label_node_v.append(root)
    c = 0
    none = ""
    while c < v.length do
      if c == 0
        print(v[c].val) if c == 0
        v.append(v[c].left)
        v.append(v[c].right)
      else
        if v [c] == nil
          none = none + ",#"
        else
          label_node_v.append(v[c])
          print("#{none},#{v[c].val}")
          none = ""
          v.append(v[c].left)
          v.append(v[c].right)
        end
      end
      c = c + 1
    end
    print("],[")
    (0...label_node_v.length).each { |i|
      print(",") if i != 0
      if label_node_v[i].next != nil
        print(label_node_v[i].next.val)
      else
        print("#")
      end
    }
    print("]}")
  end

  """
  无向图里每个节点都有一个唯一的数字ID,每个节点的序列化通过[]保存,每个节点第一个元素后跟随的是这个节点连接的其他节点,以下图
         1
       /  \
       /  \
      0 --- 2
           / \
           \_/
   序列化后为{[0,1,2],[1,2],[2,2]}
  """
  def self.GetUndirectedGraphNode(string)
    points = self.GetIntListList(string)
    ret = nil
    nodes_map = {}

    # 把所有的点构造出来
    (0...points.length).each { |i|
      v = points[i]
      next if v.length == 0
      unless nodes_map.key?(v[0])
        node = UndirectedGraphNode(v[0])
        nodes_map[v[0]] = node
        ret = node if ret == nil
      end
    }

    # 把各个边连接起来
    (0...points.length).each { |i|
      v = points[i]
      next if v.length == 0
      node = nodes_map[v[0]]
      (1...v.length).each { |j|
        node.neighbors.append(nodes_map[v[j]])
      }
    }
    ret
  end

  def self.PrintUndirectedGraphNodeInternal(root)
    if root == nil
      print("{}")
      return
    end
    print("{")
    nodes_set = {}
    nodes_map = {}
    nodes = []
    nodes.append(root)
    nodes_set.append(root)
    nodes_map[root.label] = root
    (0...nodes.length).each { |i|
      (0...nodes[i].neighbors.length).each { |j|
        n_node = nodes[i].neighbors [j]
        unless nodes_set.key?(n_node)
          nodes_set[n_node] = true
          nodes.append(n_node)
          nodes_map[n_node.label] = n_node
        end
      }
    }
    # 根据label从小到大打印
    nodes_map.values.each { |node|
      print(",") if node != nodes[0] # 不是第一个节点
      print("[{#{node.label}}")
      (0...node.neighbors.length).each { |j| print(",{#{node.neighbors[j].label}}") }
      print("]")
    }
    print("}")
  end

  def self.GetIntSet(string)
    self.GetRangeItems(string).map{ |i| self.GetInt(i) }.to_set
  end

  def self.GetIntList(string)
    self.GetRangeItems(string).map{ |i| self.GetInt(i) }
  end

  def self.GetInts(string)
    self.GetIntList(string)
  end

  def self.GetIntListList(string)
    self.GetRangeItems(string).map{ |it| self.GetIntList(it) }
  end

  def self.GetIntss(string)
    self.GetIntListList(string)
  end

  def self.PrintIntListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintIntInternal(x[i])
    }
    print("]")
  end

  def self.PrintInt(x)
    PrintIntInternal(x)
    print("\n")
  end

  def self.PrintIntList(x)
    PrintIntListInternal(x)
    print("\n")
  end

  def self.PrintIntListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintIntListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintInts(x)
    PrintIntList(x)
  end

  def self.PrintIntss(x)
    PrintIntListList(x)
  end

  def self.GetLongSet(string)
    self.GetRangeItems(string).map{|item| self.GetLong(item)}.to_set
  end


  def self.GetLongList(string)
    self.GetRangeItems(string).map{|item| self.GetLong(item)}
  end

  def self.GetLongs(string)
    self.GetLongList(string)
  end

  def self.GetLongListList(string)
    self.GetRangeItems(string).map{|item| self.GetLongList(item)}
  end

  def self.GetLongss(string)
    self.GetLongListList(string)
  end

  def self.PrintLongListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintLongInternal(x[i])
    }
    print("]")
  end

  def self.PrintLong(x)
    PrintLongInternal(x)
    print("\n")
  end

  def self.PrintLongList(x)
    PrintLongListInternal(x)
    print("\n")
  end

  def self.PrintLongListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintLongListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintLongs(x)
    PrintLongList(x)
  end

  def self.PrintLongss(x)
    PrintLongListList(x)
  end

  def self.GetFloatSet(string)
    self.GetRangeItems(string).map { |it| self.GetFloat(it)}.to_set
  end

  def self.GetFloatList(string)
    self.GetRangeItems(string).map { |it| self.GetFloat(it)}
  end

  def self.GetFloats(string)
    self.GetFloatList(string)
  end

  def self.GetFloatListList(string)
    self.GetRangeItems(string).map{|it| self.GetFloatList(it)}
  end

  def self.GetFloatss(string)
    self.GetFloatListList(string)
  end


  def self.PrintFloatListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintFloatInternal(x[i])
    }
    print("]")
  end

  def self.PrintFloat(x)
    PrintFloatInternal(x)
    print("\n")
  end

  def self.PrintFloatList(x)
    PrintFloatListInternal(x)
    print("\n")
  end

  def self.PrintFloatListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintFloatListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintFloats(x)
    PrintFloatList(x)
  end

  def self.PrintFloatss(x)
    PrintFloatListList(x)
  end


  def self.GetDoubleSet(string)
    self.GetRangeItems(string).map{ |i| self.GetDouble(i) }.to_set
  end

  def self.GetDoubleList(string)
    self.GetRangeItems(string).map{ |i| self.GetDouble(i) }
  end

  def self.GetDoubles(string)
    self.GetDoubleList(string)
  end

  def self.GetDoubleListList(string)
    self.GetRangeItems(string).map{ |i| self.GetDoubleList(i) }
  end

  def self.GetDoubless(string)
    self.GetDoubleListList(string)
  end

  def self.PrintDoubleListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintDoubleInternal(x[i])
    }
    print("]")
  end

  def self.PrintDouble(x)
    PrintDoubleInternal(x)
    print("\n")
  end

  def self.PrintDoubleList(x)
    PrintDoubleListInternal(x)
    print("\n")
  end

  def self.PrintDoubleListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintDoubleListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintDoubles(x)
    PrintDoubleList(x)
  end

  def self.PrintDoubless(x)
    PrintDoubleListList(x)
  end

  def self.GetCharSet(string)
    self.GetRangeItems(string).map {|it| self.GetChar(it)}.to_set
  end

  def self.GetCharList(string)
    self.GetRangeItems(string).map {|it| self.GetChar(it)}
  end

  def self.GetChars(string)
    self.GetCharList(string)
  end

  def self.GetCharListList(string)
    self.GetRangeItems(string).map {|it| self.GetCharList(it)}
  end

  def self.GetCharss(string)
    self.GetCharListList(string)
  end

  def self.PrintCharListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintCharInternal(x[i])
    }
    print("]")
  end

  def self.PrintChar(x)
    PrintCharInternal(x)
    print("\n")
  end

  def self.PrintCharList(x)
    PrintCharListInternal(x)
    print("\n")
  end

  def self.PrintCharListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintCharListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintChars(x)
    PrintCharList(x)
  end

  def self.PrintCharss(x)
    PrintCharListList(x)
  end

  def self.GetBoolSet(string)
    self.GetRangeItems(string).map{|it| self.GetBool(it)}.to_set
  end

  def self.GetBoolList(string)
    self.GetRangeItems(string).map{|it| self.GetBool(it)}
  end

  def self.GetBools(string)
    self.GetBoolList(string)
  end

  def self.GetBoolListList(string)
    self.GetRangeItems(string).map{|it| self.GetBoolList(it)}
  end

  def self.GetBoolss(string)
    self.GetBoolListList(string)
  end

  def self.PrintBoolListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintBoolInternal(x[i])
    }
    print("]")
  end

  def self.PrintBool(x)
    PrintBoolInternal(x)
    print("\n")
  end

  def self.PrintBoolList(x)
    PrintBoolListInternal(x)
    print("\n")
  end

  def self.PrintBoolListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintBoolListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintBools(x)
    PrintBoolList(x)
  end

  def self.PrintBoolss(x)
    PrintBoolListList(x)
  end


  def self.GetStringSet(string)
    self.GetRangeItems(string).map{|it| self.GetString(it)}.to_set
  end

  def self.GetStringList(string)
    self.GetRangeItems(string).map{|it| self.GetString(it)}
  end

  def self.GetStrings(string)
    self.GetStringList(string)
  end

  def self.GetStringListList(string)
    self.GetRangeItems(string).map{|it| self.GetStringList(it)}
  end

  def self.GetStringss(string)
    self.GetStringListList(string)
  end

  def self.PrintStringListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintStringInternal(x[i])
    }
    print("]")
  end

  def self.PrintString(x)
    PrintStringInternal(x)
    print("\n")
  end

  def self.PrintStringList(x)
    PrintStringListInternal(x)
    print("\n")
  end

  def self.PrintStringListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintStringListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintStrings(x)
    PrintStringList(x)
  end

  def self.PrintStringss(x)
    PrintStringListList(x)
  end

  def self.GetIntervalSet(string)
    self.GetRangeItems(string).map{|it| self.GetInterval(it) }.to_set
  end

  def self.GetIntervalList(string)
    self.GetRangeItems(string).map{|it| self.GetInterval(it) }
  end

  def self.GetIntervals(string)
    self.GetIntervalList(string)
  end

  def self.GetIntervalListList(string)
    self.GetRangeItems(string).map{|it| self.GetIntervalList(it) }
  end


  def self.GetIntervalss(string)
    self.GetIntervalListList(string)
  end

  def self.PrintIntervalListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintIntervalInternal(x[i])
    }
    print("]")
  end

  def self.PrintInterval(x)
    PrintIntervalInternal(x)
    print("\n")
  end

  def self.PrintIntervalList(x)
    PrintIntervalListInternal(x)
    print("\n")
  end

  def self.PrintIntervalListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintIntervalListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintIntervals(x)
    PrintIntervalList(x)
  end

  def self.PrintIntervalss(x)
    PrintIntervalListList(x)
  end

  def self.GetPointSet(string)
    self.GetRangeItems(string).map{|it| self.GetPoint(it) }.to_set
  end

  def self.GetPointList(string)
    self.GetRangeItems(string).map{|it| self.GetPoint(it) }
  end

  def self.GetPoints(string)
    self.GetPointList(string)
  end

  def self.GetPointListList(string)
    self.GetRangeItems(string).map{|it| self.GetPointList(it) }
  end

  def self.GetPointss(string)
    self.GetPointListList(string)
  end

  def self.PrintPointListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintPointInternal(x[i])
    }
    print("]")
  end

  def self.PrintPoint(x)
    PrintPointInternal(x)
    print("\n")
  end

  def self.PrintPointList(x)
    PrintPointListInternal(x)
    print("\n")
  end

  def self.PrintPointListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintPointListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintPoints(x)
    PrintPointList(x)
  end

  def self.PrintPointss(x)
    PrintPointListList(x)
  end

  def self.GetUndirectedGraphNodeSet(string)
    self.GetRangeItems(string).map{|it| self.GetUndirectedGraphNode(it)}.to_set
  end

  def self.GetUndirectedGraphNodeList(string)
    self.GetRangeItems(string).map{|it| self.GetUndirectedGraphNode(it)}
  end

  def self.GetUndirectedGraphNodes(string)
    self.GetUndirectedGraphNodeList(string)
  end

  def self.GetUndirectedGraphNodeListList(string)
    self.GetRangeItems(string).map{|it| self.GetUndirectedGraphNodeList(it)}
  end

  def self.GetUndirectedGraphNodess(string)
    self.GetUndirectedGraphNodeListList(string)
  end

  def self.PrintUndirectedGraphNodeListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintUndirectedGraphNodeInternal(x[i])
    }
    print("]")
  end

  def self.PrintUndirectedGraphNode(x)
    PrintUndirectedGraphNodeInternal(x)
    print("\n")
  end

  def self.PrintUndirectedGraphNodeList(x)
    PrintUndirectedGraphNodeListInternal(x)
    print("\n")
  end

  def self.PrintUndirectedGraphNodeListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintUndirectedGraphNodeListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintUndirectedGraphNodes(x)
    PrintUndirectedGraphNodeList(x)
  end

  def self.PrintUndirectedGraphNodess(x)
    PrintUndirectedGraphNodeListList(x)
  end

  def self.GetListNodeSet(string)
    self.GetRangeItems(string).map{|item| self.GetListNode(item)}.to_set
  end

  def self.GetListNodeList(string)
    self.GetRangeItems(string).map{|item| self.GetListNode(item)}
  end

  def self.GetListNodes(string)
    self.GetListNodeList(string)
  end

  def self.GetListNodeListList(string)
    self.GetRangeItems(string).map{|item| self.GetListNodeList(item)}
  end

  def self.GetListNodess(string)
    self.GetListNodeListList(string)
  end

  def self.PrintListNodeListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintListNodeInternal(x[i])
    }
    print("]")
  end

  def self.PrintListNode(x)
    PrintListNodeInternal(x)
    print("\n")
  end

  def self.PrintListNodeList(x)
    PrintListNodeListInternal(x)
    print("\n")
  end

  def self.PrintListNodeListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintListNodeListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintListNodes(x)
    PrintListNodeList(x)

  end

  def self.PrintListNodess(x)
    PrintListNodeListList(x)
  end

  def self.GetRandomListNodeSet(string)
    self.GetRangeItems(string).map{|item| self.GetRandomListNode(item)}.to_set
  end

  def self.GetRandomListNodeList(string)
    self.GetRangeItems(string).map{|item| self.GetRandomListNode(item)}
  end

  def self.GetRandomListNodes(string)
    self.GetRandomListNodeList(string)
  end

  def self.GetRandomListNodeListList(string)
    self.GetRangeItems(string).map{|item| self.GetRandomListNodeList(item)}
  end

  def self.GetRandomListNodess(string)
    self.GetRandomListNodeListList(string)
  end

  def self.PrintRandomListNodeListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintRandomListNodeInternal(x[i])
    }
    print("]")
  end

  def self.PrintRandomListNode(x)
    PrintRandomListNodeInternal(x)
    print("\n")
  end

  def self.PrintRandomListNodeList(x)
    PrintRandomListNodeListInternal(x)
    print("\n")
  end

  def self.PrintRandomListNodeListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintRandomListNodeListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintRandomListNodes(x)
    PrintRandomListNodeList(x)
  end

  def self.PrintRandomListNodess(x)
    PrintRandomListNodeListList(x)
  end

  def self.GetTreeNodeSet(string)
    self.GetRangeItems(string).map{|item| self.GetTreeNode (item)}.to_set
  end

  def self.GetTreeNodeList(string)
    self.GetRangeItems(string).map{|item| self.GetTreeNode (item)}
  end

  def self.GetTreeNodes(string)
    self.GetTreeNodeList(string)
  end

  def self.GetTreeNodeListList(string)
    self.GetRangeItems(string).map{|item| self.GetTreeNodeList(item)}
  end

  def self.GetTreeNodess(string)
    self.GetTreeNodeListList(string)
  end

  def self.PrintTreeNodeListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintTreeNodeInternal(x[i])
    }
    print("]")
  end

  def self.PrintTreeNode(x)
    PrintTreeNodeInternal(x)
    print("\n")
  end

  def self.PrintTreeNodeList(x)
    PrintTreeNodeListInternal(x)
    print("\n")
  end

  def self.PrintTreeNodeListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintTreeNodeListInternal(x[i])
    }
    print("]\n")
  end

  def self.PrintTreeNodes(x)
    PrintTreeNodeList(x)
  end

  def self.PrintTreeNodess(x)
    PrintTreeNodeListList(x)
  end


  def self.GetTreeLinkNodeSet(string)
    self.GetRangeItems(string).map{|item| self.GetTreeLinkNode(item)}.to_set
  end
  def self.GetTreeLinkNodeList(string)
    self.GetRangeItems(string).map{|item| self.GetTreeLinkNode(item)}
  end

  def self.GetTreeLinkNodes(string)
    self.GetTreeLinkNodeList(string)
  end

  def self.GetTreeLinkNodeListList(string)
    self.GetRangeItems(string).map{|item| self.GetTreeLinkNodeList(item)}
  end

  def self.GetTreeLinkNodess(string)
    self.GetTreeLinkNodeListList(string)
  end

  def self.PrintTreeLinkNodeListInternal(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintTreeLinkNodeInternal(x[i])
    }
    print("]")
  end


  def self.PrintTreeLinkNode(x)
    PrintTreeLinkNodeInternal(x)
    print("\n")
  end

  def self.PrintTreeLinkNodeList(x)
    PrintTreeLinkNodeListInternal(x)
    print("\n")
  end

  def self.PrintTreeLinkNodeListList(x)
    print("[")
    (0...x.length).each { |i|
      print(",") if i != 0
      PrintTreeLinkNodeListInternal(x[i])
    }
    print("]\n")
  end


  def self.PrintTreeLinkNodes(x)
    PrintTreeLinkNodeList(x)
  end

  def self.PrintTreeLinkNodess(x)
    PrintTreeLinkNodeListList(x)
  end


  OrigStdout = STDOUT.clone
  def self.ShutDownStdout
    STDOUT.flush()
    STDOUT.reopen(File.open("/dev/null", "w+"))
  end
  def self.OpenStdout
    STDOUT.flush()
    STDOUT.reopen(OrigStdout)
  end
end


if __FILE__ == $0
  line = "1 , [ 1 , 2 ],[[1],[2],[3,4,-5]],[ 1 , 2 ],[[1],[2],[3,4,5]]," # int
  line = line +  "true , [ false , true ],[[false],[false],[false,true,true]],[ true , false ],[[false],[true],[true,true,true]]," # bool
  line = line + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [ 1 , 2 ],[[1],[2],[3,4,5]]," # float
  line = line + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [],[ 1 , 2 ],[[1],[2],[3,4,5]]," # double
  line = line + " \"a\", [\"\",\"x[[[[,,,,[}}}}\"], [[acd, efg], [acd, \"efg\"]],"# string
  line = line + " a, [x, y ], [[a, b],[], [c, d]],"# char
  line = line + " 1000000000, [3000000000, 2000000000 ], [[3000000000, 2000000000 ],[13000000000, 22000000000 ]],"# long
  line = line + "{1,3,4},[{2, 4, 5},{5,6,7,89,11},{ }],[[{2, 4, 5},{5,6,7,89,11},{}],[{2, 4, 5},{5,6,7,89,11}]]," # ListNode
  line = line + "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]]," # Interval
  line = line + "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]]," # Point
  line = line + "{1,2,3,#,#,4,#,#,5},[{1,2,3,#,#,4,#,#,5}],[[{1,2,3,#,#,4,#,#,5}],[{1,2,3,#,#,4,#,#,5},{1,2,3,#,#,4,#,#,5}]]," # TreeNode
  line = line + "{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]},[{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}],[[],[{[],[]}], [{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}]]," # TreeLinkNode
  line = line + "{ -1, 8, 7,  -3,4,4,-3,#,#,-1}, [{ -1, 8, 7,  -3,4,4,-3,#,#,-1}], [[{}],[{ -1, 8, 7,  -3,4,4,-3,#,#,-1}]]," # RandomListNode
  line = line + "{[0,1,2],[1,2],[2,2]}, [{[0,1,2],[1,2],[2,2]}], [[], [{[0,1,2],[1,2],[2,2]},{[0,1,2],[1,2],[2,2]}]]" #

  parameters = NCTools.GetArguments(line)
  i = 0
  NCTools.PrintInt(NCTools.GetInt(parameters[i]))
  i = i + 1
  NCTools.PrintInts(NCTools.GetInts(parameters[i]))
  i = i + 1
  NCTools.PrintIntss(NCTools.GetIntss(parameters[i]))
  i = i + 1
  NCTools.PrintIntList(NCTools.GetIntList(parameters[i]))
  i = i + 1
  NCTools.PrintIntListList(NCTools.GetIntListList(parameters[i]))
  i = i + 1

  NCTools.PrintBool(NCTools.GetBool(parameters[i]))
  i = i + 1
  NCTools.PrintBools(NCTools.GetBools(parameters[i]))
  i = i + 1
  NCTools.PrintBoolss(NCTools.GetBoolss(parameters[i]))
  i = i + 1
  NCTools.PrintBoolList(NCTools.GetBoolList(parameters[i]))
  i = i + 1
  NCTools.PrintBoolListList(NCTools.GetBoolListList(parameters[i]))
  i = i + 1

  NCTools.PrintFloat(NCTools.GetFloat(parameters[i]))
  i = i + 1
  NCTools.PrintFloats(NCTools.GetFloats(parameters[i]))
  i = i + 1
  NCTools.PrintFloatss(NCTools.GetFloatss(parameters[i]))
  i = i + 1
  NCTools.PrintFloatList(NCTools.GetFloatList(parameters[i]))
  i = i + 1
  NCTools.PrintFloatListList(NCTools.GetFloatListList(parameters[i]))
  i = i + 1

  NCTools.PrintDouble(NCTools.GetDouble(parameters[i]))
  i = i + 1
  NCTools.PrintDoubles(NCTools.GetDoubles(parameters[i]))
  i = i + 1
  NCTools.PrintDoubless(NCTools.GetDoubless(parameters[i]))
  i = i + 1
  NCTools.PrintDoubles(NCTools.GetDoubles(parameters[i]))
  i = i + 1
  NCTools.PrintDoubleList(NCTools.GetDoubleList(parameters[i]))
  i = i + 1
  NCTools.PrintDoubleListList(NCTools.GetDoubleListList(parameters[i]))
  i = i + 1

  NCTools.PrintString(NCTools.GetString(parameters[i]))
  i = i + 1
  NCTools.PrintStringList(NCTools.GetStringList(parameters[i]))
  NCTools.PrintStrings(NCTools.GetStrings(parameters[i]))
  i = i + 1
  NCTools.PrintStringListList(NCTools.GetStringListList(parameters[i]))
  NCTools.PrintStringss(NCTools.GetStringss(parameters[i]))
  i = i + 1

  NCTools.PrintChar(NCTools.GetChar(parameters[i]))
  i = i + 1
  NCTools.PrintChars(NCTools.GetChars(parameters[i]))
  i = i + 1
  NCTools.PrintCharss(NCTools.GetCharss(parameters[i]))
  i = i + 1

  NCTools.PrintLong(NCTools.GetLong(parameters[i]))
  i = i + 1
  NCTools.PrintLongList(NCTools.GetLongList(parameters[i]))
  NCTools.PrintLongs(NCTools.GetLongs(parameters[i]))
  i = i + 1
  NCTools.PrintLongListList(NCTools.GetLongListList(parameters[i]))
  NCTools.PrintLongss(NCTools.GetLongss(parameters[i]))
  i = i + 1

  NCTools.PrintListNode(NCTools.GetListNode(parameters[i]))
  i = i + 1
  NCTools.PrintListNodeList(NCTools.GetListNodeList(parameters[i]))
  NCTools.PrintListNodes(NCTools.GetListNodes(parameters[i]))
  i = i + 1
  NCTools.PrintListNodeListList(NCTools.GetListNodeListList(parameters[i]))
  NCTools.PrintListNodess(NCTools.GetListNodess(parameters[i]))
  i = i + 1

  NCTools.PrintInterval(NCTools.GetInterval(parameters[i]))
  i = i + 1
  NCTools.PrintIntervalList(NCTools.GetIntervalList(parameters[i]))
  NCTools.PrintIntervals(NCTools.GetIntervals(parameters[i]))
  i = i + 1
  NCTools.PrintIntervalListList(NCTools.GetIntervalListList(parameters[i]))
  NCTools.PrintIntervalss(NCTools.GetIntervalss(parameters[i]))
  i = i + 1

  NCTools.PrintPoint(NCTools.GetPoint(parameters[i]))
  i = i + 1
  NCTools.PrintPointList(NCTools.GetPointList(parameters[i]))
  NCTools.PrintPoints(NCTools.GetPoints(parameters[i]))
  i = i + 1
  NCTools.PrintPointListList(NCTools.GetPointListList(parameters[i]))
  NCTools.PrintPointss(NCTools.GetPointss(parameters[i]))
  i = i + 1

  NCTools.PrintTreeNode(NCTools.GetTreeNode(parameters[i]))
  i = i + 1
  NCTools.PrintTreeNodeList(NCTools.GetTreeNodeList(parameters[i]))
  NCTools.PrintTreeNodes(NCTools.GetTreeNodes(parameters[i]))
  i = i + 1
  NCTools.PrintTreeNodeListList(NCTools.GetTreeNodeListList(parameters[i]))
  NCTools.PrintTreeNodess(NCTools.GetTreeNodess(parameters[i]))
  i = i + 1

  NCTools.PrintTreeLinkNode(NCTools.GetTreeLinkNode(parameters[i]))
  i = i + 1
  NCTools.PrintTreeLinkNodeList(NCTools.GetTreeLinkNodeList(parameters[i]))
  NCTools.PrintTreeLinkNodes(NCTools.GetTreeLinkNodes(parameters[i]))
  i = i + 1
  NCTools.PrintTreeLinkNodeListList(NCTools.GetTreeLinkNodeListList(parameters[i]))
  NCTools.PrintTreeLinkNodess(NCTools.GetTreeLinkNodess(parameters[i]))
  i = i + 1

  NCTools.PrintRandomListNode(NCTools.GetRandomListNode(parameters[i]))
  i = i + 1
  NCTools.PrintRandomListNodeList(NCTools.GetRandomListNodeList(parameters[i]))
  NCTools.PrintRandomListNodes(NCTools.GetRandomListNodes(parameters[i]))
  i = i + 1
  NCTools.PrintRandomListNodeListList(NCTools.GetRandomListNodeListList(parameters[i]))
  NCTools.PrintRandomListNodess(NCTools.GetRandomListNodess(parameters[i]))
  i = i + 1

  print NCTools.GetInt("#"), NCTools.GetLong("#"), NCTools.GetFloat("#"), NCTools.GetDouble("#")
end
