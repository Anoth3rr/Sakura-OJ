#include <iostream>
#include <string>
using namespace std;
int main() {
    string phase;
    if (!(cin >> phase)) return 1;
    long long sum = 0, x;
    if (phase == "send") {
        int n; cin >> n;
        while (n--) { cin >> x; sum += x; }
    } else if (phase == "receive") cin >> sum;
    else return 1;
    cout << sum << '\n';
}
