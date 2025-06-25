import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def python_parcala(kod):
    """
    Verilen Python kodunu ayrıştırır:
    - Fonksiyonları bulur ve döndürür.
    - Sınıfları bulur ve döndürür.
    - Ana kod bloğunu tespit eder.
    """
    try:
        # Fonksiyonları bul
        fonksiyonlar = re.findall(r"def\s+(\w+)\s*\((.*?)\):([\s\S]+?)(?=\ndef|\nclass|\Z)", kod)
        
        # Sınıfları bul
        siniflar = re.findall(r"class\s+(\w+)\s*(\(?.*?\))?:([\s\S]+?)(?=\nclass|\Z)", kod)
        
        # Ana kodu tespit et
        ana_kod = re.search(r"if\s+__name__\s*==\s*[\"']__main__[\"']:(.*)", kod, re.DOTALL)

        return {
            "fonksiyonlar": {f[0]: f"def {f[0]}({f[1]}):{f[2]}\n" for f in fonksiyonlar},
            "siniflar": {s[0]: f"class {s[0]}{s[1]}:{s[2]}\n" for s in siniflar},
            "ana_kod": ana_kod.group(0) if ana_kod else None
        }
    except Exception as e:
        logging.error(f"Python kodu ayrıştırma hatası: {e}")
        raise

def dosya_adi_duzenle(adi):
    """Fonksiyon ve sınıf adlarını dosya ismi olarak kullanılabilir hale getirir."""
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', adi)

def kodu_klasore_ayir(dosya_yolu, cikti_klasoru):
    """
    Belirtilen Python dosyasını parçalar ve içeriğini farklı dosyalara kaydeder.
    """
    try:
        os.makedirs(cikti_klasoru, exist_ok=True)
        
        with open(dosya_yolu, "r", encoding="utf-8") as file:
            kod = file.read()
        
        parcali_kod = python_parcala(kod)

        # Sınıflar için ayrı dosya oluştur
        for sinif_adi, sinif_kodu in parcali_kod.get("siniflar", {}).items():
            sinif_adi_duzenli = dosya_adi_duzenle(sinif_adi)
            with open(os.path.join(cikti_klasoru, f"{sinif_adi_duzenli}.py"), "w", encoding="utf-8") as f:
                f.write(sinif_kodu)
        
        # Fonksiyonlar için ayrı dosya oluştur
        for fonksiyon_adi, fonksiyon_kodu in parcali_kod.get("fonksiyonlar", {}).items():
            fonksiyon_adi_duzenli = dosya_adi_duzenle(fonksiyon_adi)
            with open(os.path.join(cikti_klasoru, f"{fonksiyon_adi_duzenli}.py"), "w", encoding="utf-8") as f:
                f.write(fonksiyon_kodu)

        # Ana kodu ayrı bir dosyaya kaydet
        if parcali_kod.get("ana_kod"):
            with open(os.path.join(cikti_klasoru, "main.py"), "w", encoding="utf-8") as f:
                f.write(parcali_kod["ana_kod"])

        logging.info(f"✅ '{dosya_yolu}' dosyası başarıyla ayrıştırıldı ve '{cikti_klasoru}' klasörüne kaydedildi.")
    
    except Exception as e:
        logging.error(f"Dosya ayrıştırma hatası: {e}")
        raise

# Örnek kullanım
if __name__ == "__main__":
    input_file = "ornek.py"  # İşlenecek Python dosyası
    output_folder = "cikti"   # Ayrıştırılmış kodların kaydedileceği klasör
    kodu_klasore_ayir(input_file, output_folder)
