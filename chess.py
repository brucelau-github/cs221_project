M, N = 15, 15

board = [[0]*M for _ in range(N)]

B, W = -1, 1

def is_end(board):
    for m in range(M):
        for n in range(N):
            walk(m, n)

def walk(m, n):
    
