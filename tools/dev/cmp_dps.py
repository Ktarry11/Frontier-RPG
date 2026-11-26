import json,statistics,sys,collections
b=json.load(open(sys.argv[1])); a=json.load(open(sys.argv[2]))
specs=collections.defaultdict(dict)
for k,v in b.items():
    s,lv=k.split('|'); specs[s][lv]=(v[0], a.get(k,[0])[0])
lvs=sorted({k.split('|')[1] for k in b}, key=int)
for lv in lvs:
    print('L',lv,'median', round(statistics.median(specs[s][lv][0] for s in specs)), '->', round(statistics.median(specs[s][lv][1] for s in specs)))
for s in sorted(specs):
    row=[]; ch=False
    for lv in lvs:
        x,y=specs[s][lv]
        if abs(y/x-1)>0.05: ch=True
        row.append(f"{x:5.0f}->{y:5.0f} ({y/x-1:+.0%})")
    if ch: print(f"{s:28}", '  '.join(row))
