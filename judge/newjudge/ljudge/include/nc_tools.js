//for nowcoder
var util = require('util');

module.exports = {
    TreeNode : TreeNode,
    Interval : Interval,
    Point : Point,
    TreeLinkNode : TreeLinkNode,
    RandomListNode : RandomListNode,
    UndirectedGraphNode : UndirectedGraphNode,
    ListNode : ListNode,
    ncout : ncout,
    IsBeginRange : IsBeginRange,
    IsEndRange : IsEndRange,
    GetArguments : GetArguments,
    GetRangeItems : GetRangeItems,
    GetInt : GetInt,
    PrintIntInternal : PrintIntInternal,
    GetLong : GetLong,
    PrintLongInternal : PrintLongInternal,
    GetFloat : GetFloat,
    PrintFloatInternal : PrintFloatInternal,
    GetDouble : GetDouble,
    PrintDoubleInternal : PrintDoubleInternal,
    GetString : GetString,
    PrintStringInternal : PrintStringInternal,
    GetChar : GetChar,
    PrintCharInternal : PrintCharInternal,
    GetBool : GetBool,
    PrintBoolInternal : PrintBoolInternal,
    GetInterval : GetInterval,
    PrintIntervalInternal : PrintIntervalInternal,
    GetPoint : GetPoint,
    PrintPointInternal : PrintPointInternal,
    GetTreeNode : GetTreeNode,
    PrintTreeNodeInternal : PrintTreeNodeInternal,
    GetListNode : GetListNode,
    PrintListNodeInternal : PrintListNodeInternal,
    GetRandomListNode : GetRandomListNode,
    PrintRandomListNodeInternal : PrintRandomListNodeInternal,
    GetTreeLinkNode : GetTreeLinkNode,
    PrintTreeLinkNodeInternal : PrintTreeLinkNodeInternal,
    GetUndirectedGraphNode : GetUndirectedGraphNode,
    PrintUndirectedGraphNodeInternal : PrintUndirectedGraphNodeInternal,
    GetIntList : GetIntList,
    GetInts : GetInts,
    GetIntListList : GetIntListList,
    GetIntss : GetIntss,
    PrintIntListInternal : PrintIntListInternal,
    PrintInt : PrintInt,
    PrintIntList : PrintIntList,
    PrintIntListList : PrintIntListList,
    PrintInts : PrintInts,
    PrintIntss : PrintIntss,
    GetLongList : GetLongList,
    GetLongs : GetLongs,
    GetLongListList : GetLongListList,
    GetLongss : GetLongss,
    PrintLongListInternal : PrintLongListInternal,
    PrintLong : PrintLong,
    PrintLongList : PrintLongList,
    PrintLongListList : PrintLongListList,
    PrintLongs : PrintLongs,
    PrintLongss : PrintLongss,
    GetFloatList : GetFloatList,
    GetFloats : GetFloats,
    GetFloatListList : GetFloatListList,
    GetFloatss : GetFloatss,
    PrintFloatListInternal : PrintFloatListInternal,
    PrintFloat : PrintFloat,
    PrintFloatList : PrintFloatList,
    PrintFloatListList : PrintFloatListList,
    PrintFloats : PrintFloats,
    PrintFloatss : PrintFloatss,
    GetDoubleList : GetDoubleList,
    GetDoubles : GetDoubles,
    GetDoubleListList : GetDoubleListList,
    GetDoubless : GetDoubless,
    PrintDoubleListInternal : PrintDoubleListInternal,
    PrintDouble : PrintDouble,
    PrintDoubleList : PrintDoubleList,
    PrintDoubleListList : PrintDoubleListList,
    PrintDoubles : PrintDoubles,
    PrintDoubless : PrintDoubless,
    GetCharList : GetCharList,
    GetChars : GetChars,
    GetCharListList : GetCharListList,
    GetCharss : GetCharss,
    PrintCharListInternal : PrintCharListInternal,
    PrintChar : PrintChar,
    PrintCharList : PrintCharList,
    PrintCharListList : PrintCharListList,
    PrintChars : PrintChars,
    PrintCharss : PrintCharss,
    GetBoolList : GetBoolList,
    GetBools : GetBools,
    GetBoolListList : GetBoolListList,
    GetBoolss : GetBoolss,
    PrintBoolListInternal : PrintBoolListInternal,
    PrintBool : PrintBool,
    PrintBoolList : PrintBoolList,
    PrintBoolListList : PrintBoolListList,
    PrintBools : PrintBools,
    PrintBoolss : PrintBoolss,
    GetStringList : GetStringList,
    GetStrings : GetStrings,
    GetStringListList : GetStringListList,
    GetStringss : GetStringss,
    PrintStringListInternal : PrintStringListInternal,
    PrintString : PrintString,
    PrintStringList : PrintStringList,
    PrintStringListList : PrintStringListList,
    PrintStrings : PrintStrings,
    PrintStringss : PrintStringss,
    GetIntervalList : GetIntervalList,
    GetIntervals : GetIntervals,
    GetIntervalListList : GetIntervalListList,
    GetIntervalss : GetIntervalss,
    PrintIntervalListInternal : PrintIntervalListInternal,
    PrintInterval : PrintInterval,
    PrintIntervalList : PrintIntervalList,
    PrintIntervalListList : PrintIntervalListList,
    PrintIntervals : PrintIntervals,
    PrintIntervalss : PrintIntervalss,
    GetPointList : GetPointList,
    GetPoints : GetPoints,
    GetPointListList : GetPointListList,
    GetPointss : GetPointss,
    PrintPointListInternal : PrintPointListInternal,
    PrintPoint : PrintPoint,
    PrintPointList : PrintPointList,
    PrintPointListList : PrintPointListList,
    PrintPoints : PrintPoints,
    PrintPointss : PrintPointss,
    GetUndirectedGraphNodeList : GetUndirectedGraphNodeList,
    GetUndirectedGraphNodes : GetUndirectedGraphNodes,
    GetUndirectedGraphNodeListList : GetUndirectedGraphNodeListList,
    GetUndirectedGraphNodess : GetUndirectedGraphNodess,
    PrintUndirectedGraphNodeListInternal : PrintUndirectedGraphNodeListInternal,
    PrintUndirectedGraphNode : PrintUndirectedGraphNode,
    PrintUndirectedGraphNodeList : PrintUndirectedGraphNodeList,
    PrintUndirectedGraphNodeListList : PrintUndirectedGraphNodeListList,
    PrintUndirectedGraphNodes : PrintUndirectedGraphNodes,
    PrintUndirectedGraphNodess : PrintUndirectedGraphNodess,
    GetListNodeList : GetListNodeList,
    GetListNodes : GetListNodes,
    GetListNodeListList : GetListNodeListList,
    GetListNodess : GetListNodess,
    PrintListNodeListInternal : PrintListNodeListInternal,
    PrintListNode : PrintListNode,
    PrintListNodeList : PrintListNodeList,
    PrintListNodeListList : PrintListNodeListList,
    PrintListNodes : PrintListNodes,
    PrintListNodess : PrintListNodess,
    GetRandomListNodeList : GetRandomListNodeList,
    GetRandomListNodes : GetRandomListNodes,
    GetRandomListNodeListList : GetRandomListNodeListList,
    GetRandomListNodess : GetRandomListNodess,
    PrintRandomListNodeListInternal : PrintRandomListNodeListInternal,
    PrintRandomListNode : PrintRandomListNode,
    PrintRandomListNodeList : PrintRandomListNodeList,
    PrintRandomListNodeListList : PrintRandomListNodeListList,
    PrintRandomListNodes : PrintRandomListNodes,
    PrintRandomListNodess : PrintRandomListNodess,
    GetTreeNodeList : GetTreeNodeList,
    GetTreeNodes : GetTreeNodes,
    GetTreeNodeListList : GetTreeNodeListList,
    GetTreeNodess : GetTreeNodess,
    PrintTreeNodeListInternal : PrintTreeNodeListInternal,
    PrintTreeNode : PrintTreeNode,
    PrintTreeNodeList : PrintTreeNodeList,
    PrintTreeNodeListList : PrintTreeNodeListList,
    PrintTreeNodes : PrintTreeNodes,
    PrintTreeNodess : PrintTreeNodess,
    GetTreeLinkNodeList : GetTreeLinkNodeList,
    GetTreeLinkNodes : GetTreeLinkNodes,
    GetTreeLinkNodeListList : GetTreeLinkNodeListList,
    GetTreeLinkNodess : GetTreeLinkNodess,
    PrintTreeLinkNodeListInternal : PrintTreeLinkNodeListInternal,
    PrintTreeLinkNode : PrintTreeLinkNode,
    PrintTreeLinkNodeList : PrintTreeLinkNodeList,
    PrintTreeLinkNodeListList : PrintTreeLinkNodeListList,
    PrintTreeLinkNodes : PrintTreeLinkNodes,
    PrintTreeLinkNodess : PrintTreeLinkNodess,
    test : test
};

