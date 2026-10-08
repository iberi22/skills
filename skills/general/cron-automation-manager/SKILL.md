---
name: cron-automation-manager
description: Manage and create scheduled cron jobs, automated monitoring tasks, reminders, and periodic push notifications. Use when the user asks to create or manage any scheduled task, monitoring workflow, or automated push (daily reports, GitHub monitoring, AI news tracking, price alerts, etc.). Supports multiple delivery channels such as Feishu, Telegram, DingTalk, Slack, Discord, WhatsApp, Email, or the current chat.
version: "1.0.0"
updated: "2026-04-23"
author: swal
license: MIT
tags: automation, cron, scheduler, monitoring, notifications, reminders, task-management
---

# Cron Automation Manager

This skill acts as an automation orchestrator for OpenClaw. It helps users create, manage, and monitor cron‑based automation tasks.

## When to use

Use this skill whenever the user expresses intent related to automation, scheduled tasks, monitoring, or recurring notifications.

Typical triggers include natural language such as:

- create a scheduled task
- set up a cron job
- every day / 每天 / daily reminder
- every week / weekly report
- monitor something automatically
- send me updates periodically
- automatically check something
- build a daily or weekly report
- track news, GitHub projects, prices, or keywords
- remind me regularly
- manage or inspect existing cron jobs

## Core Capabilities

1. Create cron jobs interactively
2. Manage existing tasks (list, modify, delete)
3. Deploy template automation systems
4. Route push notifications to supported delivery channels
5. Inspect automation health and detect failing tasks

## Workflow

1. Detect automation intent
2. Ask for missing parameters (schedule, target, delivery)
3. Generate cron job configuration
4. Confirm with user
5. Deploy job using the cron tool

Default behavior: each job appends its output (job name + timestamp) to `intel/daily/YYYY-MM-DD.md`, creating the file if needed. This file is the persistent data layer for trend analysis, so 7-day, weekly and 30-day analysis jobs read from `intel/daily` instead of live searches.

Example structure:

# 2026-03-22

## Job: AI News Radar
Time: 12:00

(content)

---

## Job: GitHub Trending Radar
Time: 18:00

(content)

This ensures that all automation jobs contribute to a persistent intelligence dataset.

## Delivery Channels

On first use the system may initialize the delivery configuration automatically using:

`skills/cron-automation-manager/scripts/init-delivery-config.ps1`

This script will create `config/delivery-config.json` from the example template if it does not already exist.

Users may edit the file to enable or disable delivery channels.

Delivery routing is controlled by configuration.

Primary configuration file:

`config/delivery-config.json`

If the configuration file does not exist, users should copy the template:

`config/delivery-config.example.json`

and rename it to:

`delivery-config.json`

Cron jobs should always generate reports locally first (intel/*).
The delivery router may distribute results to enabled channels defined in the config file.

Supported channels may include:

- Feishu
- Telegram
- Discord
- Web Console
- Email
- Local Files

## Templates

Predefined automation templates live in `templates/`. These allow one‑step deployment of complex automation systems.

Currently included templates:

- AI intelligence monitoring system
- GitHub trending monitor
- keyword news monitor
- price monitoring

New templates can be added without modifying the core skill.

## Example Automations

Common automation systems that can be created using this skill:

- AI news monitoring and daily tech intelligence reports
- GitHub trending project tracking
- Keyword-based news alerts
- Cryptocurrency / stock price monitoring
- Daily reminders and habit notifications
- Weekly or monthly summary reports
- System health monitoring
