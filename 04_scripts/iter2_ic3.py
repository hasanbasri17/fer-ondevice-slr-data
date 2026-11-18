"""Snowballing iterasi 2: keputusan akhir IC3 ketat (bukti tingkat perangkat) untuk kandidat yang lolos judul-abstrak.
Kandidat lolos judul-abstrak = baris iter2_seleksi.csv dengan Keputusan 'Perlu teks lengkap'. Keluaran: snowballing/iter2_ic3.csv
(kolom sama dengan ic3_ketat.csv agar bisa dibaca data_slr.py).
"""
import csv, os
from collections import Counter
DIR = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in csv.DictReader(open(os.path.join(DIR, "iter2_seleksi.csv"), encoding="utf-8-sig")) if r["Keputusan"].startswith("Perlu")]
LOLOS_TL = {"T022": "Papan RK3399Pro (NPU): latensi -30,2x (ekstraktor) dan -6,62x (LSTM); model -221x",
            "T027": "Robot Temi V3 (Android) dan Samsung A52: CPU <=30%, akurasi real-time 82,28%",
            "T030": "Raspberry Pi + Jetson TX2 + server (offloading parsial): energi sistem -30-40%",
            "T034": "Raspberry Pi 4: 11,5 FPS; 14 FPS dengan TFLite", "T052": "Raspberry Pi 4B: >13 FPS tanpa akselerator",
            "T083": "Robot asistif (ROS): 164,76 +/- 28,63 ms per prediksi", "T101": "Jetson Nano: 5,51 FPS (TensorRT FP32), <10 W",
            "T103": "Raspberry Pi + Pi-cam (sistem real-time)", "T104": "FPGA: +/-10 FPS pada 250 MHz, 2,3 W"}
LOLOS_ABS = {"T015": "Model dipasang di smartphone sebagai perangkat edge (abstrak)", "T065": "Model ringan di kontroler edge mobil (abstrak)",
             "T070": "Sistem real-time di Raspberry Pi (abstrak)", "T087": "TinyML untuk perangkat tertanam ultra-rendah daya (abstrak)"}
GUGUR_TL = {"T064": "EC1: sensor kedalaman ToF 8x8, bukan citra wajah RGB", "T014": "tanpa uji perangkat", "T036": "latensi diukur di GPU; end-to-end di kacamata belum diukur",
            "T043": "tanpa uji perangkat", "T075": "edge-fog-cloud hanya simulasi", "T094": "hanya CPU PC", "T099": "hanya GPU/CPU PC",
            "T106": "hanya 'cocok untuk edge', tanpa pengukuran"}
GUGUR_ABS = {"T019": "PDF tidak dapat diakses; abstrak hanya mengklaim dapat berjalan di perangkat mobile",
             "T033": "PDF tidak dapat diakses; abstrak kosong", "T061": "PDF tidak dapat diakses; abstrak kosong",
             "T066": "PDF tidak dapat diakses; abstrak tanpa evaluasi di perangkat", "T021": "pustaka perangkat lunak tanpa uji perangkat (abstrak)"}
out = []
for r in rows:
    i = r["ID"]
    if i in LOLOS_TL: k, c = "Lolos IC3 ketat (teks lengkap)", LOLOS_TL[i]
    elif i in LOLOS_ABS: k, c = "Lolos IC3 ketat (abstrak, PDF tidak dapat diakses)", LOLOS_ABS[i]
    elif i in GUGUR_TL: k, c = "Gugur IC3 ketat (teks lengkap)", GUGUR_TL[i]
    elif i in GUGUR_ABS: k, c = "Gugur IC3 ketat (abstrak, PDF tidak dapat diakses)", GUGUR_ABS[i]
    else: raise SystemExit("belum diputuskan: " + i)
    out.append({**r, "IC3 ketat": k, "Catatan IC3": c, "Iterasi": "2"})
with open(os.path.join(DIR, "iter2_ic3.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
print(Counter(o["IC3 ketat"] for o in out))
