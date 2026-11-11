import cv2
import logging
import numpy as np
from ultralytics import YOLO
from fast_plate_ocr import LicensePlateRecognizer
from plaka_yardimci import fotodan_oku, ucret_hesapla, dakikaya_cevir

logging.basicConfig(level=logging.INFO)

model = YOLO("license-plate-finetune-v1n.pt")
ocr = LicensePlateRecognizer("cct-xs-v2-global-model")

klasor = "veri/turk_plaka/images"

# elle yazdigim bir gunluk senaryo: saat, kamera, foto
# fotolar arac_gruplari.csv den, aracin ilk fotosu giris son fotosu cikis
senaryo = [
    ["07:45", "giris", "1.jpg"],
    ["08:20", "cikis", "23.jpg"],
    ["08:30", "giris", "4.jpg"],
    ["09:00", "giris", "10.jpg"],
    ["10:00", "cikis", "9.jpg"],
    ["13:00", "giris", "31.jpg"],
    ["14:00", "giris", "34.jpg"],
    ["15:30", "cikis", "33.jpg"],
    ["18:00", "cikis", "30.jpg"],
    ["19:20", "cikis", "36.jpg"],
]

iceride = {}       # plaka -> [giris saati, giris fotosu]
kayitlar = []


def kart_yap(plaka, giris, cikis, sure, ucret, giris_foto, cikis_foto):
    # giris ve cikis fotosu yan yana, altina bilgiler
    resimler = []
    for foto in [giris_foto, cikis_foto]:
        resim = cv2.imread(klasor + "/" + foto)
        resimler.append(cv2.resize(resim, (resim.shape[1] * 600 // resim.shape[0], 600)))
    kart = np.hstack(resimler)
    kart = cv2.copyMakeBorder(kart, 0, 120, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    cv2.putText(kart, f"{plaka}   giris {giris}   cikis {cikis}", (15, 650), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(kart, f"sure {sure // 60} sa {sure % 60} dk   ucret {ucret} TL", (15, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.imwrite(f"ekran_goruntuleri/cikis_kartlari/{plaka}.jpg", kart)


for saat, kamera, foto in senaryo:
    plaka = fotodan_oku(model, ocr, cv2.imread(klasor + "/" + foto))

    if kamera == "giris":
        iceride[plaka] = [saat, foto]
        logging.info(f"{saat} giris: {plaka}")
    else:
        giris, giris_foto = iceride.pop(plaka)
        sure = dakikaya_cevir(saat) - dakikaya_cevir(giris)
        ucret = ucret_hesapla(sure)
        kayitlar.append([plaka, giris, saat, sure, ucret])
        logging.info(f"{saat} cikis: {plaka}, {sure} dk, {ucret} TL")
        kart_yap(plaka, giris, saat, sure, ucret, giris_foto, foto)

with open("sonuclar/otopark_kayitlari.csv", "w") as dosya:
    dosya.write("plaka,giris,cikis,sure_dk,ucret_tl\n")
    for plaka, giris, cikis, sure, ucret in kayitlar:
        dosya.write(f"{plaka},{giris},{cikis},{sure},{ucret}\n")

logging.info(f"toplam gelir: {sum(k[4] for k in kayitlar)} TL")
