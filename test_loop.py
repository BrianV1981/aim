import json
import time
lines = ['{"_record_type": "fragment", "id": 9, "text": "hello"}']
fragments = []
for line in lines:
    frag = json.loads(line)
    if 'type' not in frag: frag['type'] = 'expert_knowledge'
    fragments.append(frag)

for x in fragments:
    if 'type' not in x: print("MISSING!")
    else: print("TYPE EXISTS:", x['type'])
