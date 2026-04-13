#!/usr/bin/env python3
"""Quick test for timer functionality"""

import sys
sys.path.insert(0, 'c:/Users/akhil/Downloads/F.R.I.D.A.Y')

from actions.clock import set_timer
import time

print("[TEST] Testing set_timer with 5 minutes...")
success, message = set_timer("5 minutes")
print(f"[RESULT] Success: {success}")
print(f"[RESULT] Message: {message}")

print("\n[TEST] Waiting 3 seconds before next test...")
time.sleep(3)

print("[TEST] Testing set_timer with 1 minute...")
success, message = set_timer("1 minute")
print(f"[RESULT] Success: {success}")
print(f"[RESULT] Message: {message}")
