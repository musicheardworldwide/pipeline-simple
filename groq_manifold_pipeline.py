import os
import requests
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
from schemas import OpenAIChatMessage

class Valves(BaseModel):
        GROQ_API_BASE_URL: str = "https://api.groq.com/openai/v1"
        GROQ_API_KEY: str = "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"

class Pipeline:
    def __init__(self):
        self.type = "manifold"
        self.id = "groq"
        self.name = "Groq: "
        self.valves = Valves(GROQ_API_KEY=os.getenv("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"))
        self.pipelines = self.get_models()
    
    async def on_startup(self):
        print(f"on_startup:{__name__}")
    
    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
    
    async def on_valves_updated(self):
        print(f"on_valves_updated:{__name__}")
        self.pipelines = self.get_models()
    
    def get_models(self):
        if self.valves.GROQ_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {self.valves.GROQ_API_KEY}", "Content-Type": "application/json"}
                response = requests.get(f"{self.valves.GROQ_API_BASE_URL}/models", headers=headers)
                response.raise_for_status()
                models = response.json()
                return [{"id": model["id"], "name": model.get("name", model["id"])} for model in models["data"]]
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                return [{"id": "error", "name": "Could not fetch models from Groq, please update the API Key in the valves."}]
        else:
            return []

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")
        print(messages)
        print(user_message)

        headers = {"Authorization": f"Bearer {self.valves.GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {**body, "model": model_id}
        payload.pop("user", None)
        payload.pop("chat_id", None)
        payload.pop("title", None)

        print(payload)
        try:
            response = requests.post(f"{self.valves.GROQ_API_BASE_URL}/chat/completions", json=payload, headers=headers, stream=True)
            response.raise_for_status()
            if body.get("stream"):
                return response.iter_lines()
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"
