#include "testlib.h"
#include <algorithm>
#include <iostream>
#include <vector>
using namespace std;

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);

    // Usage: gen T sumN mode seed
    int T = opt<int>(1);
    int sumN = opt<int>(2);
    int mode = opt<int>(3);
    long long seed = opt<long long>(4);
    ensuref(1 <= T && T <= 200000, "T out of range");
    ensuref(T <= sumN && sumN <= 1000000000, "sumN must be in [T, 10^9]");
    ensuref(0 <= mode && mode <= 4, "mode must be in [0, 4]");
    rnd.setSeed(seed);

    vector<int> ns(T);
    if (mode == 0) {
        // Random positive partition: the n values sum to sumN exactly.
        ns = rnd.partition(T, sumN);
    } else if (mode <= 3) {
        for (int i = 0; i < T; ++i) {
            ns[i] = sumN / T + (i < sumN % T);
        }
    } else {
        int maxN = sumN - T + 1;
        vector<int> bounds = {1, maxN};
        for (long long p = 1; p <= maxN; p *= 2) {
            for (int d = -1; d <= 1; ++d) {
                if (1 <= p + d && p + d <= maxN) {
                    bounds.push_back(int(p + d));
                }
            }
        }
        sort(bounds.begin(), bounds.end());
        bounds.erase(unique(bounds.begin(), bounds.end()), bounds.end());
        int remaining = sumN;
        for (int i = 0; i < T; ++i) {
            // Reserve at least 1 for each subsequent round.
            ns[i] = min(bounds[i % bounds.size()], remaining - (T - i - 1));
            remaining -= ns[i];
        }
    }

    cout << T << '\n';
    for (int tc = 1; tc <= T; ++tc) {
        setTestCase(tc);
        int n = ns[tc - 1];

        int x;
        if (mode == 2) x = 1;
        else if (mode == 3) x = n;
        else if (mode == 4 && tc % 4 == 1) x = 1;
        else if (mode == 4 && tc % 4 == 2) x = n;
        else if (mode == 4 && tc % 4 == 3) x = (n + 1) / 2;
        else x = rnd.next(1, n);

        // Hidden input: n and the preselected secret x.
        cout << n << ' ' << x << '\n';
    }
}
