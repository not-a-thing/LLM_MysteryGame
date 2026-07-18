from copy import deepcopy
from game_state import GameState
from helpers.json_loader import load_chapter
from llm.martha_llm import generate_martha_response
from llm.local_llm import warm_up_local_llms

def create_test_state():
    game_state=GameState()
    
    game_state.player_name="Michelle"
    game_state.chapter=1
    game_state.chapter_data=load_chapter(1)
    
    game_state.messages=deepcopy(game_state.chapter_data["starting_messages"])
    return game_state

def save_message(game_state,sender,text):
    game_state.messages["Martha"].append({
        "sender":sender,
        "text":text,
    })
    
def print_history(game_state):
    print("\n"+"="*60)
    print("CHAT HISTORY")
    print("="*60)
    
    for message in game_state.messages["Martha"]:
        sender=message.get("sender","Unknown")
        text=message.get("text","")
        
        print(f"{sender}: {text}")
    print("="*60)
    
def main():
    print("Starting Martha test...")
    print("Make sure Ollama is running.")
    print()
    
    warm_up_local_llms()
    game_state=create_test_state()
    
    print("\nCommands:")
    print("/history - show the full conversation")
    print("/reset - reset chapter")
    print("/quit - exit")
    print()
    
    while True:
        try:
            player_message=input(f"{game_state.player_name}: ").strip()
        except (KeyboardInterrupt,EOFError):
            print("\nExiting Martha Test.")
            break
        
        if not player_message:
            continue
        command=player_message.lower()
        
        if command in {"/quit","/exit",}:
            print("Exiting Martha test.")
            break
        if command=="/history":
            print_history(game_state)
            continue
        
        if command == "/reset":
            game_state = create_test_state()

            print("\nChapter 1 conversation reset.")
            print_history(game_state)
            continue

        save_message(
            game_state,
            game_state.player_name,
            player_message,
        )

        print("\nMartha is thinking...")
        
        try:
            martha_reply = generate_martha_response(
                game_state
            )

        except Exception as error:
            print("\nMartha LLM failed:")
            print(error)
            continue

        save_message(
            game_state,
            "Martha",
            martha_reply,
        )

        print(f"\nMartha: {martha_reply}\n")
        
if __name__ == "__main__":
    main()