#!/bin/bash

function rollback() {
    git checkout master
    git checkout ^HEAD
}

/root/.virtualenvs/chaos/bin/python chaos.py || rollback
