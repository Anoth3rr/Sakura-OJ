import sys

print('CONTESTANT', file=sys.stderr)
n = int(input())
low, high = 1, n
while low <= high:
    mid = (low + high) // 2
    print('?', mid, flush=True)
    reply = input().strip()
    if reply == '=':
        print('!', mid, flush=True)
        break
    if reply == '>':
        low = mid + 1
    elif reply == '<':
        high = mid - 1
    else:
        sys.exit(7)
