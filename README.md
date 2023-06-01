# Minecraft Server Java Edition

## Overview

Aims:
    - minimal setup effort
    - unrestricted potential (setup now, tweak later)
    - backups
    - map generated & http hosted (using overviewer)

## Getting Started

- install tools:
    - docker
    - python -m pip install -r requirements.txt
- setup.py
- docker-compose up

- ./rcon
    - op <your minecraft user>

- join with client (at least to test, and start playing)


## Cron Jobs

- Tasks:
    - Backup daily (clear out after 30 days)
    - Generate map (CPU intensive, do during expected downtime)
- Where to symlink tasks.cron

## Expose Online
- commands in minecraft
    - whitelist on

which ports to expose (and port forward)

