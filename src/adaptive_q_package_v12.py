#!/usr/bin/env python3
"""Launcher for the split synthetic adaptive-q v12 benchmark."""
from pathlib import Path
_here = Path(__file__).resolve().parent
for _name in ("adaptive_q_core_v12.py", "adaptive_q_codec_v12.py", "adaptive_q_package_v12_impl.py"):
    exec((_here / _name).read_text(encoding="utf-8"), globals())
