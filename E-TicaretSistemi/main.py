import json
from pathlib import Path
from google import genai
from google.genai import types

# ==========================================
# GEMINI API AYARLARI
# ==========================================
API_ANAHTARI = "API_ANAHTARINI_BURAYA_YAZ"
MODEL = "gemini-3.1-flash-lite"

client = (
    genai.Client(api_key=API_ANAHTARI)
    if API_ANAHTARI
    and API_ANAHTARI != "YENI_API_ANAHTARINI_BURAYA_YAZ"
    else None
)

JSON_DOSYASI = Path(__file__).resolve().parent / "urunler.json"


# ==========================================
# JSON İŞLEMLERİ
# ==========================================
def urunleri_yukle():
    if not JSON_DOSYASI.exists():
        return []

    try:
        with JSON_DOSYASI.open("r", encoding="utf-8") as dosya:
            veriler = json.load(dosya)

        if not isinstance(veriler, list):
            print("[HATA] JSON dosyasının yapısı hatalı.")
            return None

        return veriler

    except (json.JSONDecodeError, OSError) as hata:
        print(f"[HATA] Dosya okunamadı: {hata}")
        return None


def urunleri_kaydet(urunler):
    gecici = JSON_DOSYASI.with_suffix(".tmp")

    try:
        with gecici.open("w", encoding="utf-8") as dosya:
            json.dump(urunler, dosya, ensure_ascii=False, indent=4)

        gecici.replace(JSON_DOSYASI)
        return True

    except OSError as hata:
        print(f"[HATA] Dosya kaydedilemedi: {hata}")
        try:
            gecici.unlink(missing_ok=True)
        except OSError:
            pass
        return False


# ==========================================
# VERİ DOĞRULAMA
# ==========================================
def fiyat_al():
    while True:
        try:
            fiyat = float(
                input("Ürün fiyatı (TL): ").strip().replace(",", ".")
            )

            if 0 < fiyat < float("inf"):
                return round(fiyat, 2)

        except ValueError:
            pass

        print("[HATA] Fiyat sıfırdan büyük bir sayı olmalı.")


def stok_al(mesaj="Stok miktarı: "):
    while True:
        try:
            stok = int(input(mesaj).strip())

            if stok >= 0:
                return stok

        except ValueError:
            pass

        print("[HATA] Stok sıfır veya pozitif bir tam sayı olmalı.")


# ==========================================
# GEMINI İLE ÜRÜN ANALİZİ
# ==========================================
def gemini_analiz(aciklama):
    if client is None:
        print("[HATA] main.py içindeki API anahtarını ayarlamalısın.")
        return None

    istem = f"""
Bir e-ticaret uzmanı olarak aşağıdaki ürünü analiz et.
Türkçe yanıt ver. Olmayan teknik özellikler uydurma.

Sadece geçerli JSON üret ve şu alanları kullan:
{{
  "urun_adi": "Ürün adı",
  "kategori": "Ürün kategorisi",
  "seo_etiketleri": ["etiket1", "etiket2", "etiket3"],
  "satis_aciklamasi": "Ürün için satış açıklaması"
}}

Ürün açıklaması: {json.dumps(aciklama, ensure_ascii=False)}
"""

    try:
        yanit = client.models.generate_content(
            model=MODEL,
            contents=istem,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3,
            ),
        )

        if not yanit.text:
            print("[HATA] Gemini boş yanıt verdi.")
            return None

        veri = json.loads(yanit.text)

        if not isinstance(veri, dict):
            raise ValueError("Yanıt JSON nesnesi değil.")

        for alan in ("urun_adi", "kategori", "satis_aciklamasi"):
            if not isinstance(veri.get(alan), str) or not veri[alan].strip():
                raise ValueError(f"Eksik veya hatalı alan: {alan}")

        etiketler = veri.get("seo_etiketleri")

        if (
            not isinstance(etiketler, list)
            or not all(isinstance(e, str) and e.strip() for e in etiketler)
        ):
            raise ValueError("SEO etiketleri hatalı.")

        return veri

    except Exception as hata:
        print(f"[HATA] Gemini API işlemi başarısız: {hata}")
        return None


# ==========================================
# STOK UYARISI
# ==========================================
def stok_uyarisi(stok):
    if stok == 0:
        print("[UYARI] STOKTA YOK!")
    elif 1 <= stok <= 4:
        print("[UYARI] KRİTİK STOK!")


