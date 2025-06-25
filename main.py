import os
from p import python_parcala  # p.py içindeki fonksiyonu içe aktarır
from c import csharp_parcala  # c.py içindeki fonksiyonu içe aktarır

def dosyayi_ayir(dosya_yolu, cikti_klasoru):
    """
    Dosyayı tipine göre ayrıştırır ve çıktı klasörüne kaydeder.
    """
    os.makedirs(cikti_klasoru, exist_ok=True)

    try:
        with open(dosya_yolu, "r", encoding="utf-8", errors="ignore") as file:
            kod = file.read()
    except UnicodeDecodeError:
        print(f"❌ '{dosya_yolu}' dosyası UTF-8 kodlamasıyla okunamıyor. ISO-8859-1 kodlaması ile tekrar deneniyor...")
        with open(dosya_yolu, "r", encoding="ISO-8859-1", errors="ignore") as file:
            kod = file.read()

    dosya_tipi = dosya_yolu.split('.')[-1].lower()

    # Python dosyasını ayrıştır
    if dosya_tipi == 'py':
        parcali_kod = python_parcala(kod)
        for sinif_adi, sinif_kodu in parcali_kod.get("siniflar", {}).items():
            with open(os.path.join(cikti_klasoru, f"{sinif_adi}.txt"), "w", encoding="utf-8") as f:
                f.write(sinif_kodu)
        for fonksiyon_adi, fonksiyon_kodu in parcali_kod.get("fonksiyonlar", {}).items():
            with open(os.path.join(cikti_klasoru, f"{fonksiyon_adi}.txt"), "w", encoding="utf-8") as f:
                f.write(fonksiyon_kodu)
        if parcali_kod.get("ana_kod"):
            with open(os.path.join(cikti_klasoru, "main.txt"), "w", encoding="utf-8") as f:
                f.write(parcali_kod["ana_kod"])

    # C# dosyasını ayrıştır
    elif dosya_tipi == 'cs':
        parcali_kod = csharp_parcala(kod)
        for sinif_adi, sinif_kodu in parcali_kod.get("siniflar", {}).items():
            with open(os.path.join(cikti_klasoru, f"{sinif_adi}.txt"), "w", encoding="utf-8") as f:
                f.write(sinif_kodu)
        for metot_adi, metot_kodu in parcali_kod.get("metotlar", {}).items():
            with open(os.path.join(cikti_klasoru, f"{metot_adi}.txt"), "w", encoding="utf-8") as f:
                f.write(metot_kodu)
        if parcali_kod.get("ana_kod"):
            with open(os.path.join(cikti_klasoru, "main.txt"), "w", encoding="utf-8") as f:
                f.write(parcali_kod["ana_kod"])

    else:
        print(f"❌ Desteklenmeyen dosya tipi: {dosya_tipi}. Sadece Python (.py) ve C# (.cs) dosyaları işlenebilir.")

def terminal_arayuz():
    print("🔹 **Python ve C# Kodu Ayrıştırıcı Aracı** 🔹")
    
    while True:
        try:
            klasor_yolu = input("\n📂 Lütfen **parçalanacak dosyaların bulunduğu klasörün tam yolunu** girin: ").strip()

            if not os.path.isdir(klasor_yolu):
                raise NotADirectoryError(f"❌ '{klasor_yolu}' geçerli bir klasör yolu değil. Lütfen geçerli bir klasör yolu girin.")

            hedef_klasor = input("\n📂 Lütfen **çıktının kaydedileceği klasörün tam yolunu** girin: ").strip()

            if not os.path.exists(hedef_klasor):
                try:
                    os.makedirs(hedef_klasor)
                    print(f"✅ Klasör oluşturuldu: {hedef_klasor}")
                except Exception as e:
                    raise PermissionError(f"❌ Klasör oluşturulurken bir hata oluştu: {e}")

            dosyalar = []
            for root, dirs, files in os.walk(klasor_yolu):
                for dosya in files:
                    dosya_yolu = os.path.join(root, dosya)
                    dosyalar.append(dosya_yolu)

            if not dosyalar:
                print(f"❌ '{klasor_yolu}' klasöründe işlenecek dosya bulunamadı.")
                continue

            for dosya_yolu in dosyalar:
                dosyayi_ayir(dosya_yolu, hedef_klasor)
                print(f"✅ '{dosya_yolu}' dosyası başarıyla ayrıştırıldı ve .txt olarak kaydedildi.")

        except ValueError as ve:
            print(f"❌ {ve}")

        except FileNotFoundError as fnf_error:
            print(fnf_error)

        except PermissionError as perm_error:
            print(perm_error)

        except NotADirectoryError as dir_error:
            print(dir_error)

        except Exception as e:
            print(f"❌ Beklenmeyen bir hata oluştu: {e}")

        devam_mi = input("\n➡ Yeni bir klasör üzerinde işlem yapmak ister misiniz? (E/H): ").strip().lower()
        if devam_mi != "e":
            print("👋 Çıkış yapılıyor...")
            break

if __name__ == "__main__":
    terminal_arayuz()
