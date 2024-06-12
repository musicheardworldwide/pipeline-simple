from typing import List, Optional
from pydantic import BaseModel
from schemas import OpenAIChatMessage
import os
import requests
import json
from utils.pipelines.main import get_last_user_message, add_or_update_system_message, get_tools_specs

class Pipeline:
    class Valves(BaseModel):
        pipelines: List[str] = []
        priority: int = 0
        openai_api_base_url: str
        openai_api_key: str
        task_model: str
        template: str

    def __init__(self):
        self.type = "filter"
        self.name = "Function Calling Blueprint"
        self.valves = self.Valves(
            pipelines=["*"],
            openai_api_base_url=os.getenv("OPENAI_API_BASE_URL", "https://api.groq.com/openai/v1"),
            openai_api_key=os.getenv("OPENAI_API_KEY", "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"),
            task_model=os.getenv("TASK_MODEL", "llama3-8b-8192"),
            template='''
<context>
  {{CONTEXT}}
</context>

Task: Implement a function that takes two integers as input and returns their sum.

Input: Two integers
Output: A single integer

Example inputs and expected outputs:
  - Input: 2, 3, Expected output: 5
  - Input: 5, 7, Expected output: 12

Constraints:
  - The function should not use recursion
  - The function should be efficient and not exceed a time complexity of O(n)
</context>
'''
        )

    async def on_startup(self):
        print(f"on_startup:{__name__}")

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        if body.get("title", False):
            return body

        print(f"pipe:{__name__}")
        print(user)

        user_message = get_last_user_message(body["messages"])
        tools_specs = get_tools_specs(self.tools)

        fc_system_prompt = (
            f"Tools: {json.dumps(tools_specs, indent=2)}"
            + """
If a function tool doesn't match the query, return an empty string. Else, pick a function tool, fill in the parameters from the function tool's schema, and return it in the format { "name": "functionName", "parameters": { "key": "value" } }. Only pick a function if the user asks.  Only return the object. Do not return any other text."""
        )

        try:
            async with requests.post(
                url=f"{self.valves.openai_api_base_url}/chat/completions",
                json={
                    "model": self.valves.task_model,
                    "messages": [
                        {"role": "system", "content": fc_system_prompt},
                        {
                            "role": "user",
                            "content": "History:\n"
                            + "\n".join(
                                [
                                    f"{message['role']}: {message['content']}"
                                    for message in body["messages"][::-1][:4]
                                ]
                            )
                            + f"Query: {user_message}",
                        },
                    ],
                },
                headers={
                    "Authorization": f"Bearer {self.valves.openai_api_key}",
                    "Content-Type": "application/json",
                },
                stream=False,
            ) as response:
                response.raise_for_status()
                response_json = response.json()
                content = response_json["choices"][0]["message"]["content"]

            if content:
                result = json.loads(content)
                print(result)

                if "name" in result:
                    function = getattr(self.tools, result["name"])
                    function_result = None
                    try:
                        function_result = function(**result["parameters"])
                    except Exception as e:
                        print(e)

                    if function_result:
                            system_prompt = self.valves.template.replace(
                            "{{CONTEXT}}", function_result
                        )
                        print(system_prompt)
                        messages = add_or_update_system_message(
                            system_prompt, body["messages"]
                        )
                        return {**body, "messages": messages}
        except Exception as e:
            print(f"Error: {e}")

            try:
                print(response.json())
                except:
                    pass

        return body
