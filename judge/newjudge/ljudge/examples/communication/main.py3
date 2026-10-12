import sys

tokens = sys.stdin.read().split()
if tokens[0] == 'send':
    print(sum(map(int, tokens[2:])))
elif tokens[0] == 'receive':
    print(int(tokens[1]))
else:
    sys.exit(1)
