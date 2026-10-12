#ifndef NC_TOOLS
#define NC_TOOLS

#include <stdio.h>
#include <algorithm>
#include <bitset>
#include <assert.h>
#include <cctype>
#include <cerrno>
#include <clocale>
#include <cmath>
#include <complex>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <deque>
#include <exception>
#include <fstream>
#include <functional>
#include <limits>
#include <limits.h>
#include <list>
#include <map>
#include <iomanip>
#include <ios>
#include <iosfwd>
#include <iostream>
#include <istream>
#include <ostream>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <stdexcept>
#include <streambuf>
#include <string>
#include <utility>
#include <vector>
#include <cwchar>
#include <cwctype>
using namespace std;

#define LEFT 0
#define RIGHT 1
// 重载代码里的cout
class nc200buf : public streambuf {
public:
	nc200buf() {}
};


struct UndirectedGraphNode {
	int label;
	vector<struct UndirectedGraphNode *> neighbors;
	UndirectedGraphNode(int x) :
			label(x) {
	}
};

struct Point {
	int x;
	int y;
	Point() :
			x(0), y(0) {
	}
	Point(int xx, int yy) {
		x = xx;
		y = yy;
	}
};

struct Interval {
	int start;
	int end;
	Interval() :
			start(0), end(0) {
	}
	Interval(int s, int e) :
			start(s), end(e) {
	}
};

struct TreeNode {
	int val;
	struct TreeNode *left;
	struct TreeNode *right;
	TreeNode(int x) :
			val(x), left(NULL), right(NULL) {
	}
};
struct RandomListNode {
	int label;
	struct RandomListNode *next, *random;
	RandomListNode(int x) :
			label(x), next(NULL), random(NULL) {
	}
};

struct ListNode {
	int val;
	struct ListNode *next;
	ListNode(int x) :
			val(x), next(NULL) {
	}
};

struct TreeLinkNode {
	int val;
	struct TreeLinkNode *left;
	struct TreeLinkNode *right;
	struct TreeLinkNode *next;
	TreeLinkNode(int x) :
			val(x), left(NULL), right(NULL), next(NULL) {
	}
};

// 是不是结束字符
bool IsBeginRange(char c) {
	return c == '{' || c == '[' || c == '(';
}

bool IsEndRange(char c) {
	return c == '}' || c == ']' || c == ')';
}

vector<char*> GetArguments(char* line) {
	vector<char*> ret;
	int inrange = 0;
	size_t count = strlen(line);
	if (count == 0) {
		return ret;
	}
	char* pre_index = line;
	ret.push_back(pre_index);
	int inmao = 0;
	for (size_t i = 0; i < count; ++i) {
		if (IsBeginRange(line[i]) && !inmao) {
			++inrange;
		} else if (IsEndRange(line[i]) && !inmao) {
			--inrange;
		} else if (line[i] == '\"') {
			inmao = !inmao;
		} else if (line[i] == ',' && inrange == 0 && !inmao) {
			line[i] = '\0';
			ret.push_back(line + (i + 1));
		}
	}
	return ret;
}

// 获取集合参数到多个元素
vector<char*> GetRangeItems(char* str) {
    if (str == NULL) {
        return vector<char*>();
    }
	// [x,b,t] 去掉头解析内部到变量
	char* start_p = str;
	while (!IsBeginRange(*start_p)) {
		++start_p;
	}
	char* end_p = str + strlen(str);
	while (!IsEndRange(*end_p)) {
		--end_p;
	}
	*end_p = '\0';
	return GetArguments(start_p + 1);
}

