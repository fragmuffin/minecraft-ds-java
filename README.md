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
python3 -m pip install docker-compose
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

## Online Map (Overviewer)

An online map can be generated of your world, viewable online.

```
$ ./mc map
Creating volume "minecraft-ds-java_overviewer" with default driver
Creating minecraft-ds-java_overviewer-gen_run ... done
2023-06-09 07:37:19  Welcome to Minecraft Overviewer version 0.19.10 (13c1bdd)!
2023-06-09 07:37:19  Generating textures...
2023-06-09 07:37:27  Preprocessing...
2023-06-09 07:37:34  Rendering 1909 total tiles.
 99% [=====================================] 1895 23.22t/s eta 00h 00m 00s
2023-06-09 07:38:56  Rendering complete!
2023-06-09 07:38:57  Your render has been written to '/tmp/export', open index.html to view it.
```

You can then view it on port `8088`: http://localhost:8088

<img src="doc/img/map-01-overworld.png" width=45% />

Note: Switch on/off renders such as `RENDER_CAVES`, and `RENDER_NIGHT` in the [`docker-compose.yml`](./docker-compose.yml) file. Or create your own custom configuraiton by editing [`overviewer-config.py`](./overviewer-config.py) directly.

## Backup

Backing up couldn't be simpler than:

```bash
./mc backup
```

The first time it's run, it will create a duplicate of the `./data` folder.

Each subsequent time it's run, it will only copy new, and changed files. Any files that have not chnaged since last backed up will be [hard linked](https://en.wikipedia.org/wiki/Hard_link) to the previous backup.

### Restoring a backup

If your world is somehow unrecoverable, and you would like to revert it to a previous day, simply:

- Stop the server (`./mc stop`)
- backup once more (`./mc backup`) [optional]
- delete the `./data` directory (don't be afraid)
- copy the `./backups/<folder>` to `./data`

to summarise: example restoring backup: `20230609_180237`:

```bash
$ ./mc stop
Stopping minecraft-ds-java_overviewer_1 ... done
Stopping minecraft-ds-java_ds-java_1    ... done
$ ./mc backup
...
$ rm -rf ./data
$ cp -r backups/20230609_180237 data
$ ./mc start
Starting minecraft-ds-java_overviewer_1 ... done
Starting minecraft-ds-java_ds-java_1    ... done
```

### External backup

The above backup is stored alongside the server by default. Therefore this won't protect against theft, fire, hdd-wide corruption, and more.

The best backup you can make is on a separate device, preferably in a different building.

The easiest way to do this would be to mount an external drive (capable of hard-linking), then symlink it to the `./backups` folder.

```bash
$ mv ./backups ./backups-sidelined
$ ln -s /media/<mountpoint> ./backups
$ ./mc backup
```

Then consider deleting `./backups-sidelined` in +1 month.

Note that copying `data-sidelined` to `/media/<mountpoint>` will likey take up a lot of space, as hard-linking is unlikely to directly translate to the remote filesystem.

If this dosn't suit your purposes, please ignore the `./mc backup` feature of this project, and seek your own backup solution (there's hundreds out there)

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

## `mc` Script

The [`mc`](./mc) script (short for "Minecraft") is nothing special, it's mostly a collection of `docker-compose` calls to start, stop, and perform other operations.


```
$ ./mc --help
Usage: ./mc [--help] ACTION [parameters]

Host Setup:
    $ ./mc init             Initialise config files

Containers:
  Service Control:
    $ ./mc build [service]  Builds docker containers (optional)
    $ ./mc start [service]  Start services
    $ ./mc stop [service]   Stop services
    $ ./mc down             Stops and removes running containers

  Status & Logs:
    $ ./mc show             Shows running containers
    $ ./mc logs [service]   Display and follow logs

Tooling:
  RCON Commandline Interface:
    $ ./mc rcon             RCON interface to server (must be running)

  Cron tasks
    $ ./mc map              Genreate overviewer map files
    $ ./mc backup           Create incremental backup of server
```
