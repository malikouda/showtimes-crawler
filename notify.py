import http.client, urllib
from vars import APP_TOKEN, USER_KEY


def notify(
    title: str, message: str, url: str, priority: int
) -> http.client.HTTPResponse:
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request(
        "POST",
        "/1/messages.json",
        urllib.parse.urlencode(
            {
                "token": APP_TOKEN,
                "user": USER_KEY,
                "title": title,
                "message": message,
                "url": url,
                "priority": priority,
            }
        ),
        {"Content-type": "application/x-www-form-urlencoded"},
    )
    resp = conn.getresponse()
    return resp
