#include "testlib.h"
#include <iostream>
using namespace std;

int main(int argc, char* argv[]) {
    registerInteraction(argc, argv);

    int T = inf.readInt(1, 200000, "T");
    cout << T << endl;
    long long totalQueries = 0;
    long long sumN = 0;

    for (int tc = 1; tc <= T; ++tc) {
        setTestCase(tc);
        int n = inf.readInt(1, 1000000000, "n");
        sumN += n;
        ensuref(sumN <= 1000000000LL, "sum of n exceeds 10^9");
        int secret = inf.readInt(1, n, "x");
        int queries = 0;

        // Reveal this round's n only; never send the secret.
        cout << n << endl;
        while (true) {
            string op = ouf.readToken();
            if (op != "?" && op != "!") {
                quitf(_pe, "expected ? or !");
            }
            // The statement does not restrict query values to [1, n].
            long long guess = ouf.readLong();

            if (op == "?") {
                if (++queries > 100) {
                    quitf(_wa, "more than 100 queries in one test case");
                }
                ++totalQueries;
                // 0: guess too small; 1: correct; 2: guess too large.
                cout << (guess < secret ? 0 : guess == secret ? 1 : 2) << endl;
            } else {
                if (guess != secret) {
                    quitf(_wa, "expected %d, found %lld", secret, guess);
                }
                // No acknowledgement after !. Continue with the next n.
                break;
            }
        }
    }

    // The contestant must exit after its final answer.
    if (!ouf.seekEof()) quitf(_pe, "extra output after all test cases");
    quitf(_ok, "all rounds passed; total_queries=%lld", totalQueries);
}