function TreeNode(x) {
    this.val = x;
    this.left = null;
    this.right = null;
}

function Interval(a, b){
    this.start = a || 0;
    this.end = b || 0;
}

function Point(a, b){
    this.x = a || 0;
    this.y = b || 0;
}

function TreeLinkNode(x){
    this.val = x;
    this.left = null;
    this.right = null;
    this.next = null;
}

function RandomListNode(x){
    this.label = x;
    this.next = null;
    this.random = null;
}

function UndirectedGraphNode(x){
    this.label = x;
    this.neighbors = [];
}

function ListNode(x){
    this.val = x;
    this.next = null;
}

var LEFT = 0;
var RIGHT = 1;

function ncout(){
    return function(string, encoding, fd) {}
}

function IsBeginRange(c) {
    return c === '{' || c === '[' || c === '(';
}

function IsEndRange(c) {
    return c === '' || c === ']' || c === ')' || c === '}';
}

function GetArguments(line) {
    var ret = [];
    if (!line) {
        return ret;
    }

    var inrange = 0;
    var pre_index = 0;
    var inmao = false;
    for (var i = 0, l = line.length; i < l; i++) {
        if (IsBeginRange(line[i]) && !inmao) {
            inrange = inrange + 1;
        } else if (IsEndRange(line[i]) && !inmao) {
            inrange = inrange - 1;
        } else if (line[i] === '"') {
            inmao = !inmao;
        } else if (line[i] === ',' && inrange === 0 && !inmao) {
            ret.push(line.substring(pre_index, i));
            pre_index = i + 1;
        }
    }
    ret.push(line.substring(pre_index));
    return ret;
}

