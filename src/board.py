import torch
import cv2
from config import PLAY_AS_WHITE, MODEL_REPO_DIR, MODEL_PATH

class PieceDetector:
    def __init__(self):
        self.confidenceThreshold = 0.7
        self.playAsWhite = PLAY_AS_WHITE
        self.model = torch.hub.load(MODEL_REPO_DIR,'custom', path=MODEL_PATH, force_reload=True, source='local')
    def __convertCoordinates(self, x1, y1, x2, y2, img_size, start_white):
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        cell_size = img_size // 8

        col = center_x // cell_size       # Column (0-7)
        row = center_y // cell_size + 1   # Row (1-8)

        if start_white:
            # (0,0) is the bottom left
            row = 8 - (row - 1)
        else:
            # (0,0) is the top right
            col = 7 - col
            row = row

        # Convert column index (0-7) to letter (a-h)
        col_letter = chr(ord('a') + col)

        return row, col_letter  # Return row as number and column as letter

    def __getFenBoard(self, pieces):
        FENmap = {
            "white-rook": "R",
            "white-knight": "N",
            "white-bishop": "B",
            "white-king": "K",
            "white-queen": "Q",
            "white-pawn": "P",
            "black-rook": "r",
            "black-knight": "n",
            "black-bishop": "b",
            "black-king": "k",
            "black-queen": "q",
            "black-pawn": "p",
        }
        # Initialize an 8x8 board with empty squares represented by '1'
        board = [['1' for _ in range(8)] for _ in range(8)]
        
        # Mapping to convert column letters (a-h) to indexes (0-7)
        col_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        
        # Populate the board with the detected pieces
        for piece in pieces:
            piece_type = FENmap[piece['piece']]
            row, col_letter = piece['position']  # Position is a tuple (row, col)
            col = col_map[col_letter]            # Convert column letter to index

            # Place the piece on the board (row - 1 for 0-indexing)
            board[row - 1][col] = piece_type

        # Reverse the board to start from rank 8 (black's side) to rank 1 (white's side)
        board.reverse()

        # Build the FEN string row by row
        fen_rows = []
        for row in board:
            fen_row = ''
            empty_count = 0
            for square in row:
                if square == '1':
                    empty_count += 1  # Count empty squares
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)  # Add empty squares count to FEN
                        empty_count = 0
                    fen_row += square  # Add the piece symbol

            if empty_count > 0:
                fen_row += str(empty_count)  # Add remaining empty squares in the row

            fen_rows.append(fen_row)

        # Join the rows with '/' to form the full FEN string for the board
        fen_board = '/'.join(fen_rows)

        return fen_board
    def __detectPieces(self, img):
        img_size = img.shape[0]
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.model(img_rgb)

        # Extract the results (bounding boxes, labels, and confidence scores)
        boxes = results.xyxy[0].cpu().numpy()  # Bounding boxes (x1, y1, x2, y2, confidence, class)
        labels = results.names                # List of class labels
        confidences = results.xyxy[0][:, 4].cpu().numpy()  # Confidence scores
        classes = results.xyxy[0][:, 5].cpu().numpy()  # Class indices

        # Dictionary to store the detected pieces by their grid positions
        position_to_piece = {}

        # Loop through detected pieces, filtering by confidence threshold
        for i, box in enumerate(boxes):
            confidence = confidences[i]
            if confidence >= self.confidenceThreshold:  # Apply confidence threshold filter
                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                class_id = int(classes[i])
                label = labels[class_id]

                # Convert the coordinates to the chessboard grid system
                row, col_letter = self.__convertCoordinates(x1, y1, x2, y2, img_size, self.playAsWhite)

                # Check if the position already exists in the dictionary
                if (row, col_letter) in position_to_piece:
                    if confidence > position_to_piece[(row, col_letter)]['confidence']:
                        position_to_piece[(row, col_letter)] = {'piece': label, 'confidence': confidence}
                else:
                    position_to_piece[(row, col_letter)] = {'piece': label, 'confidence': confidence}

        # Convert the dictionary into FEN string
        pieces = [{'piece': data['piece'], 'position': position, 'confidence': data['confidence']}
                for position, data in position_to_piece.items()]
        #pieces, img, boxes, confidences, classes, labels
        return pieces

    def getPiecePlacement(self, boardImage):
        pieces = self.__detectPieces(boardImage)
        return self.__getFenBoard(pieces)
    
pieceDetector = PieceDetector()

if __name__ == "__main__":
    img = cv2.imread("start_board.jpg")
    print(pieceDetector.getPiecePlacement(img))
