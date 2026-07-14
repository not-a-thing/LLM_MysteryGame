import json
import re

from llm.local_llm import call_local_llm


VALID_CATEGORIES = {
    "casual",
    "grief",
    "broad_sarah_question",
    "timeline_question",
    "contradiction",
    "martha_behavior",
    "direct_accusation",
    "unclear",
}


CATEGORY_RULES = {
    "casual": {
        "investigation_progress_delta": 0,
        "martha_pressure_delta": 0,
        "should_unlock_unknown": False,
    },
    "grief": {
        "investigation_progress_delta": 0,
        "martha_pressure_delta": 0,
        "should_unlock_unknown": False,
    },
    "broad_sarah_question": {
        "investigation_progress_delta": 1,
        "martha_pressure_delta": 0,
        "should_unlock_unknown": False,
    },
    "timeline_question": {
        "investigation_progress_delta": 2,
        "martha_pressure_delta": 1,
        "should_unlock_unknown": True,
    },
    "contradiction": {
        "investigation_progress_delta": 2,
        "martha_pressure_delta": 2,
        "should_unlock_unknown": True,
    },
    "martha_behavior": {
        "investigation_progress_delta": 2,
        "martha_pressure_delta": 2,
        "should_unlock_unknown": True,
    },
    "direct_accusation": {
        "investigation_progress_delta": 0,
        "martha_pressure_delta": 3,
        "should_unlock_unknown": False,
    },
    "unclear": {
        "investigation_progress_delta": 0,
        "martha_pressure_delta": 0,
        "should_unlock_unknown": False,
    },
}


def extract_json(raw_text):
    if raw_text is None:
        return None

    raw_text = raw_text.strip()

    # Remove Qwen thinking sections.
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


def get_recent_chat_context(game_state, contact_name, limit=10):
    messages = game_state.messages.get(contact_name, [])
    recent_messages = messages[-limit:]
    lines = []

    for message in recent_messages:
        sender = message.get("sender", "Unknown")
        text = message.get("text", "")
        lines.append(f"{sender}: {text}")

    return "\n".join(lines)


def get_previous_player_messages(game_state, contact_name, limit=10):
    messages = game_state.messages.get(contact_name, [])
    player_messages = []

    for message in messages:
        sender = message.get("sender")
        text = message.get("text", "")

        if sender in {game_state.player_name, "Player"} and text:
            player_messages.append(text)

    return player_messages[-limit:]


