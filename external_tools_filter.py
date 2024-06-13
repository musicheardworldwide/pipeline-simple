import os
import requests
import paramiko
import ftplib
from typing import Literal

from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint


class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

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
