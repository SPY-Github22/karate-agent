import sys
import os

# Add mcp_server and agents to path
sys.path.append(os.path.join(os.path.dirname(__file__), "mcp_server"))
sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))

from pose_tool import analyze_pose, CHECKPOINT_IDS
from coach_agent import review_session, CHECKPOINT_NAMES
import memory_agent

def run_pipeline(video_path):
    print(f"--- Karate Form-Correction Concierge ---")
    print(f"Analyzing video: {video_path}\n")

    # 1. Vision Agent (MCP Tool) - Extract pose data
    print("1. Extracting pose data...")
    try:
        pose_frames = analyze_pose(video_path)
        print(f"   Successfully extracted {len(pose_frames)} frames.")
    except Exception as e:
        print(f"Error analyzing pose: {e}")
        return

    # 2. Coach Agent - Review session and generate feedback
    print("2. Coach Agent reviewing form...")
    session_summary = review_session(pose_frames)

    # 3. Memory Agent - Log session and get trends
    print("3. Logging session to memory...\n")
    memory_agent.log_session(session_summary)

    # 4. Print Clean Summary
    print("=" * 40)
    print("SESSION SUMMARY")
    print("=" * 40)
    
    print("\n[ PASS RATES & TRENDS ]")
    for cp_id, pass_rate in session_summary.get("checkpoint_pass_rate", {}).items():
        name = CHECKPOINT_NAMES.get(cp_id, cp_id)
        trend = memory_agent.get_trend(cp_id)
        print(f"- {name} ({cp_id}): {pass_rate*100:.0f}% pass rate | Trend: {trend}")

    print("\n[ COACHING NOTES ]")
    notes = session_summary.get("coaching_notes", [])
    if not notes:
        print("Great job! All checkpoints were within reference ranges.")
    else:
        # Group notes by timestamp or just print them nicely. We'll print the first 10 for brevity.
        for note in notes[:10]:
            print(f"[@ {note['timestamp_s']}s] {note['note']}")
        if len(notes) > 10:
            print(f"... and {len(notes) - 10} more notes.")

    print("=" * 40)
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <video_path>")
    else:
        run_pipeline(sys.argv[1])
