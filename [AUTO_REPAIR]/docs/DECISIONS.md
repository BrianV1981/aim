# Architectural Decisions (ADR)

This document records the major decisions that shape the project.

## 1. Baseline Initialization
- **Status:** Accepted
- **Context:** Initial workspace setup.
- **Decision:** Use A.I.M. as the primary context layer.

## 2. Dynamic Installer (2026-03-19)
- **Status:** Accepted
- **Decision:** Move all templates into the installer script to keep the repository lean and professional.
- **Consequence:** Repository contains only logic; identity is generated locally.
