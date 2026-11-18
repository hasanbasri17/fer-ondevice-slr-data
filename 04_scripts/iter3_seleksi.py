"""Snowballing iterasi 3: keputusan judul-abstrak (dengan IC3 ketat) + unduh PDF open access kandidat yang perlu teks lengkap.
Keluaran: snowballing/iter3_seleksi.csv, snowballing/pdf/Uxxx.pdf
"""
import csv, json, os, sys, time, urllib.request
DIR = os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
rows = list(csv.DictReader(open(os.path.join(DIR, "iter3_tersaring.csv"), encoding="utf-8-sig")))
PERLU = set("002 017 021 023 024 028 035 036 037".split())
REVIEW = set("005 009".split())
EC1 = set("029 034".split())        # modalitas bukan wajah / multimodal tanpa fokus wajah
EC3 = set("004 031 033".split())                    # hewan, bahasa isyarat, retraksi, topik lain
ALASAN = {"REV": "Eksklusi: studi sekunder (review/survei)", "EC1": "EC1: modalitas bukan citra wajah RGB",
          "EC3": "EC3: di luar cakupan (bukan FER manusia / artikel ditarik / topik lain)",
          "IC3": "IC3 ketat: abstrak tidak menunjukkan uji di perangkat target", "PERLU": "Perlu teks lengkap (indikasi uji perangkat)"}
UA = {"User-Agent": "Mozilla/5.0 (slr-snowballing; open-access download)", "Accept": "application/pdf,*/*"}
CF = os.path.join(DIR, "openalex_cache.json")
cache = json.load(open(CF, encoding="utf-8"))
out = []
for n, r in enumerate(rows, 1):
    k = f"{n:03d}"
    kat = "PERLU" if k in PERLU else "REV" if k in REVIEW else "EC1" if k in EC1 else "EC3" if k in EC3 else "IC3"
    oa, unduh = "", ""
    if kat == "PERLU":
        url = "https://api.openalex.org/works/" + r["OpenAlex"].rsplit("/", 1)[1] + "?select=open_access,best_oa_location"
        if url not in cache:
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "slr-snowballing/1.0"}), timeout=30) as f:
                    cache[url] = json.loads(f.read().decode()); time.sleep(0.15)
            except Exception:
                cache[url] = {}
        loc = cache[url].get("best_oa_location") or {}
        oa = (loc.get("pdf_url") or loc.get("landing_page_url") or "") if (cache[url].get("open_access") or {}).get("is_oa") else ""
        tujuan = os.path.join(DIR, "pdf", f"U{k}.pdf")
        if os.path.exists(tujuan):
            unduh = "ada"
        elif oa:
            try:
                with urllib.request.urlopen(urllib.request.Request(oa, headers=UA), timeout=60) as f:
                    d = f.read()
                if d[:5] == b"%PDF-":
                    open(tujuan, "wb").write(d); unduh = "ok"
                else:
                    unduh = "halaman landing"
            except Exception as e:
                unduh = "gagal: " + str(e)[:40]
            time.sleep(1)
    out.append({"ID": "U" + k, "DOI": r["DOI"], "Tahun": r["Tahun"], "Sumber": r["Sumber"], "Judul": r["Judul"], "Arah": r["Arah"],
                "Dari studi": r["Dari studi"], "Keputusan": ALASAN[kat], "OA": oa, "Unduh": unduh})
json.dump(cache, open(CF, "w", encoding="utf-8"), ensure_ascii=False)
with open(os.path.join(DIR, "iter3_seleksi.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
from collections import Counter
print(Counter(o["Keputusan"] for o in out))
for o in out:
    if o["Keputusan"].startswith("Perlu"):
        print(o["ID"], o["Unduh"] or "tidak OA", "|", o["Sumber"][:25], "|", o["Judul"][:70])
