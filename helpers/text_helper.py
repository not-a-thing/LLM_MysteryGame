import re

def split_into_chat_bubbles(text,max_length=80):
    """
    Split long LLM text into shorter chat message bubbles

    """
    if not text:
        return
    #Normalize spaces
    text=" ".join(text.split())
    
    #Split by sentence endings
    sentences=re.split(r"(?<=[.!?])\s+",text)
    
    bubbles=[]
    current=""
    
    for sentence in sentences:
        if not sentence:
            continue
        if len(current)+len(sentence)+1<=max_length:
            current=f"{current} {sentence}".strip()
        else:
            if current:
                bubbles.append(current)
            current=sentence
    if current:
        bubbles.append(current)
    return bubbles