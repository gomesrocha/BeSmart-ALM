#!/usr/bin/env python3
"""Start AI Orchestrator Web UI."""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == '__main__':
    import uvicorn
    
    print("🐝 Starting BeeSmart: AI Orchestrator Web UI...")
    print("📱 Open http://localhost:5010 in your browser")
    print("🤖 Using model: deepseek-coder-v2:latest")
    print("⏹️  Press Ctrl+C to stop")
    
    uvicorn.run(
        "ai_orchestrator.web_ui:app", 
        host="0.0.0.0", 
        port=5010,
        log_level="info",
        reload=False
    )
