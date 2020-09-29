# author: Matthew Turi <mxt9495@rit.edu>
from urllib.parse import urlparse

from HTTP.RequestUtils import HTTPRequest, URI, REDIRECT_STATUS_CODES, MaxRedirectsExceededError, MAX_REDIRECTS


class Request:
    def __init__(self):
        self.FOLLOW_REDIRECTS = True

    def follow_redirect(self, orig_request, response, redirect_count):
        location = response.headers.get("Location")
        if "http://" in location or "https://" in location or "www." in location:
            new_uri = location
        else:
            prev_path = orig_request.uri.parsed.path.rsplit("/", 1)[0]
            new_uri = orig_request.uri.parsed.scheme + "://" + orig_request.uri.parsed.netloc + prev_path + "/" + location

        if redirect_count is None:
            redirect_count = 0

        if redirect_count <= MAX_REDIRECTS:
            redirect_count += 1
            r = HTTPRequest(self.parse_uri(new_uri), orig_request.method, headers=orig_request.headers,
                            data=orig_request.data).send()
            return self.response_handler(r, redirect_count=redirect_count)
        else:
            raise MaxRedirectsExceededError

    def response_handler(self, http_request, redirect_count=None):
        # Check if the response we got was a redirect
        try:
            if self.FOLLOW_REDIRECTS and int(http_request.response.status_code) in REDIRECT_STATUS_CODES:
                return self.follow_redirect(http_request, http_request.response, redirect_count)
            else:
                return http_request
        except ValueError:
            pass

    @staticmethod
    def parse_uri(uri):
        parsed_uri = urlparse(uri)

        if parsed_uri.scheme == "https":
            port = 443
        elif parsed_uri.port is not None:
            port = parsed_uri.port
        else:
            port = 80

        return URI(parsed_uri, port)

    def get(self, uri, custom_headers=None, ignore_body=False):
        if custom_headers is None:
            custom_headers = {}

        default_headers = {
            'User-Agent': 'csec-380_hw3_scraper',
            'Connection': 'close'
        }
        headers = {**default_headers, **custom_headers}

        r = HTTPRequest(self.parse_uri(uri), 'GET', headers=headers, ignore_body=ignore_body).send()

        return self.response_handler(r)

    def post(self, uri, custom_headers=None, data=None):
        if custom_headers is None:
            custom_headers = {}

        default_headers = {
            'User-Agent': 'csec-380_hw3_scraper',
            'Connection': 'close'
        }
        headers = {**default_headers, **custom_headers}

        r = HTTPRequest(self.parse_uri(uri), 'POST', headers=headers, data=data).send()

        return self.response_handler(r)
