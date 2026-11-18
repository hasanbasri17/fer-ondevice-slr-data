"""Data SLR (Kitchenham): keputusan seleksi, ekstraksi data, penilaian kualitas, statistik, gambar, dan daftar pustaka.

Sumber: pencarian/gabungan_dedup.csv (84 rekaman unik dari 4 string ScienceDirect, dibuat pencarian/dedup.py)
        penulisan/crossref_cache.json (metadata resmi, dibuat penulisan/ambil_referensi.py)
CATATAN: ekstraksi & skor kualitas awalnya dari abstrak; per 15 Nov 2026 semua studi diverifikasi dari teks lengkap (TEKS_LENGKAP).
Tahap full-text (verifikasi angka, kolom 'NR') wajib dilakukan peneliti sebelum naskah dikirim.
Keluaran: pencarian/seleksi.csv, pencarian/ekstraksi_kualitas.csv, penulisan/data_slr.json, penulisan/gambar/*.png
Pemakaian (dari folder artikel_SLR): python penulisan/data_slr.py
"""
import csv, json, os, re
from collections import Counter

DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(DIR)
os.makedirs(os.path.join(DIR, "gambar"), exist_ok=True)

# ---------------------------------------------------------------- 1. seleksi (judul + abstrak)
EC1 = "008 009 016 017 036 037 042 044 047 049 056 057 058 075".split()            # bukan modalitas wajah RGB
EC2 = "002 020 023 029 030 039 040 051 061 068 069 070 071 074 079 080 082 083".split()  # efisiensi/penerapan tidak dibahas
EC3 = "007 028 038 043 045 048 050 052 053 055 059 060 062 063 064 066 067 072 078".split()  # bukan kontribusi teknis pengenalan emosi wajah
ALASAN = {"EC1": "EC1: modalitas bukan citra wajah RGB (EEG/suara/sinyal fisiologis/termal/sensor)",
          "EC2": "EC2: tidak membahas efisiensi komputasi atau penerapan di perangkat",
          "EC3": "EC3: bukan kontribusi teknis pengenalan emosi wajah (studi perilaku/psikologi/topik lain)"}

