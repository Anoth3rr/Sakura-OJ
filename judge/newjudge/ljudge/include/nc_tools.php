<?php
class TreeNode{
    var $val;
    var $left = NULL;
    var $right = NULL;
    function __construct($val){
        $this->val = $val;
    }
}

class Interval{
    var $start = 0;
    var $end = 0;
    function __construct($a, $b){
        $this->start = $a;
        $this->end = $b;
    }
}

class Point{
    var $x = 0;
    var $y = 0;
    function __construct($a, $b){
        $this->x = $a;
        $this->y = $b;
    }
}

class TreeLinkNode{
    var $val;
    var $left = NULL;
    var $right = NULL;
    var $next = NULL;
    function __construct($x){
        $this->val = $x;
    }
}

class RandomListNode{
    var $label;
    var $next = NULL;
    var $random = NULL;
    function __construct($x){
        $this->label = $x;
    }
}

class UndirectedGraphNode{
    var $label;
    var $neighbors = array();
    function __construct($x){
        $this->label = $x;
    }
}

class ListNode{
    var $val;
    var $next = NULL;
    function __construct($x){
        $this->val = $x;
    }
}

class NCTools {
    private static $LEFT = 0;
    private static $RIGHT = 1;

    private static function GetList_($line, $proc) {
        $ret = array();
        foreach(self::GetRangeItems($line) as $item) {
            $ret []= self::$proc($item);
        }
        return $ret;
    }

    private static function PrintList_($x, $proc) {
        echo "[";
        foreach ($x as $i => $item) {
            if($i !== 0){
                echo ",";
            }
            self::$proc($item);
        }
        echo "]";
    }

    public static function ncout(){
    }

    public static function IsBeginRange($c) {
        return $c == '{' || $c == '[' || $c == '(';
    }

    public static function IsEndRange($c) {
        return $c == '}' || $c == ']' || $c == ')';
    }

    public static function GetArguments($line) {
        $ret = array();
        if ($line == NULL) {
            return $ret;
        }

        $inrange = 0;
        $pre_index = 0;
        $inmao = false;
        for ($i=0;$i<strlen($line);$i++) {
            if (self::IsBeginRange($line[$i]) && !$inmao) {
                $inrange++;
            } else if (self::IsEndRange($line[$i]) && !$inmao) {
                $inrange--;
            } else if ($line[$i] === '"') {
                $inmao = !$inmao;
            } else if ($line[$i] === ',' && $inrange === 0 && !$inmao) {
                $ret []= substr($line, $pre_index, $i-$pre_index);
                $pre_index = $i + 1;
            }
        }
        $ret []= substr($line, $pre_index);
        return $ret;
    }

    public static function GetRangeItems($line) {
        if(!$line){
            return array();
        }
        $begin = 0;
        while(!self::IsBeginRange($line[$begin]) && $begin < strlen($line)){
            $begin++;
        }
        $end = strlen($line);
        while(!self::IsEndRange($line[$end-1]) && $end > 1){
            $end--;
        }
        $line = substr($line, $begin+1,$end-1-$begin-1);
        if(strlen(trim($line)) === 0){
            return array();
        }
        return self::GetArguments($line);
    }

    public static function GetInt($line){
        if(!$line){
            return 0;
        }
        return intval(trim($line));
    }

    public static function PrintIntInternal($x){
        echo $x;
    }

    public static function GetLong($line){
        //PHP_INT_MAX:9223372036854775807 is same to Long.MAX_VALUE
        return self::GetInt($line);
    }
        
    public static function PrintLongInternal($x){
        echo $x;
    }

    public static function GetFloat($line){
        if(!$line){
            return 0;
        }
        return floatval(trim($line));
    }

    public static function PrintFloatInternal($x){
        if(abs($x) < 0.000009999999){
            echo "0.00000";
        } else {
            echo number_format($x, 5, '.', ''); // 去掉千位分隔符
        }
    }

    public static function GetDouble($line){
        return self::GetFloat($line);
    }

    public static function PrintDoubleInternal($x){
        return self::PrintFloatInternal($x);
    }

    public static function GetString($line){
        if(is_null($line)){
            return NULL;
        }
        $line = trim($line);
        if(strlen($line) == 0)
            return "";

        if($line[0] == '"' && $line[strlen($line)-1] == '"'){
            return substr($line, 1, strlen($line) -2);
        }

        return $line;
    }

