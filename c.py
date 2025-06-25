import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def dosya_tipi_belirle(dosya_yolu):
    """Dosya uzantısına göre dil belirler."""
    try:
        if dosya_yolu.endswith(".cs"):
            return "csharp"
        elif dosya_yolu.endswith(".c"):
            return "c"
        elif dosya_yolu.endswith(".sh"):
            return "shell"
        else:
            raise ValueError("❌ Desteklenmeyen dosya formatı!")
    except Exception as e:
        logging.error(f"Dosya tipi belirleme hatası: {e}")
        raise

def shell_parcala(kod):
    """Shell script içindeki fonksiyonları ve ana kod bloğunu ayrıştırır."""
    try:
        fonksiyonlar = re.findall(r"(\w+)\s*\(\)\s*{([\s\S]+?)}", kod)
        ana_kod = re.sub(r"\w+\s*\(\)\s*{[\s\S]+?}", "", kod).strip()

        return {
            "fonksiyonlar": {f[0]: f"{f[0]}() {{{f[1]}}}\n" for f in fonksiyonlar},
            "ana_kod": ana_kod if ana_kod else None
        }
    except Exception as e:
        logging.error(f"Shell kodu ayrıştırma hatası: {e}")
        raise

def c_parcala(kod):
    """C kodundaki fonksiyonları, struct'ları ve ana kod bloğunu ayırır."""
    try:
        fonksiyonlar = re.findall(r"(\w+\s+\w+\s*\([^)]*\))\s*{([\s\S]+?)}", kod)
        structlar = re.findall(r"struct\s+(\w+)\s*{([\s\S]+?)};", kod)
        globals = re.findall(r"^(?!static|struct|void|int|char|float|double\s+\w+\s*\()(\w+\s+\w+\s*=.*?;|(\w+\s+\w+);)", kod, re.MULTILINE)
        main = re.search(r"(int\s+main\s*\([^)]*\))\s*{([\s\S]+?)}", kod)

        return {
            "fonksiyonlar": {f[0].split()[-1].split('(')[0]: f"{f[0]} {{{f[1]}}}\n" for f in fonksiyonlar if not f[0].strip().startswith('main')},
            "structlar": {s[0]: f"struct {s[0]} {{{s[1]}}}\n" for s in structlar},
            "globals": [g[0] for g in globals if g[0].strip()],
            "ana_kod": f"{main.group(1)} {{{main.group(2)}}}" if main else None
        }
    except Exception as e:
        logging.error(f"C kodu ayrıştırma hatası: {e}")
        raise

def csharp_parcala(kod):
    """C# kodundaki sınıfları, metotları ve ana kod bloğunu ayırır."""
    try:
        siniflar = re.findall(r"class\s+(\w+)\s*{([\s\S]+?)}", kod)
        metotlar = re.findall(r"(public|private|static)?\s*(\w+)\s+(\w+)\s*\((.*?)\)\s*{([\s\S]+?)}", kod)
        ana_kod = re.search(r"static\s+void\s+Main\s*\(\s*\)", kod)

        return {
            "siniflar": {s[0]: f"class {s[0]} {{{s[1]}}}\n" for s in siniflar},
            "metotlar": {m[2]: f"{m[0] or ''} {m[1]} {m[2]}({m[3]}) {{{m[4]}}}\n" for m in metotlar},
            "ana_kod": "static void Main()" if ana_kod else None
        }
    except Exception as e:
        logging.error(f"C# kodu ayrıştırma hatası: {e}")
        raise

def kodu_klasore_ayir(dosya_yolu, cikti_klasoru):
    """Verilen dosyayı parçalar ve içeriğini belirlenen klasöre kaydeder."""
    try:
        os.makedirs(cikti_klasoru, exist_ok=True)

        with open(dosya_yolu, "r", encoding="utf-8") as file:
            kod = file.read()

        dosya_tipi = dosya_tipi_belirle(dosya_yolu)

        if dosya_tipi == "csharp":
            parcali_kod = csharp_parcala(kod)
        elif dosya_tipi == "c":
            parcali_kod = c_parcala(kod)
        elif dosya_tipi == "shell":
            parcali_kod = shell_parcala(kod)

        # Sınıflar için dosya oluştur (C# için)
        for ad, kod in parcali_kod.get("siniflar", {}).items():
            with open(os.path.join(cikti_klasoru, f"{ad}.cs"), "w", encoding="utf-8") as f:
                f.write(kod)

        # Struct'lar için dosya oluştur (C için)
        if dosya_tipi == "c":
            for ad, kod in parcali_kod.get("structlar", {}).items():
                with open(os.path.join(cikti_klasoru, f"{ad}_struct.c"), "w", encoding="utf-8") as f:
                    f.write(kod)

            # Global değişkenler için dosya oluştur
            if parcali_kod.get("globals"):
                with open(os.path.join(cikti_klasoru, "globals.c"), "w", encoding="utf-8") as f:
                    f.write("\n".join(parcali_kod["globals"]))

        # Fonksiyonlar/Metotlar için dosya oluştur
        for ad, kod in parcali_kod.get("fonksiyonlar", {}).items():
            with open(os.path.join(cikti_klasoru, f"{ad}.c" if dosya_tipi == "c" else f"{ad}.sh"), "w", encoding="utf-8") as f:
                f.write(kod)

        for ad, kod in parcali_kod.get("metotlar", {}).items():
            with open(os.path.join(cikti_klasoru, f"{ad}.cs"), "w", encoding="utf-8") as f:
                f.write(kod)

        # Ana kodu kaydet
        if parcali_kod.get("ana_kod"):
            ana_kod_dosyasi = {
                "csharp": "Main.cs",
                "c": "main.c",
                "shell": "main.sh"
            }[dosya_tipi]

            with open(os.path.join(cikti_klasoru, ana_kod_dosyasi), "w", encoding="utf-8") as f:
                f.write(parcali_kod["ana_kod"])

        logging.info(f"✅ '{dosya_yolu}' dosyası parçalandı ve '{cikti_klasoru}' klasörüne kaydedildi.")
    
    except Exception as e:
        logging.error(f"Dosya ayrıştırma hatası: {e}")
        raise

# Örnek kullanım
if __name__ == "__main__":
    input_file = "ornek.c"  # İşlenecek dosya (örnek: .c, .cs, .sh)
    output_folder = "cikti"  # Ayrıştırılan kodların kaydedileceği klasör
    kodu_klasore_ayir(input_file, output_folder)
