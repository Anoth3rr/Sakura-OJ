package main

import (
    "fmt"
    "strings"
    "strconv"
)

//定义错误常量
const (
    LEFT = 0
    RIGHT = 1
)

func IsBeginRange(c byte) bool {
    return c == '{' || c == '[' || c == '(';
}

func IsEndRange(c byte) bool {
    return c == ']' || c == ')' || c == '}';
}

func GetArguments(line string) []string {
    var ret []string
    if (line == "") {
        return ret;
    }

    inrange := 0;
    pre_index := 0;
    inmao := false;
    for i := 0; i < len(line); i++ {
        if (IsBeginRange(line[i]) && !inmao) {
            inrange = inrange + 1;
        } else if (IsEndRange(line[i]) && !inmao) {
            inrange = inrange - 1;
        } else if (line[i] == '"') {
            inmao = !inmao;
        } else if (line[i] == ',' && inrange == 0 && !inmao) {
            ret = append(ret, line[pre_index:i])
            pre_index = i + 1;
        }
    }
    ret = append(ret, line[pre_index:])
    return ret;
}

func GetRangeItems(line string) []string {
    var ret []string
    if (line == "") {
        return ret;
    }

    begin := 0;
    for !IsBeginRange(line[begin]) && begin < len(line) {
        begin = begin + 1;
    }
    end := len(line);
    for !IsEndRange(line[end-1]) && end > 1 {
        end = end - 1;
    }
    line = line[begin + 1 : end -1];
    if(len(strings.TrimSpace(line)) == 0){
        return ret;
    }
    return GetArguments(line);
}

func GetInt(line string) int{
    if(line == ""){
        return 0;
    }
    i, err := strconv.Atoi(strings.TrimSpace(line))
    if err != nil {
        return 0;
    }
    return i;
}

func GetIntList(line string) []int {
    items := GetRangeItems(line);
    var ret []int
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetInt(items[i]))
    }
    return ret
}

func GetInts(line string) []int {
    return GetIntList(line);
}

func GetIntListList(line string) [][]int {
    items := GetRangeItems(line);
    var ret [][]int
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetIntList(items[i]))
    }
    return ret;
}

func GetIntss(line string) [][]int {
    return GetIntListList(line);
}

func PrintIntInternal(x int) {
    fmt.Printf("%d", x)
}

func PrintInt(x int) {
    PrintIntInternal(x);
    fmt.Println();
}

func PrintIntListInternal(x []int){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf("%s", ",");
        }
        PrintIntInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintIntList(x []int){
    PrintIntListInternal(x);
    fmt.Println();
}

func PrintIntListList(x [][]int){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf("%s", ",");
        }
        PrintIntListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintInts(x []int){
    PrintIntList(x);
}

func PrintIntss(x [][]int){
    PrintIntListList(x);
}

//bool
func GetBool(line string) bool{
    if(line == ""){
        return false;
    }
    i, err := strconv.ParseBool(strings.TrimSpace(line))
    if err != nil {
        return false;
    }
    return i;
}

func GetBoolList(line string) []bool {
    items := GetRangeItems(line);
    var ret []bool
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetBool(items[i]))
    }
    return ret
}

func GetBools(line string) []bool {
    return GetBoolList(line);
}

func GetBoolListList(line string) [][]bool {
    items := GetRangeItems(line);
    var ret [][]bool
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetBoolList(items[i]))
    }
    return ret;
}

func GetBoolss(line string) [][]bool {
    return GetBoolListList(line);
}

func PrintBoolInternal(x bool) {
    fmt.Printf("%t", x)
}

func PrintBool(x bool) {
    PrintBoolInternal(x);
    fmt.Println();
}

func PrintBoolListInternal(x []bool){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf("%s", ",");
        }
        PrintBoolInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintBoolList(x []bool){
    PrintBoolListInternal(x);
    fmt.Println();
}

func PrintBoolListList(x [][]bool){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf("%s", ",");
        }
        PrintBoolListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintBools(x []bool){
    PrintBoolList(x);
}