// 增加vector<T> 和 vector<vector<T> >方法
#define DEFINE_MORE_METHODS(type, get_func, print_func)\
vector<type> get_func##List(char* str) {\
    vector<type> ret;\
    vector<char*> items = GetRangeItems(str);\
    for (size_t i = 0; i < items.size(); ++i) {\
            ret.push_back(get_func(items[i]));\
    }\
    return ret;\
}\
vector<vector<type> > get_func##ListList(char* str) {\
    vector<vector<type> > ret;\
    vector<char*> items = GetRangeItems(str);\
    for (size_t i = 0; i < items.size(); ++i) {\
            ret.push_back(get_func##List(items[i]));\
    }\
    return ret;\
}\
void Print(type x) {\
	print_func(x);\
	printf("\n");\
}\
void PrintInternal(const vector<type>& v) {\
	printf("[");\
	for (size_t i = 0; i < v.size(); ++i) {\
		if (i != 0) {\
			printf(",");\
		}\
		print_func(v[i]);\
	}\
	printf("]");\
}\
void Print(const vector<type>& v) {\
	PrintInternal(v);\
	printf("\n");\
}\
\
void Print(const vector<vector<type> >& vv) {\
	printf("[");\
	for (size_t i = 0; i < vv.size(); ++i) {\
		if (i != 0) {\
			printf(",");\
		}\
		PrintInternal(vv[i]);\
	}\
	printf("]\n");\
}

// 增加vector<T> 和 vector<vector<T> > set<T>方法
#define DEFINE_MORE_METHODS_WITH_SET(type, get_func, print_func)\
DEFINE_MORE_METHODS(type, get_func, print_func)\
set<type> get_func##Set(char* str) {\
    set<type> ret;\
    vector<char*> items = GetRangeItems(str);\
    for (size_t i = 0; i < items.size(); ++i) {\
            ret.insert(get_func(items[i]));\
    }\
    return ret;\
}\
void Print(const set<type>& x) {\
	printf("{");\
	for (set<type>::iterator it = x.begin(); it != x.end(); ++it) {\
		if (it != x.begin()) {\
			printf(",");\
		}\
		print_func(*it);\
	}\
	printf("}\n");\
}

// 1
int GetInt(char* str) {
	return atoi(str);
}
void PrintInternal(int x) {
	printf("%d", x);
}
DEFINE_MORE_METHODS_WITH_SET(int, GetInt, PrintInternal)

float GetFloat(char* str) {
	return atof(str);
}
void PrintInternal(float x) {
	if (fabs(x) < 0.00000999) {
		printf("0.00000");
	} else {
		printf("%.5f", x);
	}
}
DEFINE_MORE_METHODS_WITH_SET(float, GetFloat, PrintInternal)

long GetLong(char* str) {
	return atol(str);
}
void PrintInternal(long x) {
	printf("%ld", x);
}
DEFINE_MORE_METHODS_WITH_SET(long, GetLong, PrintInternal)

double GetDouble(char* str) {
	return atof(str);
}
void PrintInternal(double x) {
	if (fabs(x) < 0.00000999) {
		printf("0.00000");
	} else {
		printf("%.5lf", x);
	}
}
DEFINE_MORE_METHODS_WITH_SET(double, GetDouble, PrintInternal)

long long GetLongLong(char* str) {
	return atoll(str);
}
void PrintInternal(long long x) {
	printf("%lld", x);
}
DEFINE_MORE_METHODS_WITH_SET(long long, GetLongLong, PrintInternal)

string GetString(char* str) {
	if (str == NULL) {
		return "";
	}
	int len = strlen(str);
	// 过滤头尾到空格
	int begin = 0;
	while (str[begin] == ' ' && begin < len) {
		++begin;
	}

	// 过滤头尾到空格
	int end = len - 1;
	while (str[end] == ' ' && end > 0) {
		--len;
	}

	if (str[begin] == '"' && str[end] == '"') {
		str[end] = '\0';
		string s = string(str + begin + 1);
		str[end] = '"';
		return s;
	} else {
		char t = str[end + 1];
		str[end + 1] = '\0';
		string s = string(str + begin);
		str[end] = t;
		return s;
	}
}
void PrintInternal(const string& s) {
	printf("\"%s\"", s.c_str());
}
DEFINE_MORE_METHODS_WITH_SET(string, GetString, PrintInternal)

bool GetBool(char* str) {
	if (str == NULL) {
		return false;
	}
	return strcmp(str, "true") == 0 ? true : false;
}
void PrintInternal(bool b) {
	if (b) {
		printf("true");
	} else {
		printf("false");
	}
}
DEFINE_MORE_METHODS_WITH_SET(bool, GetBool, PrintInternal)