function GetRangeItems(line) {
    if(!line){
        return [];
    }

    var begin = 0;
    while(!IsBeginRange(line[begin]) && begin < line.length){
        begin = begin + 1;
    }
    end = line.length;
    while(!IsEndRange(line[end-1]) && end > 1){
        end = end - 1;
    }
    line = line.substring(begin + 1, end -1);
    if(line.trim().length === 0){
        return [];
    }
    return GetArguments(line);
}

function GetInt(line){
    if(!line){
        return 0;
    }
    return parseInt(line.trim());
}

function PrintIntInternal(x){
    process.stdout.write(util.format('%d', x));
}

function GetLong(line){
    if(!line){
        return 0;
    }
    //JavaScript has a Number type which is a 64 bit floating point number*.
    return parseInt(line.trim());
}
    
function PrintLongInternal(x){
    process.stdout.write(util.format('%d', x));
}

function GetFloat(line){
    if(!line){
        return 0;
    }
    return parseFloat(line.trim());
}

function PrintFloatInternal(x){
    if(Math.abs(x) < 0.000009999999){
        process.stdout.write("0.00000");
    } else {
        process.stdout.write(x.toFixed(5));
    }
}

function GetDouble(line){
    if(!line){
        return 0;
    }
    return parseFloat(line.trim());
}

function PrintDoubleInternal(x){
    if(Math.abs(x) < 0.000009999999){
        process.stdout.write("0.00000");
    } else {
        process.stdout.write(x.toFixed(5));
    }
}

function GetString(line){
    if(!line){
        return null;
    }
    line = line.trim();
    if(line.length === 0)
        return "";

    if(line[0] === '"' && line[line.length - 1] === '"'){
        return line.substring(1, line.length - 1);
    }

    return line;
}

function PrintStringInternal(line){
    if(!line){
        process.stdout.write("");
    }
    process.stdout.write(util.format('"%s"', line));
}

function GetChar(line){
    if(!line || line.trim().length === 0){
        return '#';
    }
    return line.trim()[0];
}

function PrintCharInternal(c){
    process.stdout.write(c);
}

function GetBool(line){
    if(!line){
        return false;
    }
    return line.trim().toLowerCase() === "true";
}

function PrintBoolInternal(b){
    if(b){
        process.stdout.write("true");
    } else {
        process.stdout.write("false");
    }
}

function GetInterval(line){
    var items = GetIntList(line);
    if(items.length === 2)
        return new Interval(items[0], items[1]);
    return new Interval(0, 0);
}

function PrintIntervalInternal(interval){
    process.stdout.write(util.format('[%d,%d]', interval.start, interval.end));
}

function GetPoint(line){
    var items = GetIntList(line);
    if(items.length === 2)
        return new Point(items[0], items[1]);
    return new Point(0, 0);
}

