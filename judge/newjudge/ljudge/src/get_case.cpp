#include <iostream>
#include <fstream>
#include <string>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <stdint.h>
#include <errno.h>
#include <sys/stat.h>
#include <vector>

using namespace std;

//显示的最长的行数
#define MAX_LINE 200000

//前台最大显示为60000，减去50固定长度，再除以3
const int MAX_PRINT_SIZE = 20983;

#define INPUT "input"
#define OUTPUT "output"
#define USER_OUTPUT "user_output"
#define SLICE "slice"

class TextFileReader
{
public:
    TextFileReader(const string &filename);
    ~TextFileReader();

    // Returns the next character in the file. Returns 0 if EOF is reached, -1 if any error occurs.
    int Read();

    // Returns the next non-white-space character. Returns 0 if EOF is
    // reached, -1 if any error occurs.
    int SkipWhiteSpaces();

    // Returns true if fail to open the file
    int Fail();

    int Readn(int fd, void *buffer, size_t count);

private:
    // Returns the next character in the file, but do not forward the pointer.
    // Returns 0 if EOF is reached, -1 if any error occurs.
    int Next();

    // the file descriptor
    int fd_;

    // A internal buffer used to store unread characters
    unsigned char buffer_[1024];

    // The number of available characters in the buffer
    size_t buffer_size_;

    // A pointer pointing to the next available character in the buffer
    unsigned char *ptr_;

    // the filename associated with this instance
    const string filename_;
};

TextFileReader::TextFileReader(const string &filename) : filename_(filename)
{
    fd_ = open(filename.c_str(), O_RDONLY);
    if (fd_ < 0)
    {
        cerr << "Fail to open " << filename;
    }
    buffer_size_ = sizeof(buffer_);
    ptr_ = buffer_ + buffer_size_;
}

TextFileReader::~TextFileReader()
{
    if (fd_ >= 0)
    {
        close(fd_);
    }
}

int TextFileReader::Read()
{
    if (fd_ < 0)
    {
        return -1;
    }
    int ret = Next();
    if (ret > 0)
    {
        ++ptr_;
    }
    if (ret != '\r')
    {
        return ret;
    }

    // Treat \r\n as \n
    int t = Next();
    if (t == '\n')
    {
        ++ptr_;
    }
    return '\n';
}

int TextFileReader::SkipWhiteSpaces()
{
    int ret;
    do
    {
        ret = Read();
    } while (ret > 0 && isspace(ret) && ret != '\n');
    return ret;
}

int TextFileReader::Fail()
{
    return fd_ < 0;
}

int TextFileReader::Next()
{
    if (ptr_ - buffer_ >= buffer_size_)
    {
        if (buffer_size_ < sizeof(buffer_))
        {
            // The previous Readn returns less characters than requested, which means EOF is reached.
            // It is not necessary to invoke it again.
            return 0;
        }
        buffer_size_ = Readn(fd_, buffer_, sizeof(buffer_));
        if ((int)buffer_size_ < 0)
        {
            cerr << "Fail to read from " << filename_;
            return -1;
        }
        if (buffer_size_ == 0)
        {
            return 0;
        }
        ptr_ = buffer_;
    }
    return *ptr_;
}

int TextFileReader::Readn(int fd, void *buffer, size_t count)
{
    char *p = (char *)buffer;
    while (count > 0)
    {
        ssize_t num = read(fd, p, count);
        if (num == -1)
        {
            if (errno == EINTR)
            {
                // interrupted by a signals, read again
                continue;
            }
            cerr << "Fail to read from file";
            return -1;
        }
        if (num == 0)
        {
            // EOF
            break;
        }
        p += num;
        count -= num;
    }
    return p - (char *)buffer;
}

