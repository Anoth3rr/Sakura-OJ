
//use std::collections::VecDeque;
use std::collections::VecDeque;

pub struct NCTools  {}

#[derive(PartialEq, Eq, Debug, Clone)]
pub struct ListNode {
    pub val: i32,
    pub next: Option<Box<ListNode>>
}

impl ListNode {
    #[inline]
    fn new(val: i32) -> Self {
        ListNode {
            val: val,
            next: None,
        }
    }
}

#[derive(PartialEq, Eq, Debug, Clone)]
pub struct TreeNode {
    pub val: i32,
    pub left: Option<Box<TreeNode>>,
    pub right: Option<Box<TreeNode>>,
}

impl TreeNode {
    #[inline]
    fn new(val: i32) -> Self {
        TreeNode {
            val: val,
            left: None,
            right: None,
        }
    }
}

#[derive(PartialEq, Eq, Clone, Debug)]
pub struct Interval {
    pub start: i32,
    pub end: i32,
}

impl Interval {
    #[inline]
    fn new(start: i32, end: i32) -> Self {
        Interval {
            start: start,
            end: end,
        }
    }
}

#[derive(PartialEq, Eq, Clone, Debug)]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

impl Point {
    #[inline]
    fn new(x: i32, y: i32) -> Self {
        Point {
            x: x,
            y: y,
        }
    }
}

pub trait NCType {
    fn Get(s: &str) -> Self;
    fn PrintInternal(&self);
//    fn Print(s: Self); // 2钟写法，只是为了测试一下 rust 的generic: 这个也是可行的
}

// Int
impl NCType for i32 {
    fn Get(s :&str) -> i32 {
        s.trim().parse::<i32>().unwrap_or(0)
    }
    fn PrintInternal(&self) {
        print!("{}", self)
    }
}

// Long
impl NCType for i64 {
    fn Get(s :&str) -> i64 {
        s.trim().parse().unwrap_or(0)
    }
    fn PrintInternal(&self) {
        print!("{}", self)
    }
}

//Float
impl NCType for f32 {
    fn Get(s :&str) -> f32 {
        s.trim().parse::<f32>().unwrap_or(0.0)
    }
    fn PrintInternal(&self) {
        if self.abs() < 0.0000099999 {
            print!("0.00000");
        } else {
            print!("{:.5}", self); 
        }
    }
}


//Double
impl NCType for f64 {
    fn Get(s :&str) -> f64 {
        s.trim().parse::<f64>().unwrap_or(0.0)
    }
    fn PrintInternal(&self) {
        if self.abs() < 0.0000099999 {
            print!("0.00000");
        } else {
            print!("{:.5}", self); 
        }
    }
}

//String
impl NCType for String {
    fn Get(s :&str) -> String {
        let bytes = s.trim().as_bytes();
        let l = bytes.len();
        if bytes.len() == 0 || bytes[0] != b'\"' || bytes[l-1] != b'\"' {
            return String::from_utf8(bytes.to_vec()).unwrap();
        } else {
           // return bytes[1..(l-1)].to_vec().into()
            return String::from_utf8(bytes[1..(l-1)].to_vec()).unwrap();
        }
    }
    fn PrintInternal(&self) {
        print!("\"{}\"", self); 
    }
}

//Char
impl NCType for char {
    fn Get(s :&str) -> char {
        let bytes = s.trim().as_bytes();
        let l = bytes.len();
        if l == 0 {
            return '#';
        } else {
            return bytes[0].into();
        }
    }
    fn PrintInternal(&self) {
        print!("{}", self); 
    }
}

//Bool
impl NCType for bool {
    fn Get(s :&str) -> bool {
        s.trim() == "true"
        //s.trim().parse().unwrap_or(true)
    }
    fn PrintInternal(&self) {
        print!("{}", self); 
    }
}

