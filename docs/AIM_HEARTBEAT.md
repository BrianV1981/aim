# A.I.M. Heartbeat (System Sentinel)

The `aim-heartbeat` is a persistent infrastructure utility designed to ensure the A.I.M. ecosystem remains reachable and operative. Unlike the *Plan Pinger* (which monitors task progress), the *Heartbeat* is a system-level sentinel that ensures scheduled wake-ups, routine diagnostic checks, and persistent environmental presence.

## Operational Philosophy
The Heartbeat is the "System Clock" of A.I.M. It is typically managed by `cron` or `systemd-timers` and is responsible for ensuring that the sovereign environment does not go "stale" or "dark" during long periods of inactivity.

## Components
1.  **The Trigger:** A system-level cronjob that executes a registration script.
2.  **The Sentinel (`scripts/aim_heartbeat.py`):** A lightweight script that performs quick health checks and re-registers the A.I.M. environment in the `daemon.log`.
3.  **The Persistence:** A `cron` entry that ensures the heartbeat executes on a set schedule.

## Setup Protocol

### 1. The Sentinel Script
Ensure `scripts/aim_heartbeat.py` is configured with your environment paths.

### 2. Registering the Cronjob
To register a heartbeat (e.g., every day at 8:00 AM), add the following to your `crontab -e`:

```bash
0 8 * * * /usr/bin/python3 /home/kingb/aim/scripts/aim_heartbeat.py --log /home/kingb/aim/memory-wiki/daemon.log
```

## Maintenance & Monitoring
*   **Logs:** All heartbeats are recorded in the `daemon.log` provided at registration. 
*   **Health Checks:** If the heartbeat detects a critical failure (e.g., a missing process), it will attempt a self-repair or log an error to the Master Tracker.
