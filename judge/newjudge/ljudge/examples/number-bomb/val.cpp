#include "testlib.h"

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);

    int T = inf.readInt(1, 200000, "T");
    inf.readEoln();
    long long sumN = 0;
    for (int tc = 1; tc <= T; ++tc) {
        setTestCase(tc);
        int n = inf.readInt(1, 1000000000, "n");
        sumN += n;
        ensuref(sumN <= 1000000000LL, "sum of n exceeds 10^9");
        inf.readSpace();
        inf.readInt(1, n, "x");
        inf.readEoln();
    }
    inf.readEof();
}
