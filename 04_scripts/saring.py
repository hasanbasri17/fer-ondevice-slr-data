"""Penyaringan otomatis kandidat snowballing iterasi 1 -> snowballing/kandidat_tersaring.csv"""
import csv, os, re, sys
DIR = os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
FER = re.compile(r"(facial expression|facial emotion|face emotion|emotion recognition|expression recognition|\bFER\b|affect recognition)", re.I)
EFI = re.compile(r"(lightweight|light-weight|mobile|smartphone|edge|embedded|on-device|real-time|realtime|quantiz|distill|prun|"
                 r"efficient|raspberry|jetson|latency|compression|compact|low-power|resource-constrained|tinyml|iot)", re.I)
rows = list(csv.DictReader(open(os.path.join(DIR, "kandidat_iter1.csv"), encoding="utf-8-sig")))
alasan = {}
lolos = []
for r in rows:
    teks = r["Judul"] + " " + r["Abstrak"]
    th = int(r["Tahun"] or 0)
    if r["Sudah disaring"]: k = "sudah disaring (84 rekaman awal)"
    elif not 2021 <= th <= 2026: k = "di luar 2021-2026"
    elif r["Jenis"] != "article" or r["Jenis sumber"] != "journal": k = "bukan artikel jurnal"
    elif r["Bahasa"] not in ("en", ""): k = "bukan bahasa Inggris"
    elif not FER.search(teks): k = "tidak membahas FER/emosi wajah"
    elif not EFI.search(teks): k = "tanpa istilah efisiensi/perangkat"
    else:
        k = "lolos"; lolos.append(r)
    alasan[k] = alasan.get(k, 0) + 1
for k, v in sorted(alasan.items(), key=lambda x: -x[1]): print(f"{v:5d}  {k}")
with open(os.path.join(DIR, "kandidat_tersaring.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(lolos)
