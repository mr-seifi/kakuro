from game import Board, CSPModel

def main():
    board = Board(4, 4, {'A0B0': 'BLACK', 'A0B1': 'CLUE::20', 'A0B2': 'CLUE::19', 'A0B3': 'CLUE::7', 
                         'A1B0': 'CLUE:20:', 'A2B0': 'CLUE:19:', 'A3B0': 'CLUE:7:'})
    # board = Board(3, 3, {'A0B0': 'BLACK', 'A0B1': 'CLUE::15', 'A0B2': 'CLUE::14',
    #                      'A1B0': 'CLUE:16:', 'A2B0': 'CLUE:13:'})
    board.print_board()
    
    csp = CSPModel(board=board)
    # [print(str(c)) for c in csp.constrains]
    print(csp.solve())

if __name__ == '__main__':
    main()