#!/bin/bash

activate_path="/app/.venv/bin/activate"
if [[ -f $activate_path ]]; then
    echo "source $activate_path" >> /root/.bashrc
fi
exec /bin/bash