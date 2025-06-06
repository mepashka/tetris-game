import json
import os
from tetris import Tetromino, create_grid

SAVE_PATH = "savegame.json"
STATS_PATH = "stats.json"

def save_game(grid, current, next_piece, score):
    data = {
        "grid": grid,
        "current": current.serialize(),
        "next": next_piece.serialize(),
        "score": score
    }
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f)

def load_game():
    try:
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
            grid = data["grid"]
            current = Tetromino.deserialize(data["current"])
            next_piece = Tetromino.deserialize(data["next"])
            score = data["score"]
            return grid, current, next_piece, score
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return create_grid(), Tetromino(), Tetromino(), 0

def save_stats(score):
    stats = load_stats()
    stats["games_played"] += 1
    if score > stats["record"]:
        stats["record"] = score
    with open(STATS_PATH, "w") as f:
        json.dump(stats, f)

def load_stats():
    try:
        with open(STATS_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"record": 0, "games_played": 0}
