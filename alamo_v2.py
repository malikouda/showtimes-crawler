import logging, random, os
from time import sleep
from pathlib import Path
from collections import namedtuple
from datetime import datetime

import requests

from notify import notify

Show = namedtuple(
    "Show", ["event_type", "super_title", "title", "date_start", "date_end"]
)

logging.basicConfig(
    filename="logs/showtimes_v2.txt",
    format="%(asctime)s :: %(levelname)s :: %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)


# This function chunks text but won't chunk in the middle of a line
def chunk_respect_line_break(text, chunk_size):
    if not text:
        return None
    if not text.endswith("\n"):
        text += "\n"
    start_idx = 0
    end_idx = 0
    chunks = []

    while end_idx < len(text):
        end_idx = text.rfind("\n", start_idx, chunk_size + start_idx) + 1
        chunks.append(text[start_idx:end_idx])
        start_idx = end_idx

    return chunks


def crawl():
    border = "-" * 10
    logging.info("{0} BEGIN ALAMO APPLICATION {0}".format(border))

    random_sleep_time = random.randint(1, 5)
    logging.info("Sleeping for %s seconds", random_sleep_time)
    sleep(random_sleep_time)

    url = "https://drafthouse.com/s/mother/v2/schedule/market/austin"

    try:
        data = requests.get(url).json()["data"]

        presentations = data["presentations"]
        sessions = data["sessions"]
        shows = dict()
        for p in presentations:
            # Get first and last date for showings
            dates = [
                s["businessDateClt"]
                for s in sessions
                if s["presentationSlug"] == p["slug"]
            ]

            if dates:
                date_start, date_end = min(dates), max(dates)
            else:
                date_start, date_end = None, None

            # Unpacking nested data
            show = Show(
                # eventType and superTitle are always present but may contain nulls,
                # so 'or {}' avoids returning a NoneType to the chained .get() call
                event_type=(p.get("eventType") or {}).get("title"),
                super_title=(p.get("superTitle") or {}).get("superTitle"),
                title=p["show"]["title"],
                date_start=date_start,
                date_end=date_end,
            )
            shows[p["slug"]] = show

        # A 'slug' in this case is a unique str identifier for the presentation
        # Get existing slugs from text file and convert to set for set ops
        shows_file = "films_v2.txt"
        if os.path.exists(shows_file):
            with open(shows_file, "r") as f:
                existing_show_slugs = set(f.read().splitlines())
        else:
            file_path = Path(shows_file)
            file_path.touch()
            existing_show_slugs = set()

        # Turn the retrieved slugs into a set for set ops
        current_show_slugs = set(slug for slug in shows.keys())
        # Get all the new shows by subtracting the existing shows from the retrieved shows
        new_show_slugs = current_show_slugs - existing_show_slugs

        # Get the title for every new show
        shows_to_notify = [shows[slug] for slug in new_show_slugs]

        overlapping_tags = ["Movie Party"]

        new_shows_titles = []
        for show in shows_to_notify:
            msg = ""
            # Some event types / super titles heavily overlap
            # For example, event type "Movie Party" and super title "Movie Parties"
            # These are redundant, so just use the event type in cases like this
            if (
                show.event_type
                and show.super_title
                and (
                    show.event_type
                    == show.super_title  # Event type and super title are the same
                    or f"{show.event_type}s"
                    == show.super_title  # Event type is the simple plural of super title
                    or f"{show.event_type}"
                    in overlapping_tags  # Manual override for certain event types
                    or f"{show.super_title}"
                    in overlapping_tags  # Manual override for certain super titles
                )
            ):
                msg += f"[{show.event_type}] "
            else:  # otherwise, use both as "tags"
                if show.event_type:
                    msg += f"[{show.event_type}] "
                if show.super_title:
                    msg += f"[{show.super_title}] "
            msg += show.title

            IN_FORMAT = "%Y-%m-%d"
            OUT_FORMAT = "%b %d"

            if show.date_start or show.date_end:
                date_start = datetime.strptime(show.date_start, IN_FORMAT)
                date_end = datetime.strptime(show.date_end, IN_FORMAT)

                if date_start == date_end:
                    msg += " (" + datetime.strftime(date_start, OUT_FORMAT) + ")"
                else:
                    msg += (
                        " ("
                        + datetime.strftime(date_start, OUT_FORMAT)
                        + "-"
                        + datetime.strftime(date_end, OUT_FORMAT)
                        + ")"
                    )

            else:
                msg += " (no dates yet)"

            new_shows_titles.append(msg)

        # Takes all the generated titles with tags and turns them into a list with line breaks, sorted by title
        new_shows_notification_msg = "\n".join((sorted(new_shows_titles)))

        # Pushover can only handle 1024 characters at a time, so chunk to that size if necessary
        messages = chunk_respect_line_break(new_shows_notification_msg, 1024)

        if messages:
            logging.info(
                f"Found {len(new_show_slugs)} new films of {len(current_show_slugs)} total."
            )
            for i, message in enumerate(messages):
                sleep(1)
                notification_title = f"{len(new_show_slugs)} New Film{'s' if len(new_show_slugs) > 1 else ''} Found at the Alamo Drafthouse"
                logging.info(f"Sending notification: {notification_title}")
                if len(messages) > 1:
                    notification_title += f" ({i+1}/{len(messages)})"
                notify(
                    title=notification_title,
                    message=message.strip(),
                    priority=0,
                    # url=url,
                )
        else:
            logging.info(f"No new films found. Found {len(current_show_slugs)} films.")

        # Generate list to write to output file to compare to next time
        current_shows_slug_str = "\n".join(sorted(list(current_show_slugs)))

        # Overwrite existing list of shows with current list
        with open(shows_file, "w") as f:
            f.write(current_shows_slug_str)

    except Exception as e:
        logging.error("There was a problem while running the program: %s", str(e))
        notify(
            "Alamo Drafthouse Scraper Error",
            message=f"Scraper had an error: {str(e)}",
            priority=1,
        )

    logging.info("{0} END ALAMO APPLICATION {0}".format(border))


if __name__ == "__main__":
    crawl()
