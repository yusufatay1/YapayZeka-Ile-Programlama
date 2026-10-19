
import os
from google import genai
from google.genai import errors, types


def kod_optimize_et(spagetti_kod: str) -> None:
    os.system("cls" if os.name == "nt" else "clear")

    print("=" * 75)
    print(" YAPAY ZEKA DESTEKLİ KOD İYİLEŞTİRME VE OPTİMİZASYON ".center(75))
    print("=" * 75)

    # API anahtarını buraya yaz
    api_anahtari = ""

    if not api_anahtari:
        print("\n[HATA] API anahtarı tanımlanmamış!")
        return

    sistem_mesaji = """
    Sen kıdemli bir Yazılım Mimarı ve Performans Uzmanısın.

    Kullanıcının gönderdiği kötü yazılmış (spagetti)
    Python kodunu analiz et.

    1. Değişken isimlerini anlamlı hale getir (Clean Code).
    2. Algoritmanın çalışma hızını iyileştir.
       Örneğin O(n^2) yerine mümkünse O(n) kullan.
    3. Type Hint (Tip belirteçleri) ekle.
    4. Kodun mevcut işlevselliğini koru.
    5. Gereksiz döngüleri ortadan kaldır.

    Çıktın KESİNLİKLE sadece düzeltilmiş Python kodu olmalıdır.
    Ek açıklama veya Markdown yazma.
    """

    print("\n[AŞAMA 1] OPTİMİZE EDİLECEK SPAGETTİ KOD SİSTEME ALINDI...")
    print("\n[AŞAMA 2] REFACTORING İÇİN YAPAY ZEKAYA BAĞLANILIYOR...\n")

    try:
        # Gemini istemcisini oluştur
        with genai.Client(api_key=api_anahtari) as client:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=spagetti_kod,
                config=types.GenerateContentConfig(
                    system_instruction=sistem_mesaji,
                    temperature=0.2
                )
            )

        # Yapay zekanın ürettiği kod
        temiz_kod = response.text

        print("\n[BAŞARILI] OPTİMİZE EDİLMİŞ KOD:\n")
        print(temiz_kod)

    except errors.APIError as e:
        print(f"\n[GEMINI API HATASI] {e}")

    except Exception as e:
        print(f"\n[BEKLENMEYEN HATA] {type(e).__name__}: {e}")


# Kötü yazılmış, iç içe döngüler kullanan spagetti kod
kotu_kod = """
def bul(l):
    r = []
    for i in range(len(l)):
        if l[i] == l[j] and l[i] not in r:
            r.append(l[i])
    return r
"""


# Programı başlat
if __name__ == "__main__":
    kod_optimize_et(kotu_kod)
