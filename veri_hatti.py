import json, hashlib, random, statistics, re
from collections import Counter
from datetime import datetime, timedelta, timezone

SEMA, TUZ, KULLANICI = "1.1", "ekran-etiketi-2026", "anon_01"

def hashla(ad):
    return "acc_" + hashlib.sha256((TUZ+str(ad).lower().strip()).encode()).hexdigest()[:8]
def simdi(): return datetime.now(timezone.utc).isoformat()

HAVUZ = [
 ("20 Dakikada Pratik Akşam Yemeği Tarifi","Bugün mutfakta 20 dakikada hazırlanan bir tarif var 😍 Malzemeler basit, sonuç inanılmaz lezzetli!",["tarifler","pratikyemek","mutfaktanhaberler"],"lezzetlidakikalar","Elif Şahin"),
 ("Fırında Tavuk Nasıl Yapılır","Marine etmenin püf noktası bu 👇 Bir gece bekletirseniz fark yaratıyor",["yemektarifi","firindatavuk","aksamyemegi"],"mutfakgunlugu","Seda Aydın"),
 ("Evde 15 Dakikalık Antrenman","Ekipman yok, bahane yok. Haftada 4 gün bu rutini uygula",["evdespor","antrenman","fitnessmotivasyon"],"hareketzamani","Kaan Yıldırım"),
 ("Koşuya Yeni Başlayanlar İçin","İlk ay hız değil süre hedefleyin. Vücut adaptasyonu böyle oluyor",["kosu","yenibaslayanlar","dayaniklilik"],"asfaltnotlari","Merve Tunç"),
 ("Karadeniz Yaylalarında 3 Gün","Sisin içinden çıkan o manzarayı unutamıyorum ⛰️",["gezi","karadeniz","yayla"],"rotadefteri","Onur Kaplan"),
 ("Lizbon'da Bütçe Dostu Rehber","Tramvaya binmeden önce bu kartı alın, yarı fiyatına geziyorsunuz",["seyahat","lizbon","butcedostu"],"pasaportvekamera","Zeynep Arı"),
 ("Gitarda Bu Akoru Kaçırmayın","Tek parmak değişimiyle şarkının tamamı açılıyor 🎸",["gitar","muzik","akor"],"tellerinardinda","Berk Şen"),
 ("Vinil mi Dijital mi","Analog sesin farkını kulaklıkla bile duyabiliyorsunuz",["muzik","vinil","plak"],"platakayit","Deniz Ulu"),
 ("Suluboyada Gökyüzü Geçişi","Kağıdı ıslatmadan önce açıyı ayarlamak çok önemli 🎨",["suluboya","resim","sanat"],"firca_ve_kagit","Ece Demir"),
 ("Seramikte İlk Denemem","Çarkta merkezleme sandığımdan zormuş ama bağımlılık yapıyor",["seramik","elemegi","atolye"],"camurdanmasal","Ali Korkmaz"),
 ("Python'da Liste Kavrama","Tek satırda döngü yazmanın en temiz yolu bu",["python","yazilim","kodlama"],"kodnotlari","Cem Aksoy"),
 ("Yapay Zeka Nasıl Öğreniyor","Model aslında ezberlemiyor, örüntü çıkarıyor. Farkı bu videoda anlattım",["yapayzeka","teknoloji","egitim"],"veriyoluyla","Nil Ergün"),
 ("Yeni Telefonun Pil Testi","24 saatlik kullanımda beklediğimden iyi çıktı 🔋",["teknoloji","telefon","inceleme"],"teknokutu","Umut Bal"),
 ("Bu Oyunun Sonu Tartışılır","Final sahnesini üçüncü kez izledim, hâlâ aynı fikirdeyim 🎮",["oyun","gaming","inceleme"],"konsolgunlugu","Barış Ay"),
 ("Sonbahar Renk Paleti","Bu üç rengi bir arada kullanınca her kombin oturuyor",["moda","stil","sonbahar"],"dolapdefteri","İpek Yalçın"),
 ("Cilt Bakımında Sıra Önemli","Serumdan önce nemlendirici sürerseniz etkisi düşüyor ✨",["ciltbakimi","guzellik","rutin"],"aynakarsisi","Selin Ok"),
 ("Bu Diziyi Bitirdim","Son bölüm beklediğim gibi değildi ama yolculuk güzeldi",["dizi","eglence","izlenenler"],"ekranaltinda","Kerem Doğan"),
 ("Ders Çalışırken Odaklanma","25 dakika çalış 5 dakika dinlen. Basit ama işe yarıyor 📚",["egitim","calisma","verimlilik"],"defterkenari","Ayça Bozkurt"),
 ("Sabah Rutinimi Değiştirdim","Telefonu yatak odasından çıkarmak en zor kısmıydı",["yasam","rutin","aliskanlik"],"gunlukdenge","Tolga Ersoy"),
 ("Arkadaşlarla Kamp Notları","Çadır kurmayı öğrenmek bir akşamı kurtarıyor 🔥",["kamp","doga","arkadaslik"],"acikhavada","Sude Kara"),
]

