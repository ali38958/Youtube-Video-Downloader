---
version: 1.0.0
name: Brutalism Media Console
description: High-contrast, utilitarian Neo-Brutalist design system for YouTube Video Downloader
colors:
  bg-canvas: "#0F0F12"
  bg-surface: "#18181C"
  bg-surface-elevated: "#222228"
  bg-surface-sunken: "#08080A"
  
  border-bold: "#2E2E38"
  border-highlight: "#FFE600"
  border-subtle: "#1F1F26"
  
  accent-yellow: "#FFE600"
  accent-cyan: "#00F0FF"
  accent-red: "#FF3B30"
  accent-green: "#00E676"
  accent-purple: "#BD00FF"
  
  text-primary: "#FFFFFF"
  text-secondary: "#9E9EA8"
  text-muted: "#5A5A66"
  text-on-accent: "#000000"

typography:
  brand-title:
    fontFamily: "Segoe UI Black, Impact, sans-serif"
    fontSize: "18px"
    fontWeight: 900
    letterSpacing: "0.05em"
  section-header:
    fontFamily: "Segoe UI, sans-serif"
    fontSize: "13px"
    fontWeight: 800
    letterSpacing: "0.08em"
  body-bold:
    fontFamily: "Segoe UI, sans-serif"
    fontSize: "11px"
    fontWeight: 700
  mono-badge:
    fontFamily: "Consolas, 'Courier New', monospace"
    fontSize: "10px"
    fontWeight: 700
  mono-data:
    fontFamily: "Consolas, 'Courier New', monospace"
    fontSize: "11px"
    fontWeight: 600

rounded:
  none: "0px"
  sm: "2px"
  md: "4px"

spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"

components:
  search-bar:
    backgroundColor: "{colors.bg-surface-sunken}"
    borderColor: "{colors.accent-yellow}"
    textColor: "{colors.text-primary}"
    padding: "10px"
  action-button-primary:
    backgroundColor: "{colors.accent-yellow}"
    textColor: "{colors.text-on-accent}"
    borderWidth: "2px"
    shadowOffset: "3px 3px 0px #000000"
  action-button-secondary:
    backgroundColor: "{colors.bg-surface-elevated}"
    textColor: "{colors.text-primary}"
    borderWidth: "2px"
    shadowOffset: "2px 2px 0px #000000"
  result-card:
    backgroundColor: "{colors.bg-surface}"
    borderColor: "{colors.border-bold}"
    activeBorderColor: "{colors.accent-yellow}"
---

# Brutalism Media Console Design System

## Overview
A tactile, high-contrast Neo-Brutalist visual interface designed for high-density information display, lightning-fast video searching, playback, and queue management.

## Colors
- **Core Canvas**: `#0F0F12` with sunken viewports `#08080A`.
- **Card Panels**: `#18181C` with clean mechanical line breaks.
- **Accents**:
  - `Electric Yellow (#FFE600)` — Primary action and highlight color.
  - `Hyper Red (#FF3B30)` — Cancel, delete, and warning actions.
  - `Neon Green (#00E676)` — Download progress and completion.
  - `Electric Cyan (#00F0FF)` — Streaming and playback status.

## Typography
- **Headings & Badges**: Heavy, geometric sans-serif and monospace data fonts.
- **Utilitarian Readouts**: Monospace timecodes (`00:00 / 04:20`), bitrates, resolutions, and file sizes.

## Layout & Spatial System
- High-contrast geometric grid structure with distinct pane division.
- 0px to 2px rounded corners with sharp solid outlines.
- Clear visual hierarchy: Header Search Engine → Left Feed (Results / History) → Right Command Deck (Player & Quality Selector) → Bottom System Status Strip.

## Components & Micro-Interactions
- **Tactile Buttons**: Distinct borders with hard offsets, hover color shifts, and active depression effect.
- **Segmented Tabs**: Custom toggle bar with bold visual indicators (`[ 01 // RESULTS ]` vs `[ 02 // QUEUE & HISTORY ]`).
- **Telemetry Indicators**: Monospaced status pill tags (`[ READY ]`, `[ DOWNLOADING 8.4 MB/s ]`, `[ FINISHED ]`).

## Do's and Don'ts
- **DO**: Use sharp, well-defined borders and monospaced badges for status and metadata.
- **DO**: Use high-contrast color accents to guide user attention to primary download/watch actions.
- **DON'T**: Use soft blurred drop shadows or washed-out low-contrast gray text.
- **DON'T**: Clutter the viewport with emojis or inconsistent icon sizes.
