package main

type ListNode struct{
    Val int
    Next *ListNode
}

type TreeNode struct {
    Val int
    Left *TreeNode
    Right *TreeNode
}

type Interval struct {
    Start int
    End int
}

type Point struct {
    X int
    Y int
}

type TreeLinkNode struct {
    Val int
    Left *TreeLinkNode
    Right *TreeLinkNode
    Next *TreeLinkNode
}

type RandomListNode struct {
    Label int
    Next *RandomListNode
    Random *RandomListNode
}

type UndirectedGraphNode struct {
    Label int
    Neighbors []*UndirectedGraphNode
}