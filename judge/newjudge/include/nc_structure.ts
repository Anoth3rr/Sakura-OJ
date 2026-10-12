class Interval {
  start: number
  end: number
  constructor(start: number, end: number) {
      this.start = start 
      this.end = end 
  }
}
class Point {
  x: number
  y: number
  constructor(x: number, y: number) {
      this.x = x 
      this.y = y 
  }
}
class ListNode {
  val: number
  next: ListNode | null
  constructor(val?: number, next?: ListNode | null) {
      this.val = (val===undefined ? 0 : val)
      this.next = (next===undefined ? null : next)
  }
}
class TreeNode {
  val: number
  left: TreeNode | null
  right: TreeNode | null
  constructor(val?: number, left?: TreeNode | null, right?: TreeNode | null) {
      this.val = (val===undefined ? 0 : val)
      this.left = (left===undefined ? null : left)
      this.right = (right===undefined ? null : right)
  }
}