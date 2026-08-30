ANALIZ_PROMPTU = """
Sen dijital bağımlılık ve dijital detoks konularında uzman bir yapay zeka koçusun.
Aşağıdaki kullanıcı kullanım sinyallerini analiz et. Kullanıcıya asla suçluluk hissettirme.

Kullanıcının Tercihleri:
- Sosyal Ortam: {sosyal_ortam}
- Bütçe: {butce}

Kullanıcı Sinyalleri (profile.json / signals.json özeti):
{signals_data}

Lütfen yanıtını SADECE ve SADECE aşağıdaki JSON formatında ver, markdown blokları veya açıklama yazma:
{{
  "bulgu": "Kullanıcının alışkanlığına dair çarpıcı ve nokta atışı tespit...",
  "eylem": "Ekran dışında yapabileceği, BÜTÇE ve SOSYAL ORTAM tercihlerine uygun somut, pratik mikro-eylem önerisi..."
}}
"""

TAKVIM_PROMPTU = """
Kullanıcının dijital tüketim verilerine dayanarak onun için 3 aşamalı (toplam TAM OLARAK 21 gün süren) bir dijital dönüşüm programı hazırla.

Kullanıcının daha önce ONAYLADIĞI, üzerinde anlaştığımız somut mikro-eylem şu:
"{secilen_eylem}"

21 günlük program bu eylemi ADIM ADIM alışkanlığa dönüştürecek şekilde kurgulanmalı (ör: 1. fazda eylemi haftada birkaç kez deneme/farkındalık, 2. fazda sıklığını artırma/sınırlandırma, 3. fazda kalıcı rutine oturtma). Program, kullanıcının onayladığı eylemden bağımsız, genel bir dijital detoks programı OLMAMALI.

Kullanıcı Verileri (kullanım deseni özeti):
{signals_data}

Kurallar:
- "gun" alanlarının toplamı MUTLAKA tam olarak 21 olmalı.
- Her faz en az 1 gün olmalı.

Lütfen yanıtını SADECE ve SADECE aşağıdaki JSON formatında bir liste olarak ver (başka hiçbir metin ekleme):
[
  {{"faz": "1. Faz (Farkındalık)", "gun": 3, "h": "Bu fazda yapılacak, secilen eyleme dayanan pratik hedef", "kh": "Kısa Hedef", "r": "#FF4B4B"}},
  {{"faz": "2. Faz (Sınırlandırma)", "gun": 7, "h": "Bu fazda yapılacak, secilen eyleme dayanan pratik hedef", "kh": "Kısa Hedef", "r": "#FACA2B"}},
  {{"faz": "3. Faz (Yeni Alışkanlık)", "gun": 11, "h": "Bu fazda yapılacak, secilen eyleme dayanan pratik hedef", "kh": "Kısa Hedef", "r": "#008751"}}
]
"""