char GetChar(char* str) {
	while (*str == ' ') {
		++str;
	}
	return *str;
}
void PrintInternal(char c) {
	printf("%c", c);
}
DEFINE_MORE_METHODS_WITH_SET(char, GetChar, PrintInternal)

Point GetPoint(char* str) {
	vector<int> items = GetIntList(str);
	if (items.size() == 2) {
		return Point(items[0], items[1]);
	} else {
		return Point(0, 0);
	}
}
void PrintInternal(const Point& point) {
	printf("(%d,%d)", point.x, point.y);
}
DEFINE_MORE_METHODS(Point, GetPoint, PrintInternal)

Interval GetInterval(char* str) {
	vector<int> items = GetIntList(str);
	if (items.size() == 2) {
		return Interval(items[0], items[1]);
	} else {
		return Interval(0, 0);
	}
}
void PrintInternal(const Interval& interval) {
	printf("[%d,%d]", interval.start, interval.end);
}
DEFINE_MORE_METHODS(Interval, GetInterval, PrintInternal)

/**
 无向图里每个节点都有一个唯一的数字ID,每个节点的序列化通过[]保存,每个节点第一个元素后跟随的是这个节点连接的其他节点,以下图
 1
 /  \
     /    \
    0 --- 2
 / \
         \_/
 序列化后为{[0,1,2],[1,2],[2,2]}*/
UndirectedGraphNode* GetUndirectedGraphNode(char* str) {
	vector<vector<int> > points = GetIntListList(str);

	UndirectedGraphNode* ret = NULL;
	map<int, UndirectedGraphNode*> nodes_map;

	// 把所有的点构造出来
	for (size_t i = 0; i < points.size(); ++i) {
		const vector<int>& v = points[i];
		if (v.empty()) {
			continue;
		}
		if (nodes_map.find(v[0]) == nodes_map.end()) {
			UndirectedGraphNode* node = new UndirectedGraphNode(v[0]);
			nodes_map[v[0]] = node;
			if (ret == NULL) {
				ret = node;
			}
		}
	}

	// 把各个边连接起来
	for (size_t i = 0; i < points.size(); ++i) {
		const vector<int>& v = points[i];
		if (v.empty()) {
			continue;
		}
		UndirectedGraphNode* node = nodes_map[v[0]];
		for (size_t j = 1; j < v.size(); ++j) {
			node->neighbors.push_back(nodes_map[v[j]]);
		}
	}
	return ret;
}
void PrintInternal(UndirectedGraphNode* root) {
	if (root == NULL) {
		printf("null");
		return;
	}
	printf("{");
	if (root != NULL) {
		set<UndirectedGraphNode*> nodes_set;
		map<int, UndirectedGraphNode*> nodes_map;
		vector<UndirectedGraphNode*> nodes;
		nodes.push_back(root);
		nodes_set.insert(root);
		nodes_map[root->label] = root;
		for (size_t i = 0; i < nodes.size(); ++i) {
			for (size_t j = 0; j < nodes[i]->neighbors.size(); ++j) {
				UndirectedGraphNode* n_node = nodes[i]->neighbors[j];
				if (nodes_set.find(n_node) == nodes_set.end()) {
					nodes_set.insert(n_node);
					nodes.push_back(n_node);
					nodes_map[n_node->label] = n_node;
				}
			}
		}

		// 根据label从小到大打印
		for (map<int, UndirectedGraphNode*>::iterator it = nodes_map.begin();
				it != nodes_map.end(); ++it) {
			UndirectedGraphNode* node = it->second;
			if (it != nodes_map.begin()) {
				printf(",[%d", node->label);
			} else {
				printf("[%d", node->label);
			}
			for (size_t j = 0; j < node->neighbors.size(); ++j) {
				printf(",%d", node->neighbors[j]->label);
			}
			printf("]");
		}

	}
	printf("}");
}
void Release(UndirectedGraphNode* root) {
	if (root == NULL) {
		return;
	}
	map<int, UndirectedGraphNode*> nodes_map;
	vector<UndirectedGraphNode*> v;
	v.push_back(root);
	nodes_map[root->label] = root;
	for (size_t i = 0; i < v.size(); ++i) {
		vector<UndirectedGraphNode*>& neighbors = v[i]->neighbors;
		nodes_map[v[i]->label] = v[i];
		for (size_t j = 0; j < neighbors.size(); ++j) {
			if (nodes_map.find(neighbors[j]->label) == nodes_map.end()) {
				nodes_map[neighbors[j]->label] = neighbors[j];
				v.push_back(neighbors[j]);
			}
		}
	}

	// 删除所有的节点
	for (map<int, UndirectedGraphNode*>::iterator it = nodes_map.begin();
			it != nodes_map.end(); ++it) {
		delete it->second;
	}
}
DEFINE_MORE_METHODS(UndirectedGraphNode*, GetUndirectedGraphNode, PrintInternal)

