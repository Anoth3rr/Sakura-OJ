#include <bits/stdc++.h>
using namespace std;

#define int long long
#define pii array<int, 2>
// Do not redefine endl: interactive output must be flushed.

int ask(int x) {
    cout << "? " << x << endl;
    int p;
    if (!(cin >> p)) exit(0);
    return p;
}

void answer(int x) {
    cout << "! " << x << endl;
}

void solve() {
    int n;
    if (!(cin >> n)) exit(0);
    int l = 1, r = n;
    while (l < r) {
        int m = (l + r) / 2;
        int p = ask(m);
        if (p == 1) {
            answer(m);
            return;
        } else if (p == 0) {
            l = m + 1;
        } else if (p == 2) {
            r = m - 1;
        } else {
            exit(0);
        }
    }
    answer(l);
}

signed main() {
    ios::sync_with_stdio(0), cin.tie(0);
    int t;
    if (!(cin >> t)) return 0;
    while (t--) solve();
    return 0;
}
