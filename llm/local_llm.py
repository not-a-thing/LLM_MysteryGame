import requests

OLLAMA_URL="http://localhost:11434/api/generate"
MODEL_NAME="qwen3:1.7b"

def call_local_llm(prompt, timeout=180):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "30m",
            "options": {
                "temperature": 0.1,
                "num_predict": 250,
                "num_ctx": 2048
            },
        },
        timeout=timeout,
    )

    response.raise_for_status()
    data = response.json()

    # print("FULL OLLAMA DATA:")
    # print(data)

    return data.get("response", "")

def warm_up_local_llm():
    print("Warming up local LLM...")
    try:
        response=requests.post(
            OLLAMA_URL,
            json={
                "model":MODEL_NAME,
                "prompt":"/no_think\nReply with only: ready",
                "stream":False,
                "keep_alive":"30m",
                "options":{
                    "temperature":0,
                    "num_predict":10,
                },
            },
            timeout=180,
        )
        response.raise_for_status()
        print("Local LLM is ready.")
    except Exception as error:
        print("Could not warm up local LLM: ")
        print(error)
        