import sys
import os

# Add mcp_server to path so we can import pose_tool
sys.path.append(os.path.join(os.path.dirname(__file__), "mcp_server"))
from pose_tool import analyze_pose, CHECKPOINT_IDS

def calibrate(video_path):
    print(f"Running calibration on {video_path}...")
    try:
        frames = analyze_pose(video_path)
    except Exception as e:
        print(f"Error analyzing pose: {e}")
        return

    if not frames:
        print("No frames returned.")
        return

    stats = {
        key: {"min": float('inf'), "max": float('-inf'), "sum": 0, "count": 0}
        for key in frames[0]["checkpoints"].keys()
        if any(key.startswith(c) for c in CHECKPOINT_IDS)
    }

    for frame in frames:
        for key, value in frame["checkpoints"].items():
            if key in stats:
                stats[key]["min"] = min(stats[key]["min"], value)
                stats[key]["max"] = max(stats[key]["max"], value)
                stats[key]["sum"] += value
                stats[key]["count"] += 1

    print("\nCalibration Results (Min | Max | Avg):")
    for key, stat in stats.items():
        if stat["count"] > 0:
            avg = stat["sum"] / stat["count"]
            print(f"{key}: Min={stat['min']:.2f}, Max={stat['max']:.2f}, Avg={avg:.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python calibrate.py <path_to_video>")
    else:
        calibrate(sys.argv[1])
