#!/usr/bin/env python3
"""Start AI Orchestrator CLI."""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == '__main__':
    from ai_orchestrator.cli import main
    main()