int get_diff_line(string useroutput, string caseoutput, int *line_no)
{
    //0 for ACCEPTED, 1 for WRONG_ANSWER and 2 for PRESENTATION_ERROR.
    int ret = 0;
    TextFileReader f1(caseoutput), f2(useroutput);
    if (f1.Fail() || f2.Fail())
    {
        return -1;
    }
    *line_no = 1;
    for (;;)
    {
        // Find the first non-space character at the beginning of line.
        // Blank lines are skipped.
        int c1 = f1.Read();
        int c2 = f2.Read();
        while (isspace(c1) || isspace(c2))
        {
            if (c1 != c2)
            {
                if (c1 == '\n' && (isspace(c2) || !c2))
                {
                    //多输出换行不算pe
                }
                else if (c2 == '\n' && (isspace(c1) || !c1))
                {
                    //多输出换行不算pe
                }
                else
                {
                    ret = 2;
                }
            }
            if (isspace(c1))
            {
                if (c1 == '\n')
                {
                    *line_no = *line_no + 1;
                }
                c1 = f1.Read();
            }
            if (isspace(c2))
            {
                c2 = f2.Read();
            }
            //cout << "Bc1:" << c1 << ",c2:" << c2 << "," << *line_no << endl;
        }
        // Compare the current line.
        for (;;)
        {
            // Read until 2 files return a space or 0 together.
            while ((!isspace(c1) && c1) || (!isspace(c2) && c2))
            {
                if (c1 < 0 || c2 < 0)
                {
                    return -1;
                }
                if (c1 != c2)
                {
                    // Consecutive non-space characters should be all exactly the same
                    return 1;
                }

                if (c1 == '\n')
                {
                    *line_no = *line_no + 1;
                }
                c1 = f1.Read();
                c2 = f2.Read();
            }
            // Find the next non-space character or \n.
            while ((isspace(c1) && c1 != '\n') || (isspace(c2) && c2 != '\n'))
            {
                if (c1 != '\n' && c1 != c2)
                {
                    ret = 2;
                }
                if (isspace(c1) && c1 != '\n')
                {
                    c1 = f1.Read();
                }
                if (isspace(c2) && c2 != '\n')
                {
                    c2 = f2.Read();
                }
            }
            if (c1 < 0 || c2 < 0)
            {
                return -1;
            }
            if (!c1 && !c2)
            {
                return ret;
            }
            if ((c1 == '\n' || !c1) && (c2 == '\n' || !c2))
            {
                break;
            }
        }
        if (c1 == '\n')
        {
            *line_no = *line_no + 1;
        }
    }
    return ret;
}

void find_in_slice(ifstream &slice, int &line_no, int &input_start_line, int &input_end_line, int &output_start_line, int &output_end_line, int &thisfile_case_count, int &right_case_count, bool &has_slice)
{
    int tmp_input_start_line = 0, tmp_input_end_line = 0, tmp_output_start_line = 0, tmp_output_end_line = 0;
    //保存前一行的数据，如果没有找到对应行的话，采用前一行的数据
    int former_input_start_line = 0, former_input_end_line = 0, former_output_start_line = 0, former_output_end_line = 0;
    bool find = false;
    while (slice >> tmp_input_start_line >> tmp_input_end_line >> tmp_output_start_line >> tmp_output_end_line)
    {
        if (tmp_output_start_line <= line_no && tmp_output_end_line >= line_no)
        {
            // 找到出错行对应的测试用例范围
            input_start_line = tmp_input_start_line;
            input_end_line = tmp_input_end_line;
            output_start_line = tmp_output_start_line;
            output_end_line = tmp_output_end_line;
            find = true;
        }
        else if (tmp_output_end_line < line_no)
        {
            ++right_case_count;
            former_input_start_line = tmp_input_start_line;
            former_input_end_line = tmp_input_end_line;
            former_output_start_line = tmp_output_start_line;
            former_output_end_line = tmp_output_end_line;
        }
        ++thisfile_case_count;
        has_slice = true;
    }
    if (!find && thisfile_case_count > 0)
    {
        input_start_line = former_input_start_line;
        input_end_line = former_input_end_line;
        output_start_line = former_output_start_line;
        output_end_line = former_output_end_line;
    }
}

