#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
using namespace std;

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
		--end;
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

vector<string> GetStringList(char* str) {
    vector<string> ret;
    vector<char*> items = GetRangeItems(str);
    for (size_t i = 0; i < items.size(); ++i) {
            ret.push_back(GetString(items[i]));
    }
    return ret;
}

vector<vector<string> > GetStringListList(char* str) {
    vector<vector<string> > ret;
    vector<char*> items = GetRangeItems(str);
    for (size_t i = 0; i < items.size(); ++i) {
            ret.push_back(GetStringList(items[i]));
    }
    return ret;
}

char GetChar(char* str) {
	if(str == nullptr){
		return '#';
	}
	while (*str == ' ') {
		++str;
	}
	return *str;
}

vector<char> GetCharList(char* str) {
    vector<char> ret;
    vector<char*> items = GetRangeItems(str);
    for (size_t i = 0; i < items.size(); ++i) {
            ret.push_back(GetChar(items[i]));
    }
    return ret;
}

vector<vector<char> > GetCharListList(char* str) {
    vector<vector<char> > ret;
    vector<char*> items = GetRangeItems(str);
    for (size_t i = 0; i < items.size(); ++i) {
            ret.push_back(GetCharList(items[i]));
    }
    return ret;
}

PYBIND11_MODULE(ncpy_link_module, m)
{
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("GetArguments", &GetArguments, "A function which adds two numbers");
    m.def("GetRangeItems", &GetRangeItems, "A function which adds two numbers");

    m.def("GetString", &GetString, "A function which adds two numbers");
    m.def("GetStringList", &GetStringList, "A function which adds two numbers");
    m.def("GetStringListList", &GetStringListList, "A function which adds two numbers");

    m.def("GetChar", &GetChar, "A function which adds two numbers");
    m.def("GetCharList", &GetCharList, "A function which adds two numbers");
    m.def("GetCharListList", &GetCharListList, "A function which adds two numbers");

}

//mac 编译命令: c++ -O3 -Wall -shared -std=c++11 -undefined dynamic_lookup `python -m pybind11 --includes` ncpy_link_module.cpp -o ncpy_link_module.so
//mac 编译命令: c++ -O3 -Wall -shared -std=c++11 -undefined dynamic_lookup `python3 -m pybind11 --includes` ncpy_link_module.cpp -o ncpy_link_module`python3-config --extension-suffix` 