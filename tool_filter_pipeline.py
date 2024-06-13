import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv
import json
import os

class Sin:
    def __init__(self):
        self.email_server = smtplib.SMTP('smtp.gmail.com', 587)
        self.email_server.starttls()
        self.email_server.login('sin.ai.mhw@gmail.com', 'Dullownation123!')

    def send_email(self, recipient, subject, message):
        msg = MIMEMultipart()
        msg['From'] = 'sin.ai.mhw@gmail.com'
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        self.email_server.sendmail('sin.ai.mhw@gmail.com', recipient, msg.as_string())

    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return None

    def write_file(self, file_path, content):
        try:
            with open(file_path, 'w') as file:
                file.write(content)
        except Exception as e:
            print(f"Error writing file: {str(e)}")

    def filter_data(self, data, criteria):
        return [item for item in data if criteria(item)]

    def send_csv(self, data, file_path):
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def send_json(self, data, file_path):
        with open(file_path, 'w') as file:
            json.dump(data, file)

    def delete_file(self, file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {str(e)}")

    def send_email_with_attachment(self, recipient, subject, message, attachment):
        msg = MIMEMultipart()
        msg['From'] = 'sin.ai.mhw@gmail.com'
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        part = MIMEApplication(attachment)
        part.add_header('Content-Disposition', 'attachment', filename='attachment.txt')
        msg.attach(part)
        self.email_server.sendmail('sin.ai.mhw@gmail.com', recipient, msg.as_string())

    def receive_email(self):
        while True:
            msg = self.email_server.wait_data()
            if msg:
                print(f"Received email: {msg['Subject']}")
            else:
                break

    def close_email_server(self):
        self.email_server.quit()

# Example usage:
sin = Sin()
sin.send_email('recipient@example.com', 'Test email', 'This is a test email.')
sin.write_file('example.txt', 'This is an example file.')
sin.read_file('example.txt')
sin.filter_data(['apple', 'banana', 'cherry'], lambda x: x.startswith('a'))
sin.send_csv([['apple', 'banana'], ['cherry', 'date']], 'example.csv')
sin.send_json([{'apple': 'fruit'}, {'banana': 'fruit'}], 'example.json')
sin.delete_file('example.txt')
sin.send_email_with_attachment('recipient@example.com', 'Test email with attachment', 'This is a test email with attachment.', open('example.txt', 'rb'))
sin.receive_email()
sin.close_email_server()
