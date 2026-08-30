import json, hashlib, random, statistics, re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

SEMA, TUZ, KULLANICI = "1.0", "ekran-etiketi-2026", "anon_01"

def hashla(ad):
    return "acc_" + hashlib.sha256((TUZ + str(ad).lower().strip()).encode()).hexdigest()[:8]

def simdi():
    return datetime.now(timezone.utc).isoformat()

ILGILER = ["Fitness","Moda","Seyahat","Yemek tarifleri","Teknoloji",
           "Kişisel gelişim","Uyku","Kariyer"]

def sahte_gorunumler(gun=14):
    r = random.Random(42)
    hesaplar = [hashla(f"hesap_{i}") for i in range(35)]
    agirlik = [9,6,3,1,1,1,2,3,4,4,5,6,6,5,5,6,7,8,9,11,14,18,22,17]
    bas = (datetime.now(timezone.utc) - timedelta(days=gun)).replace(
        hour=0, minute=0, second=0, microsecond=0)
    k = []
    for g in range(gun):
        for _ in range(r.randint(40,90)):
            s = r.choices(range(24), weights=agirlik)[0]
            an = bas + timedelta(days=g, hours=s, minutes=r.randint(0,59))
            k.append({"account_hash": r.choice(hesaplar), "viewed_at": an.isoformat()})
    return k

def sahte_oturumlar(gun=14):
    r = random.Random(7)
    niyetler = [("tek mesaja bakacaktım",3),("story atacaktım",5),
                ("bir şey arayacaktım",5),("sadece bakıyordum",10)]
    bas = (datetime.now(timezone.utc) - timedelta(days=gun)).replace(
        hour=0, minute=0, second=0, microsecond=0)
    liste = []
    for g in range(gun):
        for i in range(r.randint(2,5)):
            niyet, plan = r.choice(niyetler)
            gercek = max(1, int(plan * r.uniform(1.2, 9.0)))
            ac = bas + timedelta(days=g, hours=r.randint(8,23), minutes=r.randint(0,59))
            liste.append({"session_id": f"s_{g:02d}_{i}",
                "app": r.choice(["instagram","tiktok","youtube"]),
                "opened_at": ac.isoformat(),
                "closed_at": (ac+timedelta(minutes=gercek)).isoformat(),
                "stated_intent": niyet, "intended_minutes": plan,
                "actual_minutes": gercek, "intent_gap_minutes": gercek-plan})
    return liste

def profil_kur(gorunumler, ilgiler, kaynak):
    saatler, hesaplar = Counter(), Counter()
    for k in gorunumler:
        saatler[datetime.fromisoformat(k["viewed_at"]).hour] += 1
        hesaplar[k["account_hash"]] += 1
    toplam = len(gorunumler) or 1
    gece = sum(n for s,n in saatler.items() if s>=23 or s<3)
    return {"schema_version":SEMA,"user_id":KULLANICI,"generated_at":simdi(),
        "meta_interests":ilgiler,
        "top_accounts":[{"account_hash":h,"view_count":n,"category":None}
                        for h,n in hesaplar.most_common(25)],
        "hourly_distribution":{str(s):saatler.get(s,0) for s in range(24)},
        "summary":{"total_views":len(gorunumler),"unique_accounts":len(hesaplar),
                   "night_ratio":round(gece/toplam,3),
                   "peak_hour":max(saatler,key=saatler.get) if saatler else None},
        "data_notes":{"source":kaynak,"limitations":[
            "İçerik metni export'ta yok; sadece hesap adı ve zaman var.",
            "Hesap adları geri döndürülemez şekilde rumuzlandı.",
            "category alanı boş; C dolduracak."]}}

