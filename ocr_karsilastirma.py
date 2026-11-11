import os
import csv
import time
import logging
import cv2
import pytesseract
import easyocr
from fast_plate_ocr import LicensePlateRecognizer
from plaka_yardimci import on_isle, plaka_ara, plaka_oku

logging.basicConfig(level=logging.INFO)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
easy = easyocr.Reader(["en"])
fast = LicensePlateRecognizer("cct-xs-v2-global-model")


def oku_tesseract(resim):
    # psm 7: resimde tek satir yazi var
    return pytesseract.image_to_string(resim, config="--psm 7")


def oku_easyocr(resim):
    return "".join(easy.readtext(resim, detail=0))


def oku_fast(resim):
    return plaka_oku(fast, resim)


modeller = {"Tesseract": oku_tesseract, "EasyOCR": oku_easyocr, "fast-plate-ocr": oku_fast}

# gercek plakalar, elle etiketledim
ornekler = []
with open("etiketler.csv") as dosya:
    for satir in csv.DictReader(dosya):
        ornekler.append(["gercek", "kirpintilar/" + satir["dosya"], satir["plaka"]])

# sentetik plakalar, dosya adi plakanin kendisi (01-A-2808.png)
# 100.000 plakadan her 333. sunu aliyorum, hepsi 01 ile baslamasin diye
klasor = "veri/sentetik_turk_plaka/license-plates"
for ad in sorted(os.listdir(klasor))[::333][:300]:
    ornekler.append(["sentetik", klasor + "/" + ad, ad[:-4].replace("-", "")])

sonuclar = []      # [veri, model, on isleme, dogru mu, sure]
for veri, yol, gercek in ornekler:
    resim = cv2.imread(yol)
    for on_isleme in ["yok", "var"]:
        girdi = on_isle(resim) if on_isleme == "var" else resim
        for ad, oku in modeller.items():
            bas = time.time()
            okunan = plaka_ara(oku(girdi))
            sure = (time.time() - bas) * 1000
            sonuclar.append([veri, ad, on_isleme, okunan == gercek, sure])


# her model icin dogru okuma orani ve ortalama sure
for ad in modeller:
    for on_isleme in ["yok", "var"]:
        secilen = [s for s in sonuclar if s[1] == ad and s[2] == on_isleme]
        gercek = [s for s in secilen if s[0] == "gercek"]
        sentetik = [s for s in secilen if s[0] == "sentetik"]
        gercek_oran = 100 * sum(s[3] for s in gercek) / len(gercek)
        sentetik_oran = 100 * sum(s[3] for s in sentetik) / len(sentetik)
        sure = sum(s[4] for s in secilen) / len(secilen)
        logging.info(f"{ad}, on isleme {on_isleme}: gercek %{gercek_oran:.1f}, sentetik %{sentetik_oran:.1f}, {sure:.0f} ms")