function PrintPointInternal(point){
    process.stdout.write(util.format('(%d,%d)', point.x, point.y));
}

function GetTreeNode(line){
    var items = GetRangeItems(line);
    if(items.length === 0)
        return null;
    var tree_nodes = new Array(items.length + 1);
    var current = 0;
    var current_pos = LEFT;
    var index = 1;
    tree_nodes[0] = new TreeNode(GetInt(items[0]));
    for (var i = 1; i < items.length; i++){
        if(items[i] === '#'){
            if(tree_nodes[current]){
                if(current_pos === LEFT){
                    current_pos = RIGHT;
                } else if(tree_nodes[current + 1]){
                    current = current + 1;
                    current_pos = LEFT;
                }
            }
        } else {
            tree_nodes[index] = new TreeNode(GetInt(items[i]))
            if(current_pos === LEFT){
                tree_nodes[current].left = tree_nodes[index];
                current_pos = RIGHT;
            } else {
                tree_nodes[current].right = tree_nodes[index];
                current = current + 1;
                current_pos = LEFT;
            }
            index = index + 1;
        }
    }
    return tree_nodes[0];
}

function PrintTreeNodeInternal(root){
    if(root==null){
        process.stdout.write("{}");
        return;
    }
    process.stdout.write("{");
    var v = [];
    v.push(root);
    var c = 0;
    var none = "";
    while (c < v.length){
        if (c === 0){
            process.stdout.write(util.format("%d", v[c].val));
            v.push(v[c].left);
            v.push(v[c].right);
        } else {
            if(!v[c]){
                none = none + ",#";
            } else {
                process.stdout.write(util.format("%s,%d", none, v[c].val));
                none = "";
                v.push(v[c].left);
                v.push(v[c].right);
            }
        }
        c = c+1;
    }
    process.stdout.write("}");
}

function GetListNode(string){
    var items = GetIntList(string);
    if(items.length === 0){
        return null;
    }
    var head = new ListNode(items[0]);
    var tail = head;
    for(var i = 1; i < items.length;i++){
        tail.next = new ListNode(items[i]);
        tail = tail.next;
    }
    return head;
}

function PrintListNodeInternal(head){
    if(!head){
        process.stdout.write("{}");
        return;
    }
    var current = head;
    process.stdout.write("{");
    while(current){
        if(current === head){
            process.stdout.write(util.format("%d", current.val));
        } else {
            process.stdout.write(util.format(",%d", current.val));
        }
        current = current.next;
    }
    process.stdout.write ("}");
}

// { -1, 8, 7, -3,4,4,-3,#,#,-1}
// 分为两段，前部分为ListNode,后半部分如果random==None是#，否则就是random.val
function GetRandomListNode(string){
    var items = GetRangeItems(string);
    if(items.length < 2){
        return null;
    }
    var count = items.length / 2;

    var list_nodes = new Array(count + 1);
    var nodes_map = {};
    var head = new RandomListNode(GetInt(items[0]));
    nodes_map[head.label] = head;
    list_nodes[0] = head;
    var tail = head;
    for(var i = 1; i<count;i++){
        var cur = new RandomListNode(GetInt(items[i]));
        tail.next = cur;
        tail = cur;
        nodes_map[cur.label] = cur;
        list_nodes[i] = cur;
    }

    for(var i = count; i<items.length;i++){
        if(items[i] !== '#' && nodes_map[GetInt(items[i])]){
            list_nodes [i - count].random = nodes_map[GetInt(items[i])];
        }
    }
    return head;
}

function PrintRandomListNodeInternal(head){
    if(!head){
        process.stdout.write("{}");
        return;
    }
    var current = head;
    process.stdout.write("{");
    while(current){
        if(current === head){
            process.stdout.write(util.format("%d", current.label));
        } else {
            process.stdout.write(util.format(",%d", current.label));
        }
        current = current.next;
    }
    current = head;
    while(current){
        if(current.random){
            process.stdout.write(util.format(",%d", current.random.label));
        } else {
            process.stdout.write(",#");
        }
        current = current.next;
    }
    process.stdout.write ("}");
}

// '''
// 二叉链接树序列化是通过按层遍历,#代表这这个节点为空节点,节点遍历以后再增加所有next节点数据,举个例子
//    1->None
//   / \
//  2 -> 3->None
//       /
//      4 ->None   
//      \
//       5->None

