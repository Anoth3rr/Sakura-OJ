

import Foundation
private extension String {
    func at(_ at: Int) -> Character {
        let charIndex = self.index(self.startIndex, offsetBy: at)
        return self[charIndex]
    }
    func charAt(_ at: Int) -> Character {
        let charIndex = self.index(self.startIndex, offsetBy: at)
        return self[charIndex]
    }
    func substring(_ start: Int, _ end: Int) -> String {
        return String(self[self.index(self.startIndex, offsetBy: start)..<self.index(self.startIndex, offsetBy: end)])
    }
}

public class Point {
  public var x: Int
  public var y: Int
  public init(_ x: Int, _ y: Int) {
    self.x = x
    self.y = y
  }
}

public class Interval {
  public var start: Int
  public var end: Int
  public init(_ start: Int = 0, _ end: Int = 0) {
    self.start = start
    self.end = end
  }
}

public class TreeNode {
  public var val: Int
  public var left: TreeNode?
  public var right: TreeNode?
  public init(_ val: Int=0, _ left: TreeNode?=nil, _ right: TreeNode?=nil) {
    self.val = val
    self.left = left
    self.right = right
  }
}

public class ListNode {
  public var val: Int
  public var next: ListNode?
  public init(_ val: Int = 0, _ next: ListNode? = nil) {
    self.val = val
    self.next = next
  }
}
public class RandomListNode {
  public var val: Int
  //TODO
  init(_ val: Int = 0) {
    self.val = val
  }
}

public class TreeLinkNode {
  public var val: Int
  //TODO
  init(_ val: Int = 0) {
    self.val = val
  }
}

public class UndirectedGraphNode {
  var val: Int
  //TODO
  init(_ val: Int = 0) {
    self.val = val
  }
}

class NCTools {

    private static func NCPrint( _ items: Any...) {
      for it in items { 
        print(it, separator: "", terminator: "")
      }
    }


    private static func IsBeginRange(_ c: Character) -> Bool {
      return c == "{" || c == "[" || c == "("
    }

    private static func IsEndRange(_ c: Character) -> Bool {
      return c == "}" || c == "]" || c == ")"
    }

    static func GetArguments(_ line :String) -> [String] {
      var ret = [String]()
      if line.count == 0 {
        return []
      }
      var inrange = 0
      var pre_index = 0
      var inmao = false
      for i in 0..<line.count {
        if IsBeginRange(line.at(i)) && !inmao {
          inrange += 1
        } else if IsEndRange(line.at(i)) && !inmao {
          inrange -= 1
        } else if line.at(i) == "\"" {
          inmao = !inmao
        } else if line.at(i) == "," && inrange == 0 && !inmao { 
          ret.append(line.substring(pre_index, i))
          pre_index = i + 1
        }
      }
      ret.append(line.substring(pre_index, line.count))
      return ret
    }

    private static func GetRangeItems(_ str: String) -> [String] {
      // if str == nil {
      //   return []
      // }
      var begin = 0
      while !IsBeginRange(str.charAt(begin)) && begin < str.count {
        begin += 1
      }
      var end = str.count
      while !IsEndRange(str.charAt(end-1)) && end > 1 {
        end -= 1
      }
      let str = str.substring(begin+1, end-1)
      return str.trimmingCharacters(in: .whitespacesAndNewlines).count == 0 ?
        [String](): GetArguments(str)
    }

    static func GetInt(_ str: String) -> Int {
      return Int(str.trimmingCharacters(in: .whitespacesAndNewlines)) ?? 0
    }

    static func PrintInternal(_ x: Int) {
      NCPrint(x)
    }

    static func GetLong(_ str: String) -> Int64 {
      return Int64(str.trimmingCharacters(in: .whitespacesAndNewlines)) ?? 0
    }

    static func PrintInternal(_ x:Int64) {
      NCPrint(x)
    }

    static func GetFloat(_ str: String ) -> Float {
      return Float(str.trimmingCharacters(in: .whitespacesAndNewlines)) ?? 0.0
    }

