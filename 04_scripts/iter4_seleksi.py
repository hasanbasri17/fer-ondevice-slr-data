"""Snowballing iterasi 4 (dari U017, U035, U024): keputusan judul-abstrak. Tidak ada yang lolos -> kejenuhan tercapai.
Keluaran: snowballing/iter4_seleksi.csv
"""
import csv, os
from collections import Counter
DIR = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(DIR, "iter4_tersaring.csv"), encoding="utf-8-sig")))
KEP = {"001": "IC3 ketat: Random Forest yang diklaim efisien, tanpa uji di perangkat target",
       "002": "IC3 ketat: sistem musik berbasis FER, tanpa uji di perangkat target",
       "003": "EC3: deteksi aktivitas mencurigakan, bukan FER",
       "004": "IC3 ketat: platform pendidikan (ResNet50), tanpa uji di perangkat target",
       "005": "IC3 ketat: digital twin dengan webcam di PC, tanpa perangkat target"}
assert len(rows) == len(KEP), "jumlah kandidat berubah; tinjau ulang keputusan"
out = [{"ID": f"V{n:03d}", "DOI": r["DOI"], "Tahun": r["Tahun"], "Sumber": r["Sumber"], "Judul": r["Judul"], "Arah": r["Arah"],
        "Dari studi": r["Dari studi"], "Keputusan": KEP[f"{n:03d}"]} for n, r in enumerate(rows, 1)]
with open(os.path.join(DIR, "iter4_seleksi.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
print(Counter(o["Keputusan"].split(":")[0] for o in out), "| inklusi: 0")
