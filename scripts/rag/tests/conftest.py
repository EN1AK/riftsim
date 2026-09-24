# -*- coding: utf-8 -*-
"""pytest 公共配置：把 scripts/rag 加入 sys.path 以便直接 import 被测模块。"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