    static func PrintInternal(_ d: Float) {
      if (abs(d) < 0.0000099999) {
        NCPrint("0.00000")
      } else {
        NCPrint(String(format: "%.05f", d))
      }
    }

    static func GetDouble(_ str: String) -> Double {
      return Double(str.trimmingCharacters(in: .whitespacesAndNewlines)) ?? 0.0
    }

    static func PrintInternal(_ d: Double) {
      if (abs(d) < 0.0000099999) {
        NCPrint("0.00000")
      } else {
        NCPrint(String(format: "%.05f", d))
      }
    }

    static func GetString(_ str: String ) -> String {
     // if str != nil {
      let str = str.trimmingCharacters(in: .whitespacesAndNewlines) 
      //}
      if str.at(0) != "\"" || str.at(str.count-1) != "\"" {
        return str
      }
      return str.substring(1, str.count - 1)
    }

    static func PrintInternal(_ str: String) {
      NCPrint("\"\(str)\"")
    }

    static func GetChar(_ str: String) -> Character {
      return str.trimmingCharacters(in: .whitespacesAndNewlines).count == 0 ? "#" : str.trimmingCharacters(in: .whitespacesAndNewlines).charAt(0)
    }

    static func PrintInternal(_ c: Character) {
      NCPrint(c)
    }

    static func GetBool(_ str: String) -> Bool {
      return str.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == "true"
    }

    static func PrintInternal(_ b: Bool) {
      NCPrint(b ? "true" : "false")
    }

    static func GetInterval(_ str: String) -> Interval {
      let items = GetInts(str)
      return items.count == 2 ? Interval(items[0], items[1]) : Interval(0, 0)
    }

    static func PrintInternal(_ interval :Interval) {
      NCPrint("[\(interval.start),\(interval.end)]")
    }

    static func GetPoint(_ str: String) -> Point {
      let items = GetInts(str)
      return items.count == 2 ? Point(items[0], items[1]) : Point(0, 0)
    }

    static func PrintInternal(_ point: Point) {
      NCPrint("(\(point.x),\(point.y))")
    }

    static private let LEFT = 0
    static private let RIGHT = 1
    static func GetTreeNode(_ str: String ) -> TreeNode? {
      let items = GetRangeItems(str)
      if items.isEmpty {
        return nil
      }
      var tree_nodes = [TreeNode?](repeating: nil, count: items.count + 1)
      var current = 0;
      /* 当前遍历节点位置 */
      var current_pos = LEFT;
      var index = 1;
      tree_nodes[0] = TreeNode(GetInt(items[0]))
     // print(str)
      for i in 1 ..< items.count {
        if items[i].trimmingCharacters(in: .whitespacesAndNewlines) == "#" {
          if tree_nodes[current] != nil {
            if current_pos == LEFT {
              current_pos = RIGHT
            } else if tree_nodes[current + 1] != nil {
              current += 1
              current_pos = LEFT
            }
          }
        } else {
          tree_nodes[index] = TreeNode(GetInt(items[i]))
         // NCPrint(index, ":" , items[i], ", ")
          if current_pos == LEFT {
            tree_nodes[current]!.left = tree_nodes[index]
            current_pos = RIGHT
          } else {
            tree_nodes[current]!.right = tree_nodes[index]
            current += 1
            current_pos = LEFT
          }
          index += 1
        }
      }

      return tree_nodes[0]
    }

    static func PrintInternal(_ root: TreeNode?) {
      if root ==  nil {
        NCPrint("{}")
        return
      }
      NCPrint("{")
      var v = [TreeNode?]()
      if root != nil {
        v.append(root)
      }
      var c = 0
      var none = ""
      while c < v.count {
        if c == 0 {
          NCPrint(v[c]!.val)
          v.append(v[c]!.left)
          v.append(v[c]!.right)
        } else {
          if v[c] == nil {
            none = none + ",#"
          } else {
            NCPrint("\(none),\(v[c]!.val)")
            none = ""
            v.append(v[c]!.left)
            v.append(v[c]!.right)
          }
        }
        c += 1
      }
      NCPrint("}")
    }