func PrintBoolss(x [][]bool){
    PrintBoolListList(x);
}

//long 
func GetLong(line string) int64{
    if(line == ""){
        return 0;
    }
    i, err := strconv.ParseInt(strings.TrimSpace(line), 10, 64)
    if err != nil {
        return 0;
    }
    return i;
}

func GetLongList(line string) []int64 {
    items := GetRangeItems(line);
    var ret []int64
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetLong(items[i]))
    }
    return ret
}

func GetLongs(line string) []int64 {
    return GetLongList(line);
}

func GetLongListList(line string) [][]int64 {
    items := GetRangeItems(line);
    var ret [][]int64
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetLongList(items[i]))
    }
    return ret;
}

func GetLongss(line string) [][]int64 {
    return GetLongListList(line);
}

func PrintLongInternal(x int64) {
    fmt.Printf("%d", x)
}

func PrintLong(x int64) {
    PrintLongInternal(x);
    fmt.Println();
}

func PrintLongListInternal(x []int64){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf("%s", ",");
        }
        PrintLongInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintLongList(x []int64){
    PrintLongListInternal(x);
    fmt.Println();
}

func PrintLongListList(x [][]int64){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf("%s", ",");
        }
        PrintLongListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintLongs(x []int64){
    PrintLongList(x);
}

func PrintLongss(x [][]int64){
    PrintLongListList(x);
}

//float
func GetFloat(line string) float32{
    if(line == ""){
        return 0;
    }
    i, err := strconv.ParseFloat(strings.TrimSpace(line), 32)
    if err != nil {
        return 0;
    }
    return float32(i);
}

func GetFloatList(line string) []float32 {
    items := GetRangeItems(line);
    var ret []float32
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetFloat(items[i]))
    }
    return ret
}

func GetFloats(line string) []float32 {
    return GetFloatList(line);
}

func GetFloatListList(line string) [][]float32 {
    items := GetRangeItems(line);
    var ret [][]float32
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetFloatList(items[i]))
    }
    return ret;
}

func GetFloatss(line string) [][]float32 {
    return GetFloatListList(line);
}

func PrintFloatInternal(x float32) {
    fmt.Printf("%.5f", x)
}

func PrintFloat(x float32) {
    PrintFloatInternal(x);
    fmt.Println();
}

func PrintFloatListInternal(x []float32){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintFloatInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintFloatList(x []float32){
    PrintFloatListInternal(x);
    fmt.Println();
}

func PrintFloatListList(x [][]float32){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintFloatListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintFloats(x []float32){
    PrintFloatList(x);
}

func PrintFloatss(x [][]float32){
    PrintFloatListList(x);
}

//double
func GetDouble(line string) float64{
    if(line == ""){
        return 0;
    }
    i, err := strconv.ParseFloat(strings.TrimSpace(line), 64)
    if err != nil {
        return 0;
    }
    return i;
}

func GetDoubleList(line string) []float64 {
    items := GetRangeItems(line);
    var ret []float64
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetDouble(items[i]))
    }
    return ret
}

func GetDoubles(line string) []float64 {
    return GetDoubleList(line);
}

func GetDoubleListList(line string) [][]float64 {
    items := GetRangeItems(line);
    var ret [][]float64
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetDoubleList(items[i]))
    }
    return ret;
}

func GetDoubless(line string) [][]float64 {
    return GetDoubleListList(line);
}

func PrintDoubleInternal(x float64) {
    fmt.Printf("%.5f", x)
}

func PrintDouble(x float64) {
    PrintDoubleInternal(x);
    fmt.Println();
}

func PrintDoubleListInternal(x []float64){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintDoubleInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintDoubleList(x []float64){
    PrintDoubleListInternal(x);
    fmt.Println();
}

func PrintDoubleListList(x [][]float64){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintDoubleListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintDoubles(x []float64){
    PrintDoubleList(x);
}

func PrintDoubless(x [][]float64){
    PrintDoubleListList(x);
}

//string
func GetString(line string) string {
    if(line == "") {
        return "";
    }
    line = strings.TrimSpace(line);
    if(len(line) == 0){
        return "";
    }

    if(line[0] == '"' && line[len(line) - 1] == '"'){
        return line[1:len(line) - 1];
    }

    return line;
}

func GetStringList(line string) []string {
    items := GetRangeItems(line);
    var ret []string
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetString(items[i]))
    }
    return ret
}

