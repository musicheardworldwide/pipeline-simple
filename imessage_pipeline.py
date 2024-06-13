import requests
from function_calling_blueprint import Pipeline as FunctionCallingBlueprint
import os


class iCloudConnection:
    def __init__(self, api_key: str):
        """
        Initialize the iCloud connection.
        :param api_key: The API key for iCloud/iMessage authentication.
        """
        self.api_key = api_key
        self.base_url = "https://api.icloud.com"

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate the user with iCloud/iMessage.
        :param username: The username for authentication.
        :param password: The password for authentication.
        :return: True if authentication is successful, False otherwise.
        """
        response = requests.post(
            f"{self.base_url}/auth",
            json={"username": username, "password": password, "api_key": self.api_key},
        )
        return response.status_code == 200

    def send_imessage(self, recipient: str, message: str) -> bool:
        """
        Send an iMessage.
        :param recipient: The recipient of the iMessage.
        :param message: The message to send.
        :return: True if the message is sent successfully, False otherwise.
        """
        response = requests.post(
            f"{self.base_url}/imessage/send",
            json={"recipient": recipient, "message": message, "api_key": self.api_key},
        )
        return response.status_code == 200

    def retrieve_imessages(self) -> list:
        """
        Retrieve iMessages.
        :return: A list of retrieved iMessages.
        """
        response = requests.get(
            f"{self.base_url}/imessage/retrieve", params={"api_key": self.api_key}
        )
        if response.status_code == 200:
            return response.json().get("messages", [])
        return []

    def list_icloud_files(self) -> list:
        """
        List iCloud files.
        :return: A list of iCloud files.
        """
        response = requests.get(
            f"{self.base_url}/icloud/files", params={"api_key": self.api_key}
        )
        if response.status_code == 200:
            return response.json().get("files", [])
        return []

    def upload_icloud_file(self, file_path: str) -> bool:
        """
        Upload a file to iCloud.
        :param file_path: The path of the file to upload.
        :return: True if the file is uploaded successfully, False otherwise.
        """
        with open(file_path, "rb") as file:
            response = requests.post(
                f"{self.base_url}/icloud/upload",
                files={"file": file},
                data={"api_key": self.api_key},
            )
        return response.status_code == 200

    def download_icloud_file(self, file_name: str, save_path: str) -> bool:
        """
        Download a file from iCloud.
        :param file_name: The name of the file to download.
        :param save_path: The local path to save the downloaded file.
        :return: True if the file is downloaded successfully, False otherwise.
        """
        response = requests.get(
            f"{self.base_url}/icloud/download",
            params={"file_name": file_name, "api_key": self.api_key},
            stream=True,
        )
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True
        return False


class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        ICLOUD_API_KEY: str = ""

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline
            self.icloud_connection = iCloudConnection(
                self.pipeline.valves.ICLOUD_API_KEY
            )

        def authenticate_icloud_user(self, username: str, password: str) -> str:
            """
            Authenticate a user with iCloud/iMessage.
            :param username: The username to authenticate.
            :param password: The password to authenticate.
            :return: Success or failure message.
            """
            if self.icloud_connection.authenticate(username, password):
                return "User authenticated successfully!"
            return "Authentication failed."

        def send_imessage(self, recipient: str, message: str) -> str:
            """
            Send an iMessage.
            :param recipient: The recipient of the iMessage.
            :param message: The message to send.
            :return: Success or failure message.
            """
            if self.icloud_connection.send_imessage(recipient, message):
                return f"Message sent to {recipient} successfully!"
            return "Failed to send message."

        def retrieve_imessages(self) -> list:
            """
            Retrieve iMessages.
            :return: A list of retrieved iMessages.
            """
            return self.icloud_connection.retrieve_imessages()

        def list_icloud_files(self) -> list:
            """
            List iCloud files.
            :return: A list of iCloud files.
            """
            return self.icloud_connection.list_icloud_files()

        def upload_icloud_file(self, file_path: str) -> str:
            """
            Upload a file to iCloud.
            :param file_path: The path of the file to upload.
            :return: Success or failure message.
            """
            if self.icloud_connection.upload_icloud_file(file_path):
                return f"File '{file_path}' uploaded successfully!"
            return "Failed to upload file."

        def download_icloud_file(self, file_name: str, save_path: str) -> str:
            """
            Download a file from iCloud.
            :param file_name: The name of the file to download.
            :param save_path: The local path to save the downloaded file.
            :return: Success or failure message.
            """
            if self.icloud_connection.download_icloud_file(file_name, save_path):
                return f"File '{file_name}' downloaded successfully to '{save_path}'!"
            return "Failed to download file."

    def __init__(self):
        super().__init__()
        self.name = "iCloud/iMessage Tools Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
                "ICLOUD_API_KEY": os.getenv("ICLOUD_API_KEY", ""),
            },
        )
        self.tools = self.Tools(self)

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

    async def inlet(self, body: dict, user: dict) -> dict:
        # This function is called before the OpenAI API request is made.
        print(f"inlet:{__name__}")

        print(body)
        print(user)

        return body

    async def outlet(self, body: dict, user: dict) -> dict:
        # This function is called after the OpenAI API response is completed.
        print(f"outlet:{__name__}")

        print(body)
        print(user)

        return body

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is where you can add your custom pipelines like RAG.
        print(f"pipe:{__name__}")

        # If you'd like to check for title generation, you can add the following check
        if body.get("title", False):
            print("Title Generation Request")

        print(messages)
        print(user_message)
        print(body)

        response = "Unknown command."
        if "authenticate" in user_message:
            username, password = user_message.replace("authenticate ", "").split()
            response = self.tools.authenticate_icloud_user(username, password)
        elif "send" in user_message:
            recipient, message = user_message.replace("send ", "").split(maxsplit=1)
            response = self.tools.send_imessage(recipient, message)
        elif "retrieve" in user_message:
            response = "\n".join(self.tools.retrieve_imessages())
        elif "list files" in user_message:
            response = "\n".join(self.tools.list_icloud_files())
        elif "upload" in user_message:
            file_path = user_message.replace("upload ", "")
            response = self.tools.upload_icloud_file(file_path)
        elif "download" in user_message:
            file_name, save_path = user_message.replace("download ", "").split()
            response = self.tools.download_icloud_file(file_name, save_path)

        return response
