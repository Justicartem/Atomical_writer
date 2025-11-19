import json
from atomic_writer import write_text_atomic

obj = {"users": ["gautr", "breaker"], "count": 2}
write_text_atomic("results/state.json", json.dumps(obj, ensure_ascii=False, indent=2))