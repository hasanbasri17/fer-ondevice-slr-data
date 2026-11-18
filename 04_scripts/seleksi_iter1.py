"""Keputusan seleksi judul-abstrak snowballing iterasi 1 (15 Nov 2026) + cek ketersediaan open access.
Keluaran: snowballing/seleksi_iter1.csv
"""
import csv, json, os, sys, urllib.request, time
DIR = os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
rows = list(csv.DictReader(open(os.path.join(DIR, "kandidat_tersaring.csv"), encoding="utf-8-sig")))

INK = set(("001 006 009 010 012 013 015 018 025 028 031 032 033 034 037 038 042 043 045 046 048 051 052 053 054 064 066 067 "
           "035 068 069 070 072 075 076 077 078 082 083 085 087 089 098 099 101 109 110 112 114 115 118 119 121 122 125 126 137 139 145 151").split())
REVIEW = set("004 005 019 024 056 073 088 091 092 093 096 127 136 140".split())          # studi sekunder (dipakai di Bagian 6)
EC1 = set("002 003 016 017 021 061 063 094 116 117 131 135 150 152 107".split())              # modalitas non-wajah / multimodal tanpa fokus wajah
EC3 = set("039 047 079 081 084 086 090 097 120 128 129 132 134 146 153 155".split())          # bukan klasifikasi ekspresi/emosi wajah
ALASAN = {"INK": "Inklusi (judul-abstrak)", "REV": "Eksklusi: studi sekunder (review/survei)",
          "EC1": "EC1: modalitas bukan citra wajah RGB", "EC2": "EC2: efisiensi/penerapan di perangkat tidak dibahas",
          "EC3": "EC3: bukan kontribusi klasifikasi emosi wajah"}
UA = {"User-Agent": "slr-snowballing/1.0"}
cache_f = os.path.join(DIR, "openalex_cache.json")
cache = json.load(open(cache_f, encoding="utf-8"))
out = []
for n, r in enumerate(rows, 1):
    k = f"{n:03d}"
    kat = "INK" if k in INK else "REV" if k in REVIEW else "EC1" if k in EC1 else "EC3" if k in EC3 else "EC2"
    oa = ""
    if kat == "INK":
        url = "https://api.openalex.org/works/" + r["OpenAlex"].rsplit("/", 1)[1] + "?select=open_access,best_oa_location"
        if url not in cache:
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as f:
                    cache[url] = json.loads(f.read().decode()); time.sleep(0.15)
            except Exception as e:
                cache[url] = {}
        w = cache[url]
        loc = w.get("best_oa_location") or {}
        oa = (loc.get("pdf_url") or loc.get("landing_page_url") or "") if (w.get("open_access") or {}).get("is_oa") else ""
    out.append({"ID": "S" + k, **{c: r[c] for c in ("DOI", "Tahun", "Sumber", "Judul", "Arah", "Dari studi")},
                "Keputusan": ALASAN[kat], "OA": oa})
json.dump(cache, open(cache_f, "w", encoding="utf-8"), ensure_ascii=False)
with open(os.path.join(DIR, "seleksi_iter1.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
from collections import Counter
print(Counter(o["Keputusan"] for o in out))
ink = [o for o in out if o["Keputusan"].startswith("Inklusi")]
print("inklusi:", len(ink), "| open access:", sum(1 for o in ink if o["OA"]))
print("tidak OA:", " ".join(o["ID"] + "(" + o["Sumber"][:18] + ")" for o in ink if not o["OA"]))