    public static function PrintStringInternal($line){
        if($line==NULL){
            echo "";
        }
        echo '"', $line, '"';
    }

    public static function GetChar($line){
        if($line == NULL || strlen(trim($line)) === 0){
            return '#';
        }
        return trim($line)[0];
    }

    public static function PrintCharInternal($c){
        echo $c;
    }

    public static function GetBool($line){
        if($line == NULL){
            return false;
        }
        return strtolower(trim($line)) === "true";
    }

    public static function PrintBoolInternal($b){
        if($b){
            echo "true";
        } else {
            echo "false";
        }
    }

    //int
    public static function GetIntList($line){
        return self::GetList_($line, 'GetInt');
    }

    public static function GetInts($line){
        return self::GetIntList($line);
    }

    public static function GetIntListList($line){
        return self::GetList_($line, 'GetIntList');
    }

    public static function GetIntss($line){
        return self::GetIntListList($line);
    }

    public static function PrintIntListInternal($x){
        self::PrintList_($x, 'PrintIntInternal');
    }

    public static function PrintInt($x){
        self::PrintIntInternal($x);
        echo "\n";
    }

    public static function PrintIntList($x){
        self::PrintIntListInternal($x);
        echo "\n";
    }

    public static function PrintIntListList($x){
        self::PrintList_($x, 'PrintIntListInternal');
        echo "\n";
    }

    public static function PrintInts($x){
        self::PrintIntList($x);
    }

    public static function PrintIntss($x){
        self::PrintIntListList($x);
    }

    //long
    public static function GetLongList($line){
        return self::GetList_($line, 'GetLong');
    }

    public static function GetLongs($line){
        return self::GetLongList($line);
    }

    public static function GetLongListList($line){
        return self::GetList_($line, 'GetLongList');
    }

    public static function GetLongss($line){
        return self::GetLongListList($line);
    }

    public static function PrintLongListInternal($x){
        self::PrintList_($x, 'PrintLongInternal');
    }

    public static function PrintLong($x){
        self::PrintLongInternal($x);
        echo "\n";
    }

    public static function PrintLongList($x){
        self::PrintLongListInternal($x);
        echo "\n";
    }

    public static function PrintLongListList($x){
        self::PrintList_($x, 'PrintLongListInternal');
        echo "\n";
    }

    public static function PrintLongs($x){
        self::PrintLongList($x);
    }

    public static function PrintLongss($x){
        self::PrintLongListList($x);
    }

    //float
    public static function GetFloatList($line){
        return self::GetList_($line, 'GetFloat');
    }

    public static function GetFloats($line){
        return self::GetFloatList($line);
    }

    public static function GetFloatListList($line){
        return self::GetList_($line, 'GetFloatList');
    }

    public static function GetFloatss($line){
        return self::GetFloatListList($line);
    }

    public static function PrintFloatListInternal($x){
        self::PrintList_($x, 'PrintFloatInternal');
    }

    public static function PrintFloat($x){
        self::PrintFloatInternal($x);
        echo "\n";
    }

    public static function PrintFloatList($x){
        self::PrintFloatListInternal($x);
        echo "\n";
    }

    public static function PrintFloatListList($x){
        self::PrintList_($x, 'PrintFloatListInternal');
        echo "\n";
    }

    public static function PrintFloats($x){
        self::PrintFloatList($x);
    }

    public static function PrintFloatss($x){
        self::PrintFloatListList($x);
    }

    //double
    public static function GetDoubleList($line){
        return self::GetList_($line, 'GetDouble');
    }

    public static function GetDoubles($line){
        return self::GetDoubleList($line);
    }

    public static function GetDoubleListList($line){
        return self::GetList_($line, 'GetDoubleList');
    }

    public static function GetDoubless($line){
        return self::GetDoubleListList($line);
    }

    public static function PrintDoubleListInternal($x){
        self::PrintList_($x, 'PrintDoubleInternal');
    }

    public static function PrintDouble($x){
        self::PrintDoubleInternal($x);
        echo "\n";
    }

    public static function PrintDoubleList($x){
        self::PrintDoubleListInternal($x);
        echo "\n";
    }