// {1,2,3}
ListNode* GetListNode(char* str) {
	vector<int> items = GetIntList(str);
	if (items.empty()) {
		return NULL;
	}

	ListNode* head = new ListNode(items[0]);
	ListNode* tail = head;
	for (size_t i = 1; i < items.size(); ++i) {
		ListNode* cur = new ListNode(items[i]);
		tail->next = cur;
		tail = cur;
	}

	return head;
}
void PrintInternal(ListNode* head) {
	if (head == NULL) {
		printf("null");
		return;
	}
	ListNode* current = head;
	printf("{");
	while (current != NULL) {
		if (current == head) {
			printf("%d", current->val);
		} else {
			printf(",%d", current->val);
		}
		current = current->next;
	}
	printf("}");
}
void Release(ListNode* head) {
	if (head == NULL) {
		return;
	}
	set<ListNode*> nodes_set;
	vector<ListNode*> nodes;
	nodes.push_back(head);
	nodes_set.insert(head);
	for (size_t i = 0; i < nodes.size(); ++i) {
		if (nodes[i]->next
				&& nodes_set.find(nodes[i]->next) == nodes_set.end()) {
			nodes_set.insert(nodes[i]->next);
			nodes.push_back(nodes[i]->next);
		}
		delete nodes[i];
	}
}
DEFINE_MORE_METHODS(ListNode*, GetListNode, PrintInternal)

// { -1, 8, 7,  -3,4,4,-3,#,#,-1}
// 分为两段，前部分为ListNode,后半部分如果random==NULL是#，否则就是random.val
RandomListNode* GetRandomListNode(char* str) {
	vector<char*> items = GetRangeItems(str);
	if (items.size() < 2) {
		return NULL;
	}

	size_t count = items.size() / 2;
	// 记录前一半到节点
	RandomListNode** list_nodes = new RandomListNode*[count + 1];

	map<int, RandomListNode*> nodes_map;
	RandomListNode* head = new RandomListNode(GetInt(items[0]));
	nodes_map[head->label] = head;
	list_nodes[0] = head;
	RandomListNode* tail = head;
	for (size_t i = 1; i < count; ++i) {
		RandomListNode* cur = new RandomListNode(GetInt(items[i]));
		tail->next = cur;
		tail = cur;
		nodes_map[cur->label] = cur;
		list_nodes[i] = cur;
	}

	// 遍历后部分到随机节点
	for (size_t i = count; i < items.size(); ++i) {
		if (strcmp(items[i], "#") != 0) {
			map<int, RandomListNode*>::iterator iter = nodes_map.find(
					GetInt(items[i]));
			if (iter != nodes_map.end()) {
				list_nodes[i - count]->random = iter->second;
			}
		}
	}
	delete[] list_nodes;
	return head;
}
void PrintInternal(RandomListNode* head) {
	if (head == NULL) {
		printf("null");
		return;
	}
	RandomListNode* current = head;
	printf("{");
	while (current != NULL) {
		if (current == head) {
			printf("%d", current->label);
		} else {
			printf(",%d", current->label);
		}
		current = current->next;
	}
	current = head;
	while (current != NULL) {
		if (current->random != NULL) {
			printf(",%d", current->random->label);
		} else {
			printf(",#");
		}
		current = current->next;
	}
	printf("}");
}
void Release(RandomListNode* head) {
	if (head == NULL) {
		return;
	}
	set<RandomListNode*> nodes_set;
	vector<RandomListNode*> nodes;
	nodes.push_back(head);
	nodes_set.insert(head);
	for (size_t i = 0; i < nodes.size(); ++i) {
		if (nodes[i]->next
				&& nodes_set.find(nodes[i]->next) == nodes_set.end()) {
			nodes_set.insert(nodes[i]->next);
			nodes.push_back(nodes[i]->next);
		}
		delete nodes[i];
	}
}
DEFINE_MORE_METHODS(RandomListNode*, GetRandomListNode, PrintInternal)

