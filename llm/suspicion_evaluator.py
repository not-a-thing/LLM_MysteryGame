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

    Return only one complete JSON object.
    Do not write anything before or after the JSON.

    Story:
    Sarah was found unconscious in a classroom.
    Martha secretly pushed Sarah.
    The player does not know Martha is responsible.
    Martha is pretending to be devastated.

    Recent chat:
    {recent_chat}

    Player message:
    {player_message}

    Evaluate only the player message using the recent chat context.

    Choose exactly one category:
    - casual
    - grief
    - broad_sarah_question
    - timeline_question
    - contradiction
    - martha_behavior
    - direct_accusation
    - repeated_question

    Scoring rules:

    casual or grief:
    investigation_progress_delta = 0
    martha_pressure_delta = 0
    should_unlock_unknown = false

    broad_sarah_question:
    investigation_progress_delta = 1
    martha_pressure_delta = 0
    should_unlock_unknown = true

    timeline_question:
    investigation_progress_delta = 2
    martha_pressure_delta = 1
    should_unlock_unknown = true

    contradiction:
    investigation_progress_delta = 2
    martha_pressure_delta = 2
    should_unlock_unknown = true

    martha_behavior:
    investigation_progress_delta = 2
    martha_pressure_delta = 2
    should_unlock_unknown = true

    direct_accusation:
    investigation_progress_delta = 3
    martha_pressure_delta = 3
    should_unlock_unknown = true

    repeated_question:
    investigation_progress_delta = 0
    martha_pressure_delta = 1
    should_unlock_unknown = false

    Return JSON with these exact keys:
    {{
    "investigation_progress_delta": number,
    "martha_pressure_delta": number,
    "repeated_question": boolean,
    "should_unlock_unknown": boolean,
    "category": string,
    "reason": string
    }}
    """

    raw = call_local_llm(prompt)

    print("RAW EVALUATOR:")
    print(raw)

    result = extract_json(raw)

    if result is None or result == {}:
        return {
            "investigation_progress_delta": 0,
            "martha_pressure_delta": 0,
            "repeated_question": False,
            "should_unlock_unknown": False,
            "category": "qwen_failed",
            "reason": "Evaluator failed to return valid JSON."
        }

    return {
    "investigation_progress_delta": clamp_int(
        result.get(
            "investigation_progress_delta",
            result.get("progress", 0),
        ),
        0,
        3,
    ),
    "martha_pressure_delta": clamp_int(
        result.get(
            "martha_pressure_delta",
            result.get("pressure", 0),
        ),
        0,
        3,
    ),
    "repeated_question": to_bool(
        result.get(
            "repeated_question",
            result.get("repeat", False),
        ),
    ),
    "should_unlock_unknown": to_bool(
        result.get(
            "should_unlock_unknown",
            result.get("unlock_unknown", False),
        ),
    ),
    "category": result.get("category", "unknown"),
    "reason": result.get("reason", "Qwen evaluator result."),
}

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