import pygame
import threading

from helpers.text_helper import split_into_chat_bubbles
from ui.notification import show_notification

from llm.suspicion_evaluator import evaluate_player_message

def receive_message(game_state,sender,text):
    message={
        "sender":sender,
        "text":text,
    }
    
    game_state.message[sender].append(message)
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
    
def unlock_unknown_intro(game_state):
    if game_state.unknown_unlocked:
        return
    
    unknown_data=game_state.chapter_data["unknown_unlock"]
    game_state.unknown_unlocked=True
    game_state.unknown_is_active=True
    
    queue_contact_messages(game_state,"Unknown",unknown_data["messsages"],typing_duration=900)
    
    game_state.pending_choices=unknown_data["choices"]

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
    game_state.message["Unknown"].append(
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

def handle_player_message_to_martha(game_state,player_message):
    game_state.messages["Martha"].append(
        {
            "sender":game_state.player_name,
            "text":player_message
        }
    )
    evaluation=evaluate_player_message(
        game_state,
        player_message,
    )
    print("EVALUATION: ", evaluation)
    apply_evaluation(game_state,evaluation,)
    
    #Temporary Martha response
    #Later replace with Martha LLM
    martha_reply=get_temporary_martha_reply(
        game_state,
        evaluation,
    )
    queue_contact_messages(
        game_state,
        "Martha",
        martha_reply,
        typing_duration=1200,
    )

def apply_evaluation(game_state, evaluation):
    if game_state.chapter_transition_active:
        return
    
    progress_delta=evaluation.get(
        "investigation_progress_delta",
        0,
    )
    pressure_delta=evaluation.get(
        "martha_pressure_delta",
        0,
    ) 
    
    if evaluation.get("repeated_question", False):
        # Repetition can still pressure Martha,
        # but it should not farm investigation progress.
        progress_delta = min(progress_delta, 1) 
    
    game_state.investigation_progress += progress_delta
    game_state.martha_pressure += pressure_delta 
    
    print("Progress +", progress_delta, "=>", game_state.investigation_progress)
    print("Martha pressure +", pressure_delta, "=>", game_state.martha_pressure)
    
    if (evaluation.get("should_unlock_unknown", False)
        and not game_state.unknown_unlocked):
        unlock_unknown_intro(game_state)
    
    check_chapter_checkpoint(game_state)

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
    
# def apply_suspicion_points(game_state,amount):
#     if game_state.chapter_transition_active:
#         return
#     game_state.suspicion_points+=amount
#     print("Suspicion: ",game_state.suspicion_points)
#     checkpoint=game_state.chapter_data["checkpoint_suspicion"]
    
#     if (game_state.suspicion_points>=checkpoint and not game_state.chapter_checkpoint_reached):
#         trigger_chapter_ending(game_state)

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
    
def get_temporary_martha_reply(game_state, evaluation):
    pressure = game_state.martha_pressure

    if pressure >= 6:
        return (
            "Why are you questioning me like this? "
            "I cared about Sarah too. You know that."
        )

    if pressure >= 3:
        return (
            "I do not know what you want me to say. "
            "Everything about this still feels unreal."
        )

    return (
        "I still cannot believe this happened. "
        "Sarah was just here, and now everyone is talking about her like she is gone."
    )