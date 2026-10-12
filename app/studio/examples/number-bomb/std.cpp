#include <iostream>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;
    if (!(cin >> T)) return 0;
    while (T--) {
        int n;
        if (!(cin >> n)) return 0;
        int l = 1, r = n;

        while (l < r) {
            int mid = l + (r - l) / 2;
            cout << "? " << mid << endl;

            int reply;
            if (!(cin >> reply)) return 0;
            if (reply == 0) l = mid + 1;
            else if (reply == 1) {
                l = r = mid;
            } else if (reply == 2) r = mid - 1;
            else return 0;
        }

        cout << "! " << l << endl;
        // Do not read a verdict: the next input is the next round's n.
    }
    return 0;
}
