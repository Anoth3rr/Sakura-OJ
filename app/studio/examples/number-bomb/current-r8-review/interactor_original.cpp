#include "testlib.h"
#include <bits/stdc++.h>
using namespace std;

#define int long long
#define pii array<int, 2>
// #define endl "\n"

signed main(signed argc, char *argv[]) {
    registerInteraction(argc, argv);

    int t = inf.readInt(1, 2E5, "t");
    cout << t << endl;
    inf.readEoln();

    for (int tc = 1; tc <= t; ++tc) {
        setTestCase(tc);
        int n = inf.readInt(1, 1E9, "n");
        inf.readSpace();
        int x = inf.readInt(1, n, "x");
        inf.readEoln();
        cout << n << endl;

        int q = 0;
        while (1) {
            string op = ouf.readToken("[?!]", "op");
            if (op != "?" && op != "!") quitf(_pe, "expected ? or !");
            ouf.readSpace();
            int c = ouf.readInt(1, n, "c");
            ouf.readEoln();
            if (op == "!") {
                if (x != n) quitf(_wa, "incorrect guess in test %d", tc);
                break;
            } else if (op == "?") {
                if (++q > 100) quitf(_wa, "more than 100 queries in one test case");
                int p;
                if (x == n) p = 1;
                else if (x < n) p = 0;
                else if (x > n) p = 2;
                cout << p << endl;
            }
        }
    }
    if (!ouf.seekEof()) quitf(_pe, "extra output after all test cases");
    quitf(_ok, "all tests passed");
    return 0;
}