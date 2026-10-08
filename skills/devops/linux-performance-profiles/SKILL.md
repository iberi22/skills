---
name: linux-performance-profiles
description: Switchable Linux system performance profiles (gaming, sen/headless work, default) via sysfs/sysctl/Hyprland. Generic across distros and hardware.
trigger: When the user wants to tune, profile, or switch between performance modes for gaming vs headless agent work vs balanced desktop — or set this up on a new machine.
---

# Linux Performance Profiles

Generic profile-switching system for Linux. Works on any distro with:
- AMDGPU (Navi 2x / RDNA2+) for GPU tuning
- Hyprland (optional, for compositor effects strip)
- standard Linux sysfs/sysctl interface

## Architecture

```
~/.config/system-profiles/
├── system-profile       # Main switching script (Bash)
├── profiles/            # One .conf per profile
│   ├── default.conf      # Balanced, power-efficient daily driver
│   ├── gaming.conf       # Max FPS, low latency
│   └── sen.conf          # Headless, zero UI, max compile perf
└── .current_state       # State persistence (auto-managed)
```

## Usage

```bash
sudo ~/.config/system-profiles/system-profile          # list profiles
sudo ~/.config/system-profiles/system-profile current   # show current state
sudo ~/.config/system-profiles/system-profile gaming    # switch to gaming
sudo ~/.config/system-profiles/system-profile ai        # switch to AI/compute
sudo ~/.config/system-profiles/system-profile sen       # switch to headless work
sudo ~/.config/system-profiles/system-profile default   # restore balanced
```

> Most sysfs writes need root. The script handles this transparently; just run with `sudo`.

## Profile Format

Each `.conf` file is a Bash snippet setting variables:

| Variable | Purpose | Example |
|---|---|---|
| `CPU_GOVERNOR` | Scaling governor | `performance` / `schedutil` |
| `GPU_POWER_PROFILE` | AMD DPM profile index | `1` = 3D_FULL_SCREEN, `0` = BOOTUP_DEFAULT |
| `GPU_PERF_LEVEL` | AMD force perf level | `high` / `auto` / `low` |
| `GPU_POWER_LIMIT` | Power cap in µW | `120000000` = 120W. `0` = skip (driver default) |
| `SCHED_MIGRATION_COST` | sched_migration_cost_ns | `500000` |
| `SCHED_MIN_GRANULARITY` | sched_min_granularity_ns | `2000000` |
| `SCHED_WAKEUP_GRANULARITY` | sched_wakeup_granularity_ns | `1500000` |
| `VM_DIRTY_RATIO` | vm.dirty_ratio | `5` (gaming) / `20` (default) |
| `VM_DIRTY_BG_RATIO` | vm.dirty_background_ratio | `2` (gaming) / `10` (default) |
| `AUDIO_POWER_SAVE` | snd_hda_intel power_save | `0` (off) / `10` (default) |
| `MONITOR_REFRESH` | Target refresh (for display) | `200` / `144` |
| `MONITOR_MODE` | hyprctl monitor string | `1920x1080@200Hz,0x0,1` |

### Sen-mode specific:

| Variable | Purpose | Example |
|---|---|---|
| `SEN_KILL_PROCESSES` | Processes to kill | `brave firefox eww waybar` |
| `SEN_SUSPEND_PROCESSES` | Processes to SIGSTOP | `blueman-applet blueman-tray` |
| `SEN_STOP_SERVICES` | systemd --user to stop | `waybar.service` |
| `SEN_DISABLE_EFFECTS` | Strip Hyprland compositor | `true` / `false` |

## Adding a New Profile

1. Copy an existing `.conf`:
   ```bash
   cp ~/.config/system-profiles/profiles/gaming.conf ~/.config/system-profiles/profiles/my-profile.conf
   ```
2. Edit the variables to match your needs.
3. Switch to it:
   ```bash
   sudo ~/.config/system-profiles/system-profile my-profile
   ```

## Auto-detection & Fallbacks

The script detects which subsystems are available and skips missing ones:

- **AMD GPU**: finds `card*/device/pp_power_profile_mode` → tunes DPM, power limit, perf level
- **Hyprland**: detects `hyprctl` → applies monitor mode, strips/restores compositor effects
- **Audio**: checks `snd_hda_intel/power_save` exists
- **Scheduler**: uses `sysctl -w` (works on kernel 6.18+ where procfs files moved)
- **Any missing hardware**: silently skipped with warning

## Setting Up on a New Machine

1. Copy the `~/.config/system-profiles/` directory to the new machine.
2. Edit the profile `.conf` files to match the new hardware:
   - Check `cat /sys/class/drm/card*/device/pp_power_profile_mode` for available GPU profiles
   - Check `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors` for CPU governors
   - Check `cat /sys/class/drm/card*/device/hwmon/hwmon*/power1_cap_max` for max power cap
   - Check `hyprctl monitors` for monitor name and refresh rates
3. Test each profile:
   ```bash
   sudo system-profile gaming && sudo system-profile default
   ```

## Persistence (optional)

For NixOS, add to `hardware.opengl.extraPackages` and create a `systemd.services` oneshot or udev rule. For other distros, add the script to `/usr/local/bin/` and create a udev rule or a systemd service.

```
# /etc/udev/rules.d/99-gpu-profile.rules
ACTION=="add", SUBSYSTEM=="drm", KERNEL=="card1", RUN+="/usr/local/bin/system-profile gaming"
```

## Relevant Kernel Boot Parameters (Optional)

These require a reboot and go in the bootloader config:

- `amdgpu.noretry=1` — cheaper page faults for Vulkan (reduces stutter)
- `processor.max_cstate=1` — prevent deep C-state wakeup latency
- `transparent_hugepage=madvise` — THP only when requested

## Files

- `system-profile` (script): the switching engine
- `profiles/*.conf`: profile definitions

## Pitfalls

- **GPU sysfs requires root**: always run with `sudo`. The script warns if writes fail.
- **Kernel 6.18+ changed scheduler paths**: the script uses `sysctl -w` instead of direct procfs writes. If your kernel doesn't have a particular sysctl, it's silently skipped.
- **Hyprland version differences**: `hyprctl` output format may vary. If monitor detection fails, hardcode the monitor name in the profile.
- **Multiple GPUs**: the script picks the first AMD GPU it finds. For multi-GPU systems, edit `find_amd_gpu()` to target the right card.
- **Power limit clamping**: if the requested limit exceeds `power1_cap_max`, it's clamped silently.
