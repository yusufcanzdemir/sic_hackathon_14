import json, hashlib, random, statistics, re, os
from collections import Counter
from datetime import datetime, timedelta, timezone

SEMA, TUZ, KULLANICI = "1.1", "ekran-etiketi-2026", "anon_01"

def hashla(ad):
    return "acc_" + hashlib.sha256((TUZ+str(ad).lower().strip()).encode()).hexdigest()[:8]
def simdi(): return datetime.now(timezone.utc).isoformat()

# İçerikler İngilizceye çevrildi
HAVUZ = [
 ("20-Minute Quick Dinner Recipe","Today in the kitchen there is a recipe ready in 20 minutes 😍 Ingredients are simple, the result is incredibly delicious!",["recipes","quickmeal","kitchennews"],"tastyminutes","Elif Sahin"),
 ("How to Make Baked Chicken","The trick to marinating is this 👇 Waiting overnight makes a difference",["recipe","bakedchicken","dinner"],"kitchenjournal","Seda Aydin"),
 ("15-Minute Home Workout","No equipment, no excuses. Do this routine 4 days a week",["homeworkout","training","fitnessmotivation"],"time2move","Kaan Yildirim"),
 ("For Beginner Runners","Aim for time, not speed in the first month. That's how the body adapts",["running","beginners","endurance"],"asphaltnotes","Merve Tunc"),
 ("3 Days in the Black Sea Highlands","I can't forget that view emerging from the fog ⛰️",["travel","blacksea","highlands"],"routebook","Onur Kaplan"),
 ("Budget-Friendly Guide to Lisbon","Get this card before taking the tram, you travel for half price",["travel","lisbon","budgetfriendly"],"passportandcamera","Zeynep Ari"),
 ("Don't Miss This Chord on Guitar","The whole song unlocks with a single finger change 🎸",["guitar","music","chord"],"behindthestrings","Berk Sen"),
 ("Vinyl or Digital","You can hear the difference of analog sound even with headphones",["music","vinyl","record"],"recordplay","Deniz Ulu"),
 ("Sky Transition in Watercolor","Setting the angle before wetting the paper is crucial 🎨",["watercolor","painting","art"],"brush_and_paper","Ece Demir"),
 ("My First Try in Ceramics","Centering on the wheel was harder than I thought but it's addictive",["ceramics","handmade","workshop"],"claytale","Ali Korkmaz"),
 ("List Comprehension in Python","This is the cleanest way to write a loop in a single line",["python","software","coding"],"codenotes","Cem Aksoy"),
 ("How AI Learns","The model doesn't actually memorize, it extracts patterns. I explained the difference in this video",["ai","technology","education"],"datapath","Nil Ergun"),
 ("New Phone's Battery Test","It turned out better than I expected in 24-hour usage 🔋",["technology","phone","review"],"techbox","Umut Bal"),
 ("The End of This Game is Debatable","I watched the final scene for the third time, I still hold the same opinion 🎮",["gaming","game","review"],"consolediary","Baris Ay"),
 ("Autumn Color Palette","When you use these three colors together, every outfit fits",["fashion","style","autumn"],"closetdiary","Ipek Yalcin"),
 ("Order Matters in Skincare","If you apply moisturizer before serum, its effect drops ✨",["skincare","beauty","routine"],"mirrorface","Selin Ok"),
 ("I Finished This Series","The final episode wasn't what I expected but the journey was beautiful",["series","entertainment","watched"],"underscreen","Kerem Dogan"),
 ("Focusing While Studying","Work 25 mins rest 5 mins. Simple but effective 📚",["education","study","productivity"],"notebookedge","Ayca Bozkurt"),
 ("I Changed My Morning Routine","Getting the phone out of the bedroom was the hardest part",["life","routine","habit"],"dailybalance","Tolga Ersoy"),
 ("Camping Notes with Friends","Learning to pitch a tent saves the evening 🔥",["camping","nature","friendship"],"outdoors","Sude Kara"),
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
            {"label":"Web Address (URL)","value":f"https://www.instagram.com/reel/C{r.randint(10**9,10**10)}/",
             "href":f"https://www.instagram.com/reel/C{r.randint(10**9,10**10)}/"},
            {"label":"Caption","value":acik},
            {"label":"Title","value":baslik},
            {"dict":[{"dict":[{"label":"Name","value":e}],"title":""} for e in etiketler],
             "title":"Hashtags"},
            {"dict":[{"dict":[
               {"label":"Web Address (URL)","value":f"https://www.instagram.com/{kadi}/"},
               {"label":"Name","value":isim},
               {"label":"Username","value":kadi}],"title":""}],"title":"Owner"},
            {"dict":[],"title":"Brand partner"}],
          "fbid": str(r.randint(10**16,10**17))})
    return liste