def evaluate_player_message(game_state, player_message):
    recent_chat = get_recent_chat_context(
        game_state,
        "Martha",
        limit=6,
    )

    prompt = f"""
You are a message evaluator for a mystery chat game.

The player is chatting directly with Martha.

Important:
- In the player's message, "you" and "your" refer to Martha.
- "Sarah", "she", and "her" refer to Sarah.
- Evaluate only the latest player message.
- Use the recent conversation only to understand context and repetition.

Choose one category:

casual:
Greeting, small talk, or unrelated conversation.

grief:
Sadness, shock, sympathy, or concern without investigation.

broad_sarah_question:
A general question about Sarah's feelings, behavior, relationships,
problems, or things she said.

sarah_timeline:
A question about Sarah's location, actions, or movements at a specific
time.

martha_timeline:
A question about Martha's location, actions, or movements at a specific
time. Questions using "you" normally belong here when asking about
location or actions.

incident_timeline:
A general question about the timing or sequence of the incident without
focusing mainly on Sarah or Martha.

contradiction:
The player points out a conflict between Martha's statements or between
her statement and evidence.

martha_behavior:
The player questions Martha's honesty, nervousness, avoidance, or
suspicious reactions.

direct_accusation:
The player directly accuses Martha of hurting Sarah or causing the
incident.

unclear:
The message is too vague or cannot be reliably classified.

Examples:

Player: "Why did Sarah go to the classroom late at night?"
Result:
{{"category":"sarah_timeline","repeated_question":false,"reason":"The player asks about Sarah's action at a specific time."}}

Player: "Where were you that night?"
Result:
{{"category":"martha_timeline","repeated_question":false,"reason":"The player asks about Martha's location that night."}}

Player: "What happened that night?"
Result:
{{"category":"incident_timeline","repeated_question":false,"reason":"The player asks about the incident generally."}}

Player: "Did Sarah seem upset?"
Result:
{{"category":"broad_sarah_question","repeated_question":false,"reason":"The player asks generally about Sarah's behavior."}}

Player: "Why are you hiding something?"
Result:
{{"category":"martha_behavior","repeated_question":false,"reason":"The player questions Martha's honesty."}}

Player: "You pushed Sarah, didn't you?"
Result:
{{"category":"direct_accusation","repeated_question":false,"reason":"The player directly accuses Martha of hurting Sarah."}}

Repetition:
Set repeated_question to true only when the player already asked for
essentially the same information.

These are repeated:
- "Where were you that night?"
- "Where exactly were you when Sarah was hurt?"

These are not repeated:
- "Why did Sarah go to the classroom?"
- "Where were you that night?"

The first asks about Sarah. The second asks about Martha.

Recent conversation:
{recent_chat if recent_chat else "No previous conversation."}

Latest player message:
{player_message}

Return only one valid JSON object:

{{
  "category": "category name",
  "repeated_question": false,
  "reason": "One short explanation."
}}
""".strip()

    raw = call_local_llm(prompt)

    print("RAW EVALUATOR:")
    print(repr(raw))

    # Retry once with an even shorter prompt when Qwen returns nothing.
    if raw is None or not raw.strip():
        retry_prompt = f"""
The player is chatting directly with Martha.

Classify this message:
"{player_message}"

Important:
- "you" means Martha.
- Sarah means Sarah.

Categories:
casual, grief, broad_sarah_question, sarah_timeline,
martha_timeline, incident_timeline, contradiction,
martha_behavior, direct_accusation, unclear

Examples:
"Where were you that night?" = martha_timeline
"Why did Sarah go there that night?" = sarah_timeline
"What happened that night?" = incident_timeline

Return only:
{{"category":"category","repeated_question":false,"reason":"short reason"}}
""".strip()

        raw = call_local_llm(retry_prompt)

        print("RAW RETRY:")
        print(repr(raw))

    result = extract_json(raw)

    if not isinstance(result, dict) or not result:
        return {
            "investigation_progress_delta": 0,
            "martha_pressure_delta": 0,
            "repeated_question": False,
            "category": "qwen_failed",
            "reason": "Evaluator returned an empty or invalid response.",
        }

    valid_categories = {
        "casual",
        "grief",
        "broad_sarah_question",
        "sarah_timeline",
        "martha_timeline",
        "incident_timeline",
        "contradiction",
        "martha_behavior",
        "direct_accusation",
        "unclear",
    }

    category = str(
        result.get("category", "unclear")
    ).strip().lower()

    if category not in valid_categories:
        category = "unclear"

    repeated_question = to_bool(
        result.get("repeated_question", False)
    )

    category_scores = {
        "casual": {
            "progress": 0,
            "pressure": 0,
        },
        "grief": {
            "progress": 0,
            "pressure": 0,
        },
        "broad_sarah_question": {
            "progress": 1,
            "pressure": 0,
        },
        "sarah_timeline": {
            "progress": 1,
            "pressure": 0,
        },
        "martha_timeline": {
            "progress": 2,
            "pressure": 1,
        },
        "incident_timeline": {
            "progress": 1,
            "pressure": 0,
        },
        "contradiction": {
            "progress": 2,
            "pressure": 2,
        },
        "martha_behavior": {
            "progress": 1,
            "pressure": 2,
        },
        "direct_accusation": {
            "progress": 0,
            "pressure": 3,
        },
        "unclear": {
            "progress": 0,
            "pressure": 0,
        },
    }

    scores = category_scores[category]

    progress_delta = scores["progress"]
    pressure_delta = scores["pressure"]

    if repeated_question:
        progress_delta = 0

    reason = result.get(
        "reason",
        "Qwen evaluator result.",
    )

    if not isinstance(reason, str) or not reason.strip():
        reason = "Qwen evaluator result."

    return {
        "investigation_progress_delta": progress_delta,
        "martha_pressure_delta": pressure_delta,
        "repeated_question": repeated_question,
        "category": category,
        "reason": reason.strip(),
    }

def get_failed_result():
    return {
        "investigation_progress_delta": 0,
        "martha_pressure_delta": 0,
        "repeated_question": False,
        "should_unlock_unknown": False,
        "category": "qwen_failed",
        "reason": "Evaluator failed to return valid JSON.",
    }


def to_bool(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "1",
            "yes",
        }

    return bool(value)


def clamp_int(value, minimum, maximum):
    try:
        value = int(value)
    except (ValueError, TypeError):
        value = minimum

    return max(minimum, min(maximum, value))