# ---------------------------------------------------------------- 2. ekstraksi (provisional, dari abstrak)
# lok: lokasi inferensi yang dievaluasi; tek: teknik efisiensi; dom: domain
# met: metrik efisiensi yang dilaporkan di abstrak (NR = tidak dilaporkan di abstrak)
E = {
 "P001": dict(model="ResNet18-FCN (wajah) + EEG multimodal", tek=["kuantisasi", "pruning"], plat="Perangkat edge tertanam ber-GPU", lok="edge",
              met="pruning ±60% dari 45,96 jt parameter; INT8 → memori 4× lebih kecil; latensi tanpa angka", akur="NR", dom="HCI/antarmuka", priv="Inferensi di perangkat (on-device)"),
 "P003": dict(model="Ensemble decision tree (fitur landmark)", tek=["fitur landmark ringan"], plat="6 perangkat Android/iOS (Galaxy A53, iPhone SE, dll.)", lok="mobile",
              met="48,32–65,2 FPS di semua perangkat mobile", akur="pengenalan wajah 91–94%; kepuasan 4,46/5 (550 sesi)", dom="kesehatan", priv="Perlindungan identitas; hanya ekspresi avatar yang dikirim"),
 "P004": dict(model="MTCNN terpangkas + SqueezeNet", tek=["arsitektur ringan", "akselerator AI"], plat="Intel NCS (Myriad) vs Raspberry Pi 3", lok="edge",
              met="17,07 ms (±22 FPS pipeline); daya ±1,2 W vs 3,7 W (RPi 3)", akur="emosi ±70%", dom="umum", priv="NR"),
 "P005": dict(model="EfficientNet-B0 + atensi (ATR-Net)", tek=["arsitektur ringan"], plat="Raspberry Pi 400 (TFLite) vs HPC", lok="edge",
              met="4,86 MB; 5,36 FPS (model penuh), 23,45 FPS (EfficientNet-B0 dasar)", akur="FER2013 74,22%; AffectNet-7 67,36%", dom="HCI/antarmuka", priv="NR"),
 "P006": dict(model="MobileNetV2 + ViT ringan + DistilBERT", tek=["arsitektur ringan", "kuantisasi"], plat="Samsung Galaxy A53 (Snapdragon 778G), TFLite INT8", lok="mobile",
              met="8,7 MB (−73%); latensi −55%; 35 FPS", akur="78,9% → 77,2% setelah INT8", dom="HCI/antarmuka", priv="On-device"),
 "P010": dict(model="A-MobileNet (MobileNetV1 + atensi)", tek=["arsitektur ringan"], plat="GPU RTX 2080 Ti", lok="model",
              met="3,4 jt parameter", akur="FERPlus 88,11%; RAF-DB 84,49%", dom="umum", priv="NR"),
 "P011": dict(model="MobileNet (transfer learning)", tek=["arsitektur ringan", "arsitektur mist–fog"], plat="Raspberry Pi (lapisan mist) + fog", lok="fog",
              met="mist (TFLite) 12,23 MB, 7,58 ms; fog 37,30 MB, 23,75 ms", akur="FER2013 63%", dom="smart city/IoT", priv="Pemrosesan didistribusikan ke mist/fog"),
 "P012": dict(model="AFNet + distilasi multi-lapis (MKD)", tek=["arsitektur ringan", "distilasi", "kuantisasi"], plat="Ponsel Android", lok="mobile",
              met="25,86 → 3,62 jt parameter; 231 → 86 ms (distilasi + kuantisasi)", akur="OLFER 0,859 → 0,862", dom="pendidikan", priv="NR"),
 "P013": dict(model="MPENet multi-tugas (parsing + FER)", tek=["multi-tugas"], plat="GPU RTX A6000", lok="model",
              met="11,8 ms (92,9 FPS) di GPU", akur="F1 85,9 (CelebAMask-HQ)", dom="HCI/antarmuka", priv="NR"),
 "P014": dict(model="MobileNetV3-Large (dibanding V2, V3-S, EffNet-B0, NASNetMobile)", tek=["arsitektur ringan", "pruning", "kuantisasi"],
              plat="Smartphone Motorola Moto G6", lok="mobile", met="90–98 ms; memori 4× lebih kecil setelah pruning + kuantisasi", akur="CAFE 65,78% (SOTA 13,91× parameter tidak dapat berjalan di ponsel)",
              dom="kesehatan", priv="On-device"),
 "P015": dict(model="MobileNetV2 + NASNetMobile + WOA", tek=["arsitektur ringan", "seleksi fitur"], plat="PC Core i7 + GPU 8 GB", lok="model",
              met="fitur 2,8× lebih sedikit", akur="82,5% (SVM kubik)", dom="kesehatan", priv="NR"),
 "P018": dict(model="CNN multi-tugas (MobileNet/ResNet/SENet)", tek=["arsitektur ringan", "multi-tugas"], plat="GPU TITAN Xp (server)", lok="model",
              met="MT-MobileNet 71 FPS (GPU); 4–5× lebih cepat dan 4× lebih kecil daripada MT-SENet; akurasi turun rata-rata 0,5%", akur="akurasi setara single-task", dom="HCI/antarmuka", priv="NR"),
 "P019": dict(model="SLFNet 1D-CNN + deskriptor LEDB", tek=["arsitektur ringan"], plat="CPU Core i5 (MATLAB)", lok="model",
              met="208 ribu parameter (pembanding 1,6–69,6 jt)", akur="6 dataset (NR)", dom="umum", priv="NR"),
 "P021": dict(model="Sistem IoT multi-agen (model DL mapan)", tek=["pipeline real-time"], plat="Perangkat IoT/edge multi-kamera (spesifikasi tidak dirinci)", lok="edge",
              met="50 wajah pada 25 FPS; kompleksitas −85% dibanding YOLOv8n", akur="88% (keterlibatan); r = 0,877 dengan pakar", dom="pendidikan",
              priv="Inferensi di edge; hanya indeks keterlibatan teragregasi"),
 "P022": dict(model="MiniBTR (transformer biner + HOG)", tek=["arsitektur ringan", "binarisasi"], plat="PC i7 + GTX 1070", lok="model",
              met="69 ribu parameter", akur="CK+ 95,94%", dom="umum", priv="NR"),
 "P024": dict(model="MediaPipe Face Mesh + pengklasifikasi", tek=["fitur landmark ringan"], plat="Kontinum edge/cloud (rumah pasien)", lok="edge",
              met="landmark MediaPipe <8 ms/citra; klasifikasi 0,02–25 ms", akur="CK+ hingga 0,894 (SVM)", dom="kesehatan", priv="Data disimpan di edge; hanya hasil teranonimisasi dikirim ke cloud rumah sakit"),
 "P025": dict(model="ResSENet (SE di cabang residual)", tek=["arsitektur ringan"], plat="Google Colab: GPU T4 dan CPU Xeon", lok="model",
              met="11,3 jt parameter; 2,50 GFLOPs; 34,4 ms (29,1 FPS) di CPU; 3,84 ms di GPU", akur="FER2013 65,3%; RAF-DB 83,6%", dom="umum", priv="NR"),
 "P026": dict(model="YOLOv8 (tanda wajah kantuk)", tek=["arsitektur ringan"], plat="NVIDIA Jetson Nano", lok="edge",
              met="real-time di Jetson Nano (angka FPS tidak dilaporkan)", akur="mAP50 90,1%", dom="transportasi/keselamatan", priv="Tanpa koneksi internet/cloud (area terpencil)"),
 "P027": dict(model="Fusi multimodal spatio-temporal", tek=["arsitektur ringan"], plat="NVIDIA Jetson AGX Xavier", lok="edge",
              met="15,2 ms; 23 FPS; 68,4 jt parameter (−48,2%)", akur="86,3%", dom="smart city/IoT", priv="Tugas sensitif-latensi diproses lokal di node edge"),
 "P031": dict(model="MediaPipe (deteksi wajah) + VGG-16 dalam aplikasi ponsel", tek=["—"], plat="Aplikasi ponsel", lok="mobile",
              met="tidak dilaporkan (tanpa latensi/ukuran)", akur="FER2013 0,91 (F1 0,91)", dom="kesehatan", priv="NR"),
 "P032": dict(model="MediaPipe Face Mesh/Feature Map + pengklasifikasi", tek=["fitur landmark ringan"], plat="Raspberry Pi 4B vs PC i9 (emulasi cloud)", lok="edge",
              met="1,9–10,8 FPS; daya 5–7 W; cloud 2,8–9× lebih cepat dengan daya ±20×", akur="tidak dievaluasi (fokus biaya komputasi)",
              dom="kesehatan", priv="Pemrosesan di rumah pasien (edge)"),
 "P033": dict(model="MobileNetV3 termodifikasi (emosi dimensional)", tek=["arsitektur ringan"], plat="Intel Movidius Myriad 2 (juga CPU i7, Jetson AGX Orin)", lok="edge",
              met="5 MB setelah OpenVINO (−67%); 1,5 ms (CPU), 9 ms (Myriad); 111 FPS (Myriad)", akur="JAFFE 93,5%; CK+ 96,6%; RMSE 0,413/0,389", dom="HCI/antarmuka", priv="NR"),
 "P034": dict(model="ResNet (FER) + YOLOv11 (postur)", tek=["komputasi on-board"], plat="ARM Cortex-A57/A72/A76", lok="edge",
              met="suhu puncak 36,8 °C (A57); daya >3 W pada beban tinggi; eksekusi AI 1,15–1,45 s", akur="FER 90,2%", dom="kesehatan", priv="Keamanan node IoT medis"),
 "P035": dict(model="CNN ringan + federated learning (FedXAI)", tek=["arsitektur ringan", "federated learning"], plat="Raspberry Pi 4B (TFLite)", lok="edge",
              met="3,6 jt parameter; 0,42 GFLOPs; 59,95 ms (17 FPS); RAM 166,85 MB (MobileNetV2: 513,6 ms)", akur="lintas-dataset 76,2% (terpusat), 74,3% (federated)", dom="kesehatan",
              priv="Data wajah tetap di perangkat (federated)"),
 "P041": dict(model="Pelacakan wajah TrueDepth (iOS)", tek=["fitur landmark ringan"], plat="iPad/iPhone (iOS)", lok="mobile",
              met="60 Hz; ±2% bingkai hilang; bingkai turun saat ponsel memanas", akur="studi kelayakan", dom="kesehatan", priv="Sepenuhnya on-device; tidak perlu internet"),
 "P046": dict(model="FER tertanam (AffectNet)", tek=["kuantisasi"], plat="Analisis model terkuantisasi (tanpa uji perangkat)", lok="model",
              met="kuantisasi dinamis, float16, dan integer; trade-off ukuran vs kinerja", akur="akurasi sedikit turun akibat kuantisasi input", dom="umum", priv="Pengiriman wajah terus-menerus ke cloud dinilai berisiko privasi; kuantisasi bias terhadap kulit gelap"),
 "P054": dict(model="MAGNET multi-tugas audio-visual", tek=["multi-tugas", "kuantisasi"], plat="NVIDIA Jetson AGX Orin (TensorRT)", lok="edge",
              met="69,9 jt parameter (−≈50% vs 2 model single-task); FLOPs separuh; 0,5 s/klip (2 FPS), 0,25 s (4 FPS) dengan FP16", akur="CREMA-D, sebanding dengan single-task", dom="umum", priv="NR"),
 "P065": dict(model="Jaringan atensi multi-wilayah", tek=["kompleksitas O(n)"], plat="Cloud pendidikan cerdas (tanpa pengukuran perangkat)", lok="cloud",
              met="klaim kompleksitas O(n); tidak ada latensi/ukuran", akur="+3–8% (RAF-DB, FERPlus, CAER-S)", dom="pendidikan", priv="Video dianalisis di cloud; penulis mengakui privasi siswa sulit dilindungi"),
 "P073": dict(model="EmoVisioNet (CNN ringan + atensi)", tek=["arsitektur ringan"], plat="PC i7 + RTX 3060", lok="model",
              met="2,30 jt parameter; 0,30 GFLOPs (klaim real-time di mobile tanpa pengukuran)", akur="FER2013 93,88%; FERPlus 96,91%", dom="umum", priv="NR"),
 "P076": dict(model="KDRAG (distilasi ViT-L/14 → ViT-B/32)", tek=["distilasi"], plat="Laptop dengan GPU RTX 4060", lok="model",
              met="86 jt parameter; 105–112 FPS di GPU (baseline ViT-B/32 40–45 FPS)", akur="akurasi 90,8%; RAG menambah 3,4 poin", dom="umum", priv="NR"),
 "P077": dict(model="CSBAM-MobileNet", tek=["arsitektur ringan"], plat="Jetson Nano, Raspberry Pi 4, CPU Intel i5", lok="edge",
              met="6,3 MB; 3,1 jt parameter; 0,31 GFLOPs; 52 ms (19,2 FPS) Jetson Nano; 94 ms (10,6 FPS) Raspberry Pi 4", akur="kelas 91,2%; DAiSEE 92,5%", dom="pendidikan", priv="NR"),
 "P081": dict(model="Vis-Net (ViT + CNN) + penyaringan bingkai", tek=["pipeline real-time"], plat="GPU A100", lok="model",
              met="prediksi tercepat 0,50 s/citra (Vis-NASNet); NASNetLarge ±88 jt parameter", akur="98,94%", dom="transportasi/keselamatan", priv="NR"),
 "P084": dict(model="Distilasi multi-level (ResNet-50 → ResNet-18 untuk FER resolusi rendah)", tek=["distilasi"], plat="GPU V100", lok="model",
              met="jumlah lapisan −60%", akur="FER (NR)", dom="umum", priv="NR"),
}
# ---------------------------------------------------------------- 3. penilaian kualitas (Y=1, P=0,5, N=0), provisional
QA = {  # QA1 tujuan jelas, QA2 metode ringan dijelaskan, QA3 metrik efisiensi kuantitatif, QA4 diuji di perangkat nyata,
        # QA5 kinerja pengenalan dilaporkan, QA6 membahas privasi/beban server/keterbatasan
 "P001": [1, 1, .5, 1, .5, .5], "P003": [1, .5, 1, 1, 1, 1], "P004": [1, 1, 1, 1, 1, .5], "P005": [1, 1, 1, 1, 1, .5],
 "P006": [1, 1, 1, 1, 1, .5], "P010": [1, 1, 1, 0, 1, 0], "P011": [1, 1, 1, 1, 1, .5], "P012": [1, 1, 1, 1, 1, .5],
 "P013": [1, 1, 1, 0, 1, 0], "P014": [1, 1, 1, 1, 1, 1], "P015": [1, 1, .5, 0, 1, 0], "P018": [1, 1, 1, 0, 1, 0],
 "P019": [1, 1, 1, 0, 1, 0], "P021": [1, .5, 1, .5, 1, 1], "P022": [1, 1, 1, 0, 1, 0], "P024": [1, 1, 1, .5, 1, 1],
 "P025": [1, 1, 1, 0, 1, 0], "P026": [1, 1, .5, 1, 1, .5], "P027": [1, 1, 1, 1, 1, .5], "P031": [1, .5, 0, 1, 1, 0],
 "P032": [1, 1, 1, 1, 0, 1], "P033": [1, 1, 1, 1, 1, 0], "P034": [1, .5, 1, 1, 1, .5], "P035": [1, 1, 1, 1, 1, 1],
 "P041": [1, .5, .5, 1, .5, 1], "P046": [1, 1, .5, 0, 1, 1], "P054": [1, 1, 1, 1, 1, 0], "P065": [1, 1, .5, 0, 1, 1],
 "P073": [1, 1, 1, 0, 1, 0], "P076": [1, 1, 1, 0, 1, 0], "P077": [1, 1, 1, 1, 1, 0], "P081": [1, 1, .5, 0, 1, 0],
 "P084": [1, 1, .5, 0, 1, 0],
}
TEKS_LENGKAP = ("P001 P003 P004 P005 P006 P010 P011 P012 P013 P014 "
                "P015 P018 P019 P021 P022 P024 P025 P026 P027 P032 P033 P034 P035 P041 P046 "
                "P031 P054 P073 P076 P077 P081 P084 P065").split()   # lihat teks_lengkap/catatan_teks_lengkap.md
