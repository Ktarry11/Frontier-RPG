import json,glob,collections,sys
sys.path.insert(0,'/home/claude/frontier-rpg')
from world.zone_keys import zone_key
amb=json.load(open('data/npcs/ambient_npcs.json'))['npcs']
svc=json.load(open('data/travel/travel_data.json'))['services']
tr=json.load(open('data/training/trainers.json'))
trainers=set(tr.get('class_trainers',{}))|set(tr.get('profession_trainers',{}))
qp=set()
for f in glob.glob('data/quests/*.json'):
    d=json.load(open(f))
    for q in (d.get('quests') if isinstance(d,dict) else []) or []:
        qp|={q.get('giver_npc_id'),q.get('turn_in_npc_id')}
def resident(n):
    i=n['npc_id']
    if i in qp or i in svc or i in trainers or n.get('is_mailbox') or i.startswith(('secret_','ct_','pt_','ak_','mailbox')): return False
    return True
c=collections.Counter(zone_key(n['zone']) for n in amb if resident(n))
for z in sys.argv[1:]: print(z, c[zone_key(z)])
