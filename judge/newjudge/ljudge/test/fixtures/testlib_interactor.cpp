#include "testlib.h"
#include <cstdio>
#include <fstream>
#include <iostream>
#include <string>
#include <unistd.h>

int main(int argc, char* argv[]) {
    registerInteraction(argc, argv);
    std::cerr << "INTERACTOR\n";
    ensuref(argc == 4, "expected input, transcript and answer arguments");
    setTestCase(1);
    int secret = inf.readInt(1, 100, "secret");
    int mode = inf.readInt(0, 2, "mode");
    if (mode != 1) {
        ensuref(ans.readInt() == secret, "wrong answer file was passed");
    }

    // Input/answer mounts must remain read-only.
    FILE* file = std::fopen(argv[1], "wb");
    ensuref(file == NULL, "hidden input is writable");
    file = std::fopen(argv[3], "wb");
    ensuref(file == NULL, "answer is writable");

    // Detect sharing between concurrent cases, including tout truncation.
    tout << secret << std::endl;
    ensuref(tout.good(), "transcript is not writable");
    usleep(100000);
    int recorded = -1;
    std::ifstream(argv[2]) >> recorded;
    ensuref(recorded == secret, "transcript is shared with another testcase");
    if (mode == 2) {
        tout << std::string(8192, 'x') << std::endl;
        ensuref(tout.good(), "cannot write transcript");
    }

    std::cout << 100 << std::endl;
    int count = 0;
    while (true) {
        std::string op = ouf.readToken();
        if (op != "?" && op != "!") quitf(_pe, "expected ? or !");
        int value = ouf.readInt(1, 100, "guess");
        if (op == "?") {
            if (++count > 8) quitf(_wa, "too many queries");
            std::cout << (value < secret ? ">" : value > secret ? "<" : "=") << std::endl;
        } else {
            if (value != secret) quitf(_wa, "incorrect answer");
            if (!ouf.seekEof()) quitf(_pe, "extra output");
            quitf(_ok, "testlib interaction accepted");
        }
    }
}