//Internal
impl NCType for Interval {
    fn Get(s :&str) -> Self {
        let items: Vec<i32> = NCType::Get(s);
        if items.len() == 2 {
            Interval::new(items[0], items[1])
        } else {
            Interval::new(0, 0)
        }
    }
    fn PrintInternal(&self) {
        print!("[{},{}]", self.start, self.end)
    }
}
//Point
impl NCType for Point {
    fn Get(s :&str) -> Self {
        let items: Vec<i32> = NCType::Get(s);
        if items.len() == 2 {
            Point::new(items[0], items[1])
        } else {
            Point::new(0, 0)
        }
    }
    fn PrintInternal(&self) {
        print!("({},{})", self.x, self.y)
    }
}

impl NCType for Option<Box<TreeNode>> {
    // TODO: 这个只是能跑，有没有胡乱复制或修改内存不可知；
    fn Get(s :&str) -> Self {
        let items = NCTools::GetRangeItems(s);
        if items.len() == 0 {
            return None
        }

        let mut root = TreeNode::new(NCTools::Get::<i32>(&items[0]));
        let mut dq = VecDeque::new();
        dq.push_back(&mut root.left);
        dq.push_back(&mut root.right);

        let mut i = 1;
        while let Some(no) = dq.pop_front() {
            if i >= items.len() {
                break;
            }
            if items[i].trim() != "#"  {
                let ii = NCTools::Get::<i32>(&items[i]);
                *no = Some(Box::new(TreeNode::new(ii)));
                let no = no.as_deref_mut().unwrap();
                dq.push_back(&mut no.left);
                dq.push_back(&mut no.right);
            } else {
                // println!("pass");
            }
            i = i+1;
        }
        return Some(Box::new(root));


        // let mut tree_nodes = vec![None; items.len()+1];
        
        // let mut current = 0usize;
        // let mut current_pos = NCTools::LEFT;
        // let mut index = 1usize;
        // let root = TreeNode::new(NCTools::Get::<i32>(&items[0]));
        // let root2 = TreeNode::new(NCTools::Get::<i32>(&items[0]));
        
        // tree_nodes[0] = Some(&mut root.left);
      // //  println!("{}", tree_nodes[0].unwrap().left);
        // *tree_nodes[0].unwrap()=Some(Box::new(root2));
         // for i in 1..items.len() {
         //     if items[i].trim() == "#" {
         //         if tree_nodes[current] != None {
         //             if current_pos == NCTools::LEFT {
         //                 current_pos= NCTools::RIGHT;
         //             } else if tree_nodes[current +1] != None {
         //                 current += 1;
         //                 current_pos = NCTools::LEFT;
         //             }
         //         }
         //     } else {
         //         if current_pos == NCTools::LEFT {
         //             tree_nodes[current].unwrap().left = Some(Box::new(TreeNode::new(NCTools::Get::<i32>(&items[i]))));
         //             current_pos = NCTools::RIGHT;
         //             tree_nodes[index] = Some(tree_nodes[current].unwrap().left.as_ref().unwrap());
         //         } else {
         //             // tree_nodes[current].as_ref().unwrap().borrow_mut().right = tree_nodes[index].clone();
         //             current += 1;
         //             current_pos = NCTools::LEFT;
         //         }
         //         index += 1;
         //     }
         //  }
        // return Some(Box::new(root));
    }



    // TODO: 这个只是能跑，有没有胡乱复制或修改内存不可知；
    fn PrintInternal(&self) {
        if self == &None {
            print!("{{}}");
            return;
        }
        print!("{{");
        let mut dq = VecDeque::new();
        let mut none = "".to_owned();
        dq.push_back(Some(self.as_deref().unwrap()));

        let mut first = true;
        while let Some(no) = dq.pop_front() {
            if let Some(no) = no {
                if !first {
                    print!("{},{}", none, no.val);
                    none = "".to_owned();
                } else {
                    print!("{}",no.val);
                    first=false;
                }
                if let Some(l) = no.left.as_deref() {
                    dq.push_back(Some(l));
                } else {
                    dq.push_back(None);
                }
                if let Some(r) = no.right.as_deref() {
                    dq.push_back(Some(r));
                } else {
                    dq.push_back(None);
                }
            } else {
                none = none + ",#";
            }
        }
        print!("}}");

        // let mut v: Vec<Option<Rc<RefCell<TreeNode>>>> = [self.clone()].to_vec();
        // let mut c = 0;
        // let mut none = "".to_owned();
        
        // while c < v.len() {
        //     if c == 0 {
        //         if let Some(node) = v[c].clone() {
        //             print!("{}", node.borrow().val);
        //             v.push(node.borrow().left.clone());
        //             v.push(node.borrow().right.clone());
        //         }
        //     } else {
        //         if let Some(node) = v[c].clone() {
        //             print!("{},{}", none, node.borrow().val);
        //             none = "".to_owned();
        //             v.push(node.borrow().left.clone());
        //             v.push(node.borrow().right.clone());
        //         } else {
        //             none = none + ",#";
        //         }
        //     }
        //     c += 1;
        // }

        // print!("}}");
        
        return
    }

}


