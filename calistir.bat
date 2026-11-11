@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo 1/2 OCR karsilastirmasi (10-20 dakika)...
python ocr_karsilastirma.py > calistir_log.txt 2>&1
echo 2/2 Otopark...
python otopark.py >> calistir_log.txt 2>&1
