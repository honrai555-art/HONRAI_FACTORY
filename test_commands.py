#!/usr/bin/env python
"""Quick test of bot commands to verify implementation."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment from bot/.env
bot_dir = Path(__file__).parent / "bot"
load_dotenv(bot_dir / ".env")

# Test status command
print("=" * 50)
print("Testing !status command:")
print("=" * 50)
try:
    from bot.commands.status import get_status
    print(get_status())
except Exception as e:
    print(f"ERROR: {e}")

# Test manga command (should error with missing webhook)
print("\n" + "=" * 50)
print("Testing !manga command (should show webhook error):")
print("=" * 50)
try:
    from bot.commands.manga import run_manga
    result = run_manga()
    print(f"Result: {result}")
except RuntimeError as e:
    print(f"Expected error (DISCORD_WEBHOOK_URL not set):\n  {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

# Test unity command
print("\n" + "=" * 50)
print("Testing !unity command:")
print("=" * 50)
try:
    from bot.commands.unity import run_unity
    result = run_unity()
    print(f"Result: {result}")
except RuntimeError as e:
    print(f"Config error:\n  {e}")
except FileNotFoundError as e:
    print(f"File error:\n  {e}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("All command tests completed!")
print("=" * 50)
