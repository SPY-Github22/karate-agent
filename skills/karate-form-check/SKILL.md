---
name: karate-form-check
description: >
  Use this skill when the input is a video clip or frame sequence of a person
  performing a karate kata, kihon, or stance, and the user wants feedback on
  posture, alignment, or technique correctness. Triggers on: kata videos,
  stance/rep footage, requests to "check my form", "review my kata",
  "correct my posture", or any pose-comparison task involving karate
  technique. Do NOT use for general fitness/posture (non-karate) or for
  video content unrelated to martial arts technique.
---

# Karate Form-Check Skill

## Purpose

Loads karate-specific technique knowledge on demand, so the main agent
doesn't carry martial-arts domain knowledge in its default system prompt.
This keeps the base agent lightweight and lets it flex into other
specialist roles (chess review, posture-for-desk-work, etc.) without
context rot from unrelated domain knowledge sitting in every prompt.

## Scope (Locked — Phase 1 decision)

- **Form covered:** [INSERT YOUR CHOSEN KATA SEQUENCE, e.g. "Heian Shodan,
  opening 4 moves: ready stance → down-block → step-punch → turn"]
- **Input:** pre-recorded video clip only (no live webcam)
- **Output:** per-checkpoint deviation flags + natural-language coaching note

## Checkpoints

Reference ranges are placeholders — replace with values measured from your
own correct-rep clip in Phase 1.

| ID | Checkpoint | Reference Range | Common Error |
|----|-----------|------------------|--------------|
| C1 | Shoulder line vs hip line (deg offset) | 0–5° | Shoulder drops during turn |
| C2 | Front knee angle (stance) | 90–110° | Knee collapses inward or over-extends |
| C3 | Spine tilt (forward/back lean) | ±5° from vertical | Leaning forward on punch |
| C4 | Rear leg extension angle | 160–180° | Insufficient extension, weak base |
| C5 | Hip rotation timing (relative to punch frame) | within 2 frames of fist extension | Hip rotates late, weak power transfer |
| C6 | Head/neck alignment (forward head check) | within 10° of spine line | Forward head creep under fatigue |
| C7 | Guard hand position (non-punching arm) | held at ribs, elbow tucked | Arm drifts away from body |
| C8 | Down-block arm angle | 45–60° at completion | Block finishes too high/wide |

## How the Coach Agent should use this skill

1. Receive structured joint-angle JSON from the Vision Agent (via the MCP
   `analyze_pose` tool).
2. For each checkpoint above, compare the measured value to the reference
   range for the relevant frame window.
3. Flag any checkpoint outside range as a deviation.
4. For each deviation, generate ONE specific, plain-language coaching note
   referencing the checkpoint name and the correction — not generic praise
   or criticism. Example pattern: "Your [checkpoint] is [specific deviation]
   during [moment in sequence] — [specific correction]."
5. Do not flag more than the checkpoints actually measured — no invented
   feedback.
6. If all checkpoints are within range, say so plainly rather than
   manufacturing a correction.

## Notes for the agent

- This skill assumes the Vision Agent has already produced angle data —
  it does not process raw video itself.
- Reference ranges are specific to the single practitioner who recorded the
  baseline clip. This is not a generalized karate-correctness model.
- Keep coaching language close to real dojo phrasing where possible
  (e.g. "keep your guard up", "drive the hip", "sink your stance") rather
  than clinical biomechanics language — this is a coaching tone, not a
  medical report.