void set_print_whole_file(int &input_start_line, int &input_end_line, int &output_start_line, int &output_end_line, int &line_no)
{
    input_start_line = 1;
    input_end_line = MAX_LINE;
    output_start_line = 1;
    output_end_line = MAX_LINE;
    line_no = MAX_LINE;
}

//核心模式用户输出和标准输出比较的结果
struct CompareResult
{
    int start_wrong_line_no;
    int right_case_count;
    int thisfile_case_count;
};

//找到第一个不同的行，并且统计正确的case和所有case数目
CompareResult find_diff_line(const vector<string> &outputs, const vector<string> &useroutputs)
{
    CompareResult compareResult;
    int start_wrong_line_no = -1;
    int right_case_count = 0;
    int outputs_cnt = outputs.size();
    int useroutputs_cnt = useroutputs.size();
    int thisfile_case_count = outputs_cnt;
    //2者必须相同才比较
    if (outputs_cnt == useroutputs_cnt)
    {
        for (int i = 0; i < outputs_cnt; i++)
        {
            //每一行字符串是否相同
            if (outputs[i] == useroutputs[i])
            {
                right_case_count++;
            }
            else
            {
                if (start_wrong_line_no < 0)
                {
                    start_wrong_line_no = i + 1;
                }
            }
        }
    }
    compareResult.start_wrong_line_no = start_wrong_line_no;
    compareResult.right_case_count = right_case_count;
    compareResult.thisfile_case_count = thisfile_case_count;
    return compareResult;
}

//从流里面读取输入与输出的一行到一个vector里面
vector<string> read_lines_from_file(const string &file_name)
{
    ifstream stream(file_name);
    vector<string> temp_lines;
    string temp_line;
    while (getline(stream, temp_line))
    {
        //为空的话直接跳出
        if (temp_line.empty())
        {
            break;
        }
        temp_lines.emplace_back(temp_line);
        // cout << temp_line << endl;
    }
    return temp_lines;
}

//flag=0表示input，=1表示output,=2表示user_output
void print_case(ifstream &stream, int print_start_number, int print_end_number, int flag = 0)
{
    // char line[MAX_PRINT_SIZE + 2] = {0};

    int print_byte_cnt = 0;
    //输入例子
    for (int i = 1; i <= print_end_number; ++i)
    {
        // if (!stream.getline(line, MAX_PRINT_SIZE + 2) && strlen(line) < MAX_PRINT_SIZE + 2 - 1)
        // {
        //     //有以下几种情况可能结束
        //     //1.读到结束;2.stream error
        //     //1和2都应该退出
        //     cout << i << endl;
        //     cout << strlen(line) << endl;
        //     break;
        // }
        string temp_line;

        if (!getline(stream, temp_line))
        {
            //有以下几种情况可能结束
            //1.读到结束;2.stream error
            //1和2都应该退出
            break;
        }
        int line_len = temp_line.size();

        if (i >= print_start_number)
        {
            //读的这一行太长了，先输出一部分再输出提示，然后退出
            if (line_len >= MAX_PRINT_SIZE)
            {
                string line = temp_line.substr(0, MAX_PRINT_SIZE);
                // line[MAX_PRINT_SIZE] = '\0';
                cout << line << "输出过多，无法输出完全...." << endl;
                if (flag == 1 || flag == 2)
                {
                    cout << "输出不完全，此次比较无意义" << flag << endl;
                }
                break;
            }
            else
            {
                //读总计太长了，先输出一部分再输出提示，然后退出
                print_byte_cnt += line_len;
                if (print_byte_cnt > MAX_PRINT_SIZE)
                {
                    string line = temp_line.substr(0, print_byte_cnt - MAX_PRINT_SIZE);
                    // line[MAX_PRINT_SIZE] = '\0';

                    cout << line << "输出过多，无法输出完全...." << endl;
                    if (flag == 1 || flag == 2)
                    {
                        cout << "输出不完全，此次比较无意义" << flag << endl;
                    }
                    break;
                }
                cout << temp_line << endl;
            }
        }
    }
}

