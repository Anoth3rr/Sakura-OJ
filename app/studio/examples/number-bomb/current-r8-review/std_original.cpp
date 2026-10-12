#include <bits/stdc++.h>
using namespace std;

#define int long long
#define pii array<int, 2>
// #define endl "\n"

#ifdef LOCAL_JUDGE
    #include "debug.hpp"
#else
    #define _(...) true
#endif

int ask(int x) {
    cout << "? " << x << endl;
    int r;
    cin >> r;
    return r;
}

int answer(int x) {
    cout << "! " << x << endl;
}

void solve() {
    int n;
    cin >> n;
    int l = 1, r = n;
    while (l < r) {
        int m = (l + r) / 2, r = ask(m);
        if (r == 1) {
            cout << "! " << m << endl;
            return;
        } else if (r == 0)
            l = m + 1;
        else
            r = m - 1;
    }
}

signed main() {
    ios::sync_with_stdio(0), cin.tie(0);
    cout << fixed << setprecision(20);
    int t = 1;
    cin >> t;
    for (int i = 0; i < t; ++i) {
        solve();
    }
    return 0;
}
