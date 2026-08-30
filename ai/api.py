import os
import json
import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv
from ai.prompts import ANALIZ_PROMPTU, TAKVIM_PROMPTU

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY bulunamadı! Lütfen .env dosyasını kontrol edin.")

client = genai.Client(api_key=API_KEY)
MODEL_ADI = "gemini-3.5-flash"

DUSUK_THINKING_CONFIG = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_level="low")
)

def statik_analiz_uret(veri, tercihler):
    butce_durumu = "ücretsiz" if tercihler.get("butce_tipi") == "Tamamen Ücretsiz" else "bütçe dostu"
    
    return {
        "bulgu": "Sistem (Çevrimdışı Mod): Gece geç saatlerde yoğun bir ekran kullanımınız tespit edildi.",
        "eylem": f"Tercihlerinize uygun olarak, {tercihler.get('sosyal_ortam', 'bireysel')} yapabileceğiniz {butce_durumu} bir etkinlik planlayın."
    }

def _ozetle(veri):
    if not isinstance(veri, dict):
        return veri
        
    if "attention" in veri:
        return veri

    dag = {int(s): n for s, n in veri.get("hourly_distribution", {}).items()}
    sirali = sorted(dag.items(), key=lambda x: x[1], reverse=True)
    
    b = []
    summary = veri.get("summary", {})
    
    if summary.get("night_ratio", 0) >= 0.20: 
        b.append("gece_agirlikli_kullanim")
    if (summary.get("peak_hour") or 0) >= 22: 
        b.append("yatis_oncesi_yogunlasma")
    if summary.get("unique_accounts") and summary.get("total_posts", 0) / (summary.get("unique_accounts") or 1) > 4:
        b.append("dar_hesap_dongusu")
        
    top_hashtags = veri.get("top_hashtags", [])
    if top_hashtags and summary.get("total_posts", 0) > 0:
        if top_hashtags[0].get("count", 0) / summary.get("total_posts") >= 0.15:
            b.append("tek_temada_yogunlasma")
            
    return {
        "schema_version": veri.get("schema_version", "1.1"),
        "user_id": veri.get("user_id", "anon_01"),
        "generated_at": veri.get("generated_at", datetime.datetime.now().isoformat()),
        "attention": {
            "total_posts": summary.get("total_posts", 0),
            "unique_accounts": summary.get("unique_accounts", 0),
            "night_ratio": summary.get("night_ratio", 0),
            "peak_hour": summary.get("peak_hour", 0),
            "top_hours": [{"hour": s, "posts": n} for s, n in sirali[:3]]
        },
        "top_hashtags": top_hashtags[:10],
        "ornek_gonderiler": [
            {
                "title": g.get("title"),
                "hashtags": g.get("hashtags", []),
                "viewed_at": g.get("viewed_at")
            } for g in veri.get("posts", [])[:8]
        ],
        "flags": b,
        "notes": [
            "Bütün sayısal değerler kodda hesaplandı; model hesap yapmamalı.",
            "Bu özet teşhis değildir; yalnızca kullanım desenidir."
        ]
    }

def _json_ayikla(metin):
    return metin.strip().replace("```json", "").replace("```", "").strip()

def ai_analiz_sohbeti_baslat(json_verisi, tercihler):
    """İlk analizi yapar ve sohbet geçmişini döndürür."""
    try:
        butce_metni = f"Maksimum {tercihler['butce_miktari']} TL" if tercihler['butce_tipi'] == "Ücretli / Bütçe Belirle" else "Tamamen Ücretsiz"

        hazir_prompt = ANALIZ_PROMPTU.format(
            sosyal_ortam=tercihler['sosyal_ortam'],
            butce=butce_metni,
            signals_data=json.dumps(_ozetle(json_verisi), ensure_ascii=False)
        )

        chat = client.chats.create(model=MODEL_ADI, config=DUSUK_THINKING_CONFIG)
        response = chat.send_message(hazir_prompt)

        analiz_sonucu = json.loads(_json_ayikla(response.text))
        return analiz_sonucu, chat.get_history()
    except Exception as e:
        print(f"[FALLBACK DEVREDE] Analiz API Hatası: {e}")
        return statik_analiz_uret(json_verisi, tercihler), []

def ai_analizi_revize_et(chat_history, kullanici_mesaji):
    """Mevcut hafızayı kullanarak yeni öneri ister."""
    try:
        chat = client.chats.create(model=MODEL_ADI, history=chat_history, config=DUSUK_THINKING_CONFIG)
        istek_promptu = f"Önceki eylem önerini şu sebeple beğenmedim: '{kullanici_mesaji}'. Lütfen sadece EYLEM kısmını değiştirerek, benim geri bildirimi dikkate alarak bana YENİ BİR ÖNERİ sun. Yanıtını yine SADECE JSON formatında ver."

        response = chat.send_message(istek_promptu)
        yeni_analiz = json.loads(_json_ayikla(response.text))
        return yeni_analiz, chat.get_history()
    except Exception as e:
        return {"bulgu": "Hata", "eylem": f"Revize edilemedi: {e}"}, chat_history

def ai_takvim_cagrisi(json_verisi, secilen_analiz=None):
    """21 günlük takvimi üretir."""
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

        toplam = sum(f.get("gun", 0) for f in takvim)
        if takvim and toplam != 21:
            takvim[-1]["gun"] = max(1, takvim[-1].get("gun", 0) + (21 - toplam))

        return takvim
    except Exception as e:
        return [{"faz": "Hata", "gun": 21, "h": f"Takvim oluşturulamadı: {e}", "kh": "Denge", "r": "#008751"}]