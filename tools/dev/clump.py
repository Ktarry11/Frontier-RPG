import json,sys,collections
sys.path.insert(0,'/home/claude/frontier-rpg')
from world.zone_keys import zone_key
amb=json.load(open('data/npcs/ambient_npcs.json'))['npcs']; ven=json.load(open('data/npcs/vendors.json'))['vendors']
pos=collections.defaultdict(list)
for n in amb+ven:
    if n.get('x') is not None and not n.get('is_mailbox'): pos[zone_key(str(n['zone']))].append((n['x'],n['y']))
for z in sys.argv[1:]:
    P=pos[z]; best=(0,None)
    for (x,y) in P:
        c=sum(1 for (a,b) in P if 0<=a-x<8 and 0<=b-y<8)
        if c>best[0]: best=(c,(x,y))
    print(z,len(P),'max in 8x8:',best)