    public static function PrintDoubleListList($x){
        self::PrintList_($x, 'PrintDoubleListInternal');
        echo "\n";
    }

    public static function PrintDoubles($x){
        self::PrintDoubleList($x);
    }

    public static function PrintDoubless($x){
        self::PrintDoubleListList($x);
    }

    //char
    public static function GetCharList($line){
        return self::GetList_($line, 'GetChar');
    }

    public static function GetChars($line){
        return self::GetCharList($line);
    }

    public static function GetCharListList($line){
        return self::GetList_($line, 'GetCharList');
    }

    public static function GetCharss($line){
        return self::GetCharListList($line);
    }

    public static function PrintCharListInternal($x){
        self::PrintList_($x, 'PrintCharInternal');
    }

    public static function PrintChar($x){
        self::PrintCharInternal($x);
        echo "\n";
    }

    public static function PrintCharList($x){
        self::PrintCharListInternal($x);
        echo "\n";
    }

    public static function PrintCharListList($x){
        self::PrintList_($x, 'PrintCharListInternal');
        echo "\n";
    }

    public static function PrintChars($x){
        self::PrintCharList($x);
    }

    public static function PrintCharss($x){
        self::PrintCharListList($x);
    }

    //bool
    public static function GetBoolList($line){
        return self::GetList_($line, 'GetBool');
    }

    public static function GetBools($line){
        return self::GetBoolList($line);
    }

    public static function GetBoolListList($line){
        return self::GetList_($line, 'GetBoolList');
    }

    public static function GetBoolss($line){
        return self::GetBoolListList($line);
    }

    public static function PrintBoolListInternal($x){
        self::PrintList_($x, 'PrintBoolInternal');
    }

    public static function PrintBool($x){
        self::PrintBoolInternal($x);
        echo "\n";
    }

    public static function PrintBoolList($x){
        self::PrintBoolListInternal($x);
        echo "\n";
    }

    public static function PrintBoolListList($x){
        self::PrintList_($x, 'PrintBoolListInternal');
        echo "\n";
    }

    public static function PrintBools($x){
        self::PrintBoolList($x);
    }

    public static function PrintBoolss($x){
        self::PrintBoolListList($x);
    }

    //string
    public static function GetStringList($line){
        return self::GetList_($line, 'GetString');
    }

    public static function GetStrings($line){
        return self::GetStringList($line);
    }

    public static function GetStringListList($line){
        return self::GetList_($line, 'GetStringList');
    }

    public static function GetStringss($line){
        return self::GetStringListList($line);
    }

    public static function PrintStringListInternal($x){
        self::PrintList_($x, 'PrintStringInternal');
    }

    public static function PrintString($x){
        self::PrintStringInternal($x);
        echo "\n";
    }

    public static function PrintStringList($x){
        self::PrintStringListInternal($x);
        echo "\n";
    }

    public static function PrintStringListList($x){
        self::PrintList_($x, 'PrintStringListInternal');
        echo "\n";
    }

    public static function PrintStrings($x){
        self::PrintStringList($x);
    }

    public static function PrintStringss($x){
        self::PrintStringListList($x);
    }

    //internval
    public static function GetInterval($line){
        $items = self::GetIntList($line);
        if(count($items) === 2){
            return new Interval($items[0], $items[1]);
        }
        return new Interval(0, 0);
    }

    public static function PrintIntervalInternal($interval){
        printf("[%d,%d]", $interval->start, $interval->end);
    }

    public static function GetIntervalList($line){
        return self::GetList_($line, 'GetInterval');
    }

    public static function GetIntervals($line){
        return self::GetIntervalList($line);
    }

    public static function GetIntervalListList($line){
        return self::GetList_($line, 'GetIntervalList');
    }

    public static function GetIntervalss($line){
        return self::GetIntervalListList($line);
    }

    public static function PrintIntervalListInternal($x){
        self::PrintList_($x, 'PrintIntervalInternal');
    }

    public static function PrintInterval($x){
        self::PrintIntervalInternal($x);
        echo "\n";
    }

    public static function PrintIntervalList($x){
        self::PrintIntervalListInternal($x);
        echo "\n";
    }

    public static function PrintIntervalListList($x){
        self::PrintList_($x, 'PrintIntervalListInternal');
        echo "\n";
    }

