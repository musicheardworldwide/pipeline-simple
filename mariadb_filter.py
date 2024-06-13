import os
import requests
import paramiko
import ftplib
import mysql.connector

from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint


class MariaDBConnection:
    def __init__(self, host: str, user: str, password: str, database: str):
        """
        Initialize the MariaDB connection.
        :param host: The host of the MariaDB server.
        :param user: The username to use for authentication.
        :param password: The password to use for authentication.
        :param database: The database to connect to.
        """
        self.conn = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query: str, params: tuple = None):
        """
        Execute a query on the MariaDB server.
        :param query: The SQL query to execute.
        :param params: The parameters to pass to the query.
        :return: The results of the query.
        """
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor.fetchall()

    def close_connection(self):
        """
        Close the MariaDB connection.
        """
        self.conn.close()


class Authenticator:
    def __init__(self, mariadb_connection: MariaDBConnection):
        """
        Initialize the Authenticator.
        :param mariadb_connection: An instance of MariaDBConnection.
        """
        self.mariadb_connection = mariadb_connection

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate a user.
        :param username: The username to authenticate.
        :param password: The password to authenticate.
        :return: True if the user is authenticated, False otherwise.
        """
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        results = self.mariadb_connection.execute_query(query, (username, password))
        return bool(results)


class ShortTermMemory:
    def __init__(self, mariadb_connection: MariaDBConnection):
        """
        Initialize the ShortTermMemory.
        :param mariadb_connection: An instance of MariaDBConnection.
        """
        self.mariadb_connection = mariadb_connection

    def store_data(self, data: str) -> bool:
        """
        Store data in short-term memory.
        :param data: The data to store.
        :return: True if the data is stored successfully.
        """
        query = "INSERT INTO short_term_memory (data) VALUES (%s)"
        self.mariadb_connection.execute_query(query, (data,))
        return True

    def retrieve_data(self) -> list:
        """
        Retrieve data from short-term memory.
        :return: The retrieved data.
        """
        query = "SELECT * FROM short_term_memory"
        return self.mariadb_connection.execute_query(query)


class LongTermMemory:
    def __init__(self, mariadb_connection: MariaDBConnection):
        """
        Initialize the LongTermMemory.
        :param mariadb_connection: An instance of MariaDBConnection.
        """
        self.mariadb_connection = mariadb_connection

    def store_data(self, data: str) -> bool:
        """
        Store data in long-term memory.
        :param data: The data to store.
        :return: True if the data is stored successfully.
        """
        query = "INSERT INTO long_term_memory (data) VALUES (%s)"
        self.mariadb_connection.execute_query(query, (data,))
        return True

    def retrieve_data(self) -> list:
        """
        Retrieve data from long-term memory.
        :return: The retrieved data.
        """
        query = "SELECT * FROM long_term_memory"
        return self.mariadb_connection.execute_query(query)


class Embeddings:
    def __init__(self, mariadb_connection: MariaDBConnection):
        """
        Initialize the Embeddings.
        :param mariadb_connection: An instance of MariaDBConnection.
        """
        self.mariadb_connection = mariadb_connection

    def store_embedding(self, embedding: str) -> bool:
        """
        Store an embedding.
        :param embedding: The embedding to store.
        :return: True if the embedding is stored successfully.
        """
        query = "INSERT INTO embeddings (embedding) VALUES (%s)"
        self.mariadb_connection.execute_query(query, (embedding,))
        return True

    def retrieve_embedding(self) -> list:
        """
        Retrieve embeddings.
        :return: The retrieved embeddings.
        """
        query = "SELECT * FROM embeddings"
        return self.mariadb_connection.execute_query(query)


class RAG:
    def __init__(self, mariadb_connection: MariaDBConnection):
        """
        Initialize the RAG.
        :param mariadb_connection: An instance of MariaDBConnection.
        """
        self.mariadb_connection = mariadb_connection

    def store_rag(self, rag: str) -> bool:
        """
        Store a RAG.
        :param rag: The RAG to store.
        :return: True if the RAG is stored successfully.
        """
        query = "INSERT INTO rag (rag) VALUES (%s)"
        self.mariadb_connection.execute_query(query, (rag,))
        return True

    def retrieve_rag(self) -> list:
        """
        Retrieve RAGs.
        :return: The retrieved RAGs.
        """
        query = "SELECT * FROM rag"
        return self.mariadb_connection.execute_query(query)


class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline
            self.mariadb_connection = None

        def make_http_request(self, url: str) -> str:
            """
            Make an HTTP request to a URL.
            :param url: The URL to make the request to.
            :return: The response from the server.
            """
            try:
                response = requests.get(url)
                return response.text
            except requests.RequestException as e:
                return f"Error making HTTP request: {str(e)}"

        def make_https_request(self, url: str) -> str:
            """
            Make an HTTPS request to a URL.
            :param url: The URL to make the request to.
            :return: The response from the server.
            """
            try:
                response = requests.get(url, verify=False)
                return response.text
            except requests.RequestException as e:
                return f"Error making HTTPS request: {str(e)}"

        def connect_to_ssh(self, host: str, username: str, password: str) -> str:
            """
            Connect to an SSH server.
            :param host: The hostname or IP address of the SSH server.
            :param username: The username to use for the SSH connection.
            :param password: The password to use for the SSH connection.
            :return: A success message if the connection is successful.
            """
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=host, username=username, password=password)
                return f"Connected to SSH server {host} as {username}"
            except paramiko.SSHException as e:
                return f"Error connecting to SSH server: {str(e)}"

        def upload_file_via_sftp(self, host: str, username: str, password: str, local_file: str, remote_file: str) -> str:
            """
            Upload a file via SFTP.
            :param host: The hostname or IP address of the SFTP server.
            :param username: The username to use for the SFTP connection.
            :param password: The password to use for the SFTP connection.
            :param local_file: The local file to upload.
            :param remote_file: The remote file to upload to.
            :return: A success message if the upload is successful.
            """
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, username=username, password=password)
                sftp = ssh.open_sftp()
                sftp.put(local_file, remote_file)
                sftp.close()
                ssh.close()
                return f"Uploaded file '{local_file}' to '{remote_file}'"
            except paramiko.SSHException as e:
                return f"Error uploading file: {str(e)}"

        def download_file_via_sftp(self, host: str, username: str, password: str, remote_file: str, local_file: str) -> str:
            """
            Download a file via SFTP.
            :param host: The hostname or IP address of the SFTP server.
            :param username: The username to use for the SFTP connection.
            :param password: The password to use for the SFTP connection.
            :param remote_file: The remote file to download.
            :param local_file: The local file to save the download to.
            :return: A success message if the download is successful.
            """
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, username=username, password=password)
                sftp = ssh.open_sftp()
                sftp.get(remote_file, local_file)
                sftp.close()
                ssh.close()
                return f"Downloaded file '{remote_file}' to '{local_file}'"
            except paramiko.SSHException as e:
                return f"Error downloading file: {str(e)}"

        def connect_to_ftp(self, host: str, username: str, password: str) -> str:
            """
            Connect to an FTP server.
            :param host: The hostname or IP address of the FTP server.
            :param username: The username to use for the FTP connection.
            :param password: The password to use for the FTP connection.
            :return: A success message if the connection is successful.
            """
            try:
                ftp = ftplib.FTP(host)
                ftp.login(username, password)
                return f"Connected to FTP server {host} as {username}"
            except ftplib.all_errors as e:
                return f"Error connecting to FTP server: {str(e)}"

        def upload_file_via_ftp(self, host: str, username: str, password: str, local_file: str, remote_file: str) -> str:
            """
            Upload a file via FTP.
            :param host: The hostname or IP address of the FTP server.
            :param username: The username to use for the FTP connection.
            :param password: The password to use for the FTP connection.
            :param local_file: The local file to upload.
            :param remote_file: The remote file to upload to.
            :return: A success message if the upload is successful.
            """
            try:
                ftp = ftplib.FTP(host)
                ftp.login(username, password)
                with open(local_file, 'rb') as file:
                    ftp.storbinary(f"STOR {remote_file}", file)
                return f"Uploaded file '{local_file}' to '{remote_file}'"
            except ftplib.all_errors as e:
                return f"Error uploading file: {str(e)}"

        def download_file_via_ftp(self, host: str, username: str, password: str, remote_file: str, local_file: str) -> str:
            """
            Download a file via FTP.
            :param host: The hostname or IP address of the FTP server.
            :param username: The username to use for the FTP connection.
            :param password: The password to use for the FTP connection.
            :param remote_file: The remote file to download.
            :param local_file: The local file to save the download to.
            :return: A success message if the download is successful.
            """
            try:
                ftp = ftplib.FTP(host)
                ftp.login(username, password)
                with open(local_file, 'wb') as file:
                    ftp.retrbinary(f"RETR {remote_file}", file.write)
                return f"Downloaded file '{remote_file}' to '{local_file}'"
            except ftplib.all_errors as e:
                return f"Error downloading file: {str(e)}"

        def connect_to_mariadb(self, host: str, user: str, password: str, database: str):
            """
            Connect to MariaDB.
            :param host: The host of the MariaDB server.
            :param user: The username to use for authentication.
            :param password: The password to use for authentication.
            :param database: The database to connect to.
            """
            self.mariadb_connection = MariaDBConnection(host, user, password, database)

        def authenticate_user(self, username: str, password: str) -> bool:
            """
            Authenticate a user.
            :param username: The username to authenticate.
            :param password: The password to authenticate.
            :return: True if the user is authenticated, False otherwise.
            """
            self.authenticator = Authenticator(self.mariadb_connection)
            return self.authenticator.authenticate_user(username, password)

        def store_short_term_memory(self, data: str) -> bool:
            """
            Store data in short-term memory.
            :param data: The data to store.
            :return: True if the data is stored successfully.
            """
            self.short_term_memory = ShortTermMemory(self.mariadb_connection)
            return self.short_term_memory.store_data(data)

        def retrieve_short_term_memory(self) -> list:
            """
            Retrieve data from short-term memory.
            :return: The retrieved data.
            """
            self.short_term_memory = ShortTermMemory(self.mariadb_connection)
            return self.short_term_memory.retrieve_data()

        def store_long_term_memory(self, data: str) -> bool:
            """
            Store data in long-term memory.
            :param data: The data to store.
            :return: True if the data is stored successfully.
            """
            self.long_term_memory = LongTermMemory(self.mariadb_connection)
            return self.long_term_memory.store_data(data)

        def retrieve_long_term_memory(self) -> list:
            """
            Retrieve data from long-term memory.
            :return: The retrieved data.
            """
            self.long_term_memory = LongTermMemory(self.mariadb_connection)
            return self.long_term_memory.retrieve_data()

        def store_embedding(self, embedding: str) -> bool:
            """
            Store an embedding.
            :param embedding: The embedding to store.
            :return: True if the embedding is stored successfully.
            """
            self.embeddings = Embeddings(self.mariadb_connection)
            return self.embeddings.store_embedding(embedding)

        def retrieve_embedding(self) -> list:
            """
            Retrieve embeddings.
            :return: The retrieved embeddings.
            """
            self.embeddings = Embeddings(self.mariadb_connection)
            return self.embeddings.retrieve_embedding()

        def store_rag(self, rag: str) -> bool:
            """
            Store a RAG.
            :param rag: The RAG to store.
            :return: True if the RAG is stored successfully.
            """
            self.rag = RAG(self.mariadb_connection)
            return self.rag.store_rag(rag)

        def retrieve_rag(self) -> list:
            """
            Retrieve RAGs.
            :return: The retrieved RAGs.
            """
            self.rag = RAG(self.mariadb_connection)
            return self.rag.retrieve_rag()

    def __init__(self):
        super().__init__()
        self.name = "My Tools Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
            },
        )
        self.tools = self.Tools(self)
