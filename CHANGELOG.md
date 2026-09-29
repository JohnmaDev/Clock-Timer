# Changelog

All notable changes to **Clock & Timer** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] - 2026-09-28

### 🐛 Bug Fixes
- **Notifications**: Fixed desktop notification freeze on Linux where the banner remained stuck indefinitely on the screen due to `-u critical`. Urgency is now set to `normal`, strictly honoring the 5-second automatic timeout (`-t 5000`).
- **Notifications**: Fixed missing application title and generic system gear icon (`⚙`) in desktop alerts by explicitly passing `--app-name="Clock & Timer"` (`-a`) and the application icon (`-i`).
- **Window Positioning**: Fixed window recentering bug when toggling between standard mode and Mini-HUD mode. The window now remembers and restores the exact user-defined screen position with multi-monitor boundary clamping.
- **UI Layout**: Fixed button text clipping ("Reanud", "Reinicia", "Borra") in compact widths by transitioning to modern minimalist icons (`▶`, `⏸`, `↺`, `🗑`).
- **Dialog Controls**: Fixed broken spinbox arrows in the Time Setup dialog by implementing dedicated auto-repeating stepper cards and quick chip buttons.

### 🚀 New Features & Enhancements
- **System Tray Integration**: Added background system tray icon (`^`) with a contextual menu to toggle visibility, switch between Clock and Timer modes, and exit cleanly.
- **Windows Native Notifications**: Integrated `QSystemTrayIcon.showMessage()` providing native Windows 10/11 Action Center toast notifications with app branding and sound.
- **Minimalist Icon Navigation**: Streamlined tab navigation using intuitive clock (`🕒`) and hourglass (`⏳`) icons with full localized tooltips.
- **Executable Naming**: Standardized Windows executable naming to `Clock & Timer.exe` to match the Linux and AppStream metadata identity.

---

## [1.1.1] - 2026-09-27

### 🎨 UI & UX Improvements
- **Dual Click-or-Drag Gestures**: Implemented GNOME-style dual click-or-drag interaction on navigation tabs and time displays.
- **Window Movement**: Enabled smooth full-window dragging from anywhere across Wayland, X11, and Windows.

---

## [1.1.0] - 2026-09-27

### 🚀 New Features & Enhancements
- **Mini-HUD Focus Mode**: Added ultra-compact Mini-HUD mode with integrated horizontal controls for clutter-free workflows.
- **Dynamic Font Autoscaling**: Implemented responsive font scaling for multi-hour displays.
- **Quick Presets**: Added `+1h` preset button alongside `+1m`, `+5m`, `+15m`, and `+25m`.
- **Quick Clear**: Added dedicated Clear (Trash) button to reset time to `00:00` instantly.
- **Unified Header**: Redesigned minimalist header with unified collapsible Settings panel for opacity and language selection.

---

## [1.0.0] - 2026-09-27

### 🚀 Initial Release
- **Always-on-Top Floating Widget**: Resizable frameless desktop dialog with smooth rounded corners.
- **Clock Mode**: Responsive 12h/24h digital clock with localized calendar date.
- **Timer Mode**: Countdown timer with presets, audio alerts, and desktop notifications.
- **Opacity Control**: Interactive opacity slider and mouse wheel brightness adjustment.
- **Bilingual Support**: Instant hot-switching between Spanish and English.
