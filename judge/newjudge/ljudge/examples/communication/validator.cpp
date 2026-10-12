#include <fstream>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>
using namespace std;
int main(int argc, char** argv) {
    if (argc != 4) return 1;
    ifstream input(argv[1]);
    string feedback = argv[3], phase;
    input >> phase;
    string output((istreambuf_iterator<char>(cin)), {});
    istringstream stream(output);
    long long actual, expected = 0, x;
    string extra;
    if (!(stream >> actual) || (stream >> extra)) return 43;
    if (phase == "send") {
        int n;
        if (!(input >> n) || n < 1 || n > 100000) return 1;
        while (n--) {
            if (!(input >> x) || x < -1000000 || x > 1000000) return 1;
            expected += x;
        }
        if (output.size() > 32 || actual != expected) return 43;
        ofstream state(feedback + "/expected"); state << expected << '\n';
        ofstream next(feedback + "/nextpass.in"); next << "receive\n" << output;
        if (!state || !next) return 1;
    } else if (phase == "receive") {
        ifstream state(feedback + "/expected");
        if (!(state >> expected)) return 1;
        if (actual != expected) return 43;
        ofstream(feedback + "/judgemessage.txt") << "Both passes accepted\n";
    } else return 1;
    return 42;
}
