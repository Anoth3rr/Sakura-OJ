#include <csignal>
#include <iostream>
#include <string>
#include <unistd.h>

#ifndef MODE
#define MODE 0
#endif

int main() {
    std::cerr << "CONTESTANT\n";
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n;
    if (!(std::cin >> n)) return 7;
    if (MODE == 1) { std::cout << "! 101" << std::endl; return 0; }
    if (MODE == 2) {
        std::cout << "? 50\n"; // Deliberately missing flush, with cin untied.
        std::string reply;
        std::cin >> reply;
        return 0;
    }
    if (MODE == 6) { std::cout << "oops 37" << std::endl; return 0; }
    if (MODE == 7) return 0; // Exit before sending any answer.
    if (MODE == 8) {
        std::cout << "oops 37" << std::endl;
        for (;;) std::cout << "more data\n" << std::flush;
    }
    int low = 1, high = n, answer = -1;
    while (low <= high) {
        int mid = (low + high) / 2;
        std::cout << "? " << mid << std::endl;
        std::string reply;
        if (!(std::cin >> reply)) return 8;
        if (reply == "=") { answer = mid; break; }
        if (reply == ">") low = mid + 1;
        else if (reply == "<") high = mid - 1;
        else return 9;
    }
    std::cout << "! " << answer << std::endl;
    if (MODE == 3) return 7;
    if (MODE == 4) std::raise(SIGSEGV);
    if (MODE == 5) { for (;;) {} }
    return 0;
}