func GetStrings(line string) []string {
    return GetStringList(line);
}

func GetStringListList(line string) [][]string {
    items := GetRangeItems(line);
    var ret [][]string
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetStringList(items[i]))
    }
    return ret;
}

func GetStringss(line string) [][]string {
    return GetStringListList(line);
}

func PrintStringInternal(x string) {
    fmt.Printf("\"%s\"", x)
}

func PrintString(x string) {
    PrintStringInternal(x);
    fmt.Println();
}

func PrintStringListInternal(x []string){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintStringInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintStringList(x []string){
    PrintStringListInternal(x);
    fmt.Println();
}

func PrintStringListList(x [][]string){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintStringListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintStrings(x []string){
    PrintStringList(x);
}

func PrintStringss(x [][]string){
    PrintStringListList(x);
}

//char
func GetChar(line string) byte{
    if(line == ""){
        return '#';
    }
    line = strings.TrimSpace(line)
    if(line == ""){
        return '#';
    }
    return line[0];
}

func GetCharList(line string) []byte {
    items := GetRangeItems(line);
    var ret []byte
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetChar(items[i]))
    }
    return ret
}

func GetChars(line string) []byte {
    return GetCharList(line);
}

func GetCharListList(line string) [][]byte {
    items := GetRangeItems(line);
    var ret [][]byte
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetCharList(items[i]))
    }
    return ret;
}

func GetCharss(line string) [][]byte {
    return GetCharListList(line);
}

func PrintCharInternal(x byte) {
    fmt.Printf("%s", string(x))
}

func PrintChar(x byte) {
    PrintCharInternal(x);
    fmt.Println();
}

func PrintCharListInternal(x []byte){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintCharInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintCharList(x []byte){
    PrintCharListInternal(x);
    fmt.Println();
}

func PrintCharListList(x [][]byte){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintCharListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintChars(x []byte){
    PrintCharList(x);
}

func PrintCharss(x [][]byte){
    PrintCharListList(x);
}

//listnode
func GetListNode(line string) *ListNode{
    items := GetIntList(line);
    if(len(items) == 0){
        return nil;
    }
    var head *ListNode = &ListNode{Val: items[0], Next: nil}
    var tail = head;
    for i := 1; i < len(items);i++ {
        tail.Next = &ListNode{Val: items[i], Next: nil}
        tail = tail.Next;
    }
    return head;
}

func PrintListNodeInternal(head *ListNode){
    if(head == nil){
        fmt.Printf("{}");
        return;
    }
    var current = head;
    fmt.Printf("{");
    for current != nil {
        if(current == head){
            fmt.Printf("%d", current.Val);
        } else {
            fmt.Printf(",%d", current.Val);
        }
        current = current.Next;
    }
    fmt.Printf("}");
}

func GetListNodeList(line string) []*ListNode {
    items := GetRangeItems(line);
    var ret []*ListNode
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetListNode(items[i]))
    }
    return ret
}

func GetListNodes(line string) []*ListNode {
    return GetListNodeList(line);
}

func GetListNodeListList(line string) [][]*ListNode {
    items := GetRangeItems(line);
    var ret [][]*ListNode
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetListNodeList(items[i]))
    }
    return ret;
}

func GetListNodess(line string) [][]*ListNode {
    return GetListNodeListList(line);
}

func PrintListNode(x *ListNode) {
    PrintListNodeInternal(x);
    fmt.Println();
}

