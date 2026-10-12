#ifndef NC_TOOLS
#define NC_TOOLS

#include <stdio.h>
#include <unistd.h>
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
#include <unordered_set>
#include <unordered_map>
using namespace std;

#define LEFT 0
#define RIGHT 1


// 重载代码里的cout
class nc200buf : public streambuf
{
public:
	nc200buf() {}
};

struct UndirectedGraphNode
{
	int label;
	vector<struct UndirectedGraphNode *> neighbors;
	UndirectedGraphNode(int x) : label(x)
	{
	}
};

struct Point
{
	int x;
	int y;
	Point() : x(0), y(0)
	{
	}
	Point(int xx, int yy)
	{
		x = xx;
		y = yy;
	}
};

struct Interval
{
	int start;
	int end;
	Interval() : start(0), end(0)
	{
	}
	Interval(int s, int e) : start(s), end(e)
	{
	}
};

struct TreeNode
{
	int val;
	struct TreeNode *left;
	struct TreeNode *right;
	TreeNode(int x) : val(x), left(NULL), right(NULL)
	{
	}
};
struct RandomListNode
{
	int label;
	struct RandomListNode *next, *random;
	RandomListNode(int x) : label(x), next(NULL), random(NULL)
	{
	}
};

struct ListNode
{
	int val;
	struct ListNode *next;
	ListNode(int x) : val(x), next(NULL)
	{
	}
};

struct TreeLinkNode
{
	int val;
	struct TreeLinkNode *left;
	struct TreeLinkNode *right;
	struct TreeLinkNode *next;
	TreeLinkNode(int x) : val(x), left(NULL), right(NULL), next(NULL)
	{
	}
};

// 是不是结束字符
bool IsBeginRange(char c)
{
	return c == '{' || c == '[' || c == '(';
}

bool IsEndRange(char c)
{
	return c == '}' || c == ']' || c == ')';
}

//
char *trimwhitespace(char *str)
{
	char *end;

	// Trim leading space
	while (isspace((unsigned char)*str))
		str++;

	if (*str == 0) // All spaces?
		return str;

	// Trim trailing space
	end = str + strlen(str) - 1;
	while (end > str && isspace((unsigned char)*end))
		end--;

	// Write new null terminator character
	end[1] = '\0';

	return str;
}

vector<char *> GetArguments(char *line)
{
	vector<char *> ret;
	int inrange = 0;
	size_t count = strlen(line);
	if (count == 0)
	{
		return ret;
	}
	char *pre_index = line;
	ret.push_back(pre_index);
	int inmao = 0;
	for (size_t i = 0; i < count; ++i)
	{
		if (IsBeginRange(line[i]) && !inmao)
		{
			++inrange;
		}
		else if (IsEndRange(line[i]) && !inmao)
		{
			--inrange;
		}
		else if (line[i] == '\"')
		{
			inmao = !inmao;
		}
		else if (line[i] == ',' && inrange == 0 && !inmao)
		{
			line[i] = '\0';
			ret.push_back(line + (i + 1));
		}
	}
	return ret;
}

// 获取集合参数到多个元素
vector<char *> GetRangeItems(char *str)
{
	if (str == NULL)
	{
		return vector<char *>();
	}
	// [x,b,t] 去掉头解析内部到变量
	char *start_p = str;
	while (!IsBeginRange(*start_p))
	{
		++start_p;
	}
	char *end_p = str + strlen(str);
	while (!IsEndRange(*end_p))
	{
		--end_p;
	}
	*end_p = '\0';
	return strlen(trimwhitespace(str)) == 0 ? vector<char *>() : GetArguments(start_p + 1);
}

