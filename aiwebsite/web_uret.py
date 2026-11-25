import os
import google.generativeai as genai

# 1. API Bağlantısı
# Kendi Gemini API anahtarını buraya yapıştır
API_KEY = "AQ.Ab8RN6JV_UaXQZx5COYfKTY4pXf0JiC1MFT5ygKcEC-SApEsZg"
genai.configure(api_key=API_KEY)

# Not: Ödevde gemini-3.5-flash yazıyor ama hata alırsan gemini-2.5-flash yapabilirsin
model = genai.GenerativeModel(model_name="gemini-3.5-flash")

# 2. Sistem Talimatı (Modeli kesin kurallara bağlar)
sistem_mesaji = """
Sen uzman bir Frontend (HTML5, CSS3, JavaScript) geliştiricisisin.
Kullanıcının tasarım talebine göre birbiriyle tam uyumlu 3 adet HTML sayfası üreteceksin:
1. index.html (Login Sayfası)
2. forgot_password.html (Şifremi Unuttum Sayfası)
3. signup.html (Üye Ol Sayfası)

ZORUNLU TEKNİK KURALLAR:
- Tüm CSS ve JavaScript kodları harici dosya olmadan doğrudan her HTML dosyasının içine (<style> ve <script> etiketleriyle) gömülü olmalıdır.
- Modern, profesyonel, mobil uyumlu (responsive) ve karanlık mod (Dark Mode) tasarım yap.
- Sayfalar arası geçiş bağlantıları (href="index.html", href="forgot_password.html", href="signup.html") eksiksiz çalışmalıdır.
- Butonlarda hover/parlama (glow) animasyonları olmalıdır.
- JavaScript ile form doğrulama (boş alan kontrolü, geçerli e-posta formatı kontrolü, kayıt sayfasında şifre-şifre tekrar eşleşme kontrolü) ve şifre alanlarında göster/gizle (göz ikonu) özelliği ekle.

SAYFA BİLEŞENLERİ:
- index.html: E-posta alanı, Şifre alanı (göster/gizle), Giriş Yap butonu, Şifremi Unuttum bağlantısı, Üye Ol bağlantısı.
- forgot_password.html: Şifremi Unuttum başlığı, E-posta adresi alanı, Şifre sıfırlama bağlantısı gönder butonu, Giriş sayfasına dön bağlantısı.
- signup.html: Ad Soyad alanı, E-posta alanı, Şifre alanı (göster/gizle), Şifre tekrar alanı (göster/gizle), Üye Ol butonu, Giriş sayfasına dön bağlantısı.

ÇIKTI FORMATI (ÇOK ÖNEMLİ):
Yanıtında hiçbir açıklama metni yazma. Sadece aşağıdaki ayıraç etiketlerini kullanarak 3 dosyanın tam HTML kodlarını sırayla ver:

===INDEX.HTML===
(index.html tam kodu)
===FORGOT_PASSWORD.HTML===
(forgot_password.html tam kodu)
===SIGNUP.HTML===
(signup.html tam kodu)
"""

def kodlari_ayristir_ve_kaydet(metin):
    dosyalar = [
        ("index.html", "===INDEX.HTML==="),
        ("forgot_password.html", "===FORGOT_PASSWORD.HTML==="),
        ("signup.html", "===SIGNUP.HTML===")
    ]

    for i, (dosya_adi, baslangic_etiketi) in enumerate(dosyalar):
        baslangic_indeks = metin.find(baslangic_etiketi)
        if baslangic_indeks == -1:
            print(f"[HATA] {baslangic_etiketi} etiketi model çıktısında bulunamadı!")
            continue

        icerik_baslangic = baslangic_indeks + len(baslangic_etiketi)

        # Sonraki etikete kadar olan kısmı al (son dosyaysa metnin sonuna kadar)
        if i + 1 < len(dosyalar):
            sonraki_etiket = dosyalar[i + 1][1]
            bitis_indeks = metin.find(sonraki_etiket, icerik_baslangic)
            html_kodu = metin[icerik_baslangic:bitis_indeks] if bitis_indeks != -1 else metin[icerik_baslangic:]
        else:
            html_kodu = metin[icerik_baslangic:]

        # Markdown kod bloklarını temizle
        html_kodu = html_kodu.replace("```html", "").replace("```", "").strip()

        # UTF-8 olarak kaydet
        with open(dosya_adi, "w", encoding="utf-8") as dosya:
            dosya.write(html_kodu)

        print(f"[BAŞARILI] {dosya_adi} oluşturuldu.")

def main():
    varsayilan_talep = (
        "Modern, profesyonel, karanlık temalı bir üyelik sistemi oluştur. "
        "Mor ve mavi neon renkler kullan. Login, Forgot Password ve Signup sayfaları "
        "aynı tasarım dilini kullansın. Sayfalar arasında geçişler çalışsın. "
        "Butonların üzerine gelindiğinde parlama efekti oluşsun."
    )

    print("Web sitesi tasarım talebinizi girin (Varsayılan örnek için direkt Enter'a basın):")
    tasarim_talebi = input("> ").strip()

    if not tasarim_talebi:
        tasarim_talebi = varsayilan_talep
        print("\nVarsayılan tasarım talebi kullanılıyor...")

    print("Gemini API'ye istek gönderiliyor, lütfen bekleyin...\n")

    try:
        response = model.generate_content(
            sistem_mesaji + "\n\nKullanıcı talebi:\n" + tasarim_talebi,
            generation_config={"temperature": 0.5, "max_output_tokens": 16000}
        )
        kodlari_ayristir_ve_kaydet(response.text)
        print("\nTüm işlemler tamamlandı! index.html dosyasını tarayıcıda açarak test edebilirsin.")
    except Exception as e:
        print(f"\n[HATA] API isteği sırasında bir sorun oluştu: {e}")

if __name__ == "__main__":
    main()