# Minecraft Server Java Edition

A quick and clean way to setup a minecraft java server using docker.

## Overview

Aims:

- minimal setup effort
- unrestricted potential (setup now, tweak later)
- incremental backups
- map generated & http hosted (using [overviewer](https://overviewer.org))

## Getting Started

### Hardware and Operating System

This guide will assume you're running a debian-based server (eg: [ubuntu server](https://ubuntu.com/download/server)) that's always online.
However technically this will work on any OS that can run `docker` (and `python` for the initial setup)

### Install Docker & Python

```bash
sudo apt update
sudo apt install docker-ce python3 python3-pip
```

If you want to automate initialisation, you'll also need
some python libraries.

```bash
python3 -m pip install -r scripts/requirements.txt
```

### Generate Config Files

Before we start the server, you'll need to create a few setup files.

```bash
./mc init
```

This will ask you a few questions, but will randomise everything if you don't provide answers.

Note: randomising a password may be a good idea, since it will be harder to guess.

### Start Server

```bash
./mc start
```

This will take a while the first time, because it needs to

1. download docker image(s)
1. minecraft server,
1. plugins.

Progress of step 1 will be visible, but everything running inside the container will not.

To see the server's running comentary of what it's doing (or possibly how it failed), observe the logs with:

```bash
./mc logs
```

Then press `[Ctrl]+[C]` to stop viewing the logs.

### Join Server

From your minecraft client, connect to your server.

Note: to demonstrate, I'm connecting to my local machine (127.0.0.1),
but ideally you would put your domain, or static WAN IP here.

<img src="doc/img/client-join-01-multiplayer.png" width=45% /> <img src="doc/img/client-join-02-add-server.png" width=45% />

<img src="doc/img/client-join-03-server-address.png" width=45% /> <img src="doc/img/client-join-04-server-list.png" width=45% />

<img src="doc/img/client-join-05-joined-the-game.png" width=45% /> <img src="doc/img/client-join-06-permission.png" width=45% />


If you're watching the server logs, you should see your joining the game acknowledged with:

```
ds-java_1         | [06:57:59 INFO]: UUID of player FraggyMuffin is 067b17c6-661a-4451-bde3-9722c8afbc3a
ds-java_1         | [06:57:59 INFO]: FraggyMuffin joined the game
ds-java_1         | [06:57:59 INFO]: FraggyMuffin[/172.25.0.1:54406] logged in with entity id 191 at ([world]-319.6642708784545, 80.0, 318.05661385317035)
ds-java_1         | [07:14:18 INFO]: FraggyMuffin issued server command: /co i
```

Note: the server is completely open by default, allowing anyone can join. We'll fix this in the next step.

### Make Yourself an `op`

Only an `op` can grant permissions, and there is no `op`... to get around this you can run a command on the server directly using RCON.

Using RCON we'll do the following

- Add you as an `op`
- Enable `whitelist`
- Add you to the `whitelist` (technically not necessary, because you're an `op`, but it feels like the right thing to do)

```bash
./mc rcon
Using config file: /root/.rcon-cli.env
> op FraggyMuffin
Made FraggyMuffin a server operator
> whitelist on
Whitelist is now turned on
> whitelist add FraggyMuffin
Added FraggyMuffin to the whitelist
> 
```

Press `[Ctrl]+[D]` to exit the RCON-CLI. This is likely the only time you'll need to access RCON in this way. All future commands can be done inside minecraft itself.

## Cron Jobs

Aim:

- Backup daily (clear out after 30 days)
- Generate map (CPU intensive, do during expected downtime)

When running `./mc init` in the previous section, a `tasks.cron` file will have been crated.

Now copy this to `/etc/cron.d/` to tell cron what to do and when.

```bash
sudo cp tasks.cron /etc/cron.d/minecraft.cron
sudo systemctl restart cron.service
```