// get_case
int main(int argc, char *argv[])
{
    // if (argc != 2) {
    //     cerr<<"Invalid number of arguments"<<endl;
    //     return -1;
    // }

    //int line_no = atoi(argv[1]);
    int line_no = 0;
    int diff_result = get_diff_line(USER_OUTPUT, OUTPUT, &line_no);
    if (diff_result == 0)
    {
        //accept
        return 0;
    }

    int input_start_line = line_no;
    int input_end_line = line_no;
    int output_start_line = line_no;
    int output_end_line = line_no;
    int thisfile_case_count = 0;
    int right_case_count = 0;
    bool has_slice = false;

    //为false的话，get_case.cpp里面不处理，展示case的情况通过test_case_results来计算
    bool has_more_case_count = false;
    int case_count = atoi(getenv("CASE_COUNT") ? getenv("CASE_COUNT") : "1");

    // int case_count = 1;

    //整个get_case.cpp分为2部分考虑，显示错误用例/所有用例的数目和显示错误用例的情况，0为ACM模式
    int problem_type = atoi(getenv("PROBLEM_TYPE") ? getenv("PROBLEM_TYPE") : "1");
    // int problem_type = 1;
    if (problem_type == 0)
    {
        //显示错误用例/所有用例的数目
        if (case_count == 1)
        {
            struct stat slice_buf;
            stat(SLICE, &slice_buf);

            //单个文件的并且有Slice文件的情况的ACM，获得比较假的'right_case_count'和'thisfile_case_count'
            //比如
            //input    output  user_output
            //1 1       2       2
            //2 2       4       5
            //3 3       6       6
            //4 4       8       8
            //这种情况下，应该输出的right_case_count是3，但是其实是1
            //比较特殊，这种情况很少，建议之后遇到的了，也可以改成多个文件的，暂时先这样兼容
            if (slice_buf.st_size > 0)
            {
                ifstream slice(SLICE);
                find_in_slice(slice, line_no, input_start_line, input_end_line, output_start_line, output_end_line, thisfile_case_count, right_case_count, has_slice);
            }
            //输出 0/1
            else
            {
                right_case_count = 0;
                thisfile_case_count = 1;
            }
        }
        else
        {
            has_more_case_count = true;
        }

        //这个是显示错误用例的情况
        //不管有没有slice文件,显示错误用例的单个文件in,out的所有内容和用户的所有输出
        set_print_whole_file(input_start_line, input_end_line, output_start_line, output_end_line, line_no);
    }
    //核心模式
    else
    {

        //这个是显示错误用例的情况
        vector<string> outputs = read_lines_from_file(OUTPUT);
        vector<string> useroutputs = read_lines_from_file(USER_OUTPUT);
        CompareResult compareResult = find_diff_line(outputs, useroutputs);
        if (compareResult.start_wrong_line_no > 0)
        {
            line_no = compareResult.start_wrong_line_no;
            input_start_line = line_no;
            input_end_line = line_no;
            output_start_line = line_no;
            output_end_line = line_no;
        }
        else
        { //出现问题，直接输出全部信息
            set_print_whole_file(input_start_line, input_end_line, output_start_line, output_end_line, line_no);
        }

        right_case_count = compareResult.right_case_count;
        thisfile_case_count = compareResult.thisfile_case_count;

        //显示错误用例/所有用例的数目
        if (case_count > 1)
        {
            has_more_case_count = true;
        }
    }

    ifstream inputIfstream(INPUT);
    ifstream outputIfstream(OUTPUT);
    ifstream useroutputIfstream(USER_OUTPUT);

    print_case(inputIfstream, input_start_line, input_end_line);
    // char line[MAX_LINE] = {0};
    // int input_byte_cnt = 0;
    // //输入例子
    // for (int i = 1; i <= input_end_line; ++i)
    // {
    //     if (!input.getline(line, MAX_PRINT_SIZE) && strlen(line) < MAX_PRINT_SIZE - 1)
    //     {
    //         //有以下几种情况可能结束
    //         //1.读到结束;2.line太长;3.stream error
    //         //1和3都应该退出
    //         break;
    //     }

    //     if (i >= input_start_line)
    //     {
    //         if (input_byte_cnt > MAX_PRINT_SIZE)
    //         {
    //             line[MAX_PRINT_SIZE] = '\0';
    //             cout << line << "...." << endl;
    //             break;
    //         }
    //         else
    //         {
    //             input_byte_cnt += strlen(line);
    //             cout << line << endl;
    //         }
    //     }
    // }

    cout << "Q77963306Q" << endl;

    print_case(outputIfstream, output_start_line, output_end_line, 1);

    // int output_byte_cnt = 0;
    // // 输出例子
    // if (thisfile_case_count > 0)
    // {
    //     // 已经通过读slice文件得到了测试用例数目
    //     for (int i = 1; i <= output_end_line; ++i)
    //     {
    //         if (!output.getline(line, MAX_PRINT_SIZE) && strlen(line) < MAX_PRINT_SIZE - 1)
    //         {
    //             break;
    //         }
    //         if (i >= output_start_line)
    //         {
    //             if (output_byte_cnt > MAX_PRINT_SIZE)
    //             {
    //                 line[MAX_PRINT_SIZE] = '\0';
    //                 cout << line << "...." << endl;
    //                 break;
    //             }
    //             else
    //             {
    //                 output_byte_cnt += strlen(line);
    //                 cout << line << endl;
    //             }
    //         }
    //     }
    // }
    // else
    // {
    //     // 需要读完整个文件得到测试用例数
    //     int current_no = 1;
    //     while (!output.eof())
    //     {
    //         if (!output.getline(line, MAX_PRINT_SIZE) && strlen(line) < MAX_PRINT_SIZE - 1)
    //         {
    //             break;
    //         }
    //         if (current_no >= output_start_line && current_no <= output_end_line)
    //         {
    //             if (output_byte_cnt > MAX_PRINT_SIZE)
    //             {
    //                 line[MAX_PRINT_SIZE] = '\0';
    //                 cout << line << "...." << endl;
    //                 break;
    //             }
    //             else
    //             {
    //                 output_byte_cnt += strlen(line);
    //                 cout << line << endl;
    //             }
    //         }
    //         ++current_no;
    //         ++thisfile_case_count;
    //     }
    // }

    cout << "Q77963305Q" << endl;
    // 如果这个文件里只有一个用例，那么就应该把用户输出全部输出
    int useroutput_end_line = thisfile_case_count == 1 ? MAX_LINE : line_no;
    print_case(useroutputIfstream, output_start_line, useroutput_end_line, 2);
    // int useroutput_byte_cnt = 0;

    // // 用户输出

    // for (int i = 1; i <= useroutput_end_line; ++i)
    // {
    //     if (!useroutput.getline(line, MAX_PRINT_SIZE) && strlen(line) < MAX_PRINT_SIZE - 1)
    //     {
    //         break;
    //     }
    //     if (i >= output_start_line)
    //     {
    //         if (useroutput_byte_cnt > MAX_PRINT_SIZE)
    //         {
    //             line[MAX_PRINT_SIZE] = '\0';
    //             cout << line << "...." << endl;
    //             break;
    //         }
    //         else
    //         {
    //             useroutput_byte_cnt += strlen(line);
    //             cout << line << endl;
    //         }
    //     }
    // }
    int original_right_case_count = right_case_count;
    cout << "Q77963304Q";
    // 通过比例
    if (right_case_count == 0 && line_no > 0 && !has_slice)
    {
        right_case_count = line_no - 1;
    }
    if (thisfile_case_count <= 0 || right_case_count <= 0 || right_case_count >= thisfile_case_count)
    {
        cout << 0;
    }
    else
    {
        cout << (float)100 * right_case_count / thisfile_case_count;
    }
    cout << "Q77963304Q" << endl;

    //通过case的情况
    //单个测试用例文件才处理显示case的情况
    if (!has_more_case_count)
    {
        cout << "Q77963303Q" << endl;
        cout << original_right_case_count << "," << thisfile_case_count << endl;
        cout << "Q77963302Q" << endl;
    }
    return diff_result;
}