def sinyal_kur(profil, oturumlar):
    dag = {int(s):n for s,n in profil["hourly_distribution"].items()}
    sirali = sorted(dag.items(), key=lambda x:x[1], reverse=True)
    dikkat = {"total_views":profil["summary"]["total_views"],
              "unique_accounts":profil["summary"]["unique_accounts"],
              "night_ratio":profil["summary"]["night_ratio"],
              "peak_hour":profil["summary"]["peak_hour"],
              "top_hours":[{"hour":s,"views":n} for s,n in sirali[:3]]}
    niyet = None
    if oturumlar:
        farklar = [o["intent_gap_minutes"] for o in oturumlar]
        enkotu = max(oturumlar, key=lambda o:o["intent_gap_minutes"])
        uyg, saat = defaultdict(list), defaultdict(list)
        for o in oturumlar:
            uyg[o["app"]].append(o["intent_gap_minutes"])
            saat[datetime.fromisoformat(o["opened_at"]).hour].append(o["intent_gap_minutes"])
        kotu = sorted(((s,round(statistics.mean(v),1)) for s,v in saat.items()
                       if len(v)>=2), key=lambda x:x[1], reverse=True)[:3]
        niyet = {"sessions_count":len(oturumlar),
            "median_gap_minutes":round(statistics.median(farklar),1),
            "mean_gap_minutes":round(statistics.mean(farklar),1),
            "worst_session":{"app":enkotu["app"],"stated_intent":enkotu["stated_intent"],
                "intended_minutes":enkotu["intended_minutes"],
                "actual_minutes":enkotu["actual_minutes"],"opened_at":enkotu["opened_at"]},
            "gap_by_app":{a:round(statistics.mean(v),1) for a,v in sorted(uyg.items())},
            "worst_hours":[{"hour":s,"mean_gap_minutes":d} for s,d in kotu],
            "most_common_intent":Counter(o["stated_intent"] for o in oturumlar).most_common(1)[0][0]}
    b = []
    if dikkat["night_ratio"]>=0.20: b.append("gece_agirlikli_kullanim")
    if (dikkat["peak_hour"] or 0)>=22: b.append("yatis_oncesi_yogunlasma")
    if dikkat["unique_accounts"] and dikkat["total_views"]/dikkat["unique_accounts"]>20:
        b.append("dar_hesap_dongusu")
    if niyet:
        if niyet["median_gap_minutes"]>=10: b.append("niyet_farki_yuksek")
        if niyet["worst_session"]["actual_minutes"]>=45: b.append("tek_oturum_asiri_uzun")
    return {"schema_version":SEMA,"user_id":profil["user_id"],"generated_at":simdi(),
        "attention":dikkat,"intent":niyet,"interests":profil["meta_interests"][:8],
        "top_accounts":profil["top_accounts"][:8],"flags":b,
        "notes":["Bütün sayısal değerler kodda hesaplandı; model hesap yapmamalı.",
                 "Hesap adları rumuzlanmıştır.",
                 "Bu özet teşhis değildir; yalnızca kullanım desenidir."]}

profil = profil_kur(sahte_gorunumler(), ILGILER, "sahte_veri")
oturumlar = {"schema_version":SEMA,"user_id":KULLANICI,"sessions":sahte_oturumlar()}
sinyaller = sinyal_kur(profil, oturumlar["sessions"])

for ad, veri in [("profile.json",profil),("sessions.json",oturumlar),("signals.json",sinyaller)]:
    with open(ad,"w",encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    print("yazıldı:", ad)

def kontrol_et():
    hata, uyari = [], []
    rumuz = re.compile(r"^acc_[0-9a-f]{8}$")
    p = json.load(open("profile.json",encoding="utf-8"))
    s = json.load(open("sessions.json",encoding="utf-8"))
    g = json.load(open("signals.json",encoding="utf-8"))
    for alan in ["schema_version","user_id","meta_interests","top_accounts",
                 "hourly_distribution","summary","data_notes"]:
        if alan not in p: hata.append(f"profile.json: '{alan}' eksik")
    if len(p.get("hourly_distribution",{}))!=24:
        hata.append("profile.json: hourly_distribution 24 saat olmalı")
    for h in p.get("top_accounts",[]):
        if not rumuz.match(str(h.get("account_hash",""))):
            hata.append(f"profile.json: rumuzlanmamış hesap {h.get('account_hash')}"); break
    if any(h.get("category") is None for h in p.get("top_accounts",[])):
        uyari.append("profile.json: category alanları boş (C dolduracak)")
    for i,o in enumerate(s.get("sessions",[])[:50]):
        if o.get("intent_gap_minutes")!=o.get("actual_minutes",0)-o.get("intended_minutes",0):
            hata.append(f"sessions.json[{i}]: intent_gap_minutes tutarsız")
        try: datetime.fromisoformat(o["opened_at"])
        except Exception: hata.append(f"sessions.json[{i}]: opened_at ISO 8601 değil")
    metin = json.dumps([p,s,g], ensure_ascii=False)
    if re.search(r"[\w\.-]+@[\w\.-]+\.\w+", metin): hata.append("MAHREMİYET: e-posta bulundu")
    if re.search(r"@[A-Za-z0-9_.]{3,}", metin): hata.append("MAHREMİYET: açık hesap adı bulundu")
    print("="*46)
    for m in uyari: print("  UYARI ", m)
    for m in hata:  print("  HATA  ", m)
    print("="*46)
    print(("BAŞARISIZ - " if hata else "GEÇTİ - ")+f"{len(hata)} hata, {len(uyari)} uyarı")

print("\ngörüntüleme:", profil["summary"]["total_views"],
      "| gece oranı:", profil["summary"]["night_ratio"],
      "| yoğun saat:", profil["summary"]["peak_hour"])
print("bayraklar:", ", ".join(sinyaller["flags"]))
print()
kontrol_et()
