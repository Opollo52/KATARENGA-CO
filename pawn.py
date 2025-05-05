class Pawn:
    def __init__(self, position):
        self.position = position  


    def sliding_moves(self, board, stop_color, diagonals=False, orthogonals=False):
        directions = []
        if diagonals:
            directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        if orthogonals:
            directions += [(0, 1), (1, 0), (0, -1), (-1, 0)]

        moves = []
        for dx, dy in directions:
            x, y = self.position
            while True:
                x += dx
                y += dy
                if not board.is_valid(x, y):
                    break
                if board.is_occupied(x, y):
                    break
                moves.append((x, y))
                if board.get_color(x, y) == stop_color:
                    break
        return moves
    

    def king_moves(self, board):
        x, y = self.position
        moves = [(x+dx, y+dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx or dy]
        return [(nx, ny) for nx, ny in moves if board.is_valid(nx, ny)]

    def knight_moves(self, board):
        x, y = self.position
        directions = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                      (-2, -1), (-1, -2), (1, -2), (2, -1)]
        return [(x+dx, y+dy) for dx, dy in directions if board.is_valid(x+dx, y+dy)]

    def bishop_moves(self, board, stop_color):
        return self._sliding_moves(board, stop_color, diagonals=True, orthogonals=False)

    def rook_moves(self, board, stop_color):
        return self._sliding_moves(board, stop_color, diagonals=False, orthogonals=True)

    


    def get_moves(self, board, color):
            if color == "3":
                return self.king_moves(board)
            elif color == "2":
                return self.knight_moves(board)
            elif color == "1":
                return self.bishop_moves(board, stop_color="1")
            elif color == "4":
                return self.rook_moves(board, stop_color="4")
            return []