assert set(E) == set(QA)
# Dieksklusi pada TAHAP TEKS LENGKAP (keputusan peneliti, 15 Nov 2026). Ekstraksinya tetap disimpan di E/QA sebagai jejak.
EKS_TL = {
    "P026": "Deteksi kantuk pengemudi dari tanda wajah (mata/mulut, YOLOv8), bukan klasifikasi ekspresi/emosi (EC3)",
    "P081": "Deteksi tingkat kantuk; modul emosi hanya penyaring bingkai, dan semua pengukuran di GPU A100 (EC3)",
    "P084": "Fokus utama distilasi untuk deteksi objek resolusi rendah; FER hanya eksperimen pendamping di GPU V100 (EC3)",
}

# ---------------------------------------------------------------- 3b. AMANDEMEN PROTOKOL (18 Nov 2026, disetujui peneliti)
# IC3 diperketat: wajib BUKTI TINGKAT PERANGKAT = (a) kinerja diukur di perangkat target mobile/edge/tertanam, atau
# (b) sistem dievaluasi pada lokasi pemrosesan tertentu. Berlaku sama untuk studi database dan snowballing.
EKS_IC3 = {i: "Amandemen IC3: hanya diukur di PC/GPU/cloud atau tidak diuji di perangkat target"
           for i in E if E[i]["lok"] == "model" and i not in EKS_TL}
EKS_IC3["P065"] = "Amandemen IC3: penerapan cloud hanya diklaim, tanpa evaluasi sistem"

