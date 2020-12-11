#!/bin/bash

if [ $# -eq 0 ]; then
    if [ "${DEV}" == "1" ]; then
        pip install watchdog[watchmedo]
        exec watchmedo auto-restart --recursive --pattern="*.py" --directory=wimg -- /app/run.py
    else
        exec /app/run.py
    fi
else
    exec $@
fi
