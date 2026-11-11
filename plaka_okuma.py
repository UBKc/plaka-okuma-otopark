import cv2
import logging
from collections import Counter
from ultralytics import YOLO
from fast_plate_ocr import LicensePlateRecognizer
from plaka_yardimci import plaka_oku

logging.basicConfig(level=logging.INFO)

model = YOLO("license-plate-finetune-v1n.pt")
ocr = LicensePlateRecognizer("cct-xs-v2-global-model")

video = cv2.VideoCapture("veri/giris_kamerasi.mp4")
fps = video.get(cv2.CAP_PROP_FPS)
cikis_video = cv2.VideoWriter("sonuclar/sistem_demo.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (540, 960))

okunanlar = Counter()     # plaka -> kac karede okundu

kare_no = 0
while True:
    basarili, kare = video.read()
    if not basarili:
        break
    kare_no = kare_no + 1

    sonuc = model(kare, conf=0.4)[0]
    for x1, y1, x2, y2 in sonuc.boxes.xyxy.int().tolist():
        plaka = plaka_oku(ocr, kare[y1:y2, x1:x2])
        if not plaka:
            continue

        if plaka not in okunanlar:
            logging.info(f"yeni plaka: {plaka}")
        okunanlar[plaka] = okunanlar[plaka] + 1

        cv2.rectangle(kare, (x1, y1), (x2, y2), (0, 255, 0), 4)
        cv2.putText(kare, plaka, (x1, y1 - 15), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)

    kucuk = cv2.resize(kare, (540, 960))
    cikis_video.write(kucuk)
    if kare_no % 40 == 0:
        cv2.imwrite(f"ekran_goruntuleri/sistem/kare_{kare_no}.jpg", kucuk)
    cv2.imshow("plaka okuma", kucuk)
    cv2.waitKey(1)

with open("sonuclar/okunan_plakalar.csv", "w") as dosya:
    dosya.write("plaka,okunan_kare\n")
    for plaka, sayi in okunanlar.items():
        dosya.write(f"{plaka},{sayi}\n")

cikis_video.release()
logging.info(f"{len(okunanlar)} farkli plaka okundu")