def kayit_uret(sayi=60):
    r = random.Random(11)
    agirlik=[9,6,3,1,1,1,2,3,4,4,5,6,6,5,5,6,7,8,9,11,14,18,22,17]
    bas=(datetime.now(timezone.utc)-timedelta(days=14)).replace(hour=0,minute=0,second=0,microsecond=0)
    liste=[]
    for i in range(sayi):
        baslik,acik,etiketler,kadi,isim = r.choice(HAVUZ)
        gun=r.randint(0,13); saat=r.choices(range(24),weights=agirlik)[0]
        an=bas+timedelta(days=gun,hours=saat,minutes=r.randint(0,59))
        liste.append({
          "timestamp": int(an.timestamp()), "media": [],
          "label_values": [
            {"label":"İnternet Adresi (URL)","value":f"https://www.instagram.com/reel/C{r.randint(10**9,10**10)}/",
             "href":f"https://www.instagram.com/reel/C{r.randint(10**9,10**10)}/"},
            {"label":"Açıklama","value":acik},
            {"label":"Başlık","value":baslik},
            {"dict":[{"dict":[{"label":"Ad","value":e}],"title":""} for e in etiketler],
             "title":"Konu etiketleri"},
            {"dict":[{"dict":[
               {"label":"İnternet Adresi (URL)","value":f"https://www.instagram.com/{kadi}/"},
               {"label":"Ad","value":isim},
               {"label":"Kullanıcı adı","value":kadi}],"title":""}],"title":"Sahibi"},
            {"dict":[],"title":"Marka ortağı"}],
          "fbid": str(r.randint(10**16,10**17))})
    return liste

HAM_KAYITLAR = kayit_uret(60)

def kayit_coz(kayit):
    cikti={"caption":None,"title":None,"hashtags":[],"owner_hash":None,
           "viewed_at":datetime.fromtimestamp(kayit["timestamp"],tz=timezone.utc).isoformat()}
    for blok in kayit.get("label_values",[]):
        etiket=blok.get("label"); baslik=blok.get("title")
        if etiket=="Açıklama": cikti["caption"]=blok.get("value")
        elif etiket=="Başlık": cikti["title"]=blok.get("value")
        elif baslik=="Konu etiketleri":
            for d in blok.get("dict",[]):
                for ic in d.get("dict",[]):
                    if ic.get("label")=="Ad": cikti["hashtags"].append(ic["value"])
        elif baslik=="Sahibi":
            for d in blok.get("dict",[]):
                for ic in d.get("dict",[]):
                    if ic.get("label")=="Kullanıcı adı":
                        cikti["owner_hash"]=hashla(ic["value"])
    cikti["category"]=None
    return cikti

def profil_kur(kayitlar,kaynak):
    gonderiler=[kayit_coz(k) for k in kayitlar]
    saatler,sahipler,etiketler=Counter(),Counter(),Counter()
    for g in gonderiler:
        saatler[datetime.fromisoformat(g["viewed_at"]).hour]+=1
        if g["owner_hash"]: sahipler[g["owner_hash"]]+=1
        etiketler.update(g["hashtags"])
    toplam=len(gonderiler) or 1
    gece=sum(n for s,n in saatler.items() if s>=23 or s<3)
    return {"schema_version":SEMA,"user_id":KULLANICI,"generated_at":simdi(),
      "posts":gonderiler,
      "top_hashtags":[{"tag":t,"count":n} for t,n in etiketler.most_common(15)],
      "top_accounts":[{"account_hash":h,"view_count":n,"category":None} for h,n in sahipler.most_common(25)],
      "hourly_distribution":{str(s):saatler.get(s,0) for s in range(24)},
      "summary":{"total_posts":len(gonderiler),"unique_accounts":len(sahipler),
        "unique_hashtags":len(etiketler),"night_ratio":round(gece/toplam,3),
        "peak_hour":max(saatler,key=saatler.get) if saatler else None},
      "data_notes":{"source":kaynak,"limitations":[
        "Kayıtlar sentetiktir, gerçek kullanıcı verisi değildir.",
        "Hesap adları SHA-256 ile rumuzlanmıştır.",
        "category alanı boş; C dolduracak."]}}