    public static function PrintIntervals($x){
        self::PrintIntervalList($x);
    }

    public static function PrintIntervalss($x){
        self::PrintIntervalListList($x);
    }

    //listnode
    public static function GetListNode($x){
        $items = self::GetIntList($x);
        if(count($items) === 0){
            return NULL;
        }
        $head = new ListNode($items[0]);
        $tail = $head;
        for($i = 1; $i < count($items);$i++){
            $tail->next = new ListNode($items[$i]);
            $tail = $tail->next;
        }
        return $head;
    }

    public static function PrintListNodeInternal($head){
        if($head == NULL){
            echo "{}";
            return;
        }
        $current = $head;
        echo "{";
        while($current != NULL){
            if($current === $head){
                printf("%d", $current->val);
            } else {
                printf(",%d", $current->val);
            }
            $current = $current->next;
        }
        echo "}";
    }

    public static function GetListNodeList($line){
        return self::GetList_($line, 'GetListNode');
    }

    public static function GetListNodes($line){
        return self::GetListNodeList($line);
    }

    public static function GetListNodeListList($line){
        return self::GetList_($line, 'GetListNodeList');
    }

    public static function GetListNodess($line){
        return self::GetListNodeListList($line);
    }

    public static function PrintListNodeListInternal($x){
        self::PrintList_($x, 'PrintListNodeInternal');
    }

    public static function PrintListNode($x){
        self::PrintListNodeInternal($x);
        echo "\n";
    }

    public static function PrintListNodeList($x){
        self::PrintListNodeListInternal($x);
        echo "\n";
    }

    public static function PrintListNodeListList($x){
        self::PrintList_($x, 'PrintListNodeListInternal');
        echo "\n";
    }

    public static function PrintListNodes($x){
        self::PrintListNodeList($x);
    }

    public static function PrintListNodess($x){
        self::PrintListNodeListList($x);
    }

    //point
    public static function GetPoint($line){
        $items = self::GetIntList($line);
        if(count($items) === 2)
            return new Point($items[0], $items[1]);
        return new Point(0, 0);
    }

    public static function PrintPointInternal($point){
        printf("(%d,%d)", $point->x, $point->y);
    }

    public static function GetPointList($line){
        return self::GetList_($line, 'GetPoint');
    }

    public static function GetPoints($line){
        return self::GetPointList($line);
    }

    public static function GetPointListList($line){        
        return self::GetList_($line, 'GetPointList');
    }

    public static function GetPointss($line){
        return self::GetPointListList($line);
    }

    public static function PrintPointListInternal($x){
        self::PrintList_($x, 'PrintPointInternal');
    }

    public static function PrintPoint($x){
        self::PrintPointInternal($x);
        echo "\n";
    }

    public static function PrintPointList($x){
        self::PrintPointListInternal($x);
        echo "\n";
    }

    public static function PrintPointListList($x){
        self::PrintList_($x, 'PrintPointListInternal');
        echo "\n";
    }

    public static function PrintPoints($x){
        self::PrintPointList($x);
    }

    public static function PrintPointss($x){
        self::PrintPointListList($x);
    }

    //treenode
    public static function GetTreeNode($line){
        $items = self::GetRangeItems($line);
        if(count($items) === 0)
            return NULL;
        $tree_nodes = array();
        $current = 0;
        $current_pos = self::$LEFT;
        $index = 1;
        $tree_nodes[0] = new TreeNode(self::GetInt($items[0]));
        for ($i = 1; $i < count($items); $i++){
            if($items[$i] === '#'){
                if($tree_nodes[$current]){
                    if($current_pos === self::$LEFT){
                        $current_pos = self::$RIGHT;
                    } else if($tree_nodes[$current + 1]){
                        $current++;
                        $current_pos = self::$LEFT;
                    }
                }
            } else {
                $tree_nodes[$index] = new TreeNode(self::GetInt($items[$i]));
                if($current_pos === self::$LEFT){
                    $tree_nodes[$current]->left = $tree_nodes[$index];
                    $current_pos = self::$RIGHT;
                } else {
                    $tree_nodes[$current]->right = $tree_nodes[$index];
                    $current++;
                    $current_pos = self::$LEFT;
                }
                $index++;
            }
        }
        return $tree_nodes[0];
    }