/*二叉树序列化是通过按层遍历,#代表这这个节点为空节点,举个例子
 1
 / \
      2     3
 /
 4
 5

 以上二叉树会被序列化为 {1,2,3,#,#,4,#,#,5}
 */
TreeNode* GetTreeNode(char* str) {
	vector<char*> items = GetRangeItems(str);
	if (items.empty()) {
		return NULL;
	}
	TreeNode** tree_nodes = new TreeNode*[items.size() + 1];
	int current = 0;
	/* 当前遍历节点位置 */
	int current_pos = LEFT;
	int index = 1;
	tree_nodes[0] = new TreeNode(GetInt(items[0]));
	for (size_t i = 1; i < items.size(); ++i) {
		if ('#' == *items[i]) {
			if (tree_nodes[current] != NULL) {
				if (current_pos == LEFT) {
					current_pos = RIGHT;
				} else if (tree_nodes[current + 1] != NULL) {
					++current;
					current_pos = LEFT;
				}
			}
		} else {
			tree_nodes[index] = new TreeNode(GetInt(items[i]));
			if (current_pos == LEFT) {
				tree_nodes[current]->left = tree_nodes[index];
				current_pos = RIGHT;
			} else {
				tree_nodes[current]->right = tree_nodes[index];
				++current;
				current_pos = LEFT;
			}
			++index;
		}
	}

	TreeNode* ret = tree_nodes[0];
	delete[] tree_nodes;
	return ret;
}
void PrintInternal(TreeNode* root) {
	if (root == NULL) {
		printf("null");
		return;
	}
	printf("{");
	vector<TreeNode*> v;
	if (root != NULL) {
		v.push_back(root);
	}
	size_t c = 0;
	string none;
	while (c < v.size()) {
		if (c == 0) {
			printf("%d", v[c]->val);
			v.push_back(v[c]->left);
			v.push_back(v[c]->right);
		} else {
			if (v[c] == NULL) {
				none.append(",#");
			} else {
				printf("%s,%d", none.c_str(), v[c]->val);
				none.clear();
				v.push_back(v[c]->left);
				v.push_back(v[c]->right);
			}
		}
		++c;
	}
	printf("}");
}
void Release(TreeNode* root) {
	if (root == NULL) {
		return;
	}
	set<TreeNode*> nodes_set;
	vector<TreeNode*> nodes;
	nodes.push_back(root);
	nodes_set.insert(root);
	for (size_t i = 0; i < nodes.size(); ++i) {
		if (nodes[i]->left
				&& nodes_set.find(nodes[i]->left) == nodes_set.end()) {
			nodes_set.insert(nodes[i]->left);
			nodes.push_back(nodes[i]->left);
		}
		if (nodes[i]->right
				&& nodes_set.find(nodes[i]->right) == nodes_set.end()) {
			nodes_set.insert(nodes[i]->right);
			nodes.push_back(nodes[i]->right);
		}
		delete nodes[i];
	}
}
DEFINE_MORE_METHODS(TreeNode*, GetTreeNode, PrintInternal)

/*二叉链接树序列化是通过按层遍历,#代表这这个节点为空节点,节点遍历以后再增加所有next节点数据,举个例子
 1->NULL
 / \
     2 ->3->NULL
 /
 4->NULL
 5->NULL

 以上二叉树会被序列化为 {[1,2,3,#,#,4,#,#,5],[#,3,#,#,#]}
 对于{[1,2,3,#,#,4,#,#,5],[#,5,#,#,#]}构造出来的链接树节点2的next指向5节点*/