def sinyal_kur(p):
    dag={int(s):n for s,n in p["hourly_distribution"].items()}
    sirali=sorted(dag.items(),key=lambda x:x[1],reverse=True)
    b=[]
    if p["summary"]["night_ratio"]>=0.20: b.append("gece_agirlikli_kullanim")
    if (p["summary"]["peak_hour"] or 0)>=22: b.append("yatis_oncesi_yogunlasma")
    if p["summary"]["unique_accounts"] and p["summary"]["total_posts"]/p["summary"]["unique_accounts"]>4:
        b.append("dar_hesap_dongusu")
    if p["top_hashtags"] and p["top_hashtags"][0]["count"]/p["summary"]["total_posts"]>=0.15:
        b.append("tek_temada_yogunlasma")
    return {"schema_version":SEMA,"user_id":p["user_id"],"generated_at":simdi(),
      "attention":{"total_posts":p["summary"]["total_posts"],
        "unique_accounts":p["summary"]["unique_accounts"],
        "night_ratio":p["summary"]["night_ratio"],"peak_hour":p["summary"]["peak_hour"],
        "top_hours":[{"hour":s,"posts":n} for s,n in sirali[:3]]},
      "top_hashtags":p["top_hashtags"][:10],
      "ornek_gonderiler":[{"title":g["title"],"hashtags":g["hashtags"],
        "viewed_at":g["viewed_at"]} for g in p["posts"][:8]],
      "flags":b,
      "notes":["Bütün sayısal değerler kodda hesaplandı; model hesap yapmamalı.",
               "Hesap adları rumuzlanmıştır, açık kullanıcı adı yoktur.",
               "Bu özet teşhis değildir; yalnızca kullanım desenidir."]}

profil=profil_kur(HAM_KAYITLAR,"sentetik_instagram_kayitli")
sinyaller=sinyal_kur(profil)
for ad,veri in [("profile.json",profil),("signals.json",sinyaller)]:
    with open(ad,"w",encoding="utf-8") as f: json.dump(veri,f,ensure_ascii=False,indent=2)
    print("yazıldı:",ad)

def kontrol_et():
    hata,uyari=[],[]
    rumuz=re.compile(r"^acc_[0-9a-f]{8}$")
    p=json.load(open("profile.json",encoding="utf-8")); g=json.load(open("signals.json",encoding="utf-8"))
    for a in ["schema_version","user_id","posts","top_hashtags","top_accounts",
              "hourly_distribution","summary","data_notes"]:
        if a not in p: hata.append(f"profile.json: '{a}' eksik")
    if len(p.get("hourly_distribution",{}))!=24: hata.append("profile.json: 24 saat olmalı")
    for h in p.get("top_accounts",[]):
        if not rumuz.match(str(h.get("account_hash",""))):
            hata.append(f"profile.json: rumuzlanmamış hesap {h.get('account_hash')}"); break
    for i,g2 in enumerate(p.get("posts",[])[:50]):
        if not g2.get("title") or not g2.get("caption"): hata.append(f"posts[{i}]: başlık/açıklama boş")
        try: datetime.fromisoformat(g2["viewed_at"])
        except Exception: hata.append(f"posts[{i}]: viewed_at ISO 8601 değil")
    if any(x.get("category") is None for x in p.get("top_accounts",[])):
        uyari.append("profile.json: category alanları boş (C dolduracak)")
    metin=json.dumps([p,g],ensure_ascii=False)
    if re.search(r"[\w\.-]+@[\w\.-]+\.\w+",metin): hata.append("MAHREMİYET: e-posta bulundu")
    if re.search(r"instagram\.com/[A-Za-z0-9_.]{3,}/",metin): hata.append("MAHREMİYET: açık profil linki bulundu")
    print("="*46)
    for m in uyari: print("  UYARI ",m)
    for m in hata: print("  HATA  ",m)
    print("="*46)
    print(("BAŞARISIZ - " if hata else "GEÇTİ - ")+f"{len(hata)} hata, {len(uyari)} uyarı")

print("\ngönderi:",profil["summary"]["total_posts"],
      "| hesap:",profil["summary"]["unique_accounts"],
      "| gece oranı:",profil["summary"]["night_ratio"],
      "| yoğun saat:",profil["summary"]["peak_hour"])
print("en çok etiket:",", ".join(t["tag"] for t in profil["top_hashtags"][:5]))
print("bayraklar:",", ".join(sinyaller["flags"]))
print()
kontrol_et()