# ---------------------------------------------------------------- 3c. SNOWBALLING iterasi 1 (Wohlin; OpenAlex, 15-18 Nov 2026)
# Kandidat & keputusan: snowballing/seleksi_iter1.csv dan snowballing/ic3_ketat.csv (teks: snowballing/Sxxx.txt)
SNOW = {
 "S035": dict(model="12 arsitektur ringan (63 klasifikasi + 28 regresi), TFLite", tek=["arsitektur ringan", "kuantisasi"],
              plat="Perangkat Android (aplikasi dirilis)", lok="mobile", met="latensi dievaluasi; real-time dari deteksi wajah sampai klasifikasi (angka NR, dari abstrak)",
              akur="NR", dom="HCI/antarmuka", priv="On-device"),
 "S001": dict(model="CNN (VGG16 vs AlexNet) untuk wajah + emosi", tek=["pipeline real-time"], plat="Robot humanoid (perangkat keras robot)", lok="edge",
              met="diimplementasikan real-time pada robot; latensi tidak dilaporkan", akur="VGG16 terbaik (angka per kelas)", dom="HCI/antarmuka", priv="NR"),
 "S009": dict(model="MobileNet efisien + modul ASP/SFP", tek=["arsitektur ringan", "inferensi kolaboratif edge-cloud"],
              plat="Laptop & smartphone Redmi K30 + cloud (Wi-Fi 0,2–1 MB/s)", lok="fog",
              met="offloading parsial (peta fitur antara ke cloud) memberi latensi terendah di smartphone bila bandwidth >300 KB/s; di laptop, tanpa offloading terbaik",
              akur="RAF-DB/FERPlus (NR di ekstraksi)", dom="umum", priv="Fitur antara dikirim, bukan piksel citra"),
 "S052": dict(model="EC-RFERNet", tek=["arsitektur ringan"], plat="Raspberry Pi pada robot", lok="edge",
              met="0,55 jt parameter; 2,25 MB", akur="5 dataset", dom="HCI/antarmuka", priv="NR"),
 "S053": dict(model="Ekstraktor fitur ringan + modul atensi (citra resolusi rendah)", tek=["arsitektur ringan"], plat="NVIDIA Jetson Nano 4 GB",
              lok="edge", met="47,97 FPS (Jetson Nano); 290,78 FPS (PC i7)", akur="NR", dom="umum", priv="NR"),
 "S054": dict(model="EMOTIZER (multipose, kamera RGB)", tek=["arsitektur ringan"], plat="Perangkat murah + sensor kamera RGB", lok="edge",
              met="real-time pada perangkat murah (angka NR, dari abstrak)", akur="NR", dom="HCI/antarmuka", priv="NR"),
 "S064": dict(model="Lite ResNet-50 vs MobileNetV2", tek=["arsitektur ringan"], plat="Raspberry Pi 4B", lok="edge",
              met="229 ms (2 FPS)", akur="99,8% (2 kelas, data kustom)", dom="umum", priv="NR"),
 "S069": dict(model="EfficientNet-Lite + KNN", tek=["arsitektur ringan", "kuantisasi"], plat="Raspberry Pi 4 (TFLite)", lok="edge",
              met="74,15 ms; INT8 pascapelatihan: ukuran −75%", akur="FER2013 75,26%", dom="umum", priv="NR"),
 "S070": dict(model="CNN; dilatih di cloud, inferensi di edge server", tek=["arsitektur edge"], plat="Smartphone → edge server", lok="edge",
              met="NR (dari abstrak)", akur="NR", dom="smart city/IoT", priv="Edge mengurangi pengiriman data masif ke cloud"),
 "S078": dict(model="CoDA-Net (domain terkompresi + distilasi)", tek=["arsitektur ringan", "distilasi"],
              plat="Jetson Orin Nano, SoC mobile, Raspberry Pi 5", lok="edge",
              met="6,8 jt parameter; 31,0 ms (Jetson Orin Nano), 22,0 ms (SoC mobile); 32,3 klip/s (Jetson), 5,4 klip/s (RPi 5)",
              akur="DFEW-D: 84,2% WAR dipertahankan pada degradasi berat", dom="umum", priv="NR"),
 "S082": dict(model="EmotionNet Nano (desain mesin)", tek=["arsitektur ringan"], plat="Prosesor ARM v8.2 tertanam (15/30 W)", lok="edge",
              met=">25 FPS (15 W), >70 FPS (30 W); 1,7–2,4 citra/s/W", akur="CK+ (NR di ekstraksi)", dom="umum", priv="NR"),
 "S099": dict(model="CNN multi-tugas (umur, gender, emosi)", tek=["multi-tugas", "kuantisasi"], plat="NPU RK3588 (Orange Pi)", lok="edge",
              met="hingga 285,7 FPS", akur="emosi 93,9%", dom="umum", priv="NR"),
 "S101": dict(model="Pipeline TensorFlow.js/MediaPipe (landmark + ekspresi + umur)", tek=["fitur landmark ringan"],
              plat="Browser: Xiaomi 15 dan laptop RTX 5080 (CPU/WASM/WebGL/WebGPU)", lok="mobile",
              met="108 ms (Xiaomi 15, WebGL); 18,4 ms (laptop, WebGL); 2.535 ms (CPU murni)", akur="57,65% (varian ringan)",
              dom="HCI/antarmuka", priv="Sepenuhnya di sisi klien; privasi dievaluasi"),
 "S114": dict(model="Landmark MediaPipe + FFM-L03", tek=["fitur landmark ringan"], plat="Raspberry Pi 3B+ (robot telepresensi)", lok="edge",
              met="9,59 FPS (±104 ms)", akur="+26,1 poin dibanding baseline Ciraolo", dom="kesehatan",
              priv="Landmark geometris, bukan citra RGB (selaras GDPR)"),
 "S118": dict(model="Pengenalan emosi berjenjang", tek=["arsitektur edge"], plat="Mobile edge computing (MEC) berjenjang", lok="fog",
              met="NR (dari abstrak)", akur="NR", dom="smart city/IoT", priv="NR"),
 "S121": dict(model="LiExNet (atensi kanal efisien)", tek=["arsitektur ringan"], plat="NVIDIA Jetson", lok="edge",
              met="42 ribu parameter; 0,03 MB; 1,38 GFLOPs; 530,7 FPS", akur="NR", dom="umum", priv="NR"),
 "S126": dict(model="CNN kompak 48×48", tek=["arsitektur ringan", "kuantisasi"], plat="Raspberry Pi 3B+ (robot perawat)", lok="edge",
              met="INT8: 19,30 ms (51,8 FPS, model saja); latensi −42,7% vs FP32", akur="FER2013 7 kelas", dom="kesehatan", priv="NR"),
 "S137": dict(model="CNN ringan + federated learning", tek=["arsitektur ringan", "federated learning"], plat="Raspberry Pi 4 (TFLite)", lok="edge",
              met="13,92 ms (71,8 FPS); 5,5 MB; ±107 MFLOPs; CPU 25,3%", akur="selisih federated vs terpusat 1,2 poin", dom="kesehatan",
              priv="Data wajah tetap di perangkat (federated)"),
 "S139": dict(model="ARKit blend shapes + kemiripan kosinus", tek=["fitur landmark ringan"], plat="iPhone 14 Pro (TrueDepth)", lok="mobile",
              met="penggunaan sumber daya stabil; 60→30 FPS", akur="68,30% (manusia rata-rata 58,86%)", dom="umum", priv="On-device"),
}
QA.update({
 "S035": [1, 1, .5, .5, .5, 0],
 "S001": [1, .5, 0, 1, .5, 0], "S009": [1, 1, 1, 1, 1, 1], "S052": [1, 1, 1, 1, 1, 0], "S053": [1, 1, 1, 1, .5, 0],
 "S054": [1, .5, .5, .5, .5, 0], "S064": [1, 1, 1, 1, .5, 0], "S069": [1, 1, 1, 1, 1, 0], "S070": [1, .5, .5, .5, .5, 1],
 "S078": [1, 1, 1, 1, 1, .5], "S082": [1, 1, 1, 1, 1, 0], "S099": [1, 1, 1, 1, 1, 0], "S101": [1, 1, 1, 1, .5, 1],
 "S114": [1, 1, 1, 1, 1, 1], "S118": [1, .5, .5, .5, .5, .5], "S121": [1, 1, 1, 1, .5, 0], "S126": [1, 1, 1, 1, 1, .5],
 "S137": [1, 1, 1, 1, 1, 1], "S139": [1, 1, .5, 1, 1, .5],
})
# ---------------------------------------------------------------- 3d. SNOWBALLING iterasi 2 (dari 19 studi iterasi 1; 18 Nov 2026)
# Keputusan: snowballing/iter2_seleksi.csv dan snowballing/iter2_ic3.csv (teks: snowballing/Txxx.txt)
SNOW2 = {
 "T015": dict(model="MobileNetV2 + ViT hibrida", tek=["arsitektur ringan"], plat="Smartphone sebagai perangkat edge", lok="mobile",
              met="real-time di smartphone (angka NR, dari abstrak)", akur="NR", dom="HCI/antarmuka", priv="On-device; privasi meningkat"),
 "T022": dict(model="LSTM spatio-temporal terkompresi tensor", tek=["kuantisasi", "dekomposisi tensor"], plat="Papan RK3399Pro (NPU)", lok="edge",
              met="model terkompresi hingga 221×; latensi −30,2× (ekstraktor fitur) dan −6,62× (LSTM) di NPU vs CPU papan",
              akur="CK+ 97,96%; AFEW 55,60%", dom="umum", priv="NR"),
 "T027": dict(model="MobileNetV2 (TFLite)", tek=["arsitektur ringan", "kuantisasi"], plat="Robot Temi V3 (Android) dan Samsung A52", lok="mobile",
              met="CPU ≤30%; memori dan daya dievaluasi", akur="real-time 82,28% (validasi 92,32%)", dom="HCI/antarmuka", priv="NR"),
 "T030": dict(model="FER berbasis action unit", tek=["arsitektur edge"], plat="Raspberry Pi + Jetson TX2 + server (offloading parsial)", lok="fog",
              met="energi seluruh sistem −30–40% setelah sebagian komputasi dipindah dari cloud ke edge", akur="81,05%", dom="smart city/IoT",
              priv="Sebagian komputasi di edge"),
 "T034": dict(model="FERNet/REFER (dioptimalkan untuk mobile)", tek=["arsitektur ringan", "kuantisasi"], plat="Raspberry Pi 4 bertenaga baterai", lok="edge",
              met="11,5 FPS; 14 FPS dengan TFLite", akur="hingga 97% (APFE)", dom="umum", priv="NR"),
 "T052": dict(model="Titik wajah + pengklasifikasi ML (ROS)", tek=["fitur landmark ringan"], plat="Raspberry Pi 4B (robot murah)", lok="edge",
              met=">13 FPS tanpa akselerator eksternal", akur="NR", dom="HCI/antarmuka", priv="NR"),
 "T065": dict(model="CNN ringan berstruktur pohon (citra kamera mobil + EKG)", tek=["arsitektur ringan"], plat="Kontroler edge di mobil", lok="edge",
              met="beban dan waktu eksekusi berkurang (angka NR, dari abstrak)", akur="NR", dom="smart city/IoT", priv="NR"),
 "T070": dict(model="CNN dalam", tek=["arsitektur edge"], plat="Raspberry Pi (platform edge)", lok="edge",
              met="real-time (angka NR, dari abstrak)", akur="NR", dom="umum", priv="NR"),
 "T083": dict(model="LEMON (CNN dilatasi ringan)", tek=["arsitektur ringan"], plat="Robot asistif (ROS)", lok="edge",
              met="164,76 ± 28,63 ms per prediksi", akur="NR", dom="kesehatan", priv="NR"),
 "T087": dict(model="TinyML hibrida CNN + Mamba", tek=["arsitektur ringan"], plat="Perangkat tertanam berdaya ultra-rendah", lok="edge",
              met="NR (dari abstrak)", akur="NR", dom="umum", priv="NR"),
 "T101": dict(model="Light-FER (ringan + kuantisasi)", tek=["arsitektur ringan", "kuantisasi"], plat="NVIDIA Jetson Nano (<10 W)", lok="edge",
              met="5,51 FPS (TensorRT FP32); memori terendah 1,06 GB (TFLite)", akur="melampaui 25 baseline", dom="umum", priv="NR"),
 "T103": dict(model="Deteksi wajah + SVM", tek=["pipeline real-time"], plat="Raspberry Pi + Pi-cam", lok="edge",
              met="real-time (angka latensi NR)", akur="FER2013 68%", dom="umum", priv="NR"),
 "T104": dict(model="CNN ringan integer-only", tek=["kuantisasi", "akselerator AI"], plat="Akselerator FPGA", lok="edge",
              met="±10 FPS pada 250 MHz; daya 2,3 W", akur="NR", dom="umum", priv="NR"),
}
QA.update({
 "T015": [1, .5, .5, .5, .5, .5], "T022": [1, 1, 1, 1, 1, 0], "T027": [1, 1, .5, 1, 1, 0], "T030": [1, 1, .5, 1, 1, .5],
 "T034": [1, 1, 1, 1, 1, 0], "T052": [1, 1, 1, 1, .5, 0], "T065": [1, .5, .5, .5, .5, .5], "T070": [1, .5, .5, .5, .5, 0],
 "T083": [1, 1, 1, 1, .5, 0], "T087": [1, .5, .5, .5, .5, 0], "T101": [1, 1, 1, 1, 1, 0], "T103": [1, .5, 0, 1, 1, 0],
 "T104": [1, 1, 1, 1, .5, 0],
})
# ---------------------------------------------------------------- 3e. SNOWBALLING iterasi 3 (dari 13 studi iterasi 2; 18 Nov 2026)
SNOW3 = {
 "U017": dict(model="CNN dalam (IoMT)", tek=["akselerator AI"], plat="Raspberry Pi + Intel Movidius NCS2", lok="edge",
              met="real-time di perangkat terbatas sumber daya (angka latensi NR)", akur="FER2013 73%", dom="kesehatan", priv="NR"),
 "U024": dict(model="Penerjemah emosi wearable (umpan balik getar + warna)", tek=["pipeline real-time"], plat="Perangkat wearable di pelipis",
              lok="edge", met="real-time; pengguna beradaptasi ±19 menit (dari abstrak)", akur="7 emosi", dom="kesehatan", priv="NR"),
 "U035": dict(model="MediaPipe + CNN", tek=["fitur landmark ringan"], plat="Raspberry Pi (edge AI)", lok="edge",
              met="real-time (angka latensi NR)", akur="hingga 98% (real-time)", dom="umum", priv="Pemrosesan di perangkat edge"),
}
QA.update({"U017": [1, 1, .5, 1, 1, 0], "U024": [1, .5, .5, .5, .5, 0], "U035": [1, 1, .5, 1, .5, 0]})
SNOW2.update(SNOW3)
SNOW.update(SNOW2)
E.update(SNOW)
SNOW_INK = set(SNOW)
SUMBER_SNOW = {"U024": "abstrak", "T015": "abstrak", "T065": "abstrak", "T070": "abstrak", "T087": "abstrak",
               "S052": "catatan teks lengkap (artikel 2)", "S035": "abstrak", "S054": "abstrak", "S070": "abstrak", "S118": "abstrak"}
