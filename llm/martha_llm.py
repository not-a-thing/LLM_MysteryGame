from llm.local_llm import (call_local_llm,
                           MARTHA_MODEL)
from llm.suspicion_evaluator import get_recent_chat_context
import re

def format_list(items):
    if not items:
        return "- None"
    return "\n".join(
        f"- {item}"
        for item in items
    )
    
def clean_martha_response(raw_response):
    if raw_response is None:
        return ""

    response = raw_response.strip()

    # Remove accidental speaker prefixes.
    response = re.sub(
        r"^\s*(Martha|Assistant)\s*:\s*",
        "",
        response,
        flags=re.IGNORECASE,
    )

    # Stop if the model starts writing another character's turn.
    response = re.split(
        r"\n\s*(Player|User|Unknown|Michelle)\s*:",
        response,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    # Remove quotation marks around the whole answer.
    if (
        len(response) >= 2
        and response[0] == '"'
        and response[-1] == '"'
    ):
        response = response[1:-1].strip()

    return response.strip()

def normalize_text(text):
    return " ".join(
        text.lower().strip().split()
    )

def response_was_repeated(
    game_state,
    response,
    recent_limit=4,
):
    normalized_response = normalize_text(
        response
    )

    recent_martha_messages = [
        message.get("text", "")
        for message in game_state.messages["Martha"]
        if message.get("sender") == "Martha"
    ][-recent_limit:]

    return any(
        normalize_text(previous)
        == normalized_response
        for previous in recent_martha_messages
    )

def generate_martha_response(game_state):
    recent_chat=get_recent_chat_context(game_state,"Martha",limit=12)
    chapter_data=game_state.chapter_data or {}

    martha_control=chapter_data.get("martha_control",{},)
    
    chapter_behavior=martha_control.get("chapter_behavior","Martha responds naturally and stays in character.")
    
    known_facts = martha_control.get(
        "known_facts",
        [],
    )
    
    cover_story = martha_control.get(
        "cover_story",
        [],
    )
    
    allowed_reveals=martha_control.get("allowed_reveals",[],)
    
    blocked_reveals=martha_control.get("blocked_reveals",[],)
    
    response_rules = martha_control.get(
        "response_rules",
        [],
    )

    unknown_question_behavior = martha_control.get(
        "unknown_question_behavior",
        (
            "If the answer is not defined, Martha should "
            "say she does not know."
        ),
    )

    recent_chat = get_recent_chat_context(
        game_state,
        "Martha",
        limit=12,
    )


    prompt = f"""

You are Martha in a mystery chat game.

You are speaking directly to {game_state.player_name}.

CURRENT CHAPTER:
Chapter {game_state.chapter}: {chapter_data.get("title", "")}

MARTHA'S BEHAVIOR:
{chapter_behavior}

TRUE FACTS KNOWN TO MARTHA:
{format_list(known_facts)}

MARTHA'S COVER STORY:
{format_list(cover_story)}

INFORMATION MARTHA MAY REVEAL:
{format_list(allowed_reveals)}

INFORMATION MARTHA MUST NEVER REVEAL:
{format_list(blocked_reveals)}

GENERAL RESPONSE RULES:
{format_list(response_rules)}

UNKNOWN QUESTION BEHAVIOR:
{unknown_question_behavior}

RECENT CONVERSATION:
{recent_chat}

Respond to the newest player message.

Follow these priorities in order:

1. Never reveal blocked information.
2. Never contradict the cover story.
3. Never invent facts not present in the chapter data.
4. Answer the newest question directly when possible.
5. If the answer is unknown, say you do not know or do not remember.
6. If answering would expose the truth, deny, evade, redirect, or react emotionally.
7. Mention the dorm alibi only when relevant.
8. Do not repeat the previous reply.
9. Return only Martha's reply.
10. Use one to three short sentences.

Before answering, silently check:
- Did I answer the newest question?
- Did I invent anything?
- Did I reveal blocked information?
- Did I repeat an earlier response?

Return only Martha's reply.
""".strip()

    raw_response = call_local_llm(
        prompt,
        model=MARTHA_MODEL,
        temperature=0.45,
        num_predict=160,
        num_ctx=4096,
        repeat_penalty=1.2
    )

    response = clean_martha_response(
        raw_response
    )

    if not response:
        return (
            "I don't know. Everything about this "
            "still feels confusing."
        )

    if response_was_repeated(
        game_state,
        response,
    ):
        retry_prompt = (
            prompt
            + "\n\nYour previous draft repeated an earlier reply. "
            + "Answer the newest question directly using different wording. "
            + "Do not repeat the dorm alibi unless the question concerns "
            + "Martha's whereabouts or honesty."
        )

        retry_raw = call_local_llm(
            retry_prompt,
            temperature=0.4,
            num_predict=160,
        )

        retry_response = clean_martha_response(
            retry_raw
        )

        if retry_response:
            response = retry_response

    return response
