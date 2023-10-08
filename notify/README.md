# Notify

Optional tooling to scrape server logs, and send notifications to various endpoints (webhooks).

## Setup

Copy [`keys.env.template`](./keys.env.template) file to `keys.env` (in this directory).

```bash
cp keys.env.template keys.env
```

Add apropriate keys &/or URLs.

Note: if keys are not present for a service, it will not be used.

## Running

in project path: ([`..`](..))

```bash
./mc start notify
```