    public static function PrintTreeNodeInternal($root){
        if($root == NULL){
            echo "{}";
            return;
        }
        echo "{";
        $v = array($root);
        $c = 0;
        $none = "";
        while ($c < count($v)){
            if ($c === 0){
                printf("%d", $v[$c]->val);
                array_push($v, $v[$c]->left, $v[$c]->right);
            } else {
                if($v[$c] == NULL){
                    $none = $none . ",#";
                } else {
                    printf("%s,%d", $none, $v[$c]->val);
                    $none = "";
                    array_push($v, $v[$c]->left, $v[$c]->right);
                }
            }
            $c++;
        }
        echo "}";
    }

    public static function GetTreeNodeList($line){
        return self::GetList_($line, 'GetTreeNode');
    }

    public static function GetTreeNodes($line){
        return self::GetTreeNodeList($line);
    }

    public static function GetTreeNodeListList($line){
        return self::GetList_($line, 'GetTreeNodeList');
    }

    public static function GetTreeNodess($line){
        return self::GetTreeNodeListList($line);
    }

    public static function PrintTreeNodeListInternal($x){
        self::PrintList_($x, 'PrintTreeNodeInternal');
    }

    public static function PrintTreeNode($x){
        self::PrintTreeNodeInternal($x);
        echo "\n";
    }

    public static function PrintTreeNodeList($x){
        self::PrintTreeNodeListInternal($x);
        echo "\n";
    }

    public static function PrintTreeNodeListList($x){
        self::PrintList_($x, 'PrintTreeNodeListInternal');
        echo "\n";
    }

    public static function PrintTreeNodes($x){
        self::PrintTreeNodeList($x);
    }

    public static function PrintTreeNodess($x){
        self::PrintTreeNodeListList($x);
    }

    //TreeLinkNode
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
    public static function GetTreeLinkNode($line){
        $all_items = self::GetRangeItems($line);
        $is_newversion = count($all_items) === 2 && $all_items[0][0] == '[' && $all_items[1][0] == '[';
        if(!$is_newversion){
            $all_items = array($line, "[]");
        }
        if(count($all_items) < 2)
            return NULL;
        $items = self::GetRangeItems($all_items[0]);
        if(count($items) === 0){
            return NULL;
        }

        $tree_nodes = array();
        $map_nodes = array();
        $current = 0;
        $current_pos = self::$LEFT;
        $index = 1;
        $tree_nodes[0] = new TreeLinkNode(self::GetInt($items[0]));
        for($i = 1; $i<count($items);$i++){
            if($items[$i] === '#'){
                if($tree_nodes[$current]){
                    if($current_pos === self::$LEFT){
                        $current_pos = self::$RIGHT;
                    } else if($tree_nodes[$current + 1]){
                        $current = $current + 1;
                        $current_pos = self::$LEFT;
                    }
                }
            } else {
                $label = self::GetInt($items[$i]);
                $tree_nodes [$index] = new TreeLinkNode ($label);
                $map_nodes [$label] = $tree_nodes[$index];
                if($current_pos === self::$LEFT){
                    $tree_nodes[$current]->left = $tree_nodes[$index];
                    $current_pos = self::$RIGHT;
                } else {
                    $tree_nodes[$current]->right = $tree_nodes[$index];
                    $current = $current + 1;
                    $current_pos = self::$LEFT;
                }
                $index = $index + 1;
            }
        }
        // 连接next指针
        $items = self::GetRangeItems($all_items [1]);
        for($i = 0; $i<count($items);$i++){
            if($items[$i] !== "#" && $map_nodes[self::GetInt ($items [$i])]){
                $tree_nodes[$i]->next = $tree_nodes[self::GetInt ($items [$i])];
            }
        }
        return $tree_nodes[0];
    }

