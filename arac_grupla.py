import os
import cv2
import logging
from ultralytics import YOLO
from fast_plate_ocr import LicensePlateRecognizer
from plaka_yardimci import fotodan_oku

logging.basicConfig(level=logging.INFO)

model = YOLO("license-plate-finetune-v1n.pt")
ocr = LicensePlateRecognizer("cct-xs-v2-global-model")

klasor = "veri/turk_plaka/images"
dosyalar = []
for f in os.listdir(klasor):
    if f.endswith(".jpg"):
        dosyalar.append(f)
dosyalar.sort(key=lambda f: int(f[:-4]))

# her fotodaki plakayi okuyup ayni plakalari ayni gruba atiyorum
gruplar = {}
for dosya in dosyalar:
    plaka = fotodan_oku(model, ocr, cv2.imread(klasor + "/" + dosya))
    if not plaka:
        continue

    if plaka not in gruplar:
        gruplar[plaka] = []
    gruplar[plaka].append(dosya)

with open("sonuclar/arac_gruplari.csv", "w") as dosya:
    dosya.write("plaka,foto_sayisi,fotolar\n")
    for plaka, fotolar in gruplar.items():
        dosya.write(f"{plaka},{len(fotolar)},{' '.join(fotolar)}\n")

logging.info(f"{len(gruplar)} farkli arac bulundu")
