import os
import cv2
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

# veri setindeki ardisik fotograflari giris kamerasi videosuna cevir
klasor = "veri/turk_plaka/images"
genislik, yukseklik = 1080, 1920
fps = 2
resim_sayisi = 300

dosyalar = []
for f in os.listdir(klasor):
    if f.endswith(".jpg"):
        dosyalar.append(f)
dosyalar.sort(key=lambda f: int(f[:-4]))
dosyalar = dosyalar[:resim_sayisi]

yazici = cv2.VideoWriter("veri/giris_kamerasi.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (genislik, yukseklik))

for dosya in dosyalar:
    resim = cv2.imread(klasor + "/" + dosya)
    h, w = resim.shape[:2]
    olcek = min(genislik / w, yukseklik / h)
    resim = cv2.resize(resim, (int(w * olcek), int(h * olcek)))

    # siyah zeminin ortasina yerlestir
    tuval = np.zeros((yukseklik, genislik, 3), np.uint8)
    y = (yukseklik - resim.shape[0]) // 2
    x = (genislik - resim.shape[1]) // 2
    tuval[y:y + resim.shape[0], x:x + resim.shape[1]] = resim

    # her fotograf 1 saniye gorunsun
    yazici.write(tuval)
    yazici.write(tuval)

yazici.release()
logging.info(f"veri/giris_kamerasi.mp4 olusturuldu: {len(dosyalar)} fotograf, {len(dosyalar)} saniye")
