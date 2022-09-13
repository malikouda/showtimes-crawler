import http.client, urllib
from config import settings


def notify(
    title: str, message: str, priority: int = 0, url: str = ""
) -> http.client.HTTPResponse:
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request(
        "POST",
        "/1/messages.json",
        urllib.parse.urlencode(
            {
                "token": settings.PUSHOVER_APP_TOKEN,
                "user": settings.PUSHOVER_USER_KEY,
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