    static func GetListNode(_ str: String) -> ListNode? {
      let items = GetInts(str)
      if items.count == 0 {
        return nil
      }
      let head: ListNode? = ListNode(items[0])
      var tail = head
      for i in 1 ..< items.count {
        tail?.next = ListNode(items[i])
        tail = tail?.next
      }
      return head
    }

    static func PrintInternal(_ head: ListNode?) {
      if (head == nil) {
        NCPrint("{}")
        return
      }
      var current: ListNode? = head
      NCPrint("{")
      while current != nil {
        if current === head {
          NCPrint(current!.val)
        } else {
          NCPrint(",\(current!.val)")
        }
        current = current?.next
      }
      NCPrint("}")
    }

    static func GetRandomListNode(_ str: String) -> RandomListNode  {
      // TODO
      return RandomListNode()
    }

    static func PrintInternal(_ head: RandomListNode?) {
      //TODO
    }

    /*
    * 二叉链接树序列化是通过按层遍历,#代表这这个节点为空节点,节点遍历以后再增加所有next节点数据,举个例子 1.nil / \ 2
    * .3.nil / 4.nil 5.nil
    * 
    * 以上二叉树会被序列化为 {[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}
    * 对于{[1,2,3,#,#,4,#,#,5],[#,5,#,#,#]}构造出来的链接树节点2的next指向5节点
    */
    static func GetTreeLinkNode(_ str: String) -> TreeLinkNode? {
      //TODO
      return TreeLinkNode()
    }

    static func PrintInternal(_ root: TreeLinkNode?) {
      //TODO
    }

    /**
     * 无向图里每个节点都有一个唯一的数字ID,每个节点的序列化通过[]保存,每个节点第一个元素后跟随的是这个节点连接的其他节点,以下图 1 / \ /
     * \ 0 --- 2 / \ \_/ 序列化后为{[0,1,2],[1,2],[2,2]}
     */
    static func GetUndirectedGraphNode(_ str: String) -> UndirectedGraphNode? {
      return UndirectedGraphNode()
    }

    static func PrintInternal(_ root: UndirectedGraphNode?) {
    }

    // Int
    static func GetIntSet(_ str: String) -> Set<Int> {
      return Set(GetRangeItems(str).map { GetInt($0) })
    }

    static func GetIntList(_ str: String) -> [Int] {
      return GetRangeItems(str).map{ GetInt($0) }
    }

    static func GetInts(_ str: String) -> [Int] {
      return GetRangeItems(str).map{ GetInt($0) }
    }


    static func GetIntListList(_ str: String) -> [[Int]] {
      return GetRangeItems(str).map{ GetIntList($0) }
    }

    static func GetIntss(_ str: String) -> [[Int]] {
      return GetRangeItems(str).map{ GetIntList($0) }
    }

