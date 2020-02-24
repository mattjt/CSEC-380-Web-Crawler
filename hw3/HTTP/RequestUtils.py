# author: Matthew Turi <mxt9495@rit.edu>
import socket
import ssl
from urllib.parse import ParseResult

REDIRECT_STATUS_CODES = [301, 302, 307, 308]
MAX_REDIRECTS = 4


class MaxRedirectsExceededError(Exception):
    def __str__(self):
        return 'MaxRedirectsExceededError: The requested URI has exceeded {0} redirects'.format(MAX_REDIRECTS)


class URI:
    def __init__(self, uri, port):
        assert isinstance(uri, ParseResult)
        self.parsed = uri
        self.port = port


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
            # line = line.decode("utf-8")

            # status line
            if not status_line_parsed:
                line = line.decode("utf-8")
                status_line_parsed = True
                tmp = line.split(" ")
                self.http_version = tmp[0]
                self.status_code = tmp[1]
                self.reason_phrase = tmp[2]

            # other header
            elif len(line) != 0:
                line = line.decode("utf-8")
                tmp = line.split(":", 1)
                self.headers[tmp[0]] = tmp[1].strip()

        self.data = body

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

    def __init__(self, uri, method, headers=None, data=None):
        if headers is None:
            headers = {}
        if data is None:
            data = {}

        # Sanity check that we actually got a URI
        assert isinstance(uri, URI)

        self.uri = uri
        self.method = method
        self.response = ""
        self.headers = headers
        self.data = data

    def __repr__(self):
        if self.uri.parsed.query != '':
            request = "{0} {1}?{2} HTTP/1.1\r\n".format(self.method, self.uri.parsed.path, self.uri.parsed.query)
        else:
            request = "{0} {1} HTTP/1.1\r\n".format(self.method, self.uri.parsed.path)

        request += "Host: {0}\r\n".format(self.uri.parsed.netloc)

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
            s.connect((self.uri.parsed.netloc, self.uri.port))
            # s.connect(("127.0.0.1", 1337))  # TODO REMOVE BURP PROXY
            if self.uri.port == 443 or self.uri.parsed.scheme == "https":
                s = ssl.wrap_socket(s, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE,
                                    ssl_version=ssl.PROTOCOL_SSLv23)

            s.send(bytes(self.__repr__(), "utf-8"))

            fragments = []
            while True:
                chunk = s.recv(10000)
                if not chunk:
                    break
                fragments.append(chunk)

            self.response = b"".join(fragments)
            self.response = HTTPResponse(self.response)

        return [self, self.response]
