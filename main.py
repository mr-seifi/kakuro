from game import Board, CSPModel

def main():

    board = get_board(4)
    board.print_board()
    
    csp = CSPModel(board=board)
    print(dict(sorted(csp.solve(mrv=True, lcv=True, forward_checking=False).items())))


def get_board(n):
    return {
        3: Board(3, 3, {'A0B0': 'BLACK', 'A0B1': 'CLUE::15', 'A0B2': 'CLUE::14',
                         'A1B0': 'CLUE:16:', 'A2B0': 'CLUE:13:'}),
        4: Board(4, 4, {'A0B0': 'BLACK', 'A0B1': 'CLUE::20', 'A0B2': 'CLUE::19', 'A0B3': 'CLUE::7', 
        'A1B0': 'CLUE:20:', 'A2B0': 'CLUE:19:', 'A3B0': 'CLUE:7:'}),
        5: Board(5, 5, {'A0B0': 'BLACK', 'A0B1': 'BLACK', 'A0B2': 'BLACK', 'A0B3': 'CLUE::24', 'A0B4': 'CLUE::3', 
                         'A1B0': 'BLACK', 'A1B1': 'BLACK', 'A1B2': 'CLUE:10:23', 
                         'A2B0': 'BLACK', 'A2B1': 'CLUE:14:3', 'A3B0': 'CLUE:19:', 'A3B4': 'BLACK', 
                         'A4B0': 'CLUE:10:', 'A4B3': 'BLACK', 'A4B4': 'BLACK'}),
        9: Board(9, 8, {'A0B0': 'BLACK', 'A0B1': 'BLACK', 'A0B2': 'BLACK', 'A0B3': 'CLUE::15', 'A0B4': 'CLUE::8', 'A0B5': 'BLACK', 
                        'A0B6': 'CLUE::15', 'A0B7': 'CLUE::3', 'A1B0': 'BLACK', 'A1B1': 'BLACK', 'A1B2': 'CLUE:12:8', 'A1B5': 'CLUE:4:11',
                        'A2B0': 'BLACK', 'A2B1': 'CLUE:23:16', 'A3B0': 'CLUE:12:', 'A3B3': 'BLACK', 'A3B4': 'CLUE:10:7', 'A3B7': 'BLACK',
                        'A4B0': 'CLUE:8:', 'A4B3': 'CLUE:9:20', 'A4B6': 'CLUE::8', 'A4B7': 'CLUE::10', 
                        'A5B0': 'BLACK', 'A5B1': 'BLACK', 'A5B2': 'CLUE:8:15', 'A5B5': 'CLUE:11:', 
                        'A6B0': 'BLACK', 'A6B1': 'CLUE:15:12', 'A6B4': 'CLUE::9', 'A6B5': 'CLUE:5:4',
                        'A7B0': 'CLUE:33:', 'A7B7': 'BLACK', 'A8B0': 'CLUE:8:', 'A8B3': 'CLUE:3:', 'A8B6': 'BLACK', 'A8B7': 'BLACK'}) 
    }[n]

if __name__ == '__main__':
    main()