TEKS_LENGKAP += [i for i in SNOW if i not in SUMBER_SNOW]
SNOW_META = {r["ID"]: {**r, "Iterasi": "1"} for r in csv.DictReader(open(os.path.join(BASE, "snowballing", "ic3_ketat.csv"), encoding="utf-8-sig"))}
for _b in ("iter2_ic3.csv", "iter3_ic3.csv"):
    SNOW_META.update({r["ID"]: r for r in csv.DictReader(open(os.path.join(BASE, "snowballing", _b), encoding="utf-8-sig"))})
assert SNOW_INK == {i for i, r in SNOW_META.items() if r["IC3 ketat"].startswith("Lolos")}, "SNOW harus sama dengan keputusan ic3_ketat.csv + iter2_ic3.csv"


def _n(nama):
    return len(list(csv.DictReader(open(os.path.join(BASE, "snowballing", nama), encoding="utf-8-sig"))))


def _iter(it, kand, saring):
    meta = {i: r for i, r in SNOW_META.items() if r["Iterasi"] == it}
    return {"kandidat": _n(kand) if it == "1" else sum(1 for r in csv.DictReader(open(os.path.join(BASE, "snowballing", kand), encoding="utf-8-sig"))
                                                    if not r["Saringan"].startswith("sudah")),
            "sudah_dinilai": 0 if it == "1" else _n(kand) - sum(1 for r in csv.DictReader(open(os.path.join(BASE, "snowballing", kand), encoding="utf-8-sig"))
                                                              if not r["Saringan"].startswith("sudah")),
            "lolos_otomatis": _n(saring), "lolos_abstrak": len(meta),
            "inklusi": sum(1 for r in meta.values() if r["IC3 ketat"].startswith("Lolos")),
            "gugur": sum(1 for r in meta.values() if r["IC3 ketat"].startswith("Gugur"))}

