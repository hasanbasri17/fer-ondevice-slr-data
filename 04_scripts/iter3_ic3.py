"""Snowballing iterasi 3: keputusan akhir IC3 ketat (bukti tingkat perangkat) untuk kandidat yang lolos judul-abstrak.
Kandidat lolos judul-abstrak = baris iter3_seleksi.csv dengan Keputusan 'Perlu teks lengkap'. Keluaran: snowballing/iter3_ic3.csv
(kolom sama dengan ic3_ketat.csv agar bisa dibaca data_slr.py).
"""
import csv, os
from collections import Counter
DIR = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in csv.DictReader(open(os.path.join(DIR, "iter3_seleksi.csv"), encoding="utf-8-sig")) if r["Keputusan"].startswith("Perlu")]
LOLOS_TL = {"U017": "Raspberry Pi + Intel Movidius NCS2 (IoMT), real-time; akurasi FER2013 73%",
            "U035": "Raspberry Pi (edge AI, MediaPipe + CNN), real-time"}
LOLOS_ABS = {"U024": "Penerjemah emosi wearable real-time (umpan balik getar di pelipis) diuji pada orang dewasa dengan ASD (abstrak)"}
GUGUR_TL = {"U002": "tanpa uji perangkat (kamera kelas, pemrosesan tidak di perangkat target)", "U028": "sirkuit memristif dievaluasi pada tingkat rangkaian, bukan perangkat target",
            "U036": "tanpa pengukuran di perangkat", "U037": "desain ASIC hanya sintesis/simulasi (871 uW), chip tidak difabrikasi dan diukur"}
GUGUR_ABS = {"U021": "PDF tidak dapat diakses; abstrak tanpa uji perangkat", "U023": "PDF tidak dapat diakses; abstrak tanpa uji perangkat"}
out = []
for r in rows:
    i = r["ID"]
    if i in LOLOS_TL: k, c = "Lolos IC3 ketat (teks lengkap)", LOLOS_TL[i]
    elif i in LOLOS_ABS: k, c = "Lolos IC3 ketat (abstrak, PDF tidak dapat diakses)", LOLOS_ABS[i]
    elif i in GUGUR_TL: k, c = "Gugur IC3 ketat (teks lengkap)", GUGUR_TL[i]
    elif i in GUGUR_ABS: k, c = "Gugur IC3 ketat (abstrak, PDF tidak dapat diakses)", GUGUR_ABS[i]
    else: raise SystemExit("belum diputuskan: " + i)
    out.append({**r, "IC3 ketat": k, "Catatan IC3": c, "Iterasi": "3"})
with open(os.path.join(DIR, "iter3_ic3.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
print(Counter(o["IC3 ketat"] for o in out))
