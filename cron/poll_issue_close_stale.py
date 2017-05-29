import arrow
import logging
import os
from os.path import join, abspath, dirname

import settings
import github_api as gh

THIS_DIR = dirname(abspath(__file__))
# Hopefully this isn't overwritten on pulls
LAST_POLL_FILE = join(THIS_DIR, '..', "server/last_poll.txt")
if not os.path.exists(LAST_POLL_FILE):
    with open(LAST_POLL_FILE, 'w') as f:
        dummy_data = {"comment_ids_ran": []}
        json.dump(dummy_data, f)

__log = logging.getLogger("poll_close_stale")


def poll_issue_close_stale():
    """
    Looks through all open issues. For any open issue, if the issue is
    too old and has not been recently commented on, chaosbot issues a
    /vote close...
    """

    __log.info("Checking for stale issues...")

    api = gh.API(settings.GITHUB_USER, settings.GITHUB_SECRET)

    # Get all issues
    issues = gh.issues.get_open_issues(api, settings.URN)

    __log.info("There are currently %d open issues" % len(issues))

    for issue in issues:
        last_updated = arrow.get(issue["updated_at"])

        now = arrow.utcnow()
        delta = (now - updated).total_seconds()

        if delta > settings.ISSUE_STALE_THRESHOLD:
            __log.info("Vote close issue %d" % issue["id"])

            # leave an explanatory comment
            body = "This issue hasn't been active for a while. To keep it open, react with :-1: on the `vote close` post."
            gh.comments.leave_comment(api, settings.URN, issue["id"], body)

            # then vote to close
            body = "/vote close"
            gh.comments.leave_comment(api, settings.URN, issue["id"], body)
