from game_state import GameState
from helpers.json_loader import load_chapter
from llm.suspicion_evaluator import evaluate_player_message

game_state=GameState()
game_state.chapter_data=load_chapter(1)

game_state.player_name="Michelle"
game_state.chapter=1
game_state.investigation_progress=0
game_state.martha_pressure=0
game_state.unknown_unlocked=False

game_state.messages = {
    "Martha": [
        {
            "sender": "Martha",
            "text": "Are you okay?"
        },
        {
            "sender": "Martha",
            "text": "I still cannot believe Sarah is gone."
        }
    ],
    "Unknown": []
}

text_messages=[
    "What happened to Sarah?",
    "When did you last see Sarah?",
    "You keep avoiding the question. Are you lying to me?",
    "I miss her too.",
    "That does not match what you said before."
]

for message in text_messages:
    print()
    print("=" *50)
    print("PLAYER MESSAGE:")
    print(message)
    
    result=evaluate_player_message(
        game_state,message
    )
    print("QWEN RESULT: ")
    print(result)