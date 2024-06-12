from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint
from datetime import datetime
import requests
from typing import Literal, Any, Callable, Dict

class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline
            self.tools: Dict[str, Callable] = {}

        def add_tool(self, name: str, function: Callable) -> None:
            self.tools[name] = function

        def execute_tool(self, name: str, *args, **kwargs) -> Any:
            if name in self.tools:
                return self.tools[name](*args, **kwargs)
            else:
                return f"Tool {name} not found."

    def __init__(self):
        super().__init__()
        self.name = "Modular Tools Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],
            },
        )
        self.tools = self.Tools(self)

        # Adding example tools
        self.tools.add_tool("get_current_time", ExampleTools.get_current_time)
        self.tools.add_tool("get_current_weather", ExampleTools.get_current_weather)
        self.tools.add_tool("calculator", ExampleTools.calculator)

    async def on_startup(self):
        print(f"on_startup:{__name__}")

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")

    async def inlet(self, body: dict, user: dict) -> dict:
        print(f"inlet:{__name__}")
        print(body)
        print(user)
        return body

    async def outlet(self, body: dict, user: dict) -> dict:
        print(f"outlet:{__name__}")
        print(body)
        print(user)
        return body

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")
        if body.get("title", False):
            print("Title Generation Request")
            return "Modular Tools Pipeline"
        print(messages)
        print(user_message)
        print(body)
        # Implement logic to use tools based on user_message or other criteria
        return f"{__name__} response to: {user_message}"
