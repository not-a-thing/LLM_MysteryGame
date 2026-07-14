import pygame
import threading

from copy import deepcopy

from helpers.text_helper import split_into_chat_bubbles
from ui.notification import show_notification

from llm.suspicion_evaluator import evaluate_player_message
from llm.martha_llm import generate_martha_response

def receive_message(game_state,sender,text):
    message={
        "sender":sender,
        "text":text,
    }
    
    game_state.messages[sender].append(message)
    player_is_viewing_sender={
        game_state.current_screen=="chat"
        and game_state.active_chat==sender
    }
    if not player_is_viewing_sender:
        game_state.unread_counts[sender]+=1
        show_notification(game_state,sender,text)
        
def queue_contact_messages(game_state,sender,text_or_messages,typing_duration=1200):
    """
    Makes a contact show a typing indicator first
    then sends one or more chat bubbles
    """
    if isinstance(text_or_messages,str):
        messages=split_into_chat_bubbles(text_or_messages)
    else:
        messages=text_or_messages
    game_state.typing_contact=sender
    game_state.typing_started_at=pygame.time.get_ticks()
    game_state.typing_duration=typing_duration
    game_state.queued_messages=[
        {
            "sender":sender,
            "text":message,
        }
        for message in messages
    ]
    game_state.set_contact_typing(sender,True)

def update_queued_message(game_state):
    if game_state.typing_contact is None:
        return
    current_time=pygame.time.get_ticks()
    elapsed=current_time-game_state.typing_started_at
    
    if elapsed<game_state.typing_duration:
        return
    sender=game_state.typing_contact
    game_state.set_contact_typing(sender,False)
    for message in game_state.queued_messages:
        receive_message(game_state,sender,message["text"])
    game_state.typing_contact=None
    game_state.typing_started_at=0
    game_state.typing_duration=0
    game_state.queued_messages=[]
    
    if game_state.pending_chapter_fade:
        game_state.pending_chapter_fade=False
        game_state.chapter_transition_active=True
        game_state.chapter_transition_alpha=0
        
def open_conversation(game_state,contact_name):
    game_state.active_chat=contact_name
    game_state.current_screen="chat"
    game_state.unread_counts[contact_name]=0
    
def handle_unknown_choice(game_state,choice_id):
    unknown_data=game_state.chapter_data["unknown_unlock"]
    selected_choice=None
    
    for choice in unknown_data["choices"]:
        if choice["id"]==choice_id:
            selected_choice=choice
            break
    if selected_choice is None:
        return
    
    #Add the player's selected message
    game_state.messages["Unknown"].append(
        {
            "sender":game_state.player_name,
            "text":selected_choice["text"],
        }
    )
    
    queue_contact_messages(
        game_state,
        "Unknown",
        unknown_data["response"],
        typing_duration=1200,
    )
    
    game_state.pending_choices=[]
    game_state.unknown_intro_done=True
    game_state.unknown_is_active=False
    
    game_state.set_contact_active("Unknown",False)

def run_martha_llm(game_state_snapshot, game_state):
    try:
        result = generate_martha_response(
            game_state_snapshot
        )

    except Exception as error:
        print("Martha LLM failed:", error)
        result = (
            "Sorry... I can't think clearly right now."
        )

    game_state.martha_result = result
    game_state.martha_waiting = False


def run_evaluator(
    evaluator_snapshot,
    player_message,
    game_state,
):
    try:
        result = evaluate_player_message(
            evaluator_snapshot,
            player_message,
        )

    except Exception as error:
        print("Evaluator failed:", error)

        result = {
            "investigation_progress_delta": 0,
            "repeated_question": False,
            "category": "qwen_failed",
            "reason": str(error),
        }

    game_state.evaluator_result = result
    game_state.evaluator_waiting = False
