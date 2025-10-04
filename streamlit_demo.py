#!/usr/bin/env python3
"""Launcher to run the Streamlit app from the app package."""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit app."""
    # Get the path to the streamlit app
    app_path = Path(__file__).parent / "app" / "streamlit_app.py"

    # Run streamlit with the app - use Popen to keep it running
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.headless", "true"]
    subprocess.Popen(cmd)

if __name__ == "__main__":
    main()
