#include <csignal>
#include <fstream>
#include <iostream>
#include <string>
#include <unistd.h>

// input: hidden answer, mode (0=normal, 1=require EOF, 2=judge crash).
int main() {
    std::cerr << "INTERACTOR\n";
    int secret, require_eof;
    if (!(std::ifstream("input") >> secret >> require_eof)) return 3;
    std::cout << 100 << std::endl;
    std::string op;
    int value, count = 0;
    while (std::cin >> op >> value) {
        if (op == "?") {
            if (++count > 8 || value < 1 || value > 100) return 1;
            std::cout << (value < secret ? ">" : value > secret ? "<" : "=") << std::endl;
        } else if (op == "!") {
            if (value != secret) return 1;
            if (require_eof == 2) std::raise(SIGSEGV);
            if (require_eof == 3) usleep(300000);
            if (require_eof == 4) { for (;;) {} }
            if (require_eof == 5) return 3;
            if (require_eof == 6) return 2;
            if (require_eof == 1) {
                std::string extra;
                if (std::cin >> extra) return 1;
            }
            return 0;
        } else return 1;
    }
    return 1;
}
