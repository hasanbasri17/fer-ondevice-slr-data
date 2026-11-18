import re, csv, glob, sys
recs = {}
order = []
for f in sorted(glob.glob('S*.ris')):  # R_review_terkait.ris tidak ikut (bukan studi primer)
    src = f.split('_')[0]
    cur = {}; last=None
    for line in open(f, encoding='utf-8', errors='replace'):
        m = re.match(r'^([A-Z][A-Z0-9])  - ?(.*)$', line.rstrip('\n'))
        if not m:
            if last and line.strip():
                cur[last] = cur.get(last,'') + ' ' + line.strip()
            continue
        k, v = m.groups(); last = k if k not in ('AU','KW','ER') else None
        if k == 'ER':
            key = (cur.get('DO') or cur.get('T1','')).lower().strip()
            if key in recs:
                recs[key]['src'].add(src)
            else:
                cur['src'] = {src}; recs[key] = cur; order.append(key)
            cur = {}
        elif k in ('AU','KW'):
            cur.setdefault(k, []).append(v)
        else:
            cur[k] = cur.get(k, '') + v
with open('gabungan_dedup.csv','w',newline='',encoding='utf-8-sig') as fo:
    w = csv.writer(fo)
    w.writerow(['ID','Sumber','Judul','Penulis','Jurnal','Tahun','DOI','Kata kunci','Abstrak'])
    for i,k in enumerate(order,1):
        r = recs[k]
        w.writerow([f'P{i:03d}','+'.join(sorted(r['src'])),r.get('T1',''),'; '.join(r.get('AU',[])),r.get('JO',''),r.get('PY',''),r.get('DO',''),'; '.join(r.get('KW',[])),r.get('AB','')])
print('unik:', len(order))
for i,k in enumerate(order,1):
    r = recs[k]; print(f"P{i:03d}|{'+'.join(sorted(r['src']))}|{r.get('PY','')}|{r.get('JO','')[:40]}|{r.get('T1','')[:120]}")
