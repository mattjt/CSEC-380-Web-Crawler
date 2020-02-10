# author: Matthew Turi <mxt9495@rit.edu>
import socket
import time


class HTTPResponse:
    """
    Abstracted representation of an HTTP response
    """

    def __init__(self, resp_content):
        """
        :param resp_content: Raw unparsed content of an HTTP response
        """
        self.http_version = self.status_code = self.reason_phrase = ""
        self.headers = {}
        self.data = bytes()
        self.__parse(resp_content)

    def __parse(self, content):
        parts = content.split(b"\r\n\r\n", 1)
        headers = parts[0].splitlines()
        body = parts[1]

        status_line_parsed = False
        for line in headers:
            line = line.decode("utf-8")

            # status line
            if not status_line_parsed:
                status_line_parsed = True
                tmp = line.split(" ")
                self.http_version = tmp[0]
                self.status_code = tmp[1]
                self.reason_phrase = tmp[2]

            # other header
            elif len(line) != 0:
                tmp = line.split(":", 1)
                self.headers[tmp[0]] = tmp[1].strip()

        self.data = body.decode("utf-8")

    def __repr__(self):
        response = "{0} {1} {2}\r\n".format(self.http_version, self.status_code, self.reason_phrase)

        for header, value in self.headers.items():
            response += "{0}:{1}\r\n".format(header, value)

        response += "\r\n"
        response += "{0}\r\n".format(self.data)

        return response


class HTTPRequest:
    """
    Abstracted representation of an HTTP request
    """

    def __init__(self, hostname, port, method, uri, headers=None, data=None):
        if headers is None:
            headers = {}
        if data is None:
            data = {}
        self.host = hostname
        self.port = port
        self.method = method
        self.uri = uri
        self.response = ""
        self.headers = headers
        self.data = data

    def __repr__(self):
        request = "{0} {1} HTTP/1.1\r\n".format(self.method, self.uri)
        request += "Host: {0}:{1}\r\n".format(self.host, self.port)

        for header, value in self.headers.items():
            request += "{0}: {1}\r\n".format(header, value)

        if self.data is not None:
            request += "Content-Length: {0}\r\n\r\n".format(len(self.__get_msg_body()))
            request += self.__get_msg_body()
            request += "\r\n"

        request += "\r\n"

        return request

    def __get_msg_body(self):
        msg_body = ""
        for key, value in self.data.items():
            msg_body += "{0}={1}&".format(key, value)
        return msg_body

    def send(self):
        """
        Sends the HTTP request
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.send(bytes(self.__repr__(), "utf-8"))

            # Wait before receiving response because this was being buggy and not getting all the data previously
            time.sleep(0.25)

            self.response = s.recv(4096)
            self.response = HTTPResponse(self.response)

        return self.response