# ---------------------------------------------------------------- 4. baca rekaman & tulis CSV
rek = list(csv.DictReader(open(os.path.join(BASE, "pencarian", "gabungan_dedup.csv"), encoding="utf-8-sig")))
assert len(rek) == 84
LOLOS_AB = set(E) - SNOW_INK          # lolos seleksi judul-abstrak dari database (masuk tahap teks lengkap)
LOLOS_DB = LOLOS_AB - set(EKS_TL) - set(EKS_IC3)   # studi database yang bertahan
INK = LOLOS_DB | SNOW_INK              # studi primer final
semua = set(r["ID"] for r in rek)
ec = {**{"P" + i: "EC1" for i in EC1}, **{"P" + i: "EC2" for i in EC2}, **{"P" + i: "EC3" for i in EC3}}
assert LOLOS_AB.isdisjoint(ec) and LOLOS_AB | set(ec) == semua, "setiap rekaman harus punya satu keputusan"
assert set(EKS_TL) <= LOLOS_AB
with open(os.path.join(BASE, "pencarian", "seleksi.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["ID", "Sumber", "Tahun", "Jurnal", "Judul", "DOI", "Keputusan", "Tahap", "Alasan"])
    for r in rek:
        i = r["ID"]
        if i in INK:
            k, tahap, al = "Inklusi", "teks lengkap", ""
        elif i in EKS_TL:
            k, tahap, al = "Eksklusi", "teks lengkap", EKS_TL[i]
        elif i in EKS_IC3:
            k, tahap, al = "Eksklusi", "amandemen IC3 (18 Nov 2026)", EKS_IC3[i]
        else:
            k, tahap, al = "Eksklusi", "judul-abstrak", ALASAN[ec[i]]
        w.writerow([i, r["Sumber"], r["Tahun"], r["Jurnal"], r["Judul"], r["DOI"], k, tahap, al])
byid = {r["ID"]: r for r in rek}
for i, r in SNOW_META.items():           # metadata studi snowballing dengan kunci yang sama
    byid[i] = {"ID": i, "Tahun": r["Tahun"], "Jurnal": r["Sumber"], "Judul": r["Judul"], "DOI": r["DOI"], "Sumber": "snowballing"}
with open(os.path.join(BASE, "pencarian", "ekstraksi_kualitas.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["ID", "Tahun", "Jurnal", "Judul", "Model", "Teknik efisiensi", "Platform", "Lokasi inferensi", "Metrik efisiensi",
                "Kinerja pengenalan", "Domain", "Privasi/data dikirim", "Sumber ekstraksi", "QA1", "QA2", "QA3", "QA4", "QA5", "QA6", "Skor QA"])
    for i in sorted(INK):
        e, r = E[i], byid[i]
        w.writerow([i, r["Tahun"], r["Jurnal"], r["Judul"], e["model"], "; ".join(e["tek"]), e["plat"], e["lok"], e["met"], e["akur"],
                    e["dom"], e["priv"], SUMBER_SNOW.get(i, "teks lengkap" if i in TEKS_LENGKAP else "abstrak"), *QA[i], sum(QA[i])])

# ---------------------------------------------------------------- 5. statistik
src = Counter()
for r in rek:
    for s in r["Sumber"].split("+"):
        src[s] += 1
stat = {
    "per_string_ris": {"S1": 38, "S2": 30, "S3": 10, "S4": 24},
    "total_identifikasi": 102, "unik": len(rek), "duplikat": 102 - len(rek),
    "eksklusi": {"EC1": len(EC1), "EC2": len(EC2), "EC3": len(EC3)}, "lolos_abstrak": len(LOLOS_AB),
    "eksklusi_tl": {i: EKS_TL[i] for i in sorted(EKS_TL)}, "eksklusi_ic3": sorted(EKS_IC3), "lolos_db": len(LOLOS_DB),
    "snow": {"it1": _iter("1", "kandidat_iter1.csv", "kandidat_tersaring.csv"), "it2": _iter("2", "iter2_kandidat.csv", "iter2_tersaring.csv"),
             "it3": _iter("3", "iter3_kandidat.csv", "iter3_tersaring.csv"),
             "it4": _iter("4", "iter4_kandidat.csv", "iter4_tersaring.csv"),   # 0 inklusi -> kejenuhan (iter4_seleksi.csv)
             "kandidat": 0, "lolos_otomatis": 0,
             "lolos_abstrak": len(SNOW_META), "inklusi": len(SNOW_INK),
             "dari_abstrak": sorted(i for i, v in SUMBER_SNOW.items() if v == "abstrak"),
             "gugur": dict(Counter(r["IC3 ketat"] for r in SNOW_META.values() if r["IC3 ketat"].startswith("Gugur"))),
             # gugur karena tidak ada bukti tingkat perangkat (selain EC1 yang terungkap dari teks lengkap: S119, T064)
             "gugur_tanpa_bukti": sum(1 for r in SNOW_META.values() if r["IC3 ketat"].startswith("Gugur") and not r["Catatan IC3"].startswith("EC1")),
             "gugur_ec1": sum(1 for r in SNOW_META.values() if r["IC3 ketat"].startswith("Gugur") and r["Catatan IC3"].startswith("EC1"))},
    "inklusi": len(INK),
    "tahun": dict(sorted(Counter(byid[i]["Tahun"] for i in INK).items())),
    "lokasi": dict(Counter(E[i]["lok"] for i in INK)),
    "domain": dict(Counter(E[i]["dom"] for i in INK).most_common()),
    "teknik": dict(Counter(t for i in INK for t in E[i]["tek"] if t != "—").most_common()),
    "jurnal": dict(Counter(byid[i]["Jurnal"] for i in INK).most_common()),
    "qa_rerata": round(sum(sum(QA[i]) for i in INK) / len(INK), 2),
    "qa_per_kriteria": [round(sum(QA[i][k] for i in INK) / len(INK), 2) for k in range(6)],
    "qa_rendah": sorted(i for i in INK if sum(QA[i]) < 3),
    "uji_perangkat_nyata": sorted(i for i in INK if QA[i][3] == 1),
    "teks_lengkap": len(INK & (set(TEKS_LENGKAP) | {"S052"})),   # studi final yang diekstraksi dari teks lengkap
    "teks_lengkap_dibaca": len(LOLOS_AB & set(TEKS_LENGKAP)),
    "metrik_kuantitatif": sorted(i for i in INK if QA[i][2] == 1),
}
assert sum(stat["eksklusi"].values()) + stat["lolos_abstrak"] == stat["unik"]
assert stat["lolos_abstrak"] - len(EKS_TL) - len(EKS_IC3) == stat["lolos_db"]
assert stat["lolos_db"] + stat["snow"]["inklusi"] == stat["inklusi"]
for _k in ("kandidat", "lolos_otomatis"):
    stat["snow"][_k] = sum(stat["snow"][_it][_k] for _it in ("it1", "it2", "it3", "it4"))
assert sum(stat["snow"][_it]["inklusi"] for _it in ("it1", "it2", "it3", "it4")) == stat["snow"]["inklusi"]
assert stat["snow"]["it4"]["inklusi"] == 0, "iterasi 4 menjadi dasar klaim kejenuhan"

# ---------------------------------------------------------------- 6. gambar
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

def kotak(ax, x, y, w, h, teks, warna="#EAF1F8", tepi="#3B6E9E", fs=8.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02", fc=warna, ec=tepi, lw=1))
    ax.text(x + w / 2, y + h / 2, teks, ha="center", va="center", fontsize=fs, wrap=True)
def panah(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color="#333", lw=1))

# Gambar 1: alur Kitchenham + PRISMA
fig, ax = plt.subplots(figsize=(7.2, 9.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 16); ax.axis("off")
for x, t in [(0.2, "PERENCANAAN\nkebutuhan review, RQ1–RQ5,\nprotokol, string pencarian"),
             (3.5, "PELAKSANAAN\npencarian, seleksi, penilaian\nkualitas, ekstraksi, sintesis"),
             (6.8, "PELAPORAN\nnaskah, ancaman validitas,\nbahan replikasi")]:
    kotak(ax, x, 14.6, 3.0, 1.2, t, warna="#F3F3F3", tepi="#777", fs=7.6)
panah(ax, 3.2, 15.2, 3.5, 15.2); panah(ax, 6.5, 15.2, 6.8, 15.2)
p = stat["per_string_ris"]; sn = stat["snow"]; x = stat["eksklusi"]
ax.text(0.6, 14.05, "JALUR DATABASE", fontsize=8, weight="bold", color="#3B6E9E")
kotak(ax, 0.6, 12.5, 5.4, 1.3, f"Identifikasi: ScienceDirect, 2021–2026, research article\nS1 = {p['S1']}, S2 = {p['S2']}, S3 = {p['S3']}, S4 = {p['S4']}  (total n = {stat['total_identifikasi']})", fs=8)
kotak(ax, 6.6, 12.65, 3.2, 1.0, f"Duplikat dihapus\nn = {stat['duplikat']}", warna="#FBECEC", tepi="#A33", fs=8)
kotak(ax, 0.6, 10.8, 5.4, 1.1, f"Rekaman unik disaring (judul, abstrak, kata kunci)\nn = {stat['unik']}", fs=8)
kotak(ax, 6.6, 10.45, 3.2, 1.8, f"Dieksklusi n = {sum(x.values())}\nEC1 modalitas non-wajah: {x['EC1']}\nEC2 tanpa aspek efisiensi: {x['EC2']}\nEC3 di luar cakupan: {x['EC3']}", warna="#FBECEC", tepi="#A33", fs=7.6)
kotak(ax, 0.6, 9.1, 5.4, 1.1, f"Teks lengkap dinilai kelayakannya\nn = {stat['lolos_abstrak']}", fs=8)
kotak(ax, 6.6, 8.9, 3.2, 1.5, f"Dieksklusi (teks lengkap) n = {len(EKS_TL)}\nEC3 deteksi kantuk: 2\nEC3 fokus deteksi objek: 1", warna="#FBECEC", tepi="#A33", fs=7.6)
kotak(ax, 0.6, 7.4, 5.4, 1.1, f"Amandemen IC3: bukti tingkat perangkat\nn = {stat['lolos_abstrak'] - len(EKS_TL)}", warna="#FFF8DC", tepi="#B8860B", fs=8)
kotak(ax, 6.6, 7.2, 3.2, 1.5, f"Dieksklusi (amandemen IC3)\nn = {len(EKS_IC3)}\nhanya PC/GPU/cloud atau\ntanpa uji perangkat target", warna="#FBECEC", tepi="#A33", fs=7.6)
kotak(ax, 0.6, 5.5, 4.0, 1.1, f"Studi dari database\nn = {stat['lolos_db']}", warna="#E6F4EA", tepi="#2E7D32", fs=8)
ax.text(5.15, 6.85, "JALUR SNOWBALLING", fontsize=8, weight="bold", color="#3B6E9E")
gugur_snow = sum(sn["gugur"].values())
i1, i2, i3, i4 = sn["it1"], sn["it2"], sn["it3"], sn["it4"]
def _baris(nama, d):
    return f"{nama}: {d['kandidat']:,} → {d['lolos_otomatis']} → {d['lolos_abstrak']} → {d['inklusi']}".replace(",", ".")
kotak(ax, 5.15, 3.75, 4.65, 2.95,
      "Snowballing maju + mundur (OpenAlex)\nkandidat baru → saring otomatis →\njudul-abstrak → inklusi (IC3 ketat)\n\n" +
      _baris("Iterasi 1 (30 studi DB)", i1) + "\n" + _baris(f"Iterasi 2 ({i1['inklusi']} studi it. 1)", i2) + "\n" +
      _baris(f"Iterasi 3 ({i2['inklusi']} studi it. 2)", i3) + "\n" + _baris(f"Iterasi 4 ({i3['inklusi']} studi it. 3)", i4) + "  ← jenuh",
      warna="#EAF1F8", fs=7.2)
kotak(ax, 1.8, 2.3, 6.4, 1.1, f"Studi primer final  n = {stat['inklusi']}\n({stat['lolos_db']} database + {sn['inklusi']} snowballing)", warna="#E6F4EA", tepi="#2E7D32")
kotak(ax, 1.8, 0.4, 6.4, 1.2, f"Kejenuhan tercapai pada iterasi 4 (studi baru: {i1['inklusi']} → {i2['inklusi']} →\n{i3['inklusi']} → {i4['inklusi']}). Belum dilakukan: peninjau kedua", warna="#FFF8DC", tepi="#B8860B", fs=8)
panah(ax, 3.3, 12.5, 3.3, 11.9); panah(ax, 6.0, 13.15, 6.6, 13.15); panah(ax, 3.3, 10.8, 3.3, 10.2); panah(ax, 6.0, 11.35, 6.6, 11.35)
panah(ax, 3.3, 9.1, 3.3, 8.5); panah(ax, 6.0, 9.65, 6.6, 9.65); panah(ax, 3.3, 7.4, 3.3, 6.6); panah(ax, 6.0, 7.95, 6.6, 7.95)
panah(ax, 2.6, 5.5, 3.6, 3.4); panah(ax, 7.4, 3.75, 6.4, 3.4); panah(ax, 4.6, 6.05, 5.15, 5.7); panah(ax, 5.0, 2.3, 5.0, 1.6)
panah(ax, 5.0, 14.6, 3.3, 13.8)
fig.savefig(os.path.join(DIR, "gambar", "gambar1_alur_slr.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

# Gambar 2: tahun & lokasi inferensi
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.9))
th = stat["tahun"]; a1.bar(list(th), list(th.values()), color="#3B6E9E")
for k, v in th.items(): a1.text(k, v + 0.15, str(v), ha="center", fontsize=8)
a1.set_title("(a) Studi per tahun terbit", fontsize=9); a1.set_ylabel("Jumlah studi"); a1.spines[["top", "right"]].set_visible(False)
from matplotlib.ticker import MaxNLocator
a1.yaxis.set_major_locator(MaxNLocator(integer=True))
urut = [("mobile", "On-device\nmobile"), ("edge", "Edge/\ntertanam"), ("fog", "Fog/MEC/\nedge–cloud")]
nil = [stat["lokasi"].get(k, 0) for k, _ in urut]
a2.barh([l for _, l in urut][::-1], nil[::-1], color=["#C7A33B", "#2E7D32", "#1B5E20"])
for i, v in enumerate(nil[::-1]): a2.text(v + 0.2, i, str(v), va="center", fontsize=8)
a2.set_title("(b) Lokasi inferensi yang dievaluasi", fontsize=9); a2.set_xlabel("Jumlah studi"); a2.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(DIR, "gambar", "gambar2_tahun_lokasi.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

# Gambar 3: arsitektur konseptual cloud-sentris vs on-device
fig, ax = plt.subplots(figsize=(7.4, 4.3)); ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
ax.text(0.1, 5.7, "(a) Cloud-sentris", fontsize=9.5, weight="bold"); ax.text(0.1, 2.75, "(b) On-device (diusulkan)", fontsize=9.5, weight="bold")
kotak(ax, 0.2, 4.0, 2.2, 1.2, "Ponsel pengguna\nkamera depan")
kotak(ax, 6.0, 4.0, 3.7, 1.2, "Server: deteksi wajah +\nklasifikasi ekspresi untuk\nSEMUA pengguna & bingkai", warna="#FBECEC", tepi="#A33")
panah(ax, 2.4, 4.6, 6.0, 4.6); ax.text(4.2, 4.75, "aliran video mentah", ha="center", fontsize=8)
ax.text(4.2, 4.3, "±13,8 MB/s (640×480, 15 FPS)", ha="center", fontsize=7.5, color="#A33")
kotak(ax, 0.2, 0.9, 5.0, 1.5, "Ponsel pengguna: kamera → deteksi wajah →\nmodel ringan (INT8/FP16) → label emosi\n→ agregasi per jendela waktu + log interaksi", warna="#E6F4EA", tepi="#2E7D32")
kotak(ax, 6.9, 0.9, 2.8, 1.5, "Server: hanya\nmenyimpan &\nmenganalisis ringkasan", warna="#EAF1F8")
panah(ax, 5.2, 1.65, 6.9, 1.65); ax.text(6.05, 1.8, "ringkasan", ha="center", fontsize=8)
ax.text(6.05, 1.35, "puluhan B/s", ha="center", fontsize=7.5, color="#2E7D32")
ax.text(2.7, 0.45, "Citra wajah tidak pernah meninggalkan perangkat", ha="center", fontsize=8, style="italic")
fig.savefig(os.path.join(DIR, "gambar", "gambar3_arsitektur.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------------------- 7. ilustrasi beban jaringan (perhitungan penulis)
w_, h_, c_, fps = 640, 480, 3, 15
mentah = w_ * h_ * c_ * fps                    # byte/detik, RGB 8-bit tak terkompresi
per_bingkai = (7 * 4 + 8) * fps                # 7 probabilitas float32 + stempel waktu 8 B per bingkai
agregat = 7 * 4 + 8                            # satu vektor rerata 7 kelas + stempel waktu per detik
stat["beban"] = {"mentah_Bps": mentah, "label_per_bingkai_Bps": per_bingkai, "agregat_Bps": agregat,
                 "rasio_mentah_per_bingkai": round(mentah / per_bingkai), "rasio_mentah_agregat": round(mentah / agregat),
                 "mentah_GB_per_jam": round(mentah * 3600 / 1e9, 1), "agregat_KB_per_jam": round(agregat * 3600 / 1e3, 1)}

# ---------------------------------------------------------------- 8. daftar pustaka (gaya numerik Elsevier)
cache = json.load(open(os.path.join(DIR, "crossref_cache.json"), encoding="utf-8"))
import html as _html
def bersih(t):   # Crossref menyimpan entitas HTML (&amp;); docx akan meng-escape ulang, jadi harus dibuka di sini
    return _html.unescape(re.sub(r"<[^>]+>", "", _html.unescape(t))).strip()
def fmt(m):
    au = []
    for a in m.get("author", []):
        g = a.get("given", ""); ini = " ".join(x[0] + "." for x in re.split(r"[\s\-]+", g) if x)
        au.append((ini + " " + a.get("family", "")).strip())
    if len(au) > 10: au = au[:10] + ["et al."]
    jud = bersih(m["title"][0])
    jur = bersih((m.get("short-container-title") or m.get("container-title") or [""])[0])
    th = (m.get("published-print") or m.get("published-online") or m.get("issued"))["date-parts"][0][0]
    vol = m.get("volume", ""); hal = m.get("page") or m.get("article-number", "")
    if hal and m["DOI"].lower().endswith("/" + hal.lower()): hal = ""   # nomor artikel = sufiks DOI (online-first) tidak informatif
    if m.get("type") == "proceedings-article":
        s = f"{', '.join(au)}, {jud}, in: {jur or m.get('container-title', [''])[0]}, {th}, pp. {hal}."
    else:
        s = re.sub(r"\s+\.$", ".", f"{', '.join(au)}, {jud}, {jur} {vol} ({th}) {hal}.".replace(" ()", "").replace("  ", " "))
    return s + f" https://doi.org/{m['DOI']}."
REFS = {}
for i in LOLOS_AB | SNOW_INK:           # termasuk studi yang dieksklusi di tahap teks lengkap/amandemen (disitasi sebagai jejak)
    d = byid[i]["DOI"].replace("https://doi.org/", "").lower()
    REFS[i] = fmt(cache[d])
EX = {"SRV05": "10.1177/18761364261508165", "SRV91": "10.31893/multirev.2025328", "SRV93": "10.1145/3737456",
      "YAQ": "10.1016/j.cosrev.2025.100859", "GAY": "10.1016/j.eswa.2026.132709", "SAJ": "10.1016/j.aej.2023.01.017",
      "KIT09": "10.1016/j.infsof.2008.09.009", "WOH": "10.1145/2601248.2601268", "PRISMA": "10.1136/bmj.n71",
      "SAT": "10.1016/j.sysarc.2023.102852", "SHI": "10.1109/jiot.2016.2579198", "LID": "10.1109/taffc.2020.2981446",
      "MBV3": "10.1109/iccv.2019.00140", "JAC": "10.1109/cvpr.2018.00286", "FERP": "10.1145/2993148.2993165",
      "B1": "10.32493/jtsi.v7i4.45117", "B2": "10.24269/mtkind.v18i2.10615", "B3": "10.52436/1.jutif.2026.7.2.5351",
      "B4": "10.17509/jatikom.v9i1.734"}
for k, d in EX.items():
    REFS[k] = fmt(cache[d])
REFS["KIT07"] = ("B. Kitchenham, S. Charters, Guidelines for performing systematic literature reviews in software engineering, "
                 "EBSE Technical Report EBSE-2007-01, Keele University and Durham University, 2007.")
studi = {i: {**E[i], "sumber": "teks lengkap" if i in TEKS_LENGKAP else "abstrak", "qa": QA[i], "skor": sum(QA[i]), "tahun": byid[i]["Tahun"], "jurnal": byid[i]["Jurnal"],
             "judul": byid[i]["Judul"], "penulis1": (cache[byid[i]["DOI"].replace("https://doi.org/", "").lower()].get("author") or [{}])[0].get("family", "")}
         for i in sorted(INK)}
json.dump({"stat": stat, "studi": studi, "refs": REFS}, open(os.path.join(DIR, "data_slr.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps(stat, ensure_ascii=False, indent=1))
