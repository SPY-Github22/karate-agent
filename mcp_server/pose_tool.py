"""
MCP server exposing pose analysis as a callable tool.
Maps to Unit 2 - Agent Tools & Interoperability (MCP).

This wraps MediaPipe pose extraction + joint-angle computation as a single
MCP tool: analyze_pose(video_path) -> list[FrameAngles]

Fill in the MediaPipe calls where marked. This file is structured so the
Vision Agent logic (Phase 2 of your build plan) lives here, and the Coach
Agent (coach_agent.py) calls it ONLY through the MCP interface, not directly.
"""

from mcp.server.fastmcp import FastMCP
import cv2
import mediapipe as mp
import math

mcp = FastMCP("karate-pose-tool")

mp_pose = mp.solutions.pose

# Checkpoint definitions matching skills/karate-form-check/SKILL.md
CHECKPOINT_IDS = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]


def _angle_between(a, b, c):
    """Angle at point b, formed by points a-b-c, in degrees."""
    ang = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    )
    return abs(ang) if abs(ang) <= 180 else 360 - abs(ang)


def _extract_checkpoints(landmarks) -> dict:
    """
    Convert raw MediaPipe landmarks into the 8 checkpoint values.
    TODO: replace placeholder indices with your actual reference-clip
    calibration once Phase 1 baseline is recorded.
    """
    lm = landmarks.landmark

    # Example: shoulder line vs hip line (C1) — placeholder math
    left_shoulder = (lm[11].x, lm[11].y)
    right_shoulder = (lm[12].x, lm[12].y)
    left_hip = (lm[23].x, lm[23].y)
    right_hip = (lm[24].x, lm[24].y)

    shoulder_slope = math.degrees(
        math.atan2(right_shoulder[1] - left_shoulder[1], right_shoulder[0] - left_shoulder[0])
    )
    hip_slope = math.degrees(
        math.atan2(right_hip[1] - left_hip[1], right_hip[0] - left_hip[0])
    )
    c1 = abs(shoulder_slope - hip_slope)

    # Front knee angle (C2) — placeholder, adjust left/right based on stance
    hip, knee, ankle = (lm[23].x, lm[23].y), (lm[25].x, lm[25].y), (lm[27].x, lm[27].y)
    c2 = _angle_between(hip, knee, ankle)

    # C3 spine tilt: midpoint(11,12) to midpoint(23,24) vs vertical
    mid_shoulder_x = (lm[11].x + lm[12].x) / 2
    mid_shoulder_y = (lm[11].y + lm[12].y) / 2
    mid_hip_x = (lm[23].x + lm[24].x) / 2
    mid_hip_y = (lm[23].y + lm[24].y) / 2
    dx = mid_hip_x - mid_shoulder_x
    dy = mid_hip_y - mid_shoulder_y
    c3 = abs(math.degrees(math.atan2(dx, dy)))

    # C4 rear leg extension: hip-knee-ankle angle on rear leg
    left_leg_angle = _angle_between((lm[23].x, lm[23].y), (lm[25].x, lm[25].y), (lm[27].x, lm[27].y))
    right_leg_angle = _angle_between((lm[24].x, lm[24].y), (lm[26].x, lm[26].y), (lm[28].x, lm[28].y))
    c4 = max(left_leg_angle, right_leg_angle)

    # C5 hip rotation timing: shoulder-line vs hip-line angle
    c5 = c1  # the angle itself, timing tracked across frames

    # C6 head alignment: nose(0) to shoulder-midpoint vs spine line
    c6_angle = _angle_between((mid_hip_x, mid_hip_y), (mid_shoulder_x, mid_shoulder_y), (lm[0].x, lm[0].y))
    c6 = abs(180 - c6_angle)

    # C7 guard hand position: non-punching wrist distance to torso center
    mid_torso_x = (mid_shoulder_x + mid_hip_x) / 2
    mid_torso_y = (mid_shoulder_y + mid_hip_y) / 2
    dist_left = math.hypot(lm[15].x - mid_torso_x, lm[15].y - mid_torso_y)
    dist_right = math.hypot(lm[16].x - mid_torso_x, lm[16].y - mid_torso_y)
    c7 = min(dist_left, dist_right)

    # C8 down-block angle: shoulder-elbow-wrist on blocking arm at block-completion frame
    angle_left_arm = _angle_between((lm[11].x, lm[11].y), (lm[13].x, lm[13].y), (lm[15].x, lm[15].y))
    angle_right_arm = _angle_between((lm[12].x, lm[12].y), (lm[14].x, lm[14].y), (lm[16].x, lm[16].y))
    c8 = min(angle_left_arm, angle_right_arm)

    return {
        "C1_shoulder_hip_offset_deg": round(c1, 1),
        "C2_front_knee_angle_deg": round(c2, 1),
        "C3_spine_tilt_deg": round(c3, 1),
        "C4_rear_leg_extension_deg": round(c4, 1),
        "C5_hip_rotation_angle_deg": round(c5, 1),
        "C6_head_alignment_deg": round(c6, 1),
        "C7_guard_hand_distance": round(c7, 3),
        "C8_down_block_angle_deg": round(c8, 1),
        "wrist_l_x": round(lm[15].x, 3),
        "wrist_l_y": round(lm[15].y, 3),
        "wrist_r_x": round(lm[16].x, 3),
        "wrist_r_y": round(lm[16].y, 3)
    }


@mcp.tool()
def analyze_pose(video_path: str) -> list[dict]:
    """
    Analyze a karate video clip and return per-frame checkpoint measurements.

    Args:
        video_path: path to a pre-recorded video file (mp4/mov).

    Returns:
        List of dicts, one per sampled frame:
        {"frame_index": int, "timestamp_s": float, "checkpoints": {...}}

    Security note (Unit 4): validates file type and caps frame count before
    processing to avoid unbounded resource use on malformed/oversized input.
    """
    ALLOWED_EXTENSIONS = (".mp4", ".mov", ".avi")
    MAX_FRAMES = 900  # ~30s at 30fps cap, prevents resource exhaustion

    if not video_path.lower().endswith(ALLOWED_EXTENSIONS):
        raise ValueError(f"Rejected: unsupported file type for {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Rejected: could not open video file {video_path}")

    results_out = []
    frame_idx = 0

    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5) as pose:
        while cap.isOpened() and frame_idx < MAX_FRAMES:
            success, frame = cap.read()
            if not success:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)

            if result.pose_landmarks:
                checkpoints = _extract_checkpoints(result.pose_landmarks)
                results_out.append({
                    "frame_index": frame_idx,
                    "timestamp_s": round(frame_idx / 30.0, 2),
                    "checkpoints": checkpoints,
                })

            frame_idx += 1

    cap.release()

    if not results_out:
        raise ValueError("Rejected: no pose detected in any frame — check video quality")

    return results_out


if __name__ == "__main__":
    mcp.run()
