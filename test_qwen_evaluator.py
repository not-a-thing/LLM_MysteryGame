from game_state import GameState
from helpers.json_loader import load_chapter
from llm.suspicion_evaluator import evaluate_player_message


def create_test_game_state():
    game_state = GameState()

    game_state.chapter_data = load_chapter(1)
    game_state.player_name = "Michelle"
    game_state.chapter = 1

    game_state.investigation_progress = 0
    game_state.martha_pressure = 0
    game_state.unknown_unlocked = False

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

    return game_state


def save_message(game_state, contact_name, sender, text):
    if contact_name not in game_state.messages:
        game_state.messages[contact_name] = []

    game_state.messages[contact_name].append({
        "sender": sender,
        "text": text
    })


def update_game_state(game_state, evaluation):
    game_state.investigation_progress += evaluation[
        "investigation_progress_delta"
    ]

    # game_state.martha_pressure += evaluation[
    #     "martha_pressure_delta"
    # ]


def print_evaluation(result):
    print("\nQWEN RESULT:")
    print(f"Category: {result['category']}")
    print(
        "Investigation progress delta:",
        result["investigation_progress_delta"]
    )
    # print(
    #     "Martha pressure delta:",
    #     result["martha_pressure_delta"]
    # )
    print(
        "Repeated question:",
        result["repeated_question"]
    )
    print(f"Reason: {result['reason']}")


def print_game_state(game_state):
    print("\nCURRENT GAME STATE:")
    print(
        f"Investigation progress: "
        f"{game_state.investigation_progress}"
    )
    print(
        f"Martha pressure: "
        f"{game_state.martha_pressure}"
    )
    print(
        f"Unknown unlocked: "
        f"{game_state.unknown_unlocked}"
    )


def print_chat_history(game_state):
    print("\nCHAT HISTORY:")

    messages = game_state.messages.get("Martha", [])

    for message in messages:
        sender = message.get("sender", "Unknown")
        text = message.get("text", "")
        print(f"{sender}: {text}")


def main():
    game_state = create_test_game_state()

    print("=" * 60)
    print("QWEN MYSTERY EVALUATOR TEST")
    print("=" * 60)
    print("Type a player message and press Enter.")
    print("Commands:")
    print("  /history  Show the Martha chat history")
    print("  /state    Show the current game state")
    print("  /reset    Reset the test")
    print("  /quit     Exit")
    print("=" * 60)

    while True:
        try:
            player_message = input("\nMichelle: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting evaluator test.")
            break

        if not player_message:
            continue

        command = player_message.lower()

        if command in {"/quit", "/exit"}:
            print("Exiting evaluator test.")
            break

        if command == "/history":
            print_chat_history(game_state)
            continue

        if command == "/state":
            print_game_state(game_state)
            continue

        if command == "/reset":
            game_state = create_test_game_state()
            print("Game state and chat history have been reset.")
            continue

        print("\n" + "=" * 60)
        print("PLAYER MESSAGE:")
        print(player_message)

        # Evaluate before saving the current message.
        result = evaluate_player_message(
            game_state,
            player_message
        )

        print_evaluation(result)

        # Save the player's message after evaluation.
        save_message(
            game_state=game_state,
            contact_name="Martha",
            sender=game_state.player_name,
            text=player_message
        )

        update_game_state(
            game_state,
            result
        )

        print_game_state(game_state)


if __name__ == "__main__":
    main()