// ListNode
impl NCType for Option<Box<ListNode>> {
    fn Get(s: &str) -> Self {
        let items: Vec<i32> = NCTools::Get(s);
        // println!("====");
        // println!("{}, {}", s, items.len());
        if items.len() == 0 {
            return None;
        }
        let mut dummy = ListNode::new(0);
        let mut tail = &mut dummy;
        for i in 0..items.len() {
            tail.next = Some(Box::new(ListNode::new(items[i])));
            tail = tail.next.as_deref_mut().unwrap();
        }
        return dummy.next;
    }
    fn PrintInternal(&self) {
        if self == &None {
            print!("{{}}");
            return;
        }
        let mut head = self;
        print!("{{");
        while let Some(cur) = head {
            if head == self {
                print!("{}", cur.val);
            } else {
                print!(",{}", cur.val);
            }
            head = &cur.next;
        }

        print!("}}");
    }
}

impl<T: Clone> NCType for Vec<T> where T: NCType {
    fn Get(s :&str) -> Self {
        let items: Vec<&str> = NCTools::GetRangeItems(&s);
        let mut ret: Vec<T> = [].to_vec();
        for it in items {
            ret.push(NCType::Get(it))
        }
        return ret
    }
    fn PrintInternal(&self) {
        print!("[");
        for i in 0..self.len() {
            if i != 0 {
                print!(",")
            } 
            NCTools::PrintInternal(&self[i])
        }
        print!("]");
    }

}




impl NCTools {
    const LEFT : i32 = 0;
    const RIGHT: i32 = 1;

    fn Get<T: NCType>(s :&str) -> T {
        NCType::Get(s)
    }
    fn PrintInternal<T: NCType>(v :&T) {
        v.PrintInternal();
    }

    fn Print<T: NCType>(v :&T) {
        Self::PrintInternal(v);
        print!("\n");
    }



    #[inline]
    fn IsBeginRange(c: char) -> bool {
       c == '{' || c == '[' || c == '('
    }

    #[inline]
    fn IsEndRange(c: char) -> bool {
       c == '}' || c == ']' || c == ')'
    }

    #[inline]
    fn GetArguments(line: &str) -> Vec<&str> {
        let mut ret: Vec<&str> = Vec::new();

        let bytes = line.as_bytes();
        let len = bytes.len();
        let mut inrange = 0;
        let mut pre_index = 0;
        let mut inmao = false;
        for i in 0..len {
            if Self::IsBeginRange(bytes[i].into()) && !inmao {
                inrange = inrange + 1;
            } else if Self::IsEndRange(bytes[i].into()) && !inmao {
                inrange = inrange - 1;
            } else if bytes[i] == b'\"' {
                inmao = !inmao;
            } else if bytes[i] == b',' && inrange == 0 && !inmao {
                ret.push(&line[pre_index.. i]);
                pre_index = i + 1;
            }
        }
        ret.push(&line[pre_index..]);
        return ret;
    }
    #[inline]
    fn GetRangeItems(s: &str) ->Vec<&str> {
        let bytes = s.as_bytes();

        let mut begin = 0;
        while !Self::IsBeginRange(bytes[begin].into()) && begin <bytes.len() {
            begin += 1;
        }
        let mut end = bytes.len() - 1;
        while !Self::IsEndRange(bytes[end].into()) && end > 1 {
            end -= 1;
        }
        let s = &s[begin+1..end];
        if s.trim().len() == 0{
            return [].to_vec();
        } else {
            return Self::GetArguments(s)
        }
    }



