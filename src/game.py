from board import pieceDetector
import capture
import time
from engine import engine
from config import PLAY_AS_WHITE

#Starting position
pieces = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
castling = "KQkq"
enPassant = "-"
halfMove = 0
fullMove = 1
nextMove = "w"
playAsWhite = PLAY_AS_WHITE

def updateNextMove():
    global fullMove, nextMove
    if nextMove == "w":
        nextMove = "b"
    else:
        nextMove = "w"
        fullMove = fullMove + 1
        
def expand_fen_row(row):
    expanded_row = ""
    for char in row:
        if char.isdigit():
            expanded_row += ' ' * int(char)
        else:
            expanded_row += char
    return expanded_row

def getCastling(pieces, currentCastling):
    rows = pieces.split('/')
    expanded_rows = [expand_fen_row(row) for row in rows]
    
    newCastling = ""
    if expanded_rows[7][4] == 'K' and expanded_rows[7][7] == 'R':
        if 'K' in currentCastling:
            newCastling += 'K'
    if expanded_rows[7][4] == 'K' and expanded_rows[7][0] == 'R':
        if 'Q' in currentCastling:
            newCastling += 'Q'
    if expanded_rows[0][4] == 'k' and expanded_rows[0][7] == 'r':
        if 'k' in currentCastling:
            newCastling += 'k'
    if expanded_rows[0][4] == 'k' and expanded_rows[0][0] == 'r':
        if 'q' in currentCastling:
            newCastling += 'q'
    
    return newCastling if newCastling else '-'

    
def getEnPassant():
    return "-"
def getMoveCount():
    pass
def createFenString(pieces, nextMove, castling, enPassant, halfMove, fullMove):
    return pieces +" "+ nextMove +" "+ castling +" "+ enPassant +" "+ str(halfMove) +" "+ str(fullMove)

def game():
    global pieces, nextMove, castling, enPassant
    pieceDetector.playAsWhite = playAsWhite
    if(playAsWhite):
        nextMove = "w"
    else:
        nextMove = "b"
        boardImg = capture.getChessBoard() 
        pieces = pieceDetector.getPiecePlacement(boardImg)
    while(1):
        time.sleep(1)
        boardImg = capture.getChessBoard()    
        newPieces = pieceDetector.getPiecePlacement(boardImg)
        if(newPieces == pieces or newPieces == "8/8/8/8/8/8/8/8"):
            continue
        pieces = newPieces
        updateNextMove()
        castling = getCastling(pieces, castling)
        enPassant = getEnPassant()
        getMoveCount()

        fenString = createFenString(pieces, nextMove, castling, enPassant, halfMove, fullMove)
        print(fenString)
        print(engine.getMove(fenString))
        print(engine.getPositionScore(fenString))

if __name__ == "__main__":
    game()
        