func PrintListNodeListInternal(x []*ListNode){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintListNodeInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintListNodeList(x []*ListNode){
    PrintListNodeListInternal(x);
    fmt.Println();
}

func PrintListNodeListList(x [][]*ListNode){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintListNodeListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintListNodes(x []*ListNode){
    PrintListNodeList(x);
}

func PrintListNodess(x [][]*ListNode){
    PrintListNodeListList(x);
}

//TreeNode
func GetTreeNode(line string) *TreeNode{
    items := GetRangeItems(line);
    if(len(items) == 0){
        return nil;
    }
    tree_nodes := make([]*TreeNode, len(items)+1);
    current := 0;
    current_pos := LEFT;
    index := 1;
    tree_nodes[0] = &TreeNode{Val:GetInt(items[0])};
    for i := 1; i < len(items); i++ {
        if(strings.TrimSpace(items[i]) == "#"){
            if(tree_nodes[current] != nil){
                if(current_pos == LEFT){
                    current_pos = RIGHT;
                } else if(tree_nodes[current + 1] != nil){
                    current = current + 1;
                    current_pos = LEFT;
                }
            }
        } else {
            tree_nodes[index] =  &TreeNode{Val:GetInt(items[i])}
            if(current_pos == LEFT){
                tree_nodes[current].Left = tree_nodes[index];
                current_pos = RIGHT;
            } else {
                tree_nodes[current].Right = tree_nodes[index];
                current = current + 1;
                current_pos = LEFT;
            }
            index = index + 1;
        }
    }
    return tree_nodes[0];
}

func PrintTreeNodeInternal(root *TreeNode){

    if(root == nil) {
        fmt.Printf("{}");
        return;
    }
    fmt.Printf("{");
    var v []*TreeNode
    v = append(v, root)
    c := 0;
    none := "";
    for c < len(v) {
        if (c == 0){
            fmt.Printf("%d", v[c].Val);
            v = append(v, v[c].Left)
            v = append(v, v[c].Right)
        } else {
            if(v[c] == nil){
                none = none + ",#";
            } else {
                fmt.Printf("%s,%d", none, v[c].Val);
                none = "";
                v = append(v, v[c].Left)
                v = append(v, v[c].Right)
            }
        }
        c = c+1;
    }
    fmt.Printf("}");
}

func GetTreeNodeList(line string) []*TreeNode {
    items := GetRangeItems(line);
    var ret []*TreeNode
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetTreeNode(items[i]))
    }
    return ret
}

func GetTreeNodes(line string) []*TreeNode {
    return GetTreeNodeList(line);
}

func GetTreeNodeListList(line string) [][]*TreeNode {
    items := GetRangeItems(line);
    var ret [][]*TreeNode
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetTreeNodeList(items[i]))
    }
    return ret;
}

func GetTreeNodess(line string) [][]*TreeNode {
    return GetTreeNodeListList(line);
}

func PrintTreeNode(x *TreeNode) {
    PrintTreeNodeInternal(x);
    fmt.Println();
}

func PrintTreeNodeListInternal(x []*TreeNode){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintTreeNodeInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintTreeNodeList(x []*TreeNode){
    PrintTreeNodeListInternal(x);
    fmt.Println();
}

func PrintTreeNodeListList(x [][]*TreeNode){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintTreeNodeListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintTreeNodes(x []*TreeNode){
    PrintTreeNodeList(x);
}

func PrintTreeNodess(x [][]*TreeNode){
    PrintTreeNodeListList(x);
}

//Interval
func GetInterval(line string) *Interval{

    items := GetIntList(line);
    if(len(items) == 2) {
        return &Interval{Start:items[0], End:items[1]};
    }
    return &Interval{Start:0, End:0};
}

func PrintIntervalInternal(interval *Interval){

    fmt.Printf("[%d,%d]", interval.Start, interval.End);
}

func GetIntervalList(line string) []*Interval {
    items := GetRangeItems(line);
    var ret []*Interval
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetInterval(items[i]))
    }
    return ret
}

func GetIntervals(line string) []*Interval {
    return GetIntervalList(line);
}

func GetIntervalListList(line string) [][]*Interval {
    items := GetRangeItems(line);
    var ret [][]*Interval
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetIntervalList(items[i]))
    }
    return ret;
}

