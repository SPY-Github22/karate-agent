# Karate Form-Correction Concierge Agent — Spec

Maps to Unit 5: Spec-Driven Production Grade Development in the Age of Vibe Coding.

## What it does
Analyzes a pre-recorded video of a single karate kata sequence and returns
specific, checkpoint-level coaching feedback, modeled on how a real coach
would review form after a rep.

## Architecture
- **Vision Agent / MCP tool** (`mcp_server/pose_tool.py`): extracts pose
  landmarks per frame via MediaPipe, computes 8 joint-angle checkpoints,
  exposed as the `analyze_pose` MCP tool.
- **Coach Agent** (`agents/coach_agent.py`): loads the `karate-form-check`
  skill on demand, compares checkpoint values to reference ranges, and
  generates specific coaching notes.
- **Skill** (`skills/karate-form-check/SKILL.md`): portable domain knowledge
  file — the checkpoint table, reference ranges, and coaching-tone rules —
  loaded only when a karate-video task is detected (progressive disclosure).
- **Memory Agent**: *in progress* — will log session results over time and
  report trend data (e.g. "shoulder alignment improved over last 3 sessions").

## Inputs / Outputs
- **Input:** single video file (mp4/mov/avi), one kata sequence, one person.
- **Output:** JSON summary — per-checkpoint pass rate + timestamped coaching
  notes.

## Explicit limitations (by design, not oversight)
- Single kata sequence only (locked in Phase 1) — not general karate form
  analysis.
- Pre-recorded video only — no live webcam / real-time feedback.
- Reference ranges are calibrated to one practitioner's own baseline clip —
  not a generalized correctness model across body types or belt levels.
- Rule-based deviation detection, not LLM judgment on raw numeric data —
  chosen for gradeability and reliability over flexibility.

## Security (Unit 4)
- File-type validation before processing (rejects non-video files).
- Frame-count cap (900 frames, ~30s) to prevent unbounded resource use on
  oversized input.
- No raw video retained beyond the analysis session.

## Status at time of submission
Core pipeline implemented: MCP pose tool (2 of 8 checkpoints fully wired,
6 stubbed with TODOs), Coach Agent with skill-loading and rule-based
deviation detection, SKILL.md complete. Memory Agent and full 8-checkpoint
coverage in progress — to be completed and re-submitted within the week.