def handle_player_message_to_martha(
    game_state,
    player_message,
):
    player_message = player_message.strip()

    if not player_message:
        return

    # Prevent another message while Martha is generating.
    if game_state.martha_waiting:
        print("Martha is still generating a response.")
        return

    # Take evaluator snapshot BEFORE storing the newest message.
    # This prevents it from treating the current message as repeated.
    evaluator_snapshot = deepcopy(game_state)

    # Store the player message in the real conversation.
    game_state.messages["Martha"].append(
        {
            "sender": game_state.player_name,
            "text": player_message,
        }
    )

    # Martha's snapshot includes the newest player message.
    martha_snapshot = deepcopy(game_state)

    game_state.martha_waiting = True
    game_state.martha_result = None

    game_state.evaluator_waiting = True
    game_state.evaluator_result = None

    game_state.martha_thread = threading.Thread(
        target=run_martha_llm,
        args=(
            martha_snapshot,
            game_state,
        ),
        daemon=True,
    )

    game_state.evaluator_thread = threading.Thread(
        target=run_evaluator,
        args=(
            evaluator_snapshot,
            player_message,
            game_state,
        ),
        daemon=True,
    )

    game_state.martha_thread.start()
    game_state.evaluator_thread.start()

def apply_evaluation(game_state, evaluation):
    if game_state.chapter_transition_active:
        return

    if evaluation.get("category") == "qwen_failed":
        return

    progress_delta = evaluation.get(
        "investigation_progress_delta",
        0,
    )

    if evaluation.get(
        "repeated_question",
        False,
    ):
        progress_delta = 0

    game_state.investigation_progress += (
        progress_delta
    )

    print(
        "Progress +",
        progress_delta,
        "=>",
        game_state.investigation_progress,
    )

    # Anonymous appears as a scripted story event,
    # not as an evaluator result.
    maybe_unlock_unknown_intro(game_state)

    check_chapter_checkpoint(game_state)

def maybe_unlock_unknown_intro(game_state):
    if game_state.unknown_unlocked:
        return

    # Temporary Chapter 1 trigger:
    # Anonymous appears once the player has started
    # speaking with Martha.
    player_messages = [
        message
        for message in game_state.messages["Martha"]
        if message.get("sender")
        == game_state.player_name
    ]

    if len(player_messages) >= 2:
        unlock_unknown_intro(game_state)

def check_chapter_checkpoint(game_state):
    if game_state.chapter_checkpoint_reached:
        return
    checkpoint=game_state.chapter_data["checkpoint"]
    required_progress=checkpoint["investigation_progress_required"]
    
    if game_state.investigation_progress>=required_progress:
        trigger_chapter_ending(game_state)

def unlock_unknown_intro(game_state):
    if game_state.unknown_unlocked:
        return
    chapter_start=game_state.chapter_data["chapter_start"]
    
    game_state.unknown_unlocked=True
    game_state.unknown_is_active=True
    
    queue_contact_messages(
        game_state,
        "Unknown",
        chapter_start["messages"],
        typing_duration=1000,
    )
    unknown_choices=game_state.chapter_data.get(
        "unknown_choices",
        None,
    )
    if unknown_choices is not None:
        game_state.pending_choices=unknown_choices["choices"]
    
def update_llm_tasks(game_state):
    if (
        not game_state.martha_waiting
        and game_state.martha_result is not None
    ):
        martha_reply = game_state.martha_result
        game_state.martha_result = None
        game_state.martha_thread = None

        queue_contact_messages(
            game_state,
            "Martha",
            martha_reply,
            typing_duration=1200,
        )

    if (
        not game_state.evaluator_waiting
        and game_state.evaluator_result is not None
    ):
        evaluation = game_state.evaluator_result
        game_state.evaluator_result = None
        game_state.evaluator_thread = None
        game_state.last_evaluation = evaluation

        print("EVALUATION:", evaluation)

        apply_evaluation(
            game_state,
            evaluation,
        )

def trigger_chapter_ending(game_state):
    if game_state.chapter_checkpoint_reached:
        return
    
    game_state.chapter_checkpoint_reached=True
    ending_data=game_state.chapter_data["chapter_end"]
    if not game_state.unknown_unlocked:
        game_state.unknown_unlocked = True
        
    queue_contact_messages(
        game_state,
        "Unknown",
        ending_data["messages"],
        typing_duration=1200,
    )    

    game_state.pending_chapter_fade = True
    game_state.chapter_transition_target = ending_data["fade_to"]
    