func GetIntervalss(line string) [][]*Interval {
    return GetIntervalListList(line);
}

func PrintInterval(x *Interval) {
    PrintIntervalInternal(x);
    fmt.Println();
}

func PrintIntervalListInternal(x []*Interval){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintIntervalInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintIntervalList(x []*Interval){
    PrintIntervalListInternal(x);
    fmt.Println();
}

func PrintIntervalListList(x [][]*Interval){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintIntervalListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintIntervals(x []*Interval){
    PrintIntervalList(x);
}

func PrintIntervalss(x [][]*Interval){
    PrintIntervalListList(x);
}

//Point
func GetPoint(line string) *Point{
    items := GetIntList(line);
    if(len(items) == 2) {
        return &Point{X:items[0], Y:items[1]};
    }
    return &Point{X:0, Y:0};
}

func PrintPointInternal(point *Point){
    fmt.Printf("(%d,%d)", point.X, point.Y);
}

func GetPointList(line string) []*Point {
    items := GetRangeItems(line);
    var ret []*Point
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetPoint(items[i]))
    }
    return ret
}

func GetPoints(line string) []*Point {
    return GetPointList(line);
}

func GetPointListList(line string) [][]*Point {
    items := GetRangeItems(line);
    var ret [][]*Point
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetPointList(items[i]))
    }
    return ret;
}

func GetPointss(line string) [][]*Point {
    return GetPointListList(line);
}

func PrintPoint(x *Point) {
    PrintPointInternal(x);
    fmt.Println();
}

func PrintPointListInternal(x []*Point){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintPointInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintPointList(x []*Point){
    PrintPointListInternal(x);
    fmt.Println();
}

func PrintPointListList(x [][]*Point){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintPointListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintPoints(x []*Point){
    PrintPointList(x);
}

func PrintPointss(x [][]*Point){
    PrintPointListList(x);
}

//TreeLinknode
func GetTreeLinkNode(line string) *TreeLinkNode {
    all_items := GetRangeItems(line);
    is_newversion := len(all_items) == 2 && all_items[0][0] == '[' && all_items[1][0] == '[';
    if(!is_newversion){
        all_items = make([]string, 2)
        all_items = append(all_items, line)
        all_items = append(all_items, "[]")
    }
    if(len(all_items) < 2) {
        return nil
    }
    items := GetRangeItems(all_items[0]);
    if(len(items) == 0){
        return nil
    }

    tree_nodes := make([]*TreeLinkNode, len(items)+1);
    map_nodes := make(map[int]*TreeLinkNode)
    current := 0;
    current_pos := LEFT;
    index := 1;
    tree_nodes[0] = &TreeLinkNode{Val:GetInt (items [0])};
    for i := 1; i<len(items);i++{
        if(strings.TrimSpace(items[i]) == "#"){
            if(tree_nodes[current] != nil){
                if(current_pos == LEFT){
                    current_pos = RIGHT;
                } else if(tree_nodes[current + 1] != nil){
                    current = current + 1;
                    current_pos = LEFT;
                }
            }
        } else {
            label := GetInt(items [i]);
            tree_nodes [index] = &TreeLinkNode{Val:label};
            map_nodes [label] = tree_nodes [index];
            if(current_pos == LEFT){
                tree_nodes[current].Left = tree_nodes[index];
                current_pos = RIGHT;
            } else {
                tree_nodes[current].Right = tree_nodes[index];
                current = current + 1;
                current_pos = LEFT;
            }
            index = index + 1;
        }
    }
    // 连接next指针
    items = GetRangeItems(all_items [1]);
    for i := 0; i<len(items);i++ {
        if(strings.TrimSpace(items[i]) != "#" && map_nodes[GetInt (items [i])] != nil){
            tree_nodes[i].Next = tree_nodes[GetInt (items [i])];
        }
    }
    return tree_nodes[0]
}

func PrintTreeLinkNodeInternal(root *TreeLinkNode){
    if(root == nil) {
        fmt.Printf("{}");
        return;
    }
    fmt.Printf("{[");
    var v []*TreeLinkNode
    var label_node_v []*TreeLinkNode
    if(root != nil){
        v = append(v, root)
        label_node_v = append(label_node_v, root)
    }

    c := 0;
    none := "";
    for c < len(v) {
        if(c == 0){
            fmt.Printf("%d", v[c].Val)
            v = append(v, v[c].Left)
            v = append(v, v[c].Right)
        } else {
            if(v[c] == nil) {
                none = none + ",#";
            } else {
                label_node_v = append(label_node_v, v[c])
                fmt.Printf("%s,%d", none, v[c].Val);
                none = "";
                v = append(v, v[c].Left)
                v = append(v, v[c].Right)
            }
        }
        c = c + 1;
    }
    v = make([]*TreeLinkNode, 1)
    fmt.Printf("],[");
    for i := 0;i < len(label_node_v);i++ {
        if(i!= 0){
            fmt.Printf(",");
        }
        if(label_node_v[i].Next != nil){
            fmt.Printf("%d", label_node_v[i].Next.Val);
        } else {
            fmt.Printf("#");
        }
    }
    fmt.Printf("]}");
}

func GetTreeLinkNodeList(line string) []*TreeLinkNode {
    items := GetRangeItems(line);
    var ret []*TreeLinkNode
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetTreeLinkNode(items[i]))
    }
    return ret
}

