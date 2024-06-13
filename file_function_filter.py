import os
import requests
from typing import Literal
from datetime import datetime

from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint


class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        # Add your custom parameters here
        OPENWEATHERMAP_API_KEY: str = ""
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def get_current_time(self) -> str:
            """
            Get the current time.

            :return: The current time.
            """
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            return f"Current Time = {current_time}"

        def get_current_weather(self, location: str, unit: Literal["metric", "fahrenheit"] = "fahrenheit") -> str:
            """
            Get the current weather for a location. If the location is not found, return an empty string.

            :param location: The location to get the weather for.
            :param unit: The unit to get the weather in. Default is fahrenheit.
            :return: The current weather for the location.
            """
            if self.pipeline.valves.OPENWEATHERMAP_API_KEY == "":
                return "OpenWeatherMap API Key not set, ask the user to set it up."
            else:
                units = "imperial" if unit == "fahrenheit" else "metric"
                params = {
                    "q": location,
                    "appid": self.pipeline.valves.OPENWEATHERMAP_API_KEY,
                    "units": units,
                }

                response = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather", params=params
                )
                response.raise_for_status()  # Raises an HTTPError for bad responses
                data = response.json()

                weather_description = data["weather"][0]["description"]
                temperature = data["main"]["temp"]

                return f"{location}: {weather_description.capitalize()}, {temperature}°{unit.capitalize()[0]}"

        def calculator(self, equation: str) -> str:
            """
            Calculate the result of an equation.

            :param equation: The equation to calculate.
            """
            try:
                result = eval(equation)
                return f"{equation} = {result}"
            except Exception as e:
                print(e)
                return "Invalid equation"

        def create_folder(self, folder_name: str) -> str:
            """
            Create a new folder.
            :param folder_name: The name of the folder to create.
            :return: A success message if the folder is created successfully.
            """
            folder_path = os.path.join(os.getcwd(), folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                return f"Folder '{folder_name}' created successfully!"
            else:
                return f"Folder '{folder_name}' already exists."

        def delete_folder(self, folder_name: str) -> str:
            """
            Delete a folder.
            :param folder_name: The name of the folder to delete.
            :return: A success message if the folder is deleted successfully.
            """
            folder_path = os.path.join(os.getcwd(), folder_name)
            if os.path.exists(folder_path):
                os.rmdir(folder_path)
                return f"Folder '{folder_name}' deleted successfully!"
            else:
                return f"Folder '{folder_name}' does not exist."

        def create_file(self, file_name: str, content: str = "") -> str:
            """
            Create a new file.
            :param file_name: The name of the file to create.
            :param content: The content to write to the file.
            :return: A success message if the file is created successfully.
            """
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, "w") as file:
                file.write(content)
            return f"File '{file_name}' created successfully!"

        def delete_file(self, file_name: str) -> str:
            """
            Delete a file.
            :param file_name: The name of the file to delete.
            :return: A success message if the file is deleted successfully.
            """
            file_path = os.path.join(os.getcwd(), file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                return f"File '{file_name}' deleted successfully!"
            else:
                return f"File '{file_name}' does not exist."

        def read_file(self, file_name: str) -> str:
            """
            Read the content of a file.
            :param file_name: The name of the file to read.
            :return: The content of the file.
            """
            file_path = os.path.join(os.getcwd(), file_name)
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    content = file.read()
                return content
            else:
                return f"File '{file_name}' does not exist."

        def write_to_file(self, file_name: str, content: str) -> str:
            """
            Write content to a file.
            :param file_name: The name of the file to write to.
            :param content: The content to write to the file.
            :return: A success message if the content is written successfully.
            """
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, "w") as file:
                file.write(content)
            return f"Content written to file '{file_name}' successfully!"

        def list_files(self) -> str:
            """
            List all files in the current directory.
            :return: A list of files in the current directory.
            """
            files = os.listdir(os.getcwd())
            return "Files in the current directory:\n" + "\n".join(files)

    def __init__(self):
        super().__init__()
        self.name = "My Tools Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
                "OPENWEATHERMAP_API_KEY": os.getenv("OPENWEATHERMAP_API_KEY", ""),
            },
        )
        self.tools = self.Tools(self)
