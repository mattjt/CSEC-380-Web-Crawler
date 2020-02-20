# author: Matthew Turi <mxt9495@rit.edu>
from urllib.parse import urlparse

from HTTP.RequestUtils import HTTPRequest, URI, REDIRECT_STATUS_CODES, MaxRedirectsExceededError, MAX_REDIRECTS

FOLLOW_REDIRECTS = True


def follow_redirect(response, method, headers, data, redirect_count):
    new_uri = response.headers.get("Location")

    if redirect_count is None:
        redirect_count = 0

    if redirect_count <= MAX_REDIRECTS:
        redirect_count += 1
        r = HTTPRequest(parse_uri(new_uri), method, headers=headers, data=data).send()
        return response_handler(r, redirect_count=redirect_count)
    else:
        raise MaxRedirectsExceededError


def response_handler(response, redirect_count=None):
    # Check if the response we got was a redirect
    if FOLLOW_REDIRECTS and int(response[1].status_code) in REDIRECT_STATUS_CODES:
        follow_redirect(response[1], response[0].method, response[0].headers, response[0].data, redirect_count)
    else:
        return response[1]


def parse_uri(uri):
    parsed_uri = urlparse(uri)

    if parsed_uri.scheme == "https":
        port = 443
    elif parsed_uri.port is not None:
        port = parsed_uri.port
    else:
        port = 80

    return URI(parsed_uri, port)


def get(uri, custom_headers=None):
    if custom_headers is None:
        custom_headers = {}

    default_headers = {
        'User-Agent': 'csec-380_hw3_scraper'
    }
    headers = {**default_headers, **custom_headers}

    r = HTTPRequest(parse_uri(uri), 'GET', headers=headers).send()

    return response_handler(r)


def post(uri, custom_headers=None, data=None):
    if custom_headers is None:
        custom_headers = {}

    default_headers = {
        'User-Agent': 'csec-380_hw3_scraper'
    }
    headers = {**default_headers, **custom_headers}

    r = HTTPRequest(parse_uri(uri), 'POST', headers=headers, data=data).send()

    return response_handler(r)
