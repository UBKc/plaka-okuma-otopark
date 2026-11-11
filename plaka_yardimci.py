import re
import math
import cv2

# 2 rakam il kodu, 1-3 harf, 2-5 rakam
plaka_kalibi = re.compile(r"\d{2}[A-Z]{1,3}\d{2,5}")


def on_isle(resim):
    # gri, buyut, siyah-beyaz
    gri = cv2.cvtColor(resim, cv2.COLOR_BGR2GRAY)
    gri = cv2.resize(gri, None, fx=2, fy=2)
    _, ikili = cv2.threshold(gri, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return ikili


def plaka_ara(metin):
    # buyuk harf yap, harf ve rakam disini sil, icinde plakaya benzeyen kismi bul
    metin = re.sub(r"[^A-Z0-9]", "", metin.upper())
    bulunan = plaka_kalibi.search(metin)
    if bulunan:
        return bulunan.group()
    return ""


def plaka_oku(ocr, kirpinti):
    cv2.imwrite("gecici.png", kirpinti)
    return plaka_ara(str(ocr.run("gecici.png")[0]))


def fotodan_oku(model, ocr, resim):
    sonuc = model(resim, conf=0.4)[0]
    if len(sonuc.boxes) == 0:
        return ""
    en_iyi = int(sonuc.boxes.conf.argmax())
    x1, y1, x2, y2 = sonuc.boxes.xyxy[en_iyi].int().tolist()
    return plaka_oku(ocr, resim[y1:y2, x1:x2])


def ucret_hesapla(dakika):
    if dakika <= 60:
        return 50
    elif dakika <= 120:
        return 80
    elif dakika <= 240:
        return 150
    else:
        # 4 saatten sonra baslayan her saat icin 30 tl ekleniyor
        ek_saat = math.ceil((dakika - 240) / 60)
        return 150 + ek_saat * 30


def dakikaya_cevir(saat):
    # "08:30" -> 8 * 60 + 30 = 510
    saat, dakika = saat.split(":")
    return int(saat) * 60 + int(dakika)
