#!/bin/bash

function rollback() {
    # avoid commits from the same faulty PR
    rb_commit=$(git log --author chaosbot --format=format:%H | tail -n +2 | head -n 1)
    echo "Rollback to commit $rb_commit" >&2
    git reset --hard $rb_commit

    # make supervisord re-read its config because we might have changed that
    supervisorctl reread
    supervisorctl restart chaos
}

# time the chaos server... if it crashes in 60s, then attempt a rollback
start_time=`date +%s`
/root/.virtualenvs/chaos/bin/python chaos.py
failed=$?
time_elasped=`expr $(date +%s) - $start_time`

if [ "$failed" -ne 0 ] && [ "$time_elasped" -le 60 ]; then
    echo "Crashed in less than 60 seconds!" >&2
    rollback
else
    if [ "$failed" -ne 0 ]; then
        echo "Ah! We crashed! Not attempting rollback. Exiting :'(" >&2
    else
        # I don't think this can happen, but just for good measure...
        echo "Uh, wat? We exited gracefully? Not attempting rollback. Exiting." >&2
    fi
fi

