"""
pytest 配置和共享 fixtures
"""

from __future__ import annotations

import sys
from pathlib import Path

# 确保 backend 目录在 Python path 中
sys.path.insert(0, str(Path(__file__).parent.parent))