HAM_KAYITLAR = kayit_uret(60)

def kayit_coz(kayit):
    cikti={"caption":None,"title":None,"hashtags":[],"owner_hash":None,
           "viewed_at":datetime.fromtimestamp(kayit["timestamp"],tz=timezone.utc).isoformat()}
    for blok in kayit.get("label_values",[]):
        etiket=blok.get("label"); baslik=blok.get("title")
        if etiket=="Caption": cikti["caption"]=blok.get("value")
        elif etiket=="Title": cikti["title"]=blok.get("value")
        elif baslik=="Hashtags":
            for d in blok.get("dict",[]):
                for ic in d.get("dict",[]):
                    if ic.get("label")=="Name": cikti["hashtags"].append(ic["value"])
        elif baslik=="Owner":
            for d in blok.get("dict",[]):
                for ic in d.get("dict",[]):
                    if ic.get("label")=="Username":
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
        "Records are synthetic, not real user data.",
        "Account names are pseudonymized with SHA-256.",
        "category field is empty; to be filled."]}
    }

def sinyal_kur(p):
    dag={int(s):n for s,n in p["hourly_distribution"].items()}
    sirali=sorted(dag.items(),key=lambda x:x[1],reverse=True)
    b=[]
    # NOT: Bu bayrak string'lerini bozmamak için Türkçelerini koruduk, çünkü API bunları kontrol ediyor.
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
      "notes":["All numeric values were calculated in code; model should not calculate.",
               "Account names are pseudonymized, no plaintext usernames.",
               "This summary is not a diagnosis; it's merely a usage pattern."]}

profil=profil_kur(HAM_KAYITLAR,"synthetic_instagram_records")
sinyaller=sinyal_kur(profil)
os.makedirs("data", exist_ok=True)

for ad, veri in [
    ("profile.json", profil),
    ("signals.json", sinyaller)
]:
    dosya_yolu = os.path.join("data", ad)

    with open(dosya_yolu, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

    print("Written:", dosya_yolu)

def kontrol_et():
    hata,uyari=[],[]
    rumuz=re.compile(r"^acc_[0-9a-f]{8}$")
    p = json.load(open(os.path.join("data", "profile.json"), encoding="utf-8"))
    g = json.load(open(os.path.join("data", "signals.json"), encoding="utf-8"))
    for a in ["schema_version","user_id","posts","top_hashtags","top_accounts",
              "hourly_distribution","summary","data_notes"]:
        if a not in p: hata.append(f"profile.json: '{a}' missing")
    if len(p.get("hourly_distribution",{}))!=24: hata.append("profile.json: must be 24 hours")
    for h in p.get("top_accounts",[]):
        if not rumuz.match(str(h.get("account_hash",""))):
            hata.append(f"profile.json: unpseudonymized account {h.get('account_hash')}"); break
    for i,g2 in enumerate(p.get("posts",[])[:50]):
        if not g2.get("title") or not g2.get("caption"): hata.append(f"posts[{i}]: title/caption is empty")
        try: datetime.fromisoformat(g2["viewed_at"])
        except Exception: hata.append(f"posts[{i}]: viewed_at is not ISO 8601")
    if any(x.get("category") is None for x in p.get("top_accounts",[])):
        uyari.append("profile.json: category fields are empty (to be filled)")
    metin=json.dumps([p,g],ensure_ascii=False)
    if re.search(r"[\w\.-]+@[\w\.-]+\.\w+",metin): hata.append("PRIVACY: email found")
    if re.search(r"instagram\.com/[A-Za-z0-9_.]{3,}/",metin): hata.append("PRIVACY: plaintext profile link found")
    print("="*46)
    for m in uyari: print("  WARNING ",m)
    for m in hata: print("  ERROR  ",m)
    print("="*46)
    print(("FAILED - " if hata else "PASSED - ")+f"{len(hata)} errors, {len(uyari)} warnings")

print("\nPosts:",profil["summary"]["total_posts"],
      "| Accounts:",profil["summary"]["unique_accounts"],
      "| Night Ratio:",profil["summary"]["night_ratio"],
      "| Peak Hour:",profil["summary"]["peak_hour"])
print("Top hashtags:",", ".join(t["tag"] for t in profil["top_hashtags"][:5]))
print("Flags:",", ".join(sinyaller["flags"]))
print()
kontrol_et()