//  以上二叉树会被序列化为 {[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}
//  对于{[1,2,3,#,#,4,#,#,5],[#,5,#,#,#]}构造出来的链接树节点2的next指向5节点*/
//  '''
function GetTreeLinkNode(string){
    var all_items = GetRangeItems(string);
    var is_newversion = all_items.length === 2 && all_items[0][0] == '[' && all_items[1][0] == '[';
    if(!is_newversion){
        all_items = []
        all_items.push(string);
        all_items.push("[]");
    }
    if(all_items.length < 2)
        return null;
    var items = GetRangeItems (all_items [0]);
    if(items.length === 0){
        return null;
    }

    var tree_nodes = new Array(items.length + 1);
    var map_nodes = {};
    var current = 0;
    var current_pos = LEFT;
    var index = 1;
    tree_nodes [0] = new TreeLinkNode(GetInt (items [0]));
    for(var i = 1; i<items.length;i++){
        if(items[i] === '#'){
            if(tree_nodes[current]){
                if(current_pos === LEFT){
                    current_pos = RIGHT;
                } else if(tree_nodes[current + 1]){
                    current = current + 1;
                    current_pos = LEFT;
                }
            }
        } else {
            label = GetInt (items [i]);
            tree_nodes [index] = new TreeLinkNode (label);
            map_nodes [label] = tree_nodes [index];
            if(current_pos === LEFT){
                tree_nodes[current].left = tree_nodes[index];
                current_pos = RIGHT;
            } else {
                tree_nodes[current].right = tree_nodes[index];
                current = current + 1;
                current_pos = LEFT;
            }
            index = index + 1;
        }
    }
    // 连接next指针
    items = GetRangeItems(all_items [1]);
    for(var i = 0; i<items.length;i++){
        if(items[i] !== "#" && map_nodes[GetInt (items [i])]){
            tree_nodes [i].next = tree_nodes[GetInt (items [i])];
        }
    }
    return tree_nodes [0]
}

function PrintTreeLinkNodeInternal(root){
    if(!root){
        process.stdout.write("null");
        return;
    }
    process.stdout.write("{[");
    var v = []
    var label_node_v = []
    if(root){
        v.push(root);
        label_node_v.push(root);
    }
    var c = 0;
    var none = "";
    while(c < v.length){
        if(c === 0){
            process.stdout.write(util.format("%d", v[c].val));
            v.push(v [c].left)
            v.push(v [c].right)
        } else {
            if(!v[c]) {
                none = none + ",#";
            } else {
                label_node_v.push(v[c]);
                process.stdout.write(util.format("%s,%d", none, v[c].val));
                none = "";
                v.push(v[c].left);
                v.push(v[c].right);
            }
        }
        c = c + 1;
    }
    v = [];
    process.stdout.write("],[");
    for(var i = 0;i < label_node_v.length;i++){
        if(i!== 0){
            process.stdout.write(",");
        }
        if(label_node_v[i].next){
            process.stdout.write(util.format("%d", label_node_v [i].next.val));
        } else {
            process.stdout.write("#");
        }
    }
    process.stdout.write("]}");
}

// '''
// 无向图里每个节点都有一个唯一的数字ID,每个节点的序列化通过[]保存,每个节点第一个元素后跟随的是这个节点连接的其他节点,以下图
//        1 
//      /  \
//      /  \
//     0 --- 2
//          / \
//          \_/
//  序列化后为{[0,1,2],[1,2],[2,2]}
//  '''
function GetUndirectedGraphNode (string){
    points = GetIntListList (string)

    var ret = null;
    var nodes_map = {};
    
    //把所有的点构造出来
    for(var i = 0; i < len(points); i++){
        var v = points[i];
        if(v.length === 0){
            continue;
        }
        if(nodes_map(v[0]) === undefined){
            var node = new UndirectedGraphNode (v[0]);
            nodes_map [v[0]] = node;
            if(!ret){
                ret = node;
            }
        }
    }
    
    //把各个边连接起来
    for(var i = 0; i < len(points); i++){
        var v = points [i];
        if(v.length === 0){
            continue;
        }
        var node = nodes_map[v [0]];
        for(var j = 1;j<v.length;j++){
            node.neighbors.push(nodes_map[v[j]]);
        }
    }
    return ret;
}
    
