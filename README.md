# Karate Form-Correction Concierge Agent

This is a capstone project for Google's 5-Day AI Agents Intensive course. It analyzes a pre-recorded video of a single karate kata sequence and provides specific, checkpoint-level coaching feedback, modeled after how a real coach would review form.

## Architecture

The system is composed of several specialized components working together:

1. **Vision Agent (MCP Tool)** (`mcp_server/pose_tool.py`)
   - Uses MediaPipe to extract pose landmarks from each frame of the video.
   - Computes 8 specific joint-angle checkpoints (e.g., spine tilt, knee angle).
   - Exposed as an MCP tool (`analyze_pose`).

2. **Coach Agent** (`agents/coach_agent.py`)
   - Loads the `karate-form-check` skill (domain knowledge) on demand.
   - Compares the measured checkpoint values against reference ranges.
   - Generates specific, plain-language coaching notes based on rule-based deviations.

3. **Memory Agent** (`agents/memory_agent.py`)
   - Logs session results to a JSON file (`data/sessions.json`).
   - Tracks historical pass rates across sessions and reports improvement trends.

## Setup & Execution

### Prerequisites

Ensure you have Python installed, then install the necessary dependencies:

```bash
pip install opencv-python mediapipe mcp
```

### Calibration (One-time Setup)

Before using the pipeline on practice footage, you need to calibrate the reference ranges using a baseline "perfect form" clip.

```bash
python calibrate.py <path_to_baseline_video.mp4>
```
Take the output values from this script and update `REFERENCE_RANGES` in `agents/coach_agent.py` and `skills/karate-form-check/SKILL.md`.

### Running the Pipeline

Analyze a video by running the full pipeline:

```bash
python run_pipeline.py <path_to_video.mp4>
```

This will output a clean summary of your performance, including pass rates, historical trends, and specific coaching notes for any deviations detected.
