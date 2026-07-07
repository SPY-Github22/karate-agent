# Karate Form-Correction Concierge Agent

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
- **Memory Agent** (`agents/memory_agent.py`): logs session results over time and
  reports trend data (e.g. "shoulder alignment improved over last 3 sessions").

## Setup

1. Install dependencies:
   ```bash
   pip install mediapipe opencv-python mcp
   ```
2. Run the Coach Agent test scaffold:
   ```bash
   python agents/coach_agent.py
   ```
   (This will run a manual test using sample data.)
3. Run the full pipeline with a test video:
   ```bash
   python run_pipeline.py <video_path.mp4>
   ```

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