// 增加vector<T> 和 vector<vector<T> >方法
#define DEFINE_MORE_METHODS(type, get_func, print_func)                 \
	vector<type> get_func##List(char *str)                              \
	{                                                                   \
		vector<type> ret;                                               \
		vector<char *> items = GetRangeItems(str);                      \
		for (size_t i = 0; i < items.size(); ++i)                       \
		{                                                               \
			ret.push_back(get_func(items[i]));                          \
		}                                                               \
		return ret;                                                     \
	}                                                                   \
	vector<vector<type>> get_func##ListList(char *str)                  \
	{                                                                   \
		vector<vector<type>> ret;                                       \
		vector<char *> items = GetRangeItems(str);                      \
		for (size_t i = 0; i < items.size(); ++i)                       \
		{                                                               \
			ret.push_back(get_func##List(items[i]));                    \
		}                                                               \
		return ret;                                                     \
	}                                                                   \
	void Print(type x)                                                  \
	{                                                                   \
		print_func(x);                                                  \
		printf("%s", "\n");                                             \
	}                                                                   \
	void PrintInternal(const vector<type> &v)                           \
	{                                                                   \
		printf("%s", "[");                                              \
		for (size_t i = 0; i < v.size(); ++i)                           \
		{                                                               \
			if (i != 0)                                                 \
			{                                                           \
				printf("%s", ",");                                      \
			}                                                           \
			print_func(v[i]);                                           \
		}                                                               \
		printf("%s", "]");                                              \
	}                                                                   \
	void Print(const vector<type> &v)                                   \
	{                                                                   \
		PrintInternal(v);                                               \
		printf("%s", "\n");                                             \
	}                                                                   \
                                                                        \
	void Print(const vector<vector<type>> &vv)                          \
	{                                                                   \
		printf("%s", "[");                                              \
		for (size_t i = 0; i < vv.size(); ++i)                          \
		{                                                               \
			if (i != 0)                                                 \
			{                                                           \
				printf("%s", ",");                                      \
			}                                                           \
			PrintInternal(vv[i]);                                       \
		}                                                               \
		printf("%s", "]\n");                                            \
	}                                                                   \
                                                                        \
	type *get_func##Array(char *str, int *arrayLength)                  \
	{                                                                   \
		vector<char *> items = GetRangeItems(str);                      \
		size_t len = items.size();                                      \
		type *ret = new type[len];                                      \
		for (size_t i = 0; i < len; ++i)                                \
		{                                                               \
			ret[i] = get_func(items[i]);                                \
		}                                                               \
		(*arrayLength) = len;                                           \
		return ret;                                                     \
	}                                                                   \
                                                                        \
	type **get_func##ArrayArray(char *str, int *rowSize, int **colSize) \
	{                                                                   \
		vector<char *> items = GetRangeItems(str);                      \
		size_t rlen = items.size();                                     \
		type **ret = new type *[rlen];                                  \
		(*rowSize) = rlen;                                              \
		(*colSize) = new int[rlen];                                     \
		for (size_t i = 0; i < rlen; ++i)                               \
		{                                                               \
			ret[i] = get_func##Array(items[i], &(*colSize)[i]);         \
		}                                                               \
		return ret;                                                     \
	}                                                                   \
                                                                        \
	void PrintInternal(type *v, int len)                                \
	{                                                                   \
		printf("%s", "[");                                              \
		for (int i = 0; i < len; ++i)                                   \
		{                                                               \
			if (i != 0)                                                 \
			{                                                           \
				printf("%s", ",");                                      \
			}                                                           \
			print_func(v[i]);                                           \
		}                                                               \
		printf("%s", "]");                                              \
	}                                                                   \
	void Print(type *a, int len)                                        \
	{                                                                   \
		PrintInternal(a, len);                                          \
		printf("%s", "\n");                                             \
	}                                                                   \
                                                                        \
	void Print(type **vv, int rowlen, int *colen)                       \
	{                                                                   \
		printf("%s", "[");                                              \
		for (int i = 0; i < rowlen; ++i)                                \
		{                                                               \
			if (i != 0)                                                 \
			{                                                           \
				printf("%s", ",");                                      \
			}                                                           \
			PrintInternal(vv[i], colen[i]);                             \
		}                                                               \
		printf("%s", "]\n");                                            \
	}

// 增加vector<T> 和 vector<vector<T> > set<T>方法
#define DEFINE_MORE_METHODS_WITH_SET(type, get_func, print_func) \
	DEFINE_MORE_METHODS(type, get_func, print_func)

int GetInt(char *str)
{
	return atoi(str);
}
void PrintInternal(int x)
{
	printf("%d", x);
}
DEFINE_MORE_METHODS_WITH_SET(int, GetInt, PrintInternal)

char *GetCharxing(char *str)
{
	if (str == NULL)
	{
		return "";
	}
	int len = strlen(str);
	// 过滤头尾到空格
	int begin = 0;
	while (str[begin] == ' ' && begin < len)
	{
		++begin;
	}

	// 过滤头尾到空格
	int end = len - 1;
	while (str[end] == ' ' && end > 0)
	{
		--end;
	}

	if (str[begin] == '"' && str[end] == '"')
	{
		str[end] = '\0';
		return str + begin + 1;
	}
	else
	{
		char t = str[end + 1];
		str[end + 1] = '\0';
		return str + begin;
	}
}
void PrintInternal(char *str)
{
	printf("\"%s\"", str);
}
DEFINE_MORE_METHODS_WITH_SET(char *, GetCharxing, PrintInternal)

float GetFloat(char *str)
{
	return atof(str);
}
void PrintInternal(float x)
{
	if (fabs(x) < 0.00000999)
	{
		printf("%.5f", 0.00000);
	}
	else
	{
		printf("%.5f", x);
	}
}
DEFINE_MORE_METHODS_WITH_SET(float, GetFloat, PrintInternal)

long GetLong(char *str)
{
	return atol(str);
}
void PrintInternal(long x)
{
	printf("%ld", x);
}
DEFINE_MORE_METHODS_WITH_SET(long, GetLong, PrintInternal)

double GetDouble(char *str)
{
	return atof(str);
}
void PrintInternal(double x)
{
	if (fabs(x) < 0.00000999)
	{
		printf("%.5lf", 0.00000);
	}
	else
	{
		printf("%.5lf", x);
	}
}
DEFINE_MORE_METHODS_WITH_SET(double, GetDouble, PrintInternal)

long long GetLongLong(char *str)
{
	return atoll(str);
}
void PrintInternal(long long x)
{
	printf("%lld", x);
}
DEFINE_MORE_METHODS_WITH_SET(long long, GetLongLong, PrintInternal)

string GetString(char *str)
{
	if (str == NULL)
	{
		return "";
	}
	int len = strlen(str);
	// 过滤头尾到空格
	int begin = 0;
	while (str[begin] == ' ' && begin < len)
	{
		++begin;
	}

	// 过滤头尾到空格
	int end = len - 1;
	while (str[end] == ' ' && end > 0)
	{
		--end;
	}

	if (str[begin] == '"' && str[end] == '"')
	{
		str[end] = '\0';
		string s = string(str + begin + 1);
		str[end] = '"';
		return s;
	}
	else
	{
		char t = str[end + 1];
		str[end + 1] = '\0';
		string s = string(str + begin);
		str[end] = t;
		return s;
	}
}
void PrintInternal(const string &s)
{
	printf("\"%s\"", s.c_str());
}
DEFINE_MORE_METHODS_WITH_SET(string, GetString, PrintInternal)

bool GetBool(char *str)
{
	if (str == NULL)
	{
		return false;
	}
	return strcmp(str, "true") == 0 ? true : false;
}
void PrintInternal(bool b)
{
	if (b)
	{
		printf("%s", "true");
	}
	else
	{
		printf("%s", "false");
	}
}
DEFINE_MORE_METHODS_WITH_SET(bool, GetBool, PrintInternal)

char GetChar(char *str)
{
	if (str == nullptr)
	{
		return '#';
	}
	while (*str == ' ')
	{
		++str;
	}
	return *str;
}
void PrintInternal(char c)
{
	printf("%c", c);
}
DEFINE_MORE_METHODS_WITH_SET(char, GetChar, PrintInternal)

Point GetPoint(char *str)
{
	vector<int> items = GetIntList(str);
	if (items.size() == 2)
	{
		return Point(items[0], items[1]);
	}
	else
	{
		return Point(0, 0);
	}
}
void PrintInternal(const Point &point)
{
	printf("(%d,%d)", point.x, point.y);
}
DEFINE_MORE_METHODS(Point, GetPoint, PrintInternal)

Interval GetInterval(char *str)
{
	vector<int> items = GetIntList(str);
	if (items.size() == 2)
	{
		return Interval(items[0], items[1]);
	}
	else
	{
		return Interval(0, 0);
	}
}
void PrintInternal(const Interval &interval)
{
	printf("[%d,%d]", interval.start, interval.end);
}
DEFINE_MORE_METHODS(Interval, GetInterval, PrintInternal)

// {1,2,3}
ListNode *GetListNode(char *str)
{
	vector<int> items = GetIntList(str);
	if (items.empty())
	{
		return NULL;
	}

	ListNode *head = new ListNode(items[0]);
	ListNode *tail = head;
	for (size_t i = 1; i < items.size(); ++i)
	{
		ListNode *cur = new ListNode(items[i]);
		tail->next = cur;
		tail = cur;
	}

	return head;
}
void PrintInternal(ListNode *head)
{
	if (head == NULL)
	{
		printf("%s", "{}");
		return;
	}
	ListNode *current = head;
	printf("%s", "{");
	while (current != NULL)
	{
		if (current == head)
		{
			printf("%d", current->val);
		}
		else
		{
			printf(",%d", current->val);
		}
		current = current->next;
	}
	printf("%s", "}");
}
void Release(ListNode *head)
{
	if (head == NULL)
	{
		return;
	}
	set<ListNode *> nodes_set;
	vector<ListNode *> nodes;
	nodes.push_back(head);
	nodes_set.insert(head);
	for (size_t i = 0; i < nodes.size(); ++i)
	{
		if (nodes[i]->next && nodes_set.find(nodes[i]->next) == nodes_set.end())
		{
			nodes_set.insert(nodes[i]->next);
			nodes.push_back(nodes[i]->next);
		}
		delete nodes[i];
	}
}
DEFINE_MORE_METHODS(ListNode *, GetListNode, PrintInternal)

/*二叉树序列化是通过按层遍历,#代表这这个节点为空节点,举个例子
 1
 / \
      2     3
 /
 4
 5

 以上二叉树会被序列化为 {1,2,3,#,#,4,#,#,5}
 */
TreeNode *GetTreeNode(char *str)
{
	vector<char *> items = GetRangeItems(str);
	if (items.empty())
	{
		return NULL;
	}
	TreeNode **tree_nodes = new TreeNode *[items.size() + 1];
	int current = 0;
	/* 当前遍历节点位置 */
	int current_pos = LEFT;
	int index = 1;
	tree_nodes[0] = new TreeNode(GetInt(items[0]));
	for (size_t i = 1; i < items.size(); ++i)
	{
		if ('#' == *trimwhitespace(items[i]))
		{
			if (tree_nodes[current] != NULL)
			{
				if (current_pos == LEFT)
				{
					current_pos = RIGHT;
				}
				else if (tree_nodes[current + 1] != NULL)
				{
					++current;
					current_pos = LEFT;
				}
			}
		}
		else
		{
			tree_nodes[index] = new TreeNode(GetInt(items[i]));
			if (current_pos == LEFT)
			{
				tree_nodes[current]->left = tree_nodes[index];
				current_pos = RIGHT;
			}
			else
			{
				tree_nodes[current]->right = tree_nodes[index];
				++current;
				current_pos = LEFT;
			}
			++index;
		}
	}

	TreeNode *ret = tree_nodes[0];
	delete[] tree_nodes;
	return ret;
}
void PrintInternal(TreeNode *root)
{
	if (root == NULL)
	{
		printf("%s", "{}");
		return;
	}
	printf("%s", "{");
	vector<TreeNode *> v;
	if (root != NULL)
	{
		v.push_back(root);
	}
	size_t c = 0;
	string none;
	while (c < v.size())
	{
		if (c == 0)
		{
			printf("%d", v[c]->val);
			v.push_back(v[c]->left);
			v.push_back(v[c]->right);
		}
		else
		{
			if (v[c] == NULL)
			{
				none.append(",#");
			}
			else
			{
				printf("%s,%d", none.c_str(), v[c]->val);
				none.clear();
				v.push_back(v[c]->left);
				v.push_back(v[c]->right);
			}
		}
		++c;
	}
	printf("%s", "}");
}
void Release(TreeNode *root)
{
	if (root == NULL)
	{
		return;
	}
	set<TreeNode *> nodes_set;
	vector<TreeNode *> nodes;
	nodes.push_back(root);
	nodes_set.insert(root);
	for (size_t i = 0; i < nodes.size(); ++i)
	{
		if (nodes[i]->left && nodes_set.find(nodes[i]->left) == nodes_set.end())
		{
			nodes_set.insert(nodes[i]->left);
			nodes.push_back(nodes[i]->left);
		}
		if (nodes[i]->right && nodes_set.find(nodes[i]->right) == nodes_set.end())
		{
			nodes_set.insert(nodes[i]->right);
			nodes.push_back(nodes[i]->right);
		}
		delete nodes[i];
	}
}
DEFINE_MORE_METHODS(TreeNode *, GetTreeNode, PrintInternal)

#endif
