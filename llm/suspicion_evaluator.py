import json
import re
from llm.local_llm import call_local_llm

def extract_json(raw_text):
    if raw_text is None:
        return None

    raw_text = raw_text.strip()

    raw_text = re.sub(
        r"<think>.*?</think>",
        "",
        raw_text,
        flags=re.DOTALL,
    ).strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    start = raw_text.find("{")
    end = raw_text.rfind("}")

    if start != -1 and end != -1 and end > start:
        possible_json = raw_text[start:end + 1]

        try:
            return json.loads(possible_json)
        except json.JSONDecodeError:
            pass

    return None

def get_recent_chat_context(game_state,contact_name,limit=10):
    messages=game_state.messages.get(contact_name,[])
    recent_messages=messages[-limit:]
    lines=[]
    
    for message in recent_messages:
        sender=message["sender"]
        text=message["text"]
        lines.append(f"{sender}:{text}")
    return "\n".join(lines)

def evaluate_player_message(game_state, player_message):
    recent_chat = get_recent_chat_context(
        game_state,
        "Martha",
        limit=6,
    )
    
    prompt = f"""
    You are a hidden evaluator for a mystery chat game.

    You must return one JSON object.
    Do not write anything before or after the JSON.

    Story truth:
    Sarah was found unconscious in a classroom.
    Martha secretly pushed Sarah.
    The player does not know Martha is responsible.

    Recent Martha conversation:
    {recent_chat}

    Latest player message:
    {player_message}

    Evaluate the latest player message.

    Use this scoring:

    investigation_progress_delta:
    0 = casual, emotional, repeated, or unrelated
    1 = broad question about Sarah or what happened
    2 = asks about timeline, classroom, accident, contradiction, missing details, or Martha's behavior
    3 = directly accuses Martha or corners her

    martha_pressure_delta:
    0 = no pressure
    1 = mild pressure
    2 = defensive pressure
    3 = direct accusation

    Return JSON in exactly this structure:

    {{
    "investigation_progress_delta": 1,
    "martha_pressure_delta": 0,
    "repeated_question": false,
    "should_unlock_unknown": true,
    "category": "broad_sarah_question",
    "reason": "The player asks what happened to Sarah."
    }}
    """

#     prompt = f"""
# Return only valid JSON.

# You are a hidden evaluator for a mystery chat game.

# Story truth:
# Sarah was found unconscious in a university classroom.
# Martha secretly pushed Sarah during an argument.
# Sarah hit a desk or table.
# Martha believes Sarah died.
# Martha is pretending to be devastated.
# The player does not know Martha is responsible.

# Current chapter: {game_state.chapter}
# Investigation progress: {game_state.investigation_progress}
# Martha pressure: {game_state.martha_pressure}
# Unknown unlocked: {game_state.unknown_unlocked}

# Recent Martha conversation:
# {recent_chat}

# Latest player message:
# {player_message}

# Evaluate the latest player message based on meaning and recent context.

# investigation_progress_delta:
# 0 = casual, emotional, repeated, unrelated, or does not investigate
# 1 = broad question about Sarah or what happened
# 2 = asks about timeline, classroom, accident, contradiction, missing details, or Martha's behavior
# 3 = directly accuses Martha, corners her, or exposes a major inconsistency

# martha_pressure_delta:
# 0 = no pressure
# 1 = mild discomfort
# 2 = defensive pressure
# 3 = direct accusation or serious threat to Martha's cover

# Rules:
# If the player repeats the same question without adding new pressure, investigation_progress_delta should be 0.
# If the player repeats a question but challenges Martha's avoidance, progress can be 1 and pressure can be higher.
# Do not reveal or invent story events.

# Return exactly this JSON object:
# {{
#   "investigation_progress_delta": 0,
#   "martha_pressure_delta": 0,
#   "repeated_question": false,
#   "should_unlock_unknown": false,
#   "category": "casual",
#   "reason": "short private reason"
# }}
# """

    raw = call_local_llm(prompt)
    print("RAW EVALUATOR:")
    print(raw)

    result = extract_json(raw)
    
    if result == {}:
        print("Qwen returned empty JSON.")
        result = None
        
    if result is None:
        return {
            "investigation_progress_delta": 0,
            "martha_pressure_delta": 0,
            "repeated_question": False,
            "should_unlock_unknown": False,
            "category": "casual",
            "reason": "Evaluator failed to return valid JSON."
        }

    result["investigation_progress_delta"] = clamp_int(
        result.get("investigation_progress_delta", 0),
        0,
        3,
    )

    result["martha_pressure_delta"] = clamp_int(
        result.get("martha_pressure_delta", 0),
        0,
        3,
    )

    result["repeated_question"] = to_bool(
        result.get("repeated_question", False)
    )

    result["should_unlock_unknown"] = to_bool(
        result.get("should_unlock_unknown", False)
    )

    if "category" not in result:
        result["category"] = "unknown"

    if "reason" not in result:
        result["reason"] = "No reason returned."

    return result

def to_bool(value):
    if isinstance(value,bool):
        return value
    if isinstance(value,str):
        return value.lower()=="true"
    
    return bool(value)

def clamp_int(value, minimum, maximum):
    try:
        value = int(value)
    except (ValueError, TypeError):
        value = minimum

    return max(minimum, min(maximum, value))