    static func PrintIntListInternal(_ x: [Int]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintInt(_ x: Int) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintIntList(_ x: [Int]) {
      PrintIntListInternal(x)
      NCPrint("\n")
    }
    static func PrintInts(_ x: [Int]) {
      PrintIntListInternal(x)
      NCPrint("\n")
    }

    static func PrintIntListList(_ x: [[Int]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintIntListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintIntss(_ x: [[Int]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintIntListInternal(x[i])
      }
      NCPrint("]\n")
    }

    // Bool
    static func GetBoolSet(_ str: String) -> Set<Bool> {
      return Set(GetRangeItems(str).map { GetBool($0) })
    }

    static func GetBoolList(_ str: String) -> [Bool] {
      return GetRangeItems(str).map{ GetBool($0) }
    }

    static func GetBools(_ str: String) -> [Bool] {
      return GetRangeItems(str).map{ GetBool($0) }
    }


    static func GetBoolListList(_ str: String) -> [[Bool]] {
      return GetRangeItems(str).map{ GetBoolList($0) }
    }

    static func GetBoolss(_ str: String) -> [[Bool]] {
      return GetRangeItems(str).map{ GetBoolList($0) }
    }

    static func PrintBoolListInternal(_ x: [Bool]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintBool(_ x: Bool) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintBoolList(_ x: [Bool]) {
      PrintBoolListInternal(x)
      NCPrint("\n")
    }
    static func PrintBools(_ x: [Bool]) {
      PrintBoolListInternal(x)
      NCPrint("\n")
    }

    static func PrintBoolListList(_ x: [[Bool]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintBoolListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintBoolss(_ x: [[Bool]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintBoolListInternal(x[i])
      }
      NCPrint("]\n")
    }

    // Float
    static func GetFloatSet(_ str: String) -> Set<Float> {
      return Set(GetRangeItems(str).map { GetFloat($0) })
    }

    static func GetFloatList(_ str: String) -> [Float] {
      return GetRangeItems(str).map{ GetFloat($0) }
    }

    static func GetFloats(_ str: String) -> [Float] {
      return GetRangeItems(str).map{ GetFloat($0) }
    }


    static func GetFloatListList(_ str: String) -> [[Float]] {
      return GetRangeItems(str).map{ GetFloatList($0) }
    }

    static func GetFloatss(_ str: String) -> [[Float]] {
      return GetRangeItems(str).map{ GetFloatList($0) }
    }

    static func PrintFloatListInternal(_ x: [Float]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintFloat(_ x: Float) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintFloatList(_ x: [Float]) {
      PrintFloatListInternal(x)
      NCPrint("\n")
    }
    static func PrintFloats(_ x: [Float]) {
      PrintFloatListInternal(x)
      NCPrint("\n")
    }

    static func PrintFloatListList(_ x: [[Float]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintFloatListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintFloatss(_ x: [[Float]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintFloatListInternal(x[i])
      }
      NCPrint("]\n")
    }

    // Double
    static func GetDoubleSet(_ str: String) -> Set<Double> {
      return Set(GetRangeItems(str).map { GetDouble($0) })
    }

    static func GetDoubleList(_ str: String) -> [Double] {
      return GetRangeItems(str).map{ GetDouble($0) }
    }

    static func GetDoubles(_ str: String) -> [Double] {
      return GetRangeItems(str).map{ GetDouble($0) }
    }


    static func GetDoubleListList(_ str: String) -> [[Double]] {
      return GetRangeItems(str).map{ GetDoubleList($0) }
    }

    static func GetDoubless(_ str: String) -> [[Double]] {
      return GetRangeItems(str).map{ GetDoubleList($0) }
    }

    static func PrintDoubleListInternal(_ x: [Double]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintDouble(_ x: Double) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintDoubleList(_ x: [Double]) {
      PrintDoubleListInternal(x)
      NCPrint("\n")
    }
    static func PrintDoubles(_ x: [Double]) {
      PrintDoubleListInternal(x)
      NCPrint("\n")
    }

    static func PrintDoubleListList(_ x: [[Double]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintDoubleListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintDoubless(_ x: [[Double]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintDoubleListInternal(x[i])
      }
      NCPrint("]\n")
    }

    // String
    static func GetStringSet(_ str: String) -> Set<String> {
      return Set(GetRangeItems(str).map { GetString($0) })
    }

    static func GetStringList(_ str: String) -> [String] {
      return GetRangeItems(str).map{ GetString($0) }
    }

    static func GetStrings(_ str: String) -> [String] {
      return GetRangeItems(str).map{ GetString($0) }
    }


    static func GetStringListList(_ str: String) -> [[String]] {
      return GetRangeItems(str).map{ GetStringList($0) }
    }

    static func GetStringss(_ str: String) -> [[String]] {
      return GetRangeItems(str).map{ GetStringList($0) }
    }

    static func PrintStringListInternal(_ x: [String]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintString(_ x: String) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintStringList(_ x: [String]) {
      PrintStringListInternal(x)
      NCPrint("\n")
    }
    static func PrintStrings(_ x: [String]) {
      PrintStringListInternal(x)
      NCPrint("\n")
    }

    static func PrintStringListList(_ x: [[String]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintStringListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintStringss(_ x: [[String]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintStringListInternal(x[i])
      }
      NCPrint("]\n")
    }

    // Char
    static func GetCharSet(_ str: String) -> Set<Character> {
      return Set(GetRangeItems(str).map { GetChar($0) })
    }

    static func GetCharList(_ str: String) -> [Character] {
      return GetRangeItems(str).map{ GetChar($0) }
    }

    static func GetChars(_ str: String) -> [Character] {
      return GetRangeItems(str).map{ GetChar($0) }
    }


    static func GetCharListList(_ str: String) -> [[Character]] {
      return GetRangeItems(str).map{ GetCharList($0) }
    }

    static func GetCharss(_ str: String) -> [[Character]] {
      return GetRangeItems(str).map{ GetCharList($0) }
    }

    static func PrintCharListInternal(_ x: [Character]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintChar(_ x: Character) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintCharList(_ x: [Character]) {
      PrintCharListInternal(x)
      NCPrint("\n")
    }
    static func PrintChars(_ x: [Character]) {
      PrintCharListInternal(x)
      NCPrint("\n")
    }

    static func PrintCharListList(_ x: [[Character]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintCharListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintCharss(_ x: [[Character]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintCharListInternal(x[i])
      }
      NCPrint("]\n")
    }

    // Long
    static func GetLongSet(_ str: String) -> Set<Int64> {
      return Set(GetRangeItems(str).map { GetLong($0) })
    }

    static func GetLongList(_ str: String) -> [Int64] {
      return GetRangeItems(str).map{ GetLong($0) }
    }

    static func GetLongs(_ str: String) -> [Int64] {
      return GetRangeItems(str).map{ GetLong($0) }
    }


    static func GetLongListList(_ str: String) -> [[Int64]] {
      return GetRangeItems(str).map{ GetLongList($0) }
    }

    static func GetLongss(_ str: String) -> [[Int64]] {
      return GetRangeItems(str).map{ GetLongList($0) }
    }

    static func PrintLongListInternal(_ x: [Int64]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintLong(_ x: Int64) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintLongList(_ x: [Int64]) {
      PrintLongListInternal(x)
      NCPrint("\n")
    }
    static func PrintLongs(_ x: [Int64]) {
      PrintLongListInternal(x)
      NCPrint("\n")
    }

    static func PrintLongListList(_ x: [[Int64]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintLongListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintLongss(_ x: [[Int64]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintLongListInternal(x[i])
      }
      NCPrint("]\n")
    }

    // ListNode
    // static func GetListNodeSet(_ str: String) -> Set<ListNode?> {
      // return Set(GetRangeItems(str).map { GetListNode($0) })
    // }

    static func GetListNodeList(_ str: String) -> [ListNode?] {
      return GetRangeItems(str).map{ GetListNode($0) }
    }

    static func GetListNodes(_ str: String) -> [ListNode?] {
      return GetRangeItems(str).map{ GetListNode($0) }
    }


    static func GetListNodeListList(_ str: String) -> [[ListNode?]] {
      return GetRangeItems(str).map{ GetListNodeList($0) }
    }

    static func GetListNodess(_ str: String) -> [[ListNode?]] {
      return GetRangeItems(str).map{ GetListNodeList($0) }
    }

    static func PrintListNodeListInternal(_ x: [ListNode?]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintListNode(_ x: ListNode?) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintListNodeList(_ x: [ListNode?]) {
      PrintListNodeListInternal(x)
      NCPrint("\n")
    }
    static func PrintListNodes(_ x: [ListNode?]) {
      PrintListNodeListInternal(x)
      NCPrint("\n")
    }

    static func PrintListNodeListList(_ x: [[ListNode?]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintListNodeListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintListNodess(_ x: [[ListNode?]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintListNodeListInternal(x[i])
      }
      NCPrint("]\n")
    }

    // Point
    // static func GetPointSet(_ str: String) -> Set<Point> {
    //   return Set(GetRangeItems(str).map { GetPoint($0) })
    // }

    static func GetPointList(_ str: String) -> [Point] {
      return GetRangeItems(str).map{ GetPoint($0) }
    }

    static func GetPoints(_ str: String) -> [Point] {
      return GetRangeItems(str).map{ GetPoint($0) }
    }


    static func GetPointListList(_ str: String) -> [[Point]] {
      return GetRangeItems(str).map{ GetPointList($0) }
    }

    static func GetPointss(_ str: String) -> [[Point]] {
      return GetRangeItems(str).map{ GetPointList($0) }
    }

    static func PrintPointListInternal(_ x: [Point]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintPoint(_ x: Point) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintPointList(_ x: [Point]) {
      PrintPointListInternal(x)
      NCPrint("\n")
    }
    static func PrintPoints(_ x: [Point]) {
      PrintPointListInternal(x)
      NCPrint("\n")
    }

    static func PrintPointListList(_ x: [[Point]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintPointListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintPointss(_ x: [[Point]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintPointListInternal(x[i])
      }
      NCPrint("]\n")
    }
    // Interval
    // static func GetIntervalSet(_ str: String) -> Set<Interval> {
    //   return Set(GetRangeItems(str).map { GetInterval($0) })
    // }

    static func GetIntervalList(_ str: String) -> [Interval] {
      return GetRangeItems(str).map{ GetInterval($0) }
    }

    static func GetIntervals(_ str: String) -> [Interval] {
      return GetRangeItems(str).map{ GetInterval($0) }
    }


    static func GetIntervalListList(_ str: String) -> [[Interval]] {
      return GetRangeItems(str).map{ GetIntervalList($0) }
    }

    static func GetIntervalss(_ str: String) -> [[Interval]] {
      return GetRangeItems(str).map{ GetIntervalList($0) }
    }

    static func PrintIntervalListInternal(_ x: [Interval]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintInterval(_ x: Interval) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintIntervalList(_ x: [Interval]) {
      PrintIntervalListInternal(x)
      NCPrint("\n")
    }
    static func PrintIntervals(_ x: [Interval]) {
      PrintIntervalListInternal(x)
      NCPrint("\n")
    }

    static func PrintIntervalListList(_ x: [[Interval]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintIntervalListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintIntervalss(_ x: [[Interval]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintIntervalListInternal(x[i])
      }
      NCPrint("]\n")
    }

    // TreeNode
    // static func GetTreeNodeSet(_ str: String) -> Set<TreeNode> {
    //   return Set(GetRangeItems(str).map { GetTreeNode($0) })
    // }

    static func GetTreeNodeList(_ str: String) -> [TreeNode?] {
      return GetRangeItems(str).map{ GetTreeNode($0) }
    }

    static func GetTreeNodes(_ str: String) -> [TreeNode?] {
      return GetRangeItems(str).map{ GetTreeNode($0) }
    }


    static func GetTreeNodeListList(_ str: String) -> [[TreeNode?]] {
      return GetRangeItems(str).map{ GetTreeNodeList($0) }
    }

    static func GetTreeNodess(_ str: String) -> [[TreeNode?]] {
      return GetRangeItems(str).map{ GetTreeNodeList($0) }
    }

    static func PrintTreeNodeListInternal(_ x: [TreeNode?]) {
      NCPrint("[")
      for i in 0..<x.count {
        if i != 0 {
          NCPrint(",")
        }
        PrintInternal(x[i])
      }
      NCPrint("]")
    }

    static func PrintTreeNode(_ x: TreeNode?) {
      PrintInternal(x)
      NCPrint("\n")
    }

    static func PrintTreeNodeList(_ x: [TreeNode?]) {
      PrintTreeNodeListInternal(x)
      NCPrint("\n")
    }
    static func PrintTreeNodes(_ x: [TreeNode?]) {
      PrintTreeNodeListInternal(x)
      NCPrint("\n")
    }

    static func PrintTreeNodeListList(_ x: [[TreeNode?]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintTreeNodeListInternal(x[i])
      }
      NCPrint("]\n")
    }

    static func PrintTreeNodess(_ x: [[TreeNode?]]) {
      NCPrint("[")
      for i in 0..<x.count {
        if (i != 0) {
          NCPrint(",")
        }
        PrintTreeNodeListInternal(x[i])
      }
      NCPrint("]\n")
    }


    private static func Testing() {
      var line = "1 , [ 1 , 2 ],[[1],[2],[3,4,-5]],[ 1 , 2 ],[[1],[2],[3,4,5]]," // int
        line = line +  "true , [ false , true ],[[false],[false],[false,true,true]],[ true , false ],[[false],[true],[true,true,true]]," // bool
        line = line + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [ 1 , 2 ],[[1],[2],[3,4,5]]," // float
        line = line + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [],[ 1 , 2 ],[[1],[2],[3,4,5]]," // double
        line = line + " \"a\", [\"\",\"x[[[[,,,,[}}}}\"], [[acd, efg], [acd, \"efg\"]],"// string
        line = line + " a, [x, y ], [[a, b],[], [c, d]],"// char
        line = line + " 1000000000, [3000000000, 2000000000 ], [[3000000000, 2000000000 ],[13000000000, 22000000000 ]],"// long
        line = line + "{1,3,4},[{2, 4, 5},{5,6,7,89,11},{ }],[[{2, 4, 5},{5,6,7,89,11},{}],[{2, 4, 5},{5,6,7,89,11}]]," // ListNode
        line = line + "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]]," // Interval
        line = line + "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]]," // Point
        line = line + "{1,2,3,#,#,4,#,#,5},[{1,2,3,#,#,4,#,#,5}],[[{1,2,3,#,#,4,#,#,5}],[{1,2,3,#,#,4,#,#,5},{1,2,3,#,#,4,#,#,5}]]," // TreeNode
        line = line + "{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]},[{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}],[[],[{[],[]}], [{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}]]," // TreeLinkNode
        line = line + "{ -1, 8, 7,  -3,4,4,-3,#,#,-1}, [{ -1, 8, 7,  -3,4,4,-3,#,#,-1}], [[{}],[{ -1, 8, 7,  -3,4,4,-3,#,#,-1}]]," // RandomListNode
        line = line + "{[0,1,2],[1,2],[2,2]}, [{[0,1,2],[1,2],[2,2]}], [[], [{[0,1,2],[1,2],[2,2]},{[0,1,2],[1,2],[2,2]}]]" //
        
        var i = 0
        let parameters = GetArguments(line)
        i = 0
        PrintInt(GetInt(parameters[i]))
        i = i + 1
        PrintIntList(GetInts(parameters[i]))
        i = i + 1
        PrintIntListList(GetIntss(parameters[i]))
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
      
        
        /*PrintTreeLinkNode(GetTreeLinkNode(parameters[i]))*/
        /*i = i + 1*/
        /*PrintTreeLinkNodeList(GetTreeLinkNodeList(parameters[i]))*/
        /*PrintTreeLinkNodes(GetTreeLinkNodes(parameters[i]))*/
        /*i = i + 1*/
        /*PrintTreeLinkNodeListList(GetTreeLinkNodeListList(parameters[i]))*/
        /*PrintTreeLinkNodess(GetTreeLinkNodess(parameters[i]))*/
        /*i = i + 1*/
        
        /*PrintRandomListNode(GetRandomListNode(parameters[i]))*/
        /*i = i + 1*/
        /*PrintRandomListNodeList(GetRandomListNodeList(parameters[i]))*/
        /*PrintRandomListNodes(GetRandomListNodes(parameters[i]))*/
        /*i = i + 1*/
        /*PrintRandomListNodeListList(GetRandomListNodeListList(parameters[i]))*/
        /*PrintRandomListNodess(GetRandomListNodess(parameters[i]))*/
        /*i = i + 1*/
        

    }
}
// Testing()