function PrintUndirectedGraphNodeInternal (root){
    if(!root){
        process.stdout.write ("null");
        return;
    }
    process.stdout.write ("{");
    if(root){
        var nodes_set = {};
        var nodes_map = {};
        var nodes = [];
        nodes.push(root);
        nodes_set[root] = true;
        nodes_map[root.label] = root;
        for(var i = 0;i<nodes.length;i++){
            for(var j = 0;j<nodes[i].neighbors.length;j++){
                var n_node = nodes [i].neighbors [j];
                if(nodes_set[n_node] === undefined){
                    nodes_set[n_node] = true;
                    nodes.push(n_node);
                    nodes_map[n_node.label] = n_node;
                }
            }
        }
    
        //根据label从小到大打印
        for(var key in nodes_map) {
            var node = nodes_map[key];
            if(node !== nodes [0]){
                process.stdout.write (util.format(",[%d", node.label));
            } else {
                process.stdout.write (util.format("[%d", node.label));
            }
            for(var j = 0;j<node.neighbors.length;j++){
                process.stdout.write (utl.format(",%d", node.neighbors.get(j).label));
            }
            process.stdout.write ("]");
        }
    }
    process.stdout.write ("}")
}

function GetIntList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetInt(items[i]));
    }
    return ret
}

function GetInts(string){
    return GetIntList(string);
}

function GetIntListList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetIntList(items[i]));
    }
    return ret;
}

function GetIntss(string){
    return GetIntListList(string);
}

function PrintIntListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintIntInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintInt(x){
    PrintIntInternal(x);
    process.stdout.write('\n');
}

function PrintIntList(x){
    PrintIntListInternal(x);
    process.stdout.write('\n');
}

function PrintIntListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintIntListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintInts(x){
    PrintIntList(x);
}

function PrintIntss(x){
    PrintIntListList(x);
}

function GetLongList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetLong(items[i]));
    }
    return ret
}

function GetLongs(string){
    return GetLongList(string);
}

function GetLongListList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetLongList(items[i]));
    }
    return ret;
}

function GetLongss(string){
    return GetLongListList(string);
}

function PrintLongListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintLongInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintLong(x){
    PrintLongInternal(x);
    process.stdout.write('\n');
}

function PrintLongList(x){
    PrintLongListInternal(x);
    process.stdout.write('\n');
}

function PrintLongListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintLongListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintLongs(x){
    PrintLongList(x);
}

function PrintLongss(x){
    PrintLongListList(x);
}

function GetFloatList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetFloat(items[i]));
    }
    return ret;
}

function GetFloats(string){
    return GetFloatList(string);
}

function GetFloatListList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetFloatList(items[i]));
    }
    return ret;
}

function GetFloatss(string){
    return GetFloatListList(string);
}

function PrintFloatListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintFloatInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintFloat(x){
    PrintFloatInternal(x);
    process.stdout.write('\n');
}

function PrintFloatList(x){
    PrintFloatListInternal(x);
    process.stdout.write('\n');
}

function PrintFloatListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintFloatListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintFloats(x){
    PrintFloatList(x);
}

function PrintFloatss(x){
    PrintFloatListList(x);
}

function GetDoubleList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetDouble(items[i]));
    }
    return ret;
}

function GetDoubles(string){
    return GetDoubleList(string);
}

function GetDoubleListList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetDoubleList(items[i]));
    }
    return ret;
}

function GetDoubless(string){
    return GetDoubleListList(string);
}

function PrintDoubleListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintDoubleInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintDouble(x){
    PrintDoubleInternal(x);
    process.stdout.write('\n');
}

function PrintDoubleList(x){
    PrintDoubleListInternal(x);
    process.stdout.write('\n');
}

function PrintDoubleListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintDoubleListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintDoubles(x){
    PrintDoubleList(x);
}

function PrintDoubless(x){
    PrintDoubleListList(x);
}

function GetCharList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetChar(items[i]));
    }
    return ret;
}

function GetChars(string){
    return GetCharList(string);
}

function GetCharListList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetCharList(items[i]));
    }
    return ret;
}

function GetCharss(string){
    return GetCharListList(string);
}

function PrintCharListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintCharInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintChar(x){
    PrintCharInternal(x);
    process.stdout.write('\n');
}

function PrintCharList(x){
    PrintCharListInternal(x);
    process.stdout.write('\n');
}

function PrintCharListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintCharListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintChars(x){
    PrintCharList(x);
}

function PrintCharss(x){
    PrintCharListList(x);
}

function GetBoolList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetBool(items[i]));
    }
    return ret;
}

function GetBools(string){
    return GetBoolList(string);
}

function GetBoolListList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetBoolList(items[i]));
    }
    return ret;
}

function GetBoolss(string){
    return GetBoolListList(string);
}

function PrintBoolListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintBoolInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintBool(x){
    PrintBoolInternal(x);
    process.stdout.write('\n');
}

function PrintBoolList(x){
    PrintBoolListInternal(x);
    process.stdout.write('\n');
}

function PrintBoolListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintBoolListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintBools(x){
    PrintBoolList(x);
}

function PrintBoolss(x){
    PrintBoolListList(x);
}

function GetStringList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetString(items[i]));
    }
    return ret;
}

function GetStrings(string){
    return GetStringList(string);
}

function GetStringListList(string){
    var items = GetRangeItems(string);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetStringList(items[i]));
    }
    return ret;
}

function GetStringss(string){
    return GetStringListList(string);
}

function PrintStringListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintStringInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintString(x){
    PrintStringInternal(x);
    process.stdout.write('\n');
}

function PrintStringList(x){
    PrintStringListInternal(x);
    process.stdout.write('\n');
}

function PrintStringListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintStringListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintStrings(x){
    PrintStringList(x);
}

function PrintStringss(x){
    PrintStringListList(x);
}

function GetIntervalList(Interval){
    var items = GetRangeItems(Interval);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetInterval(items[i]));
    }
    return ret;
}

function GetIntervals(Interval){
    return GetIntervalList(Interval);
}

function GetIntervalListList(Interval){
    var items = GetRangeItems(Interval);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetIntervalList(items[i]));
    }
    return ret;
}

function GetIntervalss(Interval){
    return GetIntervalListList(Interval);
}

function PrintIntervalListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintIntervalInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintInterval(x){
    PrintIntervalInternal(x);
    process.stdout.write('\n');
}

function PrintIntervalList(x){
    PrintIntervalListInternal(x);
    process.stdout.write('\n');
}

function PrintIntervalListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintIntervalListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintIntervals(x){
    PrintIntervalList(x);
}

function PrintIntervalss(x){
    PrintIntervalListList(x);
}

function GetPointList(Point){
    var items = GetRangeItems(Point);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetPoint(items[i]));
    }
    return ret;
}

function GetPoints(Point){
    return GetPointList(Point);
}

function GetPointListList(Point){
    var items = GetRangeItems(Point);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetPointList(items[i]));
    }
    return ret;
}

function GetPointss(Point){
    return GetPointListList(Point);
}

function PrintPointListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintPointInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintPoint(x){
    PrintPointInternal(x);
    process.stdout.write('\n');
}

function PrintPointList(x){
    PrintPointListInternal(x);
    process.stdout.write('\n');
}

function PrintPointListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintPointListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintPoints(x){
    PrintPointList(x);
}

function PrintPointss(x){
    PrintPointListList(x);
}

function GetUndirectedGraphNodeList(UndirectedGraphNode){
    var items = GetRangeItems(UndirectedGraphNode);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetUndirectedGraphNode(items[i]));
    }
    return ret;
}

function GetUndirectedGraphNodes(UndirectedGraphNode){
    return GetUndirectedGraphNodeList(UndirectedGraphNode);
}

function GetUndirectedGraphNodeListList(UndirectedGraphNode){
    var items = GetRangeItems(UndirectedGraphNode);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetUndirectedGraphNodeList(items[i]));
    }
    return ret;
}

function GetUndirectedGraphNodess(UndirectedGraphNode){
    return GetUndirectedGraphNodeListList(UndirectedGraphNode);
}

function PrintUndirectedGraphNodeListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintUndirectedGraphNodeInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintUndirectedGraphNode(x){
    PrintUndirectedGraphNodeInternal(x);
    process.stdout.write('\n');
}

function PrintUndirectedGraphNodeList(x){
    PrintUndirectedGraphNodeListInternal(x);
    process.stdout.write('\n');
}

function PrintUndirectedGraphNodeListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintUndirectedGraphNodeListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintUndirectedGraphNodes(x){
    PrintUndirectedGraphNodeList(x);
}

function PrintUndirectedGraphNodess(x){
    PrintUndirectedGraphNodeListList(x);
}

function GetListNodeList(ListNode){
    var items = GetRangeItems(ListNode);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetListNode(items[i]));
    }
    return ret;
}

function GetListNodes(ListNode){
    return GetListNodeList(ListNode);
}

function GetListNodeListList(ListNode){
    var items = GetRangeItems(ListNode);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetListNodeList(items[i]));
    }
    return ret;
}

function GetListNodess(ListNode){
    return GetListNodeListList(ListNode);
}

function PrintListNodeListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintListNodeInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintListNode(x){
    PrintListNodeInternal(x);
    process.stdout.write('\n');
}

