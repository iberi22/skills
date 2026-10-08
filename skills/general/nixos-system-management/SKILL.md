---
name: nixos-system-management
description: "Reglas operativas NixOS SWAL (flakes+git, overlays prohibidos, puertos, offline Rust, nix profile) + router a nixos-desktop y swal-desktop-management."
version: 1.1.0-reconstructed
author: Hermes Agent (RECONSTRUCTED 2026-09-07 tras incidente skills 2026-09-06 — validar)
tags: [nixos, flakes, system, admin, swal-desktop]
related_skills: [nixos-desktop, swal-desktop-management, swal-home-manager]
---

# NixOS System Management (reglas + router)

> ⚠️ RECONSTRUCTED 2026-09-07 — cuerpo original irrecuperable tras el
> incidente de skills. Reconstruido desde memoria ecosistema + skills
> hermanos. Belal: validar antes de confiar detalles.

## Reglas duras (NixOS 25.05 estable)

1. **Flakes + Git**: fuente única `~/nixos-config` (`/etc/nixos` es symlink).
   Nix ignora archivos no trackeados → `git add` (como usuario, nunca
   `sudo git`) y luego `swal-check switch`. Detalle: skill `swal-home-manager`.
2. **Overlays inestables PROHIBIDOS en produccion** (Mesa, Glibc,
   Hyprland, Chromium): rompen keyring Brave y pila Wayland.
3. **Puertos**: `8006` Xavier · `8003` Cortex/PgHeart · `11434` Ollama.
4. **Rust offline**: `~/.cargo/config.toml` (`offline = true`); compilar
   con `cargo build/test` plano salvo OK explicito.
5. **Instalacion**: permanente = declarativo (`home.nix` usuario / `configuration.nix`
   sistema); `nix profile` solo para pruebas ad-hoc (nunca nix-env). Editor: `subl`.

## Router

- Config/depuracion desktop (Hyprland, GPU, gaming, flakes): `nixos-desktop`
  (en `software-development/`).
- Gestion SWAL Desktop (operativa diaria): `swal-desktop-management`.
- home-manager, dotfiles, rebuild seguro (`swal-check`): `swal-home-manager` (canonica).
- Cambios de sistema: proponer, verificar con `dry-build` cuando aplique,
  y pedir OK antes del `switch` real.
