"""Amandemen protokol (18 Nov 2026, disetujui peneliti): IC3 diperketat menjadi BUKTI TINGKAT PERANGKAT, yaitu
(a) kinerja diukur di perangkat target mobile/edge/tertanam, atau (b) sistem dievaluasi pada lokasi pemrosesan tertentu
(on-device/edge/fog/cloud). Berlaku sama untuk 30 studi lama dan 59 kandidat snowballing.
Skrip ini mencatat keputusan untuk kandidat snowballing -> snowballing/ic3_ketat.csv dan membuat daftar unduh manual.
"""
import csv, os
DIR = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in csv.DictReader(open(os.path.join(DIR, "seleksi_iter1.csv"), encoding="utf-8-sig")) if r["Keputusan"].startswith("Inklusi")]
LOLOS_TL = {"S053": "Jetson Nano 47,97 FPS", "S082": "Prosesor ARM tertanam: >25 FPS (15 W), >70 FPS (30 W)",
            "S119": "Pelatihan + inferensi di Jetson Nano (5 W / Max-N)", "S121": "Jetson: 530,7 FPS; memori 0,03 MB",
            "S137": "Raspberry Pi 4: 13,92 ms (71,8 FPS), TFLite 5,5 MB; federated", "S139": "On-device iPhone 14 Pro (ARKit)"}
GUGUR_TL = {"S006": "tanpa uji perangkat", "S033": "tanpa uji perangkat", "S034": "tanpa uji perangkat", "S038": "tanpa uji perangkat",
            "S043": "tanpa uji perangkat", "S075": "efisiensi hanya analisis teoretis", "S077": "FPS diukur di GPU",
            "S110": "tanpa uji perangkat", "S112": "tanpa uji perangkat", "S115": "cloud, latensi belum diuji",
            "S122": "FPS hanya diperkirakan, tidak diukur di perangkat", "S125": "tanpa uji perangkat", "S151": "tanpa uji perangkat"}
# --- hasil PDF yang diunduh peneliti (18 Nov 2026)
LOLOS_TL.update({"S001": "Diimplementasikan pada perangkat keras robot humanoid (angka latensi tidak dilaporkan)",
                 "S009": "Inferensi kolaboratif edge-cloud: peta fitur antara dikirim, bukan piksel",
                 "S064": "Raspberry Pi 4B: 229 ms (2 FPS)", "S069": "Raspberry Pi 4: 74,15 ms; TFLite INT8 (ukuran -75%)",
                 "S078": "Jetson Orin Nano 31,0 ms; SoC mobile 22,0 ms; Raspberry Pi 5 5,4 klip/s",
                 "S099": "NPU RK3588 (Orange Pi), hingga 285,7 FPS", "S101": "Browser di sisi klien: Xiaomi 15 108 ms (WebGL)",
                 "S114": "Raspberry Pi 3B+: 9,59 FPS (landmark)", "S126": "Raspberry Pi 3B+: INT8 19,30 ms"})
LOLOS_TL.pop("S119")                   # teks lengkap: emosi dari TEKS (BERT, kalimat MELD), bukan wajah
GUGUR_TL.update({"S119": "EC1: pengenalan emosi dari teks (BERT/MELD), bukan wajah; diketahui dari teks lengkap",
                 "S068": "hanya CPU PC", "S072": "dilatih/diuji di GPU cloud; perangkat wearable hanya diusulkan",
                 "S087": "semua pengukuran di GPU RTX 3090", "S109": "PC dengan RTX 3090"})
LOLOS_LAIN = {"S035": ("Lolos IC3 ketat (abstrak; awalnya salah digolongkan sebagai review)", "91 model TFLite diuji akurasi & latensi; aplikasi Android dirilis"),
              "S052": ("Lolos IC3 ketat (catatan teks lengkap artikel 2)", "Raspberry Pi pada robot; 0,55 jt parameter, 2,25 MB"),
              "S054": ("Lolos IC3 ketat (abstrak, PDF tidak dapat diakses)", "Real-time pada perangkat murah dengan sensor kamera RGB"),
              "S070": ("Lolos IC3 ketat (abstrak, PDF tidak dapat diakses)", "Smartphone -> edge server; model dilatih di cloud"),
              "S118": ("Lolos IC3 ketat (abstrak, PDF tidak dapat diakses)", "Sistem pengenalan emosi berjenjang berbasis MEC")}
GUGUR_TANPA_PDF = {"S010": "PDF tidak dapat diakses; abstrak hanya menyebut CPU tanpa perangkat target",
                   "S025": "PDF tidak dapat diakses; abstrak tanpa uji perangkat",
                   "S032": "PDF tidak dapat diakses; catatan artikel 2 tanpa uji perangkat",
                   "S076": "PDF tidak dapat diakses; klaim cocok untuk edge tanpa pengukuran",
                   "S145": "PDF tidak dapat diakses; dirancang untuk edge tanpa pengukuran"}
out = []
for r in rows:
    i = r["ID"]
    if i in LOLOS_TL: k, cat = "Lolos IC3 ketat (teks lengkap)", LOLOS_TL[i]
    elif i in LOLOS_LAIN: k, cat = LOLOS_LAIN[i]
    elif i in GUGUR_TL: k, cat = "Gugur IC3 ketat (teks lengkap)", GUGUR_TL[i]
    elif i in GUGUR_TANPA_PDF: k, cat = "Gugur IC3 ketat (abstrak, PDF tidak dapat diakses)", GUGUR_TANPA_PDF[i]
    else: k, cat = "Gugur IC3 ketat (abstrak)", "abstrak tidak menyebut uji di perangkat target"
    out.append({**r, "IC3 ketat": k, "Catatan IC3": cat})
with open(os.path.join(DIR, "ic3_ketat.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
from collections import Counter
print(Counter(o["IC3 ketat"] for o in out))
L = ["# Daftar unduh PDF snowballing (22 studi)", "",
     "Simpan PDF ke folder `eksekusi/artikel_SLR/snowballing/pdf/` dengan nama **`Sxxx.pdf`** (misalnya `S069.pdf`).",
     "Kalau nama aslinya tidak diganti juga tidak apa-apa; saya akan mencocokkan lewat judul.", "",
     "| Simpan sebagai | Tahun | Jurnal | Judul | Tautan (DOI) |", "|---|---|---|---|---|"]
for o in out:
    if o["IC3 ketat"] == "Perlu teks lengkap":
        L.append(f"| [ ] {o['ID']}.pdf | {o['Tahun']} | {o['Sumber']} | {o['Judul']} | https://doi.org/{o['DOI']} |")
open(os.path.join(DIR, "DAFTAR_UNDUH_SNOWBALLING.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
