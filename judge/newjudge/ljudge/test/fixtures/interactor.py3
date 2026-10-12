import sys

print('INTERACTOR', file=sys.stderr)
secret, mode = map(int, open('input').read().split())
print(100, flush=True)
queries = 0
for line in sys.stdin:
    op, value = line.split()
    value = int(value)
    if op == '?':
        queries += 1
        if queries > 8 or not 1 <= value <= 100:
            sys.exit(1)
        print('>' if value < secret else '<' if value > secret else '=', flush=True)
    elif op == '!':
        sys.exit(0 if value == secret else 1)
    else:
        sys.exit(1)
sys.exit(1)
