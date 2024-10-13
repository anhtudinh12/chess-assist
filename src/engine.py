import chess
import chess.engine
from config import ENGINE_PATH, ENGINE_DEPTH, ENGINE_LEVEL, ENGINE_THREADS
class Engine:
    def __init__(self, enginePath):
        self.path = enginePath
        
    def initialize(self):
        self.engine = chess.engine.SimpleEngine.popen_uci(self.path)
        self.engine.configure({
            "Skill Level": ENGINE_LEVEL,
            "Threads": ENGINE_THREADS
        })

    def getMove(self, fenString):
        if not self.engine:
            self.initialize()
        board = chess.Board(fenString)
        depthLimit = chess.engine.Limit(depth=ENGINE_DEPTH)
        move = self.engine.play(board, depthLimit)
        return move.move

    def getPositionScore(self, fenString):
        if not self.engine:
            self.initialize()
        board = chess.Board(fenString)
        depthLimit = chess.engine.Limit(depth=ENGINE_DEPTH)
        info = self.engine.analyse(board, depthLimit)
        score = info['score'].relative
        if score.is_mate():
            result = f"M{score.mate()}"
        else:
            # Convert centipawns to pawns and return
            result = f"Score: {score.score() / 100:.2f}"
        return result

    def quit(self):
        if self.engine:
            self.engine.quit()
            self.engine = None

engine = Engine(ENGINE_PATH)
engine.initialize()

if __name__ == "__main__":
    fenString = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    playResult = engine.getMove(fenString, ENGINE_DEPTH)
    print(playResult.move)