function PrintListNodeList(x){
    PrintListNodeListInternal(x);
    process.stdout.write('\n');
}

function PrintListNodeListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintListNodeListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintListNodes(x){
    PrintListNodeList(x);
}

function PrintListNodess(x){
    PrintListNodeListList(x);
}

function GetRandomListNodeList(RandomListNode){
    var items = GetRangeItems(RandomListNode);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetRandomListNode(items[i]));
    }
    return ret;
}

function GetRandomListNodes(RandomListNode){
    return GetRandomListNodeList(RandomListNode);
}

function GetRandomListNodeListList(RandomListNode){
    var items = GetRangeItems(RandomListNode);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetRandomListNodeList(items[i]));
    }
    return ret;
}

function GetRandomListNodess(RandomListNode){
    return GetRandomListNodeListList(RandomListNode);
}

function PrintRandomListNodeListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintRandomListNodeInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintRandomListNode(x){
    PrintRandomListNodeInternal(x);
    process.stdout.write('\n');
}

function PrintRandomListNodeList(x){
    PrintRandomListNodeListInternal(x);
    process.stdout.write('\n');
}

function PrintRandomListNodeListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintRandomListNodeListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintRandomListNodes(x){
    PrintRandomListNodeList(x);
}

function PrintRandomListNodess(x){
    PrintRandomListNodeListList(x);
}

function GetTreeNodeList(TreeNode){
    var items = GetRangeItems(TreeNode);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetTreeNode(items[i]));
    }
    return ret;
}

function GetTreeNodes(TreeNode){
    return GetTreeNodeList(TreeNode);
}

function GetTreeNodeListList(TreeNode){
    var items = GetRangeItems(TreeNode);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetTreeNodeList(items[i]));
    }
    return ret;
}

function GetTreeNodess(TreeNode){
    return GetTreeNodeListList(TreeNode);
}

function PrintTreeNodeListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintTreeNodeInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintTreeNode(x){
    PrintTreeNodeInternal(x);
    process.stdout.write('\n');
}

function PrintTreeNodeList(x){
    PrintTreeNodeListInternal(x);
    process.stdout.write('\n');
}

function PrintTreeNodeListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintTreeNodeListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintTreeNodes(x){
    PrintTreeNodeList(x);
}

function PrintTreeNodess(x){
    PrintTreeNodeListList(x);
}

function GetTreeLinkNodeList(TreeLinkNode){
    var items = GetRangeItems(TreeLinkNode);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetTreeLinkNode(items[i]));
    }
    return ret;
}

function GetTreeLinkNodes(TreeLinkNode){
    return GetTreeLinkNodeList(TreeLinkNode);
}

function GetTreeLinkNodeListList(TreeLinkNode){
    var items = GetRangeItems(TreeLinkNode);
    var ret = []
    for (var i = 0; i < items.length; i++){
        ret.push(GetTreeLinkNodeList(items[i]));
    }
    return ret;
}

function GetTreeLinkNodess(TreeLinkNode){
    return GetTreeLinkNodeListList(TreeLinkNode);
}

function PrintTreeLinkNodeListInternal(x){
    process.stdout.write('[');
    for(var i = 0; i < x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintTreeLinkNodeInternal(x[i]);
    }
    process.stdout.write(']');
}

function PrintTreeLinkNode(x){
    PrintTreeLinkNodeInternal(x);
    process.stdout.write('\n');
}

function PrintTreeLinkNodeList(x){
    PrintTreeLinkNodeListInternal(x);
    process.stdout.write('\n');
}

function PrintTreeLinkNodeListList(x){
    process.stdout.write("[");
    for(var i = 0; i< x.length; i++){
        if(i !== 0)
            process.stdout.write(',');
        PrintTreeLinkNodeListInternal(x[i]);
    }
    process.stdout.write("]\n");
}

function PrintTreeLinkNodes(x){
    PrintTreeLinkNodeList(x);
}

function PrintTreeLinkNodess(x){
    PrintTreeLinkNodeListList(x);
}

function test(){
    // int
    line = "1 , [ 1 , 2 ],[[1],[2],[3,4,-5]],[ 1 , 2 ],[[1],[2],[3,4,5]],";
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
    // #
    line = line + "{[0,1,2],[1,2],[2,2]}, [{[0,1,2],[1,2],[2,2]}], [[], [{[0,1,2],[1,2],[2,2]},{[0,1,2],[1,2],[2,2]}]]";

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
}