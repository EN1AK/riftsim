# -*- coding: utf-8 -*-
"""Print selected sections of the B006 probe dump."""
import json, sys

fn = sys.argv[4] if len(sys.argv) > 4 else "workspace/checkpoints/stage4b_b006_probe.json"
d = json.load(open(fn, encoding="utf-8"))
key = sys.argv[1]
obj = d[key]
s = json.dumps(obj, ensure_ascii=False, indent=1)
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
hi = int(sys.argv[3]) if len(sys.argv) > 3 else len(s)
print(s[lo:hi])
