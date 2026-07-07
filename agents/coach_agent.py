"""
Coach Agent - loads the karate-form-check skill on demand and reasons over
pose data returned by the MCP pose tool.

Maps to:
- Unit 1: agent perceive -> reason -> act loop
- Unit 2: calls analyze_pose via MCP, does not import pose logic directly
- Unit 3: loads skills/karate-form-check/SKILL.md only when video input
  triggers it (progressive disclosure, not hardcoded in system prompt)
"""

import json
from pathlib import Path

SKILL_PATH = Path(__file__).parent.parent / "skills" / "karate-form-check" / "SKILL.md"

# Reference ranges -- keep in sync with SKILL.md table.
# TODO: replace with values calibrated from your own correct-rep clip.
REFERENCE_RANGES = {
    "C1_shoulder_hip_offset_deg": (0, 5),
    "C2_front_knee_angle_deg": (90, 110),
    "C3_spine_tilt_deg": (0, 5),
    "C4_rear_leg_extension_deg": (160, 180),
    "C5_hip_rotation_angle_deg": (0, 15), # Placeholder
    "C6_head_alignment_deg": (0, 10),
    "C7_guard_hand_distance": (0, 0.2), # Distance placeholder
    "C8_down_block_angle_deg": (45, 60),
}

CHECKPOINT_NAMES = {
    "C1_shoulder_hip_offset_deg": "shoulder-hip alignment",
    "C2_front_knee_angle_deg": "front knee angle",
    "C3_spine_tilt_deg": "spine tilt",
    "C4_rear_leg_extension_deg": "rear leg extension",
    "C5_hip_rotation_angle_deg": "hip rotation timing",
    "C6_head_alignment_deg": "head alignment",
    "C7_guard_hand_distance": "guard hand position",
    "C8_down_block_angle_deg": "down-block angle",
}

CORRECTION_HINTS = {
    "C1_shoulder_hip_offset_deg": "keep your shoulders level with your hips through the turn",
    "C2_front_knee_angle_deg": "adjust your stance depth — knee angle should stay in range through the stance",
    "C3_spine_tilt_deg": "avoid leaning forward on the punch, keep back straight",
    "C4_rear_leg_extension_deg": "fully extend your rear leg to maintain a strong base",
    "C5_hip_rotation_angle_deg": "snap your hip simultaneously with your punch, avoid late rotation",
    "C6_head_alignment_deg": "keep your head up and aligned with your spine, avoid forward creep",
    "C7_guard_hand_distance": "tuck your guard elbow in and keep the non-punching hand close to your ribs",
    "C8_down_block_angle_deg": "finish your block with the arm angled between 45-60 degrees, not too high or wide",
}


def load_skill() -> str:
    """
    Progressive disclosure in action: this skill file is only read when a
    karate-video task is actually triggered, not held in the base agent's
    always-on context.
    """
    return SKILL_PATH.read_text()


def _flag_deviations(frame_checkpoints: dict) -> list[dict]:
    flags = []
    for key, value in frame_checkpoints.items():
        if key not in REFERENCE_RANGES:
            continue
        low, high = REFERENCE_RANGES[key]
        if not (low <= value <= high):
            flags.append({
                "checkpoint": key,
                "value": value,
                "expected_range": (low, high),
            })
    return flags


def _coaching_note(flag: dict) -> str:
    """
    Turns a raw deviation flag into a specific, plain-language coaching note.
    """
    name = CHECKPOINT_NAMES.get(flag["checkpoint"], flag["checkpoint"])
    hint = CORRECTION_HINTS.get(flag["checkpoint"], "adjust toward the reference range")
    low, high = flag["expected_range"]
    return (
        f"Your {name} measured {flag['value']}, outside the {low}-{high} "
        f"reference range — {hint}."
    )


def review_session(pose_frames: list[dict]) -> dict:
    """
    Main entry point. pose_frames is the list returned by the MCP
    analyze_pose tool.

    Returns a session summary: per-frame notes + overall pass/fail per
    checkpoint, ready to hand to the Memory Agent for logging.
    """
    _ = load_skill()  # confirms skill loads; full text used if wiring to an LLM call

    all_notes = []
    checkpoint_pass_count = {}
    checkpoint_total_count = {}

    for frame in pose_frames:
        flags = _flag_deviations(frame["checkpoints"])
        for key in frame["checkpoints"]:
            if key not in REFERENCE_RANGES:
                continue
            checkpoint_total_count[key] = checkpoint_total_count.get(key, 0) + 1
            if key not in [f["checkpoint"] for f in flags]:
                checkpoint_pass_count[key] = checkpoint_pass_count.get(key, 0) + 1

        for flag in flags:
            all_notes.append({
                "timestamp_s": frame["timestamp_s"],
                "note": _coaching_note(flag),
            })

    summary = {
        "total_frames_analyzed": len(pose_frames),
        "coaching_notes": all_notes,
        "checkpoint_pass_rate": {
            key: round(checkpoint_pass_count.get(key, 0) / total, 2)
            for key, total in checkpoint_total_count.items()
        },
    }
    return summary


if __name__ == "__main__":
    example_frames = [
        {"frame_index": 0, "timestamp_s": 0.0, "checkpoints": {
            "C1_shoulder_hip_offset_deg": 12.0,
            "C2_front_knee_angle_deg": 95.0,
        }},
    ]
    print(json.dumps(review_session(example_frames), indent=2))