func GetTreeLinkNodes(line string) []*TreeLinkNode {
    return GetTreeLinkNodeList(line);
}

func GetTreeLinkNodeListList(line string) [][]*TreeLinkNode {
    items := GetRangeItems(line);
    var ret [][]*TreeLinkNode
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetTreeLinkNodeList(items[i]))
    }
    return ret;
}

func GetTreeLinkNodess(line string) [][]*TreeLinkNode {
    return GetTreeLinkNodeListList(line);
}

func PrintTreeLinkNode(x *TreeLinkNode) {
    PrintTreeLinkNodeInternal(x);
    fmt.Println();
}

func PrintTreeLinkNodeListInternal(x []*TreeLinkNode) {
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintTreeLinkNodeInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintTreeLinkNodeList(x []*TreeLinkNode){
    PrintTreeLinkNodeListInternal(x);
    fmt.Println();
}

func PrintTreeLinkNodeListList(x [][]*TreeLinkNode){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintTreeLinkNodeListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintTreeLinkNodes(x []*TreeLinkNode){
    PrintTreeLinkNodeList(x);
}

func PrintTreeLinkNodess(x [][]*TreeLinkNode){
    PrintTreeLinkNodeListList(x);
}

//RandomListNode
func GetRandomListNode(line string) *RandomListNode{

    items := GetRangeItems(line);
    if(len(items) < 2){
        return nil
    }
    count := len(items) / 2;

    list_nodes := make([]*RandomListNode, count+1);
    nodes_map := make(map[int]*RandomListNode)
    head := &RandomListNode{Label:GetInt(items[0])};
    nodes_map[head.Label] = head;
    list_nodes[0] = head;
    tail := head;
    for i := 1; i<count;i++ {
        cur := &RandomListNode{Label:GetInt(items[i])};
        tail.Next = cur;
        tail = cur;
        nodes_map[cur.Label] = cur;
        list_nodes[i] = cur;
    }

    for i := count; i<len(items);i++ {
        if(strings.TrimSpace(items[i]) != "#" && nodes_map[GetInt(items[i])] != nil){
            list_nodes [i - count].Random = nodes_map[GetInt(items[i])];
        }
    }
    return head;
}

func PrintRandomListNodeInternal(head *RandomListNode){

    if(head == nil){
        fmt.Printf("{}");
        return;
    }
    current := head;
    fmt.Printf("{");
    for current != nil {
        if(current == head){
            fmt.Printf("%d", current.Label);
        } else {
            fmt.Printf(",%d", current.Label);
        }
        current = current.Next;
    }
    current = head;
    for current != nil {
        if(current.Random != nil){
            fmt.Printf(",%d", current.Random.Label);
        } else {
            fmt.Printf(",#");
        }
        current = current.Next;
    }
    fmt.Printf("}");
}

func GetRandomListNodeList(line string) []*RandomListNode {
    items := GetRangeItems(line);
    var ret []*RandomListNode
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetRandomListNode(items[i]))
    }
    return ret
}

