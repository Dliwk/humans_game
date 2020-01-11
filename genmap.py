import sys
n = int(sys.argv[1])
for i in range(2 - n, 3):
    print(f'wall {2 - n} {i}')
    print(f'wall {2} {i}')
    print(f'ground {i} {2 - n}')
    print(f'ground {i} {2}')

