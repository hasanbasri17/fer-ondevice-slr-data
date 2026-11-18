"""Snowballing (Wohlin 2014) iterasi 1 via OpenAlex: referensi (mundur) dan sitasi (maju) dari studi primer final.
Keluaran: snowballing/openalex_cache.json, snowballing/kandidat_iter1.csv
Pemakaian (dari folder artikel_SLR): python -I snowballing/ambil_openalex.py
"""
import csv, json, os, sys, time, urllib.parse, urllib.request

DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(DIR)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
data = json.load(open(os.path.join(BASE, "penulisan", "data_slr.json"), encoding="utf-8"))
rek = {r["ID"]: r for r in csv.DictReader(open(os.path.join(BASE, "pencarian", "gabungan_dedup.csv"), encoding="utf-8-sig"))}
INK = sorted(data["studi"])
SUDAH = {r["DOI"].replace("https://doi.org/", "").lower() for r in rek.values() if r["DOI"]}   # 84 rekaman yang sudah disaring
UA = {"User-Agent": "slr-snowballing/1.0"}
CF = os.path.join(DIR, "openalex_cache.json")
cache = json.load(open(CF, encoding="utf-8")) if os.path.exists(CF) else {}


def get(url):
    if url in cache:
        return cache[url]
    for coba in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as f:
                cache[url] = json.loads(f.read().decode("utf-8"))
                time.sleep(0.15)
                return cache[url]
        except Exception as e:
            print("ulang", url[:90], e); time.sleep(2)
    return None


SEL = "id,doi,title,publication_year,type,language,primary_location,abstract_inverted_index,referenced_works,cited_by_count"
seed, kandidat = {}, {}
for i in INK:
    doi = rek[i]["DOI"].replace("https://doi.org/", "").lower()
    w = get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi) + "?select=" + SEL)
    if not w:
        print("TIDAK DITEMUKAN", i, doi); continue
    seed[i] = w
    # mundur: referensi
    refs = w.get("referenced_works") or []
    for n in range(0, len(refs), 50):
        ids = "|".join(r.rsplit("/", 1)[1] for r in refs[n:n + 50])
        hasil = get(f"https://api.openalex.org/works?filter=openalex:{ids}&per-page=50&select={SEL}")
        for x in (hasil or {}).get("results", []):
            kandidat.setdefault(x["id"], {"w": x, "arah": set(), "dari": set()})
            kandidat[x["id"]]["arah"].add("mundur"); kandidat[x["id"]]["dari"].add(i)
    # maju: yang menyitasi
    wid = w["id"].rsplit("/", 1)[1]
    hal = 1
    while True:
        hasil = get(f"https://api.openalex.org/works?filter=cites:{wid}&per-page=200&page={hal}&select={SEL}")
        res = (hasil or {}).get("results", [])
        for x in res:
            kandidat.setdefault(x["id"], {"w": x, "arah": set(), "dari": set()})
            kandidat[x["id"]]["arah"].add("maju"); kandidat[x["id"]]["dari"].add(i)
        if len(res) < 200:
            break
        hal += 1
    print(i, "ref:", len(refs), "| disitasi:", w.get("cited_by_count"))
json.dump(cache, open(CF, "w", encoding="utf-8"), ensure_ascii=False)


def abstrak(inv):
    if not inv:
        return ""
    pos = sorted((p, kata) for kata, ps in inv.items() for p in ps)
    return " ".join(k for _, k in pos)


seed_ids = {w["id"] for w in seed.values()}
with open(os.path.join(DIR, "kandidat_iter1.csv"), "w", newline="", encoding="utf-8-sig") as f:
    wr = csv.writer(f)
    wr.writerow(["OpenAlex", "DOI", "Tahun", "Jenis", "Bahasa", "Sumber", "Jenis sumber", "Judul", "Arah", "Dari studi", "Sudah disaring", "Abstrak"])
    for k, v in kandidat.items():
        if k in seed_ids:
            continue
        w = v["w"]
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        so = (w.get("primary_location") or {}).get("source") or {}
        src, srctype = so.get("display_name", ""), so.get("type", "")
        wr.writerow([k, doi, w.get("publication_year"), w.get("type"), w.get("language"), src, srctype, w.get("title") or "",
                     "+".join(sorted(v["arah"])), " ".join(sorted(v["dari"])), "ya" if doi in SUDAH else "",
                     abstrak(w.get("abstract_inverted_index"))])
print("seed ditemukan:", len(seed), "/", len(INK), "| kandidat unik:", len(kandidat) - len(seed_ids & set(kandidat)))
