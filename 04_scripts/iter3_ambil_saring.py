"""Snowballing iterasi 3 (Wohlin): referensi (mundur) + sitasi (maju) dari studi hasil iterasi 2 via OpenAlex.
Kandidat yang sudah dinilai (database, iterasi 1, iterasi 2) dilewati.
Saringan otomatis sama dengan iterasi 1 (saring.py).
Keluaran: snowballing/iter3_kandidat.csv (semua kandidat baru) dan snowballing/iter3_tersaring.csv (lolos saringan otomatis)
Pemakaian (dari folder artikel_SLR): python -I snowballing/iter3_ambil_saring.py
"""
import csv, json, os, re, sys, time, urllib.parse, urllib.request
DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(DIR)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = {"User-Agent": "slr-snowballing/1.0"}
CF = os.path.join(DIR, "openalex_cache.json")
cache = json.load(open(CF, encoding="utf-8"))


def get(url):
    if url in cache:
        return cache[url]
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as f:
                cache[url] = json.loads(f.read().decode("utf-8")); time.sleep(0.15); return cache[url]
        except Exception as e:
            print("ulang", url[:80], e); time.sleep(2)
    return None


# --- yang sudah pernah dinilai
sudah_doi = {r["DOI"].replace("https://doi.org/", "").lower()
             for r in csv.DictReader(open(os.path.join(BASE, "pencarian", "gabungan_dedup.csv"), encoding="utf-8-sig")) if r["DOI"]}
iter1 = list(csv.DictReader(open(os.path.join(DIR, "kandidat_iter1.csv"), encoding="utf-8-sig")))
sudah_id = {r["OpenAlex"] for r in iter1}
sudah_doi |= {r["DOI"] for r in iter1 if r["DOI"]}
iter2 = list(csv.DictReader(open(os.path.join(DIR, "iter2_kandidat.csv"), encoding="utf-8-sig")))
sudah_id |= {r["OpenAlex"] for r in iter2}
sudah_doi |= {r["DOI"] for r in iter2 if r["DOI"]}
sudah_id |= {r["OpenAlex"] for r in csv.DictReader(open(os.path.join(DIR, "iter2_seleksi.csv"), encoding="utf-8-sig")) if r.get("OpenAlex")}
seed = [r for r in csv.DictReader(open(os.path.join(DIR, "iter2_ic3.csv"), encoding="utf-8-sig")) if r["IC3 ketat"].startswith("Lolos")]
SEL = "id,doi,title,publication_year,type,language,primary_location,abstract_inverted_index,referenced_works,cited_by_count"
kand, seed_ids = {}, set()
for r in seed:
    w = get("https://api.openalex.org/works/doi:" + urllib.parse.quote(r["DOI"]) + "?select=" + SEL)
    if not w:
        print("seed tidak ditemukan", r["ID"]); continue
    seed_ids.add(w["id"])
    refs = w.get("referenced_works") or []
    for n in range(0, len(refs), 50):
        ids = "|".join(x.rsplit("/", 1)[1] for x in refs[n:n + 50])
        for x in (get(f"https://api.openalex.org/works?filter=openalex:{ids}&per-page=50&select={SEL}") or {}).get("results", []):
            kand.setdefault(x["id"], {"w": x, "arah": set(), "dari": set()}); kand[x["id"]]["arah"].add("mundur"); kand[x["id"]]["dari"].add(r["ID"])
    wid, hal = w["id"].rsplit("/", 1)[1], 1
    while True:
        res = (get(f"https://api.openalex.org/works?filter=cites:{wid}&per-page=200&page={hal}&select={SEL}") or {}).get("results", [])
        for x in res:
            kand.setdefault(x["id"], {"w": x, "arah": set(), "dari": set()}); kand[x["id"]]["arah"].add("maju"); kand[x["id"]]["dari"].add(r["ID"])
        if len(res) < 200: break
        hal += 1
    print(r["ID"], "ref:", len(refs), "| disitasi:", w.get("cited_by_count"))
json.dump(cache, open(CF, "w", encoding="utf-8"), ensure_ascii=False)


def abstrak(inv):
    return " ".join(k for _, k in sorted((p, k) for k, ps in (inv or {}).items() for p in ps))


FER = re.compile(r"(facial expression|facial emotion|face emotion|emotion recognition|expression recognition|\bFER\b|affect recognition)", re.I)
EFI = re.compile(r"(lightweight|light-weight|mobile|smartphone|edge|embedded|on-device|real-time|realtime|quantiz|distill|prun|"
                 r"efficient|raspberry|jetson|latency|compression|compact|low-power|resource-constrained|tinyml|iot)", re.I)
semua, lolos, hit = [], [], {}
for k, v in kand.items():
    w = v["w"]
    if k in seed_ids:
        continue
    doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
    so = (w.get("primary_location") or {}).get("source") or {}
    row = {"OpenAlex": k, "DOI": doi, "Tahun": w.get("publication_year"), "Jenis": w.get("type"), "Bahasa": w.get("language"),
           "Sumber": so.get("display_name", ""), "Jenis sumber": so.get("type", ""), "Judul": w.get("title") or "",
           "Arah": "+".join(sorted(v["arah"])), "Dari studi": " ".join(sorted(v["dari"])), "Abstrak": abstrak(w.get("abstract_inverted_index"))}
    teks, th = row["Judul"] + " " + row["Abstrak"], int(row["Tahun"] or 0)
    if k in sudah_id or (doi and doi in sudah_doi): a = "sudah dinilai (database/iterasi 1-2)"
    elif not 2021 <= th <= 2026: a = "di luar 2021-2026"
    elif row["Jenis"] != "article" or row["Jenis sumber"] != "journal": a = "bukan artikel jurnal"
    elif row["Bahasa"] not in ("en", "", None): a = "bukan bahasa Inggris"
    elif not FER.search(teks): a = "tidak membahas FER/emosi wajah"
    elif not EFI.search(teks): a = "tanpa istilah efisiensi/perangkat"
    else: a = "lolos"; lolos.append(row)
    row["Saringan"] = a; semua.append(row); hit[a] = hit.get(a, 0) + 1
for nama, data in (("iter3_kandidat.csv", semua), ("iter3_tersaring.csv", lolos)):
    with open(os.path.join(DIR, nama), "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=list(semua[0].keys())); wr.writeheader(); wr.writerows(data)
print("kandidat unik:", len(semua))
for a, n in sorted(hit.items(), key=lambda x: -x[1]): print(f"{n:5d}  {a}")
