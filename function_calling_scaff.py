from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint
from typing import Any, Callable, Dict

class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        # Add your custom valves here if needed
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline
            self.tools: Dict[str, Callable] = {}

        def add_tool(self, name: str, function: Callable) -> None:
            """
            Add a tool to the pipeline.
            :param name: The name of the tool.
            :param function: The function to be used as the tool.
            """
            self.tools[name] = function

        def execute_tool(self, name: str, *args, **kwargs) -> Any:
            """
            Execute a tool by name.
            :param name: The name of the tool.
            :param args: Arguments to pass to the tool.
            :param kwargs: Keyword arguments to pass to the tool.
            :return: The result of the tool execution.
            """
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
                "pipelines": ["*"],  # Connect to all pipelines
            },
        )
        self.tools = self.Tools(self)

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        # Dynamically load tools here if needed
        # Example: self.tools.add_tool("current_time", self.tools.get_current_time)
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

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
