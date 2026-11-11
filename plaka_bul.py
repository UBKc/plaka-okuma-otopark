import os
import cv2
import logging
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)

model = YOLO("license-plate-finetune-v1n.pt")

klasor = "veri/turk_plaka/images"
os.makedirs("kirpintilar", exist_ok=True)
os.makedirs("ekran_goruntuleri/tespit", exist_ok=True)

dosyalar = []
for f in os.listdir(klasor):
    if f.endswith(".jpg"):
        dosyalar.append(f)
dosyalar.sort(key=lambda f: int(f[:-4]))
dosyalar = dosyalar[:300]

bulunan = 0
for sira, dosya in enumerate(dosyalar):
    resim = cv2.imread(klasor + "/" + dosya)
    sonuc = model(resim, conf=0.4)[0]
    kutular = sonuc.boxes.xyxy.int().tolist()
    if len(kutular) > 0:
        bulunan = bulunan + 1

    # plakalari kesip kaydediyorum
    for i, (x1, y1, x2, y2) in enumerate(kutular):
        cv2.imwrite(f"kirpintilar/{dosya[:-4]}_{i}.jpg", resim[y1:y2, x1:x2])

    # ilk 20 fotoyu kutulu kaydediyorum
    if sira < 20:
        cizili = sonuc.plot(line_width=10)
        cv2.imwrite(f"ekran_goruntuleri/tespit/{dosya}", cv2.resize(cizili, None, fx=0.2, fy=0.2))

logging.info(f"plaka bulunan foto: {bulunan}/{len(dosyalar)}")
