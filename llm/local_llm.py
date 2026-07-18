import requests

OLLAMA_URL="http://localhost:11434/api/generate"
EVALUATOR_MODEL="qwen3:1.7b"
MARTHA_MODEL="qwen3:4b"

def call_local_llm(
    prompt,
    model,
    timeout=180,
    temperature=0.1,
    num_predict=300,
    num_ctx=4096,
    repeat_penalty=1.1,
):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "keep_alive": "30m",
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
                "num_ctx": num_ctx,
                "repeat_penalty":repeat_penalty,
                "repeat_last_n":128,
                "top_p":0.9,
            },
        },
        timeout=timeout,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("response", "")

def warm_up_model(model_name):
    print(f"Warming up {model_name}...")

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model_name,
                "prompt": "Reply only with: ready",
                "stream": False,
                "think": False,
                "keep_alive": "30m",
                "options": {
                    "temperature": 0,
                    "num_predict": 10,
                },
            },
            timeout=180,
        )

        response.raise_for_status()
        print(f"{model_name} is ready.")

    except Exception as error:
        print(
            f"Could not warm up {model_name}:",
            error,
        )
        
def warm_up_local_llms():
    warm_up_model(EVALUATOR_MODEL)
    warm_up_model(MARTHA_MODEL)        