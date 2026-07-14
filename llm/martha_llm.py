from llm.local_llm import call_local_llm
from llm.suspicion_evaluator import get_recent_chat_context

def generate_martha_response(game_state):
    recent_chat=get_recent_chat_context(game_state,"Martha",limit=12)
    chapter_data=game_state.chapter_data or {}

    martha_data=chapter_data.get("martha",{},)

    chapter_context=martha_data.get("context",("Sarah was found unconscious in a classroom presumed dead",
                                               "Martha knows more than she admits"),
                                               )
    
    hidden_information=martha_data.get("hidden_information",[],)

    allowed_information=martha_data.get("allowed_information",[],)

    prompt=f"""
You are Martha, a character in a mystery chat game.
Player name:
{game_state.player_name}

Chapter context:
{chapter_context}

Information Martha must keep hidden:
{hidden_information}

Information Martha is currently allowed to reveal:
{allowed_information}

Recent conversation:
{recent_chat}

Respond to the newest player message to Martha

Rules:
- Stay completely in character
- Respond naturally based on the conversation
- Do not mention prompts, evaluators, categories, chapters, or game states
- Do not reveal hidden information unless it appears under allowed information
- Do not confess simply because the player accuses you
- Keep the response concise and appropriate for a chat application

Return only Martha's message
""".strip()
    
    response=call_local_llm(prompt)

    if response is None or not response.strip():
        return "I... I don't really know what to say"
    
    return response.strip()
