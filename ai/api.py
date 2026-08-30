# ai/api.py
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from ai.prompts import ANALIZ_PROMPTU, TAKVIM_PROMPTU

# .env dosyasındaki şifreyi yükle
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY bulunamadı! Lütfen .env dosyasını kontrol edin.")

# NOT: eski `google.generativeai` paketi tamamen kullanımdan kaldırıldı
# (artık güncelleme/bugfix almıyor ve ThinkingConfig gibi yeni alanları
# desteklemiyor). Onun yerine resmi, güncel `google-genai` paketini kullanıyoruz.
client = genai.Client(api_key=API_KEY)
MODEL_ADI = "gemini-3.5-flash"

# Bu görev (bulgu + eylem / takvim fazı üretmek) derin reasoning gerektiren bir
# görev değil, sabit şemalı bir JSON üretimi. Gemini 3.x modellerinde thinking
# varsayılan olarak açık (yüksek) ve çok turlu sohbetlerde her turda önceki
# "thought" bağlamı taşınıyor; bu da revize isteklerini turdan tura
# yavaşlatıyor. Bunu düşük bir seviyeye çekiyoruz (tamamen kapatmak
# Gemini 3.x modellerinde mümkün değil, ama "low" gecikmeyi ciddi azaltır).
DUSUK_THINKING_CONFIG = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_level="low")
)


def _ozetle(veri):
    """
    Modelin hesap-hesap ham veriyi (data/profile.json formatı) görmesine gerek yok;
    zaten kodda hesaplanmış özet alanları (summary, hourly_distribution, top_hashtags)
    gönderiyoruz. Bu, prompt boyutunu ciddi şekilde küçültür ve gecikmeyi azaltır.
    Eğer veri zaten özet formattaysa (signals.json gibi, "attention" alanı varsa)
    olduğu gibi geçilir.
    """
    if not isinstance(veri, dict):
        return veri
    if "attention" in veri:
        return veri  # zaten özet (signals.json) formatında

    return {
        "summary": veri.get("summary", {}),
        "hourly_distribution": veri.get("hourly_distribution", {}),
        "top_hashtags": veri.get("top_hashtags", [])[:10],
    }
    # ham gönderi/hesap listelerini (posts, top_accounts) BİLEREK dahil etmiyoruz.


def _json_ayikla(metin):
    return metin.strip().replace("```json", "").replace("```", "").strip()


def ai_analiz_sohbeti_baslat(json_verisi, tercihler):
    """İlk analizi yapar ve SOHBET GEÇMİŞİNİ (hafızayı) döndürür."""
    try:
        butce_metni = f"Maksimum {tercihler['butce_miktari']} TL" if tercihler['butce_tipi'] == "Ücretli / Bütçe Belirle" else "Tamamen Ücretsiz"

        hazir_prompt = ANALIZ_PROMPTU.format(
            sosyal_ortam=tercihler['sosyal_ortam'],
            butce=butce_metni,
            signals_data=json.dumps(_ozetle(json_verisi), ensure_ascii=False)
        )

        # Sohbet başlat (hafıza boş)
        chat = client.chats.create(model=MODEL_ADI, config=DUSUK_THINKING_CONFIG)
        response = chat.send_message(hazir_prompt)

        analiz_sonucu = json.loads(_json_ayikla(response.text))

        # Sonucu ve güncel hafızayı dönüyoruz
        return analiz_sonucu, chat.get_history()
    except Exception as e:
        return {"bulgu": f"Hata oluştu: {e}", "eylem": "Bir süre ekrandan uzaklaş."}, []


def ai_analizi_revize_et(chat_history, kullanici_mesaji):
    """Mevcut hafızayı kullanarak yapay zekadan YENİ bir öneri ister."""
    try:
        # Eski hafızayı yükleyerek sohbeti kaldığı yerden başlat
        chat = client.chats.create(model=MODEL_ADI, history=chat_history, config=DUSUK_THINKING_CONFIG)

        istek_promptu = f"Önceki eylem önerini şu sebeple beğenmedim: '{kullanici_mesaji}'. Lütfen sadece EYLEM kısmını değiştirerek, benim geri bildirimi dikkate alarak bana YENİ BİR ÖNERİ sun. Yanıtını yine SADECE JSON formatında ver."

        response = chat.send_message(istek_promptu)
        yeni_analiz = json.loads(_json_ayikla(response.text))

        # Güncel hafızayı tekrar döndür
        return yeni_analiz, chat.get_history()
    except Exception as e:
        return {"bulgu": "Hata", "eylem": f"Revize edilemedi: {e}"}, chat_history


def ai_takvim_cagrisi(json_verisi, secilen_analiz=None):
    """
    21 günlük takvimi üretir (Tek atımlık istek, hafızaya gerek yok).
    secilen_analiz: kullanıcının Adım 2'de onayladığı {'bulgu':..., 'eylem':...}
    sözlüğü. Takvim, bu spesifik eylem etrafında kurgulanır; verilmezse
    genel bir program üretilir (ideal olan her zaman verilmesidir).
    """
    try:
        secilen_eylem = (secilen_analiz or {}).get("eylem", "Genel ekran süresi azaltma")
        hazir_prompt = TAKVIM_PROMPTU.format(
            secilen_eylem=secilen_eylem,
            signals_data=json.dumps(_ozetle(json_verisi), ensure_ascii=False),
        )
        response = client.models.generate_content(
            model=MODEL_ADI, contents=hazir_prompt, config=DUSUK_THINKING_CONFIG
        )
        takvim = json.loads(_json_ayikla(response.text))

        # Modelin "gun" toplamını her zaman 21 yapacağı garanti değil; son fazı
        # ayarlayarak arayüzdeki 21 günlük gride tam oturmasını sağlıyoruz.
        toplam = sum(f.get("gun", 0) for f in takvim)
        if takvim and toplam != 21:
            takvim[-1]["gun"] = max(1, takvim[-1].get("gun", 0) + (21 - toplam))

        return takvim
    except Exception as e:
        return [{"faz": "Hata", "gun": 21, "h": f"Takvim oluşturulamadı: {e}", "kh": "Denge", "r": "#008751"}]