#ifndef TOOLS
#define TOOLS

#include <stdio.h>
#include <algorithm>
#include <bitset>
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
#include <unordered_set>
#include <unordered_map>
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

char* split(char** t, char c) {
	char* s = *t;
	if (s == NULL || *s == '\0') {
		return NULL;
	}

	char* p = s;
	while (*p != '\0' && *p != c) {
		++p;
	}
	if (*p == c) {
		*t = p + 1;
	} else {
		*t = NULL;
	}
	*p = '\0';
	return s;
}

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

vector<char*> GetArguments(char* line, int arg_count) {
	vector<char*> ret;
	int inrange = 0;
	size_t count = strlen(line);
	char* pre_index = line;
	ret.push_back(pre_index);
	int inmao = 0;
	for (size_t i = 0; i < count; ++i) {
		if (line[i] == '[' || line[i] == '{') {
			++inrange;
		} else if (line[i] == ']' || line[i] == '}') {
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

// {a,b,c} [1,3,4] [] {a} [{a,c},{d,e}]
int GetListItemCount(char* str) {
	if (str == NULL) {
		return 0;
	}
	if (strcmp(str, "[]") == 0 || strcmp(str, "{}") == 0) {
		return 0;
	}
	int count = 1;
	char* p = str;
	int inrange = 0;
	int inmao = 0;
	// 判断最多有多少个节点
	/*while (*p) {
		if (*p == ',') {
			++count;
		} else if (*p == ']' && *(p - 1) != '[') {
			++count;
		} else if (*p == '}' && *(p - 1) != '{') {
			++count;
		}
		++p;
	}*/
	while (*p) {
		if (*p == ',' && inrange == 1 && !inmao) {
			++count;
		} else if (*p == ']' || *p == '}') {
			--inrange;
		} else if (*p == '[' || *p == '{') {
			++inrange;
		} else if (*p == '\"') {
			inmao = !inmao;
		}
		++p;
	}
	return count;
}

// 1
int GetInt(char* str) {
	return atoi(str);
}

// 支持[1,2,3,-4,5]
// [,,] -> 空
// [] -> 空
vector<int> GetVectorInt(char* str) {
	vector<int> ret;
	char* p = str;
	char* start_p = p;
	while (*p) {
		if (*start_p == '[' || *start_p == ' ') {
			++start_p;
		}
		if ((*p == ',' || *p == ']') && start_p != p) {
			char t = *p;
			*p = '\0';
			ret.push_back(GetInt(start_p));
			*p = t;
			start_p = p + 1;
		}
		++p;
	}
	return ret;
}

double GetDouble(char* str) {
	return atof(str);
}

// 支持[1,2,3,-4,5]
// [,,] -> 空
// [] -> 空
vector<double> GetVectorDouble(char* str) {
	vector<double> ret;
	char* p = str;
	char* start_p = p;
	while (*p) {
		if (*start_p == '[' || *start_p == ' ') {
			++start_p;
		}
		if ((*p == ',' || *p == ']') && start_p != p) {
			char t = *p;
			*p = '\0';
			ret.push_back(GetDouble(start_p));
			*p = t;
			start_p = p + 1;
		}
		++p;
	}
	return ret;
}

//  [a,b,c,d,e]
// [ ]->有个空格的char
vector<char> GetVectorChar(char* str) {
	vector<char> ret;
	// 预估大概是一半的长度
	ret.reserve(strlen(str) / 2);
	char* p = str;
	while (*p) {
		if (*p != ']' && *p != '[' && *p != ',') {
			ret.push_back(*p);
		}
		++p;
	}
	return ret;
}


// "aaa"
string GetString(char* str) {
	if (str == NULL) {
		return "";
	}
	size_t len = strlen(str);
	if (str[0] == '"' && str[len-1] == '"') {
		str[len-1] = '\0';
		string s = string(str + 1);
		str[len-1] = '"';
		return s;
	} else {
		return string(str);
	}
}


//["abc","def","","kk"]
vector<string> GetVectorString(char* str) {
	vector<string> ret;
	int count = GetListItemCount(str);
	if (count == 0) {
		return ret;
	}
	char* p = str;
	char* start_p = p;
	// 过滤前面的空格
	while (*start_p != '[') {
		++start_p;
	}
	++start_p;
	int inmao = 0;
	while (*p) {
		if (*p == ']' || (*p == ',' && !inmao)) {
			char t = *p;
			*p = '\0';
			ret.push_back(GetString(start_p));
			*p = t;
			start_p = p + 1;
		} else if (*p == '\"') {
			inmao = !inmao;
		}
		++p;
	}
	return ret;
}

//[["z","ed","kk"],["ab","dd","zz"]]
vector<vector<string> > GetVVectorString(char* str) {
	// 根据，分割成多个[],然后生成多个vector
	vector<vector<string> > ret;
	if (GetListItemCount(str) == 0) {
		return ret;
	}
	char* p = str;
	char* start_p = p;
	int inrange = 0;
	while (*p) {

		if (*p == '[') {
			++inrange;
			if (inrange == 2) {
				start_p = p;
			}
		} else if (*p == ']') {
			--inrange;
		}

		if ((*p == ',' && inrange == 1) || (*p == ']' && inrange == 0)){
			char t = *p;
			*p = '\0';
			ret.push_back(GetVectorString(start_p));
			*p = t;
		}

		++p;
	}
	return ret;
}

//[ [ 1 , 2 ] ,[ 3 , 4 , -6 ] ]
vector<vector<int> > GetVVectorInt(char* str) {
	// 根据，分割成多个[],然后生成多个vector
	vector<vector<int> > ret;
	if (GetListItemCount(str) == 0) {
		return ret;
	}
	char* p = str;
	char* start_p = p;
	int inrange = 0;
	while (*p) {

		if (*p == '[') {
			++inrange;
			if (inrange == 2) {
				start_p = p;
			}
		} else if (*p == ']') {
			--inrange;
		}

		if ((*p == ',' && inrange == 1) || (*p == ']' && inrange == 0)){
			char t = *p;
			*p = '\0';
			ret.push_back(GetVectorInt(start_p));
			*p = t;
		}

		++p;
	}
	return ret;
}

//[aa,bb,cc]
vector<vector<char> > GetVVectorChar(char* str) {
	vector<string> vs = GetVectorString(str);
	vector<vector<char> > ret;
	for (size_t i = 0; i < vs.size(); ++i) {
		vector<char> vc;
		vc.reserve(vs[i].size());
		for (size_t j = 0; j < vs[i].size(); ++j) {
			vc.push_back(vs[i][j]);
		}
		ret.push_back(vc);
	}
	return ret;
}

//"aaa"
char* GetChar(char* str) {
	if (str == NULL) {
		return NULL;
	}
	size_t len = strlen(str);
	if (str[0] == '"' && str[len-1] == '"') {
		str[len-1] = '\0';
		return str + 1;
	} else {
		return str;
	}
}
/*

 Nodes are labeled uniquely.
 We use # as a separator for each node, and , as a separator for node label and each neighbor of the node.

 As an example, consider the serialized graph {0,1,2#1,2#2,2}.

 The graph has a total of three nodes, and therefore contains three parts as separated by #.

 First node is labeled as 0. Connect node 0 to both nodes 1 and 2.
 Second node is labeled as 1. Connect node 1 to node 2.
 Third node is labeled as 2. Connect node 2 to node 2 (itself), thus forming a self-cycle.

 Visually, the graph looks like the following:

	   1
	  / \
     /   \
    0 --- 2
         / \
         \_/
 {0,1,2#1,2#2,2}.
 */
struct UndirectedGraphNode* GetUndirectedGraphNode(char* str) {
	vector<int> tmp;
	vector<vector<int> > points;
	char* p = str;
	char* start_p = p;
	while (*p) {
		if (*start_p == '{' || *start_p == ' ') {
			++start_p;
		}
		if ((*p == ',' || *p == '}' || *p == '#') && start_p != p) {
			char t = *p;
			*p = '\0';
			tmp.push_back(atoi(start_p));
			*p = t;

			if (*p == '#' || *p == '}') {
				points.push_back(tmp);
				tmp.clear();
			}
			start_p = p + 1;
		}
		++p;
	}

	struct UndirectedGraphNode* ret = NULL;
	map<int, struct UndirectedGraphNode*> nodes_map;

	// 把所有的点构造出来
	for (size_t i = 0; i < points.size(); ++i) {
		const vector<int>& v = points[i];
		if (v.empty()) {
			continue;
		}
		if (nodes_map.find(v[0]) == nodes_map.end()) {
			struct UndirectedGraphNode* node = new UndirectedGraphNode(v[0]);
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
		struct UndirectedGraphNode* node = nodes_map[v[0]];
		for (size_t j = 1; j < v.size(); ++j) {
			node->neighbors.push_back(nodes_map[v[j]]);
		}
	}
	return ret;
}

// [1,3] (1,3)
struct Interval GetInterval(char* str) {
	struct Interval ret;
	char* p = str;
	char* start_p = p;
	while (*start_p == '[' || *start_p == ' ' || *start_p == '(') {
		++start_p;
	}
	while (*p && *p != ',') {
		++p;
	}
	*p = '\0';
	ret.start = atoi(start_p);
	ret.end = atoi(p + 1);
	return ret;
}

// [[1,2],[3,4],[5,6]]
vector<struct Interval> GetVectorInterval(char* str) {
	vector<Interval> ret;
	if (GetListItemCount(str) == 0) {
		return ret;
	}
	char* p = str;
	char* start_p = p;
	int inrange = 0;
	while (*p) {
		if (*p == '[') {
			++inrange;
			if (inrange == 2) {
				start_p = p;
			}
		} else if (*p == ']') {
			--inrange;
		}

		if ((*p == ',' && inrange == 1) || (*p == ']' && inrange == 0)){
			char t = *p;
			*p = '\0';
			ret.push_back(GetInterval(start_p));
			*p = t;
		}

		++p;
	}
	return ret;
}

// {1,2,3}
struct ListNode* GetListNode(char* str) {
	if (str == NULL)
		return NULL;
	int count = GetListItemCount(str);
	if (count == 0) {
		return NULL;
	}
	char* p = str;
	char* start_p = p;
	int index = 0;

	while (*start_p != '{') {
		++start_p;
	}
	++start_p;

	struct ListNode** list_nodes = new ListNode*[count + 1];
	while (*p) {
		if (*p == ',' || *p == '}') {
			char t = *p;
			*p = '\0';
			list_nodes[index] = new ListNode(atoi(start_p));
			if (index > 0) {
				list_nodes[index - 1]->next = list_nodes[index];
			}
			++index;
			*p = t;
			start_p = p + 1;
		}
		++p;
	}

	struct ListNode* ret = list_nodes[0];
	delete[] list_nodes;
	return ret;
}

//[{1,2,3},{1,2}]
vector<struct ListNode*> GetVectorListNode(char* str) {
	vector<struct ListNode*> ret;
	if (GetListItemCount(str) == 0) {
		return ret;
	}
	char* p = str;
	char* start_p = p;
	int inrange = 0;
	while (*p) {
		if (*p == '[') {
			++inrange;
		} else if (*p == ']') {
			--inrange;
		}

		if (*p == '}' && inrange == 1) {
			char t = *(p + 1);
			*(p + 1) = '\0';
			ret.push_back(GetListNode(start_p));
			*(p + 1) = t;
			start_p = p + 1;
		}

		if (*start_p != '{') {
			++start_p;
		}
		++p;
	}
	return ret;
}

// { -1, 8, 7,  -3,4,4,-3,#,#,-1}
// 分为两段，前部分为ListNode,后半部分如果random==NULL是#，否则就是random.val
struct RandomListNode* GetRandomListNode(char* str) {
	map<int, RandomListNode*> nodes_map;
	// 先统计总共有多少个元素
	int count = GetListItemCount(str);
	if (count == 0) {
		return NULL;
	}
	count = count / 2;
	char* p = str;
	char* start_p = p;

	int index = 0;
	struct RandomListNode** list_nodes = new struct RandomListNode*[count + 1];
	while (*p) {
		if (*start_p == ' ' || *start_p == '{') {
			++start_p;
		}

		if (*p == ',' || *p == '}') {
			if (start_p == p) {
				// 忽略空的段 {1,,2}->1,2
				++start_p;
				++p;
			} else {
				*p = '\0';
				if (index < count) {
					list_nodes[index] = new RandomListNode(atoi(start_p));
					nodes_map[list_nodes[index]->label] = list_nodes[index];
					if (index > 0) {
						list_nodes[index - 1]->next = list_nodes[index];
					}
				} else {
					// random 指针
					if (strcmp(start_p, "#") != 0) {
						map<int, RandomListNode*>::iterator iter =
								nodes_map.find(atoi(start_p));
						if (iter != nodes_map.end()) {
							list_nodes[index - count]->random = iter->second;
						}
					}
				}
				++index;
				start_p = p + 1;
				p = start_p;
			}
		} else {
			++p;
		}
	}
	struct RandomListNode* root = list_nodes[0];
	delete[] list_nodes;
	return root;
}

struct TreeLinkNode* GetTreeLinkNode(char* str) {
	if (str == NULL)
		return NULL;
	int count = GetListItemCount(str);
	if (count == 0) {
		return NULL;
	}
	char* p = str;
	char* start_p = str;

	struct TreeLinkNode** tree_nodes = new struct TreeLinkNode*[count + 1];
	/* 当前遍历节点 */
	int current = 0;
	/* 当前遍历节点位置 */
	int current_pos = 0;
	int index = 0;
	while (*p) {
		if (*start_p == ' ' || *start_p == '{') {
			++start_p;
		}

		if (*p == '}' || *p == ',') {
			char t = *p;
			*p = '\0';

			if (*start_p == '#') {
				if (tree_nodes[current] != NULL) {
					if (current_pos == LEFT) {
						current_pos = RIGHT;
					} else if (tree_nodes[current + 1] != NULL) {
						++current;
						current_pos = LEFT;
					}
				}
			} else {
				tree_nodes[index] = new TreeLinkNode(atoi(start_p));

				/* 第一个节点 */
				if (index == 0) {
					current = 0;
					current_pos = LEFT;
				} else {
					if (current_pos == LEFT) {
						tree_nodes[current]->left = tree_nodes[index];
						current_pos = RIGHT;
					} else {
						tree_nodes[current]->right = tree_nodes[index];
						++current;
						current_pos = LEFT;
					}
				}

				++index;
			}
			*p = t;
			start_p = p + 1;
		}

		++p;
	}

	struct TreeLinkNode* ret = tree_nodes[0];
	delete[] tree_nodes;
	return ret;
}

// [(1,2),(1,3)]
vector<struct Point> GetVectorPoint(char* str) {
	vector<struct Point> ret;
	if (GetListItemCount(str) == 0) {
		return ret;
	}
	char* p = str;
	char* start_p = p;
	int inrange = 0;
	while (*p) {
		if (*p == '[') {
			++inrange;
		} else if (*p == ']') {
			--inrange;
		}

		if (*p == ')' && inrange == 1) {
			char t = *(p + 1);
			*(p + 1) = '\0';
			struct Interval interval = GetInterval(start_p);
			struct Point point = { interval.start, interval.end };
			ret.push_back(point);
			*(p + 1) = t;
			start_p = p + 1;
		}

		if (*start_p != '(' || inrange != 1) {
			++start_p;
		}
		++p;
	}
	return ret;
}

// [aaa,dd,fff,,dfd]
unordered_set<string> GetUnorderedSetString(char* str) {
	unordered_set<string> ret;
	char* p = str;
	char* start_p = p;
	while (*start_p != '[') {
		++start_p;
	}
	++start_p;
	while (*p) {
		if (*p == ']' || *p == ',') {
			char t = *p;
			*p = '\0';
			ret.insert(GetString(start_p));
			*p = t;
			start_p = p + 1;
		}
		++p;
	}
	return ret;
}

void Print(int x) {
	printf("%d\n", x);
}

void Print(struct TreeLinkNode* root) {
	printf("{");
	vector<struct TreeLinkNode*> v;
	if (root != NULL) {
		v.push_back(root);
	}
	size_t c = 0;
	string none;
	while (c < v.size()) {
		if (c == 0) {
			printf("%d,#", v[c]->val);
			v.push_back(v[c]->left);
			v.push_back(v[c]->right);
		} else {
			if (v[c] != NULL) {
				if (v[c]->next != NULL) {
					printf("%s,%d", none.c_str(), v[c]->val);
				} else {
					printf("%s,%d,#", none.c_str(), v[c]->val);
				}

				none.clear();
				v.push_back(v[c]->left);
				v.push_back(v[c]->right);
			}
		}
		++c;
	}
	printf("}\n");
}

void PrintTreeNode(struct TreeNode* root) {
	printf("{");
	vector<struct TreeNode*> v;
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

void Print(struct TreeNode* root) {
	PrintTreeNode(root);
	printf("\n");
}

void PrintListNode(struct ListNode* head) {
	struct ListNode* current = head;
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

void Print(const struct Interval& interval) {
	printf("[%d,%d]\n", interval.start, interval.end);
}

void Print(struct ListNode* head) {
	PrintListNode(head);
	printf("\n");
}

void Print(struct UndirectedGraphNode* root) {
	printf("{");
	if (root != NULL) {
		set<struct UndirectedGraphNode*> nodes_set;
		map<int, struct UndirectedGraphNode*> nodes_map;
		vector<struct UndirectedGraphNode*> nodes;
		nodes.push_back(root);
		nodes_set.insert(root);
		nodes_map[root->label] = root;
		for (size_t i = 0; i < nodes.size(); ++i) {
			for (size_t j = 0; j < nodes[i]->neighbors.size(); ++j) {
				struct UndirectedGraphNode* n_node = nodes[i]->neighbors[j];
				if (nodes_set.find(n_node) == nodes_set.end()) {
					nodes_set.insert(n_node);
					nodes.push_back(n_node);
					nodes_map[n_node->label] = n_node;
				}
			}
		}

		// 根据label从小到大打印
		for (map<int, struct UndirectedGraphNode*>::iterator it = nodes_map.begin(); it != nodes_map.end(); ++it) {
			struct UndirectedGraphNode* node = it->second;
			if (it != nodes_map.begin()) {
				printf("#%d", node->label);
			} else {
				printf("%d", node->label);
			}
			for (size_t j = 0; j < node->neighbors.size(); ++j) {
				printf(",%d", node->neighbors[j]->label);
			}
		}

	}
	printf("}\n");
}

void Print(struct RandomListNode* head) {
	struct RandomListNode* current = head;
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
	printf("}\n");
}

void Print(const string& s) {
	printf("\"%s\"\n", s.c_str());
}

void Print(char* str) {
	if (str) {
		printf("\"%s\"\n", str);
	} else {
		printf("null\n");
	}
}

void Print(bool b) {
	if (b) {
		printf("true\n");
	} else {
		printf("false\n");
	}
}

void Print(double d) {
	printf("%.05lf\n", d);
}

void PrintVector(const vector<int>& x) {
	printf("[");
	for (size_t i = 0; i < x.size(); ++i) {
		if (i != 0) {
			printf(",");
		}
		printf("%d", x[i]);
	}
	printf("]");
}

void PrintVector(const vector<char>& x) {
	printf("[");
	for (size_t i = 0; i < x.size(); ++i) {
		if (i != 0) {
			printf(",");
		}
		printf("%c", x[i]);
	}
	printf("]");
}

void PrintVector(const vector<string>& x) {
	printf("[");
	for (size_t i = 0; i < x.size(); ++i) {
		if (i != 0) {
			printf(",\"%s\"", x[i].c_str());
		} else {
			printf("\"%s\"", x[i].c_str());
		}
	}
	printf("]");
}

void Print(const vector<int>& x) {
	PrintVector(x);
	printf("\n");
}

void Print(const vector<char>& x) {
	PrintVector(x);
	printf("\n");
}

void Print(const vector<struct Interval>& x) {
	printf("[");
	for (size_t i = 0; i < x.size(); ++i) {
		if (i != 0) {
			printf(",");
		}
		printf("[%d,%d]", x[i].start, x[i].end);
	}
	printf("]\n");
}

void Print(const vector<string>& x) {
	PrintVector(x);
	printf("\n");
}

void Print(const vector<vector<string> > vvs) {
	printf("[");
	for (size_t i = 0; i < vvs.size(); ++i) {
		if (i != 0) {
			printf(",");
		}
		PrintVector(vvs[i]);
	}
	printf("]\n");
}

void Print(const vector<vector<int> >& vv) {
	printf("[");
	for (size_t i = 0; i < vv.size(); ++i) {
		if (i != 0) {
			printf(",");
		}
		PrintVector(vv[i]);
	}
	printf("]\n");
}

void Print(const vector<vector<char> >& vv) {
	printf("[");
	for (size_t i = 0; i < vv.size(); ++i) {
		if (i != 0) {
			printf(",");
		}
		const vector<char>& v = vv[i];
		for (size_t j = 0; j < v.size(); ++j) {
			printf("%c", v[j]);
		}
	}
	printf("]\n");
}

void Print(const vector<struct TreeNode*> & v) {
	printf("[");
	for (size_t i = 0; i < v.size(); ++i) {
		if (i != 0) {
			printf(",");
		}
		PrintTreeNode(v[i]);
	}
	printf("]\n");
}

void Print(int A[], size_t num) {
	printf("[");
	for (size_t i = 0; i < num; ++i) {
		if (i == 0) {
			printf("%d", A[i]);
		} else {
			printf(",%d", A[i]);
		}
	}
	printf("]\n");
}

void Print(vector<int>& A, size_t num) {
	Print(&A[0], num);
}

void Print(const vector<struct ListNode*> & v) {
	printf("[");
	for (size_t i = 0; i < v.size(); ++i) {
		if (i != 0) {
			printf(",");
		}
		PrintListNode(v[i]);
	}
	printf("]\n");
}

/*
 The serialization of a binary tree follows a level order traversal, where '#'
 signifies a path terminator where no node exists below.

 Here's an example:

 1
 / \
2   3
 /
 4
 5

 The above binary tree is serialized as "{1,2,3,#,#,4,#,#,5}".
 */
struct TreeNode* GetTreeNode(char* str) {
	if (str == NULL)
		return NULL;
	int count = GetListItemCount(str);
	if (count == 0) {
		return NULL;
	}
	char* p = str;
	char* start_p = str;

	struct TreeNode** tree_nodes = new struct TreeNode*[count + 1];
	/* 当前遍历节点 */
	int current = 0;
	/* 当前遍历节点位置 */
	int current_pos = 0;
	int index = 0;
	while (*p) {
		if (*start_p == ' ' || *start_p == '{') {
			++start_p;
		}

		if (*p == '}' || *p == ',') {
			char t = *p;
			*p = '\0';

			if (*start_p == '#') {
				if (tree_nodes[current] != NULL) {
					if (current_pos == LEFT) {
						current_pos = RIGHT;
					} else if (tree_nodes[current + 1] != NULL) {
						++current;
						current_pos = LEFT;
					}
				}
			} else {
				tree_nodes[index] = new TreeNode(atoi(start_p));

				/* 第一个节点 */
				if (index == 0) {
					current = 0;
					current_pos = LEFT;
				} else {
					if (current_pos == LEFT) {
						tree_nodes[current]->left = tree_nodes[index];
						current_pos = RIGHT;
					} else {
						tree_nodes[current]->right = tree_nodes[index];
						++current;
						current_pos = LEFT;
					}
				}

				++index;
			}
			*p = t;
			start_p = p + 1;
		}

		++p;
	}

	struct TreeNode* ret = tree_nodes[0];
	delete[] tree_nodes;
	return ret;
}

void Release(struct TreeNode* root) {
	if (root == NULL)
		return;
	set<struct TreeNode*> nodes_set;
	vector<struct TreeNode*> nodes;
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

void Release(struct ListNode* head) {
	if (head == NULL)
		return;
	set<struct ListNode*> nodes_set;
	vector<struct ListNode*> nodes;
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

void Release(struct RandomListNode* head) {
	if (head == NULL)
		return;
	set<struct RandomListNode*> nodes_set;
	vector<struct RandomListNode*> nodes;
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

void Release(struct TreeLinkNode* root) {
	if (root == NULL)
		return;
	set<struct TreeLinkNode*> nodes_set;
	vector<struct TreeLinkNode*> nodes;
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

void Release(struct UndirectedGraphNode* root) {
	if (root == NULL)
		return;
	map<int, struct UndirectedGraphNode*> nodes_map;
	vector<struct UndirectedGraphNode*> v;
	v.push_back(root);
	nodes_map[root->label] = root;
	for (size_t i = 0; i < v.size(); ++i) {
		vector<struct UndirectedGraphNode*>& neighbors = v[i]->neighbors;
		nodes_map[v[i]->label] = v[i];
		for (size_t j = 0; j < neighbors.size(); ++j) {
			if (nodes_map.find(neighbors[j]->label) == nodes_map.end()) {
				nodes_map[neighbors[j]->label] = neighbors[j];
				v.push_back(neighbors[j]);
			}
		}
	}

	// 删除所有的节点
	for (map<int, struct UndirectedGraphNode*>::iterator it = nodes_map.begin();
			it != nodes_map.end(); ++it) {
		delete it->second;
	}
}

#endif