# ==========================================
# 1 - YENİ ÜRÜN EKLE
# ==========================================
def urun_ekle():
    urunler = urunleri_yukle()

    if urunler is None:
        return

    print("\n--- YENİ ÜRÜN EKLE ---")

    aciklama = input("Ürün açıklaması: ").strip()

    if not aciklama:
        print("[HATA] Ürün açıklaması boş olamaz.")
        return

    fiyat = fiyat_al()
    stok = stok_al()

    print("\n[API] Gemini ürün bilgilerini oluşturuyor...")

    analiz = gemini_analiz(aciklama)

    if analiz is None:
        print("Ürün kaydedilmedi.")
        return

    kodlar = {
        u.get("urun_kodu")
        for u in urunler
        if isinstance(u, dict)
    }

    sira = 1
    while f"URN-{sira:04d}" in kodlar:
        sira += 1

    yeni_urun = {
        "urun_kodu": f"URN-{sira:04d}",
        "urun_adi": analiz["urun_adi"].strip(),
        "kategori": analiz["kategori"].strip(),
        "seo_etiketleri": [
            e.strip() for e in analiz["seo_etiketleri"]
        ],
        "satis_aciklamasi": analiz["satis_aciklamasi"].strip(),
        "urun_aciklamasi": aciklama,
        "fiyat": fiyat,
        "stok": stok,
    }

    urunler.append(yeni_urun)

    if urunleri_kaydet(urunler):
        print("\n[BASARILI] Ürün kaydedildi.")
        print("Ürün Kodu:", yeni_urun["urun_kodu"])
        print("Ürün Adı:", yeni_urun["urun_adi"])
        print("Kategori:", yeni_urun["kategori"])
        print("Fiyat:", yeni_urun["fiyat"], "TL")
        print("Stok:", yeni_urun["stok"])
        print("SEO:", ", ".join(yeni_urun["seo_etiketleri"]))
        print("Açıklama:", yeni_urun["satis_aciklamasi"])
        stok_uyarisi(stok)


# ==========================================
# 2 - ÜRÜNLERİ LİSTELE
# ==========================================
def urunleri_listele():
    urunler = urunleri_yukle()

    if urunler is None:
        return

    if not urunler:
        print("\nHenüz kayıtlı ürün yok.")
        return

    print("\n--- ÜRÜN LİSTESİ ---")

    for urun in urunler:
        if not isinstance(urun, dict):
            continue

        print("-" * 45)
        print("Kod:", urun.get("urun_kodu", "-"))
        print("Ürün:", urun.get("urun_adi", "-"))
        print("Kategori:", urun.get("kategori", "-"))
        print("Fiyat:", urun.get("fiyat", 0), "TL")
        print("Stok:", urun.get("stok", 0))
        print("SEO:", ", ".join(urun.get("seo_etiketleri", [])))
        print("Açıklama:", urun.get("satis_aciklamasi", "-"))


# ==========================================
# 3 - ÜRÜN ARA
# ==========================================
def urun_ara():
    urunler = urunleri_yukle()

    if urunler is None:
        return

    arama = input("\nÜrün adı veya kodu: ").strip().casefold()

    if not arama:
        print("[HATA] Arama boş olamaz.")
        return

    bulunanlar = [
        u for u in urunler
        if isinstance(u, dict)
        and (
            arama in str(u.get("urun_adi", "")).casefold()
            or arama in str(u.get("urun_kodu", "")).casefold()
        )
    ]

    if not bulunanlar:
        print("Ürün bulunamadı.")
        return

    for urun in bulunanlar:
        print("-" * 35)
        print("Kod:", urun.get("urun_kodu"))
        print("Ürün:", urun.get("urun_adi"))
        print("Fiyat:", urun.get("fiyat"), "TL")
        print("Stok:", urun.get("stok"))


# ==========================================
# 4 - STOK GÜNCELLE
# ==========================================
def stok_guncelle():
    urunler = urunleri_yukle()

    if urunler is None:
        return

    kod = input("\nÜrün kodu: ").strip().upper()

    urun = next(
        (
            u for u in urunler
            if isinstance(u, dict)
            and str(u.get("urun_kodu", "")).upper() == kod
        ),
        None,
    )

    if urun is None:
        print("[HATA] Ürün bulunamadı.")
        return

    print("Mevcut stok:", urun.get("stok", 0))
    eski_stok = urun.get("stok", 0)
    yeni_stok = stok_al("Yeni stok miktarı: ")

    urun["stok"] = yeni_stok

    if urunleri_kaydet(urunler):
        print(
            f"[BASARILI] Stok {eski_stok} -> {yeni_stok} olarak güncellendi."
        )
        stok_uyarisi(yeni_stok)


# ==========================================
# ANA MENÜ
# ==========================================
def menu():
    while True:
        print("\n========== E-TİCARET YÖNETİM PANELİ ==========")
        print("1 - Yeni Ürün Ekle")
        print("2 - Ürünleri Listele")
        print("3 - Ürün Ara")
        print("4 - Stok Güncelle")
        print("5 - Çıkış")

        secim = input("Seçiminiz: ").strip()

        if secim == "1":
            urun_ekle()
        elif secim == "2":
            urunleri_listele()
        elif secim == "3":
            urun_ara()
        elif secim == "4":
            stok_guncelle()
        elif secim == "5":
            print("Program kapatılıyor. Görüşürüz!")
            break
        else:
            print("[HATA] Geçersiz seçim. 1-5 arasında seçim yap.")

if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram sonlandırıldı.")