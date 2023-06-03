#!/usr/bin/env bash
set -eo pipefail
if [ -n "$VERBOSE" ] ; then set -x ; fi

cd $(dirname $0)

show_help() {
    [ "$@" ] && echo "$@"
cat << ENDHELPTEXT
Usage: ./${0##*/} [--help] ACTION [parameters]

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

ENDHELPTEXT
}

# ====================== Setup ======================
init() {
    # TODO: change method of support, it's a bit rude to install stuff like this.
    python -m pip install -r scripts/requirements.txt
    python scripts/setup.py "$@"
}

# ====================== Container Control ======================
build() {
    docker-compose build "$@"
}

start() {
    docker-compose up -d "$@"
}

stop() {
    docker-compose stop "$@"
}

restart() {
    stop "$@"
    start "$@"
}

down() {
    docker-compose down
}

destroy() {
    docker-compose kill "$@"
    docker-compose rm -fv "$@"
}


# ====================== Status & Logs ======================
show() {
    docker-compose ps
}

logs() {
    docker-compose logs --tail="100" -f "$@"
}


# ====================== Tools ======================
rcon() {
    docker-compose exec ds-java rcon-cli "$@"
}

map() {
    # bugfix: cron job
    # mitigation for "docker-compose: command not found"... root cause unknown
    export PATH=$PATH:/usr/local/bin
    docker-compose run --rm overviewer-gen
}

backup() {
    bash scripts/backup.sh
}

# ====================== Mainline ======================
# Option parsing
case "$1" in
    # Setup
    init)       init "${@:2}" ;;

    # Container Control:
    build)      build "${@:2}" ;;
    start)      start "${@:2}" ;;
    stop)       stop "${@:2}" ;;
    restart)    restart "${@:2}" ;;
    down)       down "${@:2}" ;;
    destroy)    destroy "${@:2}" ;;

    # Status & Logs:
    show)       show "${@:2}" ;;
    logs)       logs "${@:2}" ;;

    # Tools:
    rcon)       rcon "${@:2}" ;;
    map)        map "${@:2}" ;;
    backup)     backup "${@:2}" ;;

    # Help Text
    -h|--help|help)
        show_help
        exit 0 ;;
    *)
        show_help >&2
        exit 1 ;;
esac