    fn Testing() {
        let mut line = "1 , [ 1 , 2 ],[[1],[2],[3,4,-5]],[ 1 , 2 ],[[1],[2],[3,4,5]],".to_owned(); // int
        line = line
                + "true , [ false , true ],[[false],[false],[false,true,true]],[ true , false ],[[false],[true],[true,true,true]],"; // bool
        line = line
                + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [ 1 , 2 ],[[1],[2],[3,4,5]],"; // float
        line = line
               + "1.2 , [ 1.3 , 2.4 ],[[1.0],[-2],[3,4,5]], [],[ 1 , 2 ],[[1],[2],[3,4,5]],"; // double
        line = line
                + " \"a\", [\"\",\"x[[[[,,,,[}}}}\"], [[acd, efg], [acd, \"efg\"]],";// string
        line = line + " a, [x, y ], [[a, b],[], [c, d]],";// char
        line = line
                + " 1000000000, [3000000000, 2000000000 ], [[3000000000, 2000000000 ],[13000000000, 22000000000 ]],";// long
        line = line
                + "{1,3,4},[{2, 4, 5},{5,6,7,89,11},{ }],[[{2, 4, 5},{5,6,7,89,11},{}],[{2, 4, 5},{5,6,7,89,11}]],"; // ListNode
        line = line
                + "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]],"; // Interval
        line = line
                + "[1,3],[{2, 5},{5,11}],[[{2, 5},{5,6}],[{ 4, 5},{89,11}]],"; // Point
        line = line
                + "{1,2,3,#,#,4,#,#,5},[{1,2,3,#,#,4,#,#,5}],[[{1,2,3,#,#,4,#,#,5}],[{1,2,3,#,#,4,#,#,5},{1,2,3,#,#,4,#,#,5}]],"; // TreeNode
        line = line
                + "{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]},[{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}],[[],[{[],[]}], [{[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}]],"; // TreeLinkNode
        line = line
                + "{ -1, 8, 7,  -3,4,4,-3,#,#,-1}, [{ -1, 8, 7,  -3,4,4,-3,#,#,-1}], [[{}],[{ -1, 8, 7,  -3,4,4,-3,#,#,-1}]],"; // RandomListNode
        line = line
                + "{[0,1,2],[1,2],[2,2]}, [{[0,1,2],[1,2],[2,2]}], [[], [{[0,1,2],[1,2],[2,2]},{[0,1,2],[1,2],[2,2]}]]"; //

        let parameters = NCTools::GetArguments(&line);
        // // NCTools.Print(parameters);
        let mut i = 0usize;
        NCTools::Print(&Self::Get::<i32>(parameters[i])); i += 1;
        NCTools::Print(&NCTools::Get::<Vec<i32>>(parameters[i])); i += 1;
        NCTools::Print(&NCTools::Get::<Vec<Vec<i32>>>(parameters[i])); i += 1;
        NCTools::Print(&NCTools::Get::<Vec<i32>>(parameters[i])); i += 1;
        NCTools::Print(&NCTools::Get::<Vec<Vec<i32>>>(parameters[i])); i += 1;

        NCTools::Print(&<bool>::Get(parameters[i])); i += 1;
        NCTools::Print(&<Vec<bool>>::Get(parameters[i])); i += 1;
        NCTools::Print(&<Vec<Vec<bool>>>::Get(parameters[i])); i += 1;
        NCTools::Print(&Self::Get::<Vec<bool>>(parameters[i])); i += 1;
        NCTools::Print(&Self::Get::<Vec<Vec<bool>>>(parameters[i])); i += 1;

        NCTools::Print(&<f32>::Get(parameters[i])); i += 1;
        NCTools::Print(&<Vec<f32>>::Get(parameters[i])); i += 1;
        NCTools::Print(&<Vec<Vec<f32>>>::Get(parameters[i])); i += 1;
        NCTools::Print(&Self::Get::<Vec<f32>>(parameters[i])); i += 1;
        NCTools::Print(&Self::Get::<Vec<Vec<f32>>>(parameters[i])); i += 1;

        NCTools::Print(&<f64>::Get(parameters[i])); i += 1;
        NCTools::Print(&<Vec<f64>>::Get(parameters[i])); i += 1;
        NCTools::Print(&<Vec<Vec<f64>>>::Get(parameters[i])); i += 1;
        NCTools::Print(&Self::Get::<Vec<f64>>(parameters[i])); i += 1;
        NCTools::Print(&Self::Get::<Vec<f64>>(parameters[i])); i += 1;
        NCTools::Print(&Self::Get::<Vec<Vec<f64>>>(parameters[i])); i += 1;

        NCTools::Print(&<String>::Get(parameters[i])); i += 1;
        NCTools::Print(&<Vec<String>>::Get(parameters[i]));
        NCTools::Print(&Self::Get::<Vec<String>>(parameters[i])); i += 1;
        NCTools::Print(&<Vec<Vec<String>>>::Get(parameters[i]));
        NCTools::Print(&Self::Get::<Vec<Vec<String>>>(parameters[i])); i += 1;

        NCTools::Print(&NCTools::Get::<char>(parameters[i])); i += 1;
        NCTools::Print(&NCTools::Get::<Vec<char>>(parameters[i])); i += 1;
        NCTools::Print(&NCTools::Get::<Vec<Vec<char>>>(parameters[i])); i += 1;

        NCTools::Print(&NCTools::Get::<i64>(parameters[i])); i+= 1;
        NCTools::Print(&NCTools::Get::<Vec<i64>>(parameters[i])); 
        NCTools::Print(&NCTools::Get::<Vec<i64>>(parameters[i])); i+=1;
        NCTools::Print(&NCTools::Get::<Vec<Vec<i64>>>(parameters[i]));
        NCTools::Print(&NCTools::Get::<Vec<Vec<i64>>>(parameters[i])); i+=1;

        NCTools::Print(&NCTools::Get::<Option<Box<ListNode>>>(parameters[i])); i = i + 1;
        NCTools::Print(&NCTools::Get::<Vec<Option<Box<ListNode>>>>(parameters[i]));
        NCTools::Print(&NCTools::Get::<Vec<Option<Box<ListNode>>>>(parameters[i])); i = i + 1;
        NCTools::Print(&NCTools::Get::<Vec<Vec<Option<Box<ListNode>>>>>(parameters[i]));
        NCTools::Print(&NCTools::Get::<Vec<Vec<Option<Box<ListNode>>>>>(parameters[i])); i = i + 1;


        NCTools::Print(&NCTools::Get::<Interval>(parameters[i])); i+=1;
        NCTools::Print(&NCTools::Get::<Vec<Interval>>(parameters[i])); 
        NCTools::Print(&NCTools::Get::<Vec<Interval>>(parameters[i])); i+=1;
        NCTools::Print(&NCTools::Get::<Vec<Vec<Interval>>>(parameters[i]));
        NCTools::Print(&NCTools::Get::<Vec<Vec<Interval>>>(parameters[i])); i+=1;

        NCTools::Print(&NCTools::Get::<Point>(parameters[i])); i+=1;
        NCTools::Print(&NCTools::Get::<Vec<Point>>(parameters[i])); 
        NCTools::Print(&NCTools::Get::<Vec<Point>>(parameters[i])); i+=1;
        NCTools::Print(&NCTools::Get::<Vec<Vec<Point>>>(parameters[i]));
        NCTools::Print(&NCTools::Get::<Vec<Vec<Point>>>(parameters[i])); i+=1;

        NCTools::Print(&NCTools::Get::<Option<Box<TreeNode>>>(parameters[i])); i = i + 1;
        NCTools::Print(&NCTools::Get::<Vec<Option<Box<TreeNode>>>>(parameters[i]));
        NCTools::Print(&NCTools::Get::<Vec<Option<Box<TreeNode>>>>(parameters[i])); i = i + 1;
        NCTools::Print(&NCTools::Get::<Vec<Vec<Option<Box<TreeNode>>>>>(parameters[i]));
        NCTools::Print(&NCTools::Get::<Vec<Vec<Option<Box<TreeNode>>>>>(parameters[i])); //i = i + 1;

    }
        
}        