TreeLinkNode* GetTreeLinkNode(char* str) {
	string tmp = string(str);
	vector<char*> all_items = GetRangeItems(str);
	// 老版本只有{1,3,34}这种格式
    bool is_newversion = all_items.size() == 2 && all_items[0][0] == '[' && all_items[1][0] == '[';
    if (!is_newversion) {
        all_items.clear();
        all_items.push_back(&tmp[0]);
        all_items.push_back(NULL);
    }
	if (all_items.empty()) {
		return NULL;
	}
	vector<char*> items = GetRangeItems(all_items[0]);
	if (items.empty()) {
		return NULL;
	}

	TreeLinkNode** tree_nodes = new TreeLinkNode*[items.size() + 1];
	map<int, TreeLinkNode*> map_nodes;
	int current = 0;
	/* 当前遍历节点位置 */
	int current_pos = LEFT;
	int index = 1;
	tree_nodes[0] = new TreeLinkNode(GetInt(items[0]));
	for (size_t i = 1; i < items.size(); ++i) {
		if ('#' == *items[i]) {
			if (tree_nodes[current] != NULL) {
				if (current_pos == LEFT) {
					current_pos = RIGHT;
				} else if (tree_nodes[current + 1] != NULL) {
					++current;
					current_pos = LEFT;
				}
			}
		} else {
			int label = GetInt(items[i]);
			tree_nodes[index] = new TreeLinkNode(label);
			map_nodes[label] = tree_nodes[index];
			if (current_pos == LEFT) {
				tree_nodes[current]->left = tree_nodes[index];
				current_pos = RIGHT;
			} else {
				tree_nodes[current]->right = tree_nodes[index];
				++current;
				current_pos = LEFT;
			}
			++index;
		}
	}

	// 连接next指针
	items = GetRangeItems(all_items[1]);
	for (size_t i = 0; i < items.size(); ++i) {
		if (*items[i] != '#') {
			map<int, TreeLinkNode*>::iterator it = map_nodes.find(
					GetInt(items[i]));
			if (it != map_nodes.end()) {
				tree_nodes[i]->next = it->second;
			}
		}
	}

	TreeLinkNode* ret = tree_nodes[0];
	delete[] tree_nodes;
	return ret;
}
void PrintInternal(TreeLinkNode* root) {
	if (root == NULL) {
		printf("null");
		return;
	}
	printf("{[");
	vector<TreeLinkNode*> v;
	vector<TreeLinkNode*> label_node_v;
	if (root != NULL) {
		v.push_back(root);
		label_node_v.push_back(root);
	}
	size_t c = 0;
	string none;
	while (c < v.size()) {
		if (c == 0) {
			printf("%d", v[c]->val);
			v.push_back(v[c]->left);
			v.push_back(v[c]->right);
		} else {
			if (v[c] == NULL) {
				none.append(",#");
			} else {
				label_node_v.push_back(v[c]);
				printf("%s,%d", none.c_str(), v[c]->val);
				none.clear();
				v.push_back(v[c]->left);
				v.push_back(v[c]->right);
			}
		}
		++c;
	}
	v.clear();
	printf("],[");
	for (size_t i = 0; i < label_node_v.size(); ++i) {
		if (i != 0) {
			printf(",");
		}
		if (label_node_v[i]->next != NULL) {
			printf("%d", label_node_v[i]->next->val);
		} else {
			printf("#");
		}
	}
	printf("]}");
}
void Release(TreeLinkNode* root) {
	if (root == NULL) {
		return;
	}
	set<TreeLinkNode*> nodes_set;
	vector<TreeLinkNode*> nodes;
	nodes.push_back(root);
	nodes_set.insert(root);
	for (size_t i = 0; i < nodes.size(); ++i) {
		if (nodes[i]->left
				&& nodes_set.find(nodes[i]->left) == nodes_set.end()) {
			nodes_set.insert(nodes[i]->left);
			nodes.push_back(nodes[i]->left);
		}
		if (nodes[i]->right
				&& nodes_set.find(nodes[i]->right) == nodes_set.end()) {
			nodes_set.insert(nodes[i]->right);
			nodes.push_back(nodes[i]->right);
		}
		delete nodes[i];
	}
}
DEFINE_MORE_METHODS(TreeLinkNode*, GetTreeLinkNode, PrintInternal)

#endif