    public static function PrintTreeLinkNodeInternal($root){
        if($root == NULL){
            echo "null";
            return;
        }
        echo "{[";
        $v = array();
        $label_node_v = array();
        if($root){
            $v []= $root;
            $label_node_v []= $root;
        }
        $c = 0;
        $none = "";
        while($c < count($v)){
            if($c === 0){
                printf("%d", $v[$c]->val);
                array_push($v, $v[$c]->left, $v[$c]->right);
            } else {
                if($v[$c] == NULL) {
                    $none = $none . ",#";
                } else {
                    $label_node_v []= $v[$c];
                    printf("%s,%d", $none, $v[$c]->val);
                    $none = "";
                    array_push($v, $v[$c]->left, $v[$c]->right);
                }
            }
            $c = $c + 1;
        }
        $v = array();
        echo "],[";
        foreach ($label_node_v as $i => $node){
            if($i!== 0){
                echo ",";
            }
            if($node->next){
                printf("%d", $node->next->val);
            } else {
                echo "#";
            }
        }
        echo "]}";
    }

    public static function GetTreeLinkNodeList($line){
        return self::GetList_($line, 'GetTreeLinkNode');
    }

    public static function GetTreeLinkNodes($line){
        return self::GetTreeLinkNodeList($line);
    }

    public static function GetTreeLinkNodeListList($line){
        return self::GetList_($line, 'GetTreeLinkNodeList');
    }

    public static function GetTreeLinkNodess($line){
        return self::GetTreeLinkNodeListList($line);
    }

    public static function PrintTreeLinkNodeListInternal($x){
        self::PrintList_($x, 'PrintTreeLinkNodeInternal');
    }

    public static function PrintTreeLinkNode($x){
        self::PrintTreeLinkNodeInternal($x);
        echo "\n";
    }

    public static function PrintTreeLinkNodeList($x){
        self::PrintTreeLinkNodeListInternal($x);
        echo "\n";
    }

    public static function PrintTreeLinkNodeListList($x){
        self::PrintList_($x, 'PrintTreeLinkNodeListInternal');
        echo "\n";
    }

    public static function PrintTreeLinkNodes($x){
        self::PrintTreeLinkNodeList($x);
    }

    public static function PrintTreeLinkNodess($x){
        self::PrintTreeLinkNodeListList($x);
    }

    //RandomListNode
    // { -1, 8, 7, -3,4,4,-3,#,#,-1}
    // 分为两段，前部分为ListNode,后半部分如果random==None是#，否则就是random.val
    public static function GetRandomListNode($line){
        $items = self::GetRangeItems($line);
        if(count($items) < 2){
            return NULL;
        }
        $count = count($items) / 2;

        $list_nodes = array();
        $nodes_map = array();
        $head = new RandomListNode(self::GetInt($items[0]));
        $nodes_map[$head->label] = $head;
        $list_nodes[0] = $head;
        $tail = $head;
        for($i = 1; $i<$count;$i++){
            $cur = new RandomListNode(self::GetInt($items[$i]));
            $tail->next = $cur;
            $tail = $cur;
            $nodes_map[$cur->label] = $cur;
            $list_nodes[$i] = $cur;
        }

        for($i = $count; $i<count($items);$i++){
            if($items[$i] !== '#' && $nodes_map[self::GetInt($items[$i])]){
                $list_nodes[$i - $count]->random = $nodes_map[self::GetInt($items[$i])];
            }
        }
        return $head;
    }

    public static function PrintRandomListNodeInternal($head){
        if($head == NULL){
            echo "{}";
            return;
        }
        $current = $head;
        echo "{";
        while($current != NULL){
            if($current === $head){
                printf("%d", $current->label);
            } else {
                printf(",%d", $current->label);
            }
            $current = $current->next;
        }
        $current = $head;
        while($current != NULL){
            if($current->random != NULL){
                printf(",%d", $current->random->label);
            } else {
                echo ",#";
            }
            $current = $current->next;
        }
        echo "}";
    }

    public static function GetRandomListNodeList($line){
        return self::GetList_($line, 'GetRandomListNode');
    }

    public static function GetRandomListNodes($line){
        return self::GetRandomListNodeList($line);
    }

    public static function GetRandomListNodeListList($line){
        return self::GetList_($line, 'GetRandomListNodeList');
    }

    public static function GetRandomListNodess($line){
        return self::GetRandomListNodeListList($line);
    }

    public static function PrintRandomListNodeListInternal($x){
        self::PrintList_($x, 'PrintRandomListNodeInternal');
    }

    public static function PrintRandomListNode($x){
        self::PrintRandomListNodeInternal($x);
        echo "\n";
    }

    public static function PrintRandomListNodeList($x){
        self::PrintRandomListNodeListInternal($x);
        echo "\n";
    }

    public static function PrintRandomListNodeListList($x){
        self::PrintList_($x, 'PrintRandomListNodeListInternal');
        echo "\n";
    }

    public static function PrintRandomListNodes($x){
        self::PrintRandomListNodeList($x);
    }

    public static function PrintRandomListNodess($x){
        self::PrintRandomListNodeListList($x);
    }

    public static function test(){
        $line = "";
        $line = $line . "1 , [ 1 , 2 ],[[1],[2],[3,4,-5]],[ 1 , 2 ],[[1],[2],[3,4,5]],"; # int
        $line = $line . "true , [ false , true ],[[false],[false],[false,true,true]],[ true , false ],[[false],[true],[true,true,true]],"; # bool
        $line = $line . "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [ 1 , 2 ],[[1],[2],[3,4,5]],"; # float
        $line = $line . "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [],[ 1 , 2 ],[[1],[2],[3,4,5]],"; # double
        $line = $line . " \"a\", [\"\",\"x[[[[,,,,[}}}}\"], [[acd, efg], [acd, \"efg\"]],";# string
        $line = $line . " a, [x, y ], [[a, b],[], [c, d]],";# char
        $line = $line . " 1000000000, [3000000000, 2000000000 ], [[3000000000, 2000000000 ],[13000000000, 22000000000 ]],";# long
        //ListNode
        $line = $line . "{1,3,4},[{2, 4, 5},{5,6,7,89,11},{ }],[[{2, 4, 5},{5,6,7,89,11},{}],[{2, 4, 5},{5,6,7,89,11}]],"; 
        //Interval
        $line = $line . "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]],";
        //Point
        $line = $line . "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]],"; 
        //TreeNode
        $line = $line . "{1,2,3,#,#,4,#,#,5},[{1,2,3,#,#,4,#,#,5}],[[{1,2,3,#,#,4,#,#,5}],[{1,2,3,#,#,4,#,#,5},{1,2,3,#,#,4,#,#,5}]],";
        // TreeLinkNode
        $line = $line . "{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]},[{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}],[[],[{[],[]}], [{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}]],"; 
        // RandomListNode
        $line = $line . "{ -1, 8, 7,  -3,4,4,-3,#,#,-1}, [{ -1, 8, 7,  -3,4,4,-3,#,#,-1}], [[{}],[{ -1, 8, 7,  -3,4,4,-3,#,#,-1}]],";
        //
        $line = $line . "{[0,1,2],[1,2],[2,2]}, [{[0,1,2],[1,2],[2,2]}], [[], [{[0,1,2],[1,2],[2,2]},{[0,1,2],[1,2],[2,2]}]]";

        $parameters = self::GetArguments($line);
        $i = 0;
        self::PrintInt(self::GetInt($parameters[$i]));
        $i++;
        self::PrintInts(self::GetInts($parameters[$i]));
        $i++;
        self::PrintIntss(self::GetIntss($parameters[$i]));
        $i++;
        self::PrintIntList(self::GetIntList($parameters[$i]));
        $i++;
        self::PrintIntListList(self::GetIntListList($parameters[$i]));
        $i++;

        self::PrintBool(self::GetBool($parameters[$i]));
        $i++;
        self::PrintBools(self::GetBools($parameters[$i]));
        $i++;
        self::PrintBoolss(self::GetBoolss($parameters[$i]));
        $i++;
        self::PrintBoolList(self::GetBoolList($parameters[$i]));
        $i++;
        self::PrintBoolListList(self::GetBoolListList($parameters[$i]));
        $i++;

        self::PrintFloat(self::GetFloat($parameters[$i]));
        $i++;
        self::PrintFloats(self::GetFloats($parameters[$i]));
        $i++;
        self::PrintFloatss(self::GetFloatss($parameters[$i]));
        $i++;
        self::PrintFloatList(self::GetFloatList($parameters[$i]));
        $i++;
        self::PrintFloatListList(self::GetFloatListList($parameters[$i]));
        $i++;
        
        self::PrintDouble(self::GetDouble($parameters[$i]));
        $i++;
        self::PrintDoubles(self::GetDoubles($parameters[$i]));
        $i++;
        self::PrintDoubless(self::GetDoubless($parameters[$i]));
        $i++;
        self::PrintDoubles(self::GetDoubles($parameters[$i]));
        $i++;
        self::PrintDoubleList(self::GetDoubleList($parameters[$i]));
        $i++;
        self::PrintDoubleListList(self::GetDoubleListList($parameters[$i]));
        $i++;

        self::PrintString(self::GetString($parameters[$i]));
        $i++;
        self::PrintStringList(self::GetStringList($parameters[$i]));
        self::PrintStrings(self::GetStrings($parameters[$i]));
        $i++;
        self::PrintStringListList(self::GetStringListList($parameters[$i]));
        self::PrintStringss(self::GetStringss($parameters[$i]));
        $i++;
        
        self::PrintChar(self::GetChar($parameters[$i]));
        $i++;
        self::PrintChars(self::GetChars($parameters[$i]));
        $i++;
        self::PrintCharss(self::GetCharss($parameters[$i]));
        $i++;

        self::PrintLong(self::GetLong($parameters[$i]));
        $i++;
        self::PrintLongList(self::GetLongList($parameters[$i]));
        self::PrintLongs(self::GetLongs($parameters[$i]));
        $i++;
        self::PrintLongListList(self::GetLongListList($parameters[$i]));
        self::PrintLongss(self::GetLongss($parameters[$i]));
        $i++;

        self::PrintListNode(self::GetListNode($parameters[$i]));
        $i++;
        self::PrintListNodeList(self::GetListNodeList($parameters[$i]));
        self::PrintListNodes(self::GetListNodes($parameters[$i]));
        $i++;
        self::PrintListNodeListList(self::GetListNodeListList($parameters[$i]));
        self::PrintListNodess(self::GetListNodess($parameters[$i]));
        $i++;
        
        self::PrintInterval(self::GetInterval($parameters[$i]));
        $i++;
        self::PrintIntervalList(self::GetIntervalList($parameters[$i]));
        self::PrintIntervals(self::GetIntervals($parameters[$i]));
        $i++;
        self::PrintIntervalListList(self::GetIntervalListList($parameters[$i]));
        self::PrintIntervalss(self::GetIntervalss($parameters[$i]));
        $i++;

        self::PrintPoint(self::GetPoint($parameters[$i]));
        $i++;
        self::PrintPointList(self::GetPointList($parameters[$i]));
        self::PrintPoints(self::GetPoints($parameters[$i]));
        $i++;
        self::PrintPointListList(self::GetPointListList($parameters[$i]));
        self::PrintPointss(self::GetPointss($parameters[$i]));
        $i++;
        
        self::PrintTreeNode(self::GetTreeNode($parameters[$i]));
        $i++;
        self::PrintTreeNodeList(self::GetTreeNodeList($parameters[$i]));
        self::PrintTreeNodes(self::GetTreeNodes($parameters[$i]));
        $i++;
        self::PrintTreeNodeListList(self::GetTreeNodeListList($parameters[$i]));
        self::PrintTreeNodess(self::GetTreeNodess($parameters[$i]));
        $i++;

        self::PrintTreeLinkNode(self::GetTreeLinkNode($parameters[$i]));
        $i++;
        self::PrintTreeLinkNodeList(self::GetTreeLinkNodeList($parameters[$i]));
        self::PrintTreeLinkNodes(self::GetTreeLinkNodes($parameters[$i]));
        $i++;
        self::PrintTreeLinkNodeListList(self::GetTreeLinkNodeListList($parameters[$i]));
        self::PrintTreeLinkNodess(self::GetTreeLinkNodess($parameters[$i]));
        $i++;
        
        self::PrintRandomListNode(self::GetRandomListNode($parameters[$i]));
        $i++;
        self::PrintRandomListNodeList(self::GetRandomListNodeList($parameters[$i]));
        self::PrintRandomListNodes(self::GetRandomListNodes($parameters[$i]));
        $i++;
        self::PrintRandomListNodeListList(self::GetRandomListNodeListList($parameters[$i]));
        self::PrintRandomListNodess(self::GetRandomListNodess($parameters[$i]));
        $i++;

    }
}

//NCTools::test();
//echo "\nend";