func GetRandomListNodes(line string) []*RandomListNode {
    return GetRandomListNodeList(line);
}

func GetRandomListNodeListList(line string) [][]*RandomListNode {
    items := GetRangeItems(line);
    var ret [][]*RandomListNode
    for i := 0; i < len(items); i++ {
        ret = append(ret, GetRandomListNodeList(items[i]))
    }
    return ret;
}

func GetRandomListNodess(line string) [][]*RandomListNode {
    return GetRandomListNodeListList(line);
}

func PrintRandomListNode(x *RandomListNode) {
    PrintRandomListNodeInternal(x);
    fmt.Println();
}

func PrintRandomListNodeListInternal(x []*RandomListNode){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintRandomListNodeInternal(x[i]);
    }
    fmt.Printf("]");
}

func PrintRandomListNodeList(x []*RandomListNode){
    PrintRandomListNodeListInternal(x);
    fmt.Println();
}

func PrintRandomListNodeListList(x [][]*RandomListNode){
    fmt.Printf("[");
    for i := 0; i < len(x); i++ {
        if(i != 0) {
            fmt.Printf(",");
        }
        PrintRandomListNodeListInternal(x[i]);
    }
    fmt.Println("]");
}

func PrintRandomListNodes(x []*RandomListNode){
    PrintRandomListNodeList(x);
}

func PrintRandomListNodess(x [][]*RandomListNode){
    PrintRandomListNodeListList(x);
}

func nowcoder_test() {
//func main() {
    //int
    line := "1 , [ 1 , 2 ],[[1],[2],[3,4,-5]],[ 1 , 2 ],[[1],[2],[3,4,5]],"
    // bool
    line = line +  "true , [ false , true ],[[false],[false],[false,true,true]],[ true , false ],[[false],[true],[true,true,true]],";
    // float
    line = line + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [ 1 , 2 ],[[1],[2],[3,4,5]],";
    // double
    line = line + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [],[ 1 , 2 ],[[1],[2],[3,4,5]],";
    // string
    line = line + " \"a\", [\"\",\"x[[[[,,,,[}}}}\"], [[acd, efg], [acd, \"efg\"]],";
    // char
    line = line + " a, [x, y ], [[a, b],[], [c, d]],";
    // long
    line = line + " 1000000000, [3000000000, 2000000000 ], [[3000000000, 2000000000 ],[13000000000, 22000000000 ]],";
    // ListNode
    line = line + "{1,3,4},[{2, 4, 5},{5,6,7,89,11},{ }],[[{2, 4, 5},{5,6,7,89,11},{}],[{2, 4, 5},{5,6,7,89,11}]],"; 
    // Interval
    line = line + "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]],";
    // Point
    line = line + "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]],"; 
    // TreeNode
    line = line + "{1,2,3,#,#,4,#,#,5},[{1,2,3,#,#,4,#,#,5}],[[{1,2,3,#,#,4,#,#,5}],[{1,2,3,#,#,4,#,#,5},{1,2,3,#,#,4,#,#,5}]],";
    // TreeLinkNode
    line = line + "{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]},[{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}],[[],[{[],[]}], [{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}]],"; 
    // RandomListNode
    line = line + "{ -1, 8, 7,  -3,4,4,-3,#,#,-1}, [{ -1, 8, 7,  -3,4,4,-3,#,#,-1}], [[{}],[{ -1, 8, 7,  -3,4,4,-3,#,#,-1}]],";
    

    // stdbak := os.Stdout
    // os.Stdout = nil
    // fmt.Println("haha")
    // os.Stdout = stdbak

    parameters := GetArguments(line)
    i := 0
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

}