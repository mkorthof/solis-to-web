# Service

## wrapper

To use the `run.sh` wrapper, update `User`, `WorkingDirectory`, `PIDFile`, the script paths, and `PATH` in `solis-run.service` for your installation, install and enable:

```sh
sudo cp systemd/solis.service /etc/systemd/system/solis.service
sudo systemctl daemon-reload
sudo systemctl enable --now solis-run.service
```

## uv

Alternatively, run uv directly with systemd, update `User`, `WorkingDirectory`, and `ExecStart` in `solis.service` for your installation. Install and enable this unit instead of `solis.service`:

```sh
sudo cp systemd/solis-uv.service /etc/systemd/system/solis.service
sudo systemctl daemon-reload
sudo systemctl enable --now solis.service
```

Check status with `systemctl status solis.service` and logs with `journalctl -u solis.service` (or 'solis-uv').

The wrapper writes application logs to `solis.log`.


Do not enable both units; they start the same client and use the same PID and data files.
