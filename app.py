import streamlit as st, json, datetime
import plotly.graph_objects as go
import time
import requests
import os
from streamlit_lottie import st_lottie

# ==========================================
# 0. YARDIMCI FONKSİYONLAR VE SABİTLER
# ==========================================
AYLAR = ["", "Ocak", "Subat", "Mart", "Nisan", "Mayis", "Haziran", "Temmuz", "Agustos", "Eylul", "Ekim", "Kasim", "Aralik"]
BUGUN = datetime.date(2026, 8, 29)
NO_BAR = {'displayModeBar': False}

def rb(d, m): 
    return "#FF4B4B" if d/m >= 0.7 else "#FACA2B" if d/m >= 0.4 else "#008751"

def bar_ciz(x, y):
    m_val = max(y) if y else 1
    fig = go.Figure(go.Bar(
        x=x, y=y, 
        marker=dict(color=[rb(v, m_val) for v in y], line=dict(width=0)), 
        text=y, textposition='outside', 
        textfont=dict(color='#64748b')
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
        margin=dict(l=0, r=0, t=20, b=0), 
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#64748b", size=10)), 
        yaxis=dict(showgrid=False, zeroline=False, visible=False), 
        height=250, showlegend=False
    )
    return fig

def donut_ciz(isimler, degerler):
    renkler = ["#008751", "#34C759", "#FACA2B", "#FF4B4B", "#64748b"]
    fig = go.Figure(go.Pie(
        labels=isimler, values=degerler, hole=0.65, 
        marker=dict(colors=renkler), 
        textinfo='label+percent', textposition='outside', hoverinfo='label+value'
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
        margin=dict(l=0, r=0, t=20, b=0), showlegend=False, height=250
    )
    return fig

def lottie_yukle(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def daktilo_efekti(metin, hiz=0.015):
    for harf in metin:
        yield harf
        time.sleep(hiz)

# --- YAPAY ZEKA BACKEND SİMÜLASYONLARI ---
def ai_analiz_cagrisi(json_verisi):
    return {
        "bulgu": "Gece 22:00 sularında içerik tüketiminde ani bir zirve var. Bu saatlerde 'DIY/Hobi' içerikleriyle başlayıp pasif kaydırma döngüsüne giriyorsun.",
        "eylem": "Yatmadan 1 saat önce telefonu farklı bir odaya bırakarak 'Dijital Gün Batımı' rutinine başla."
    }

def ai_takvim_cagrisi(json_verisi):
    return [
        {"faz": "1. Faz (Farkındalık)", "gun": 3, "h": "Tüketim tetikleyicilerini gözlemle.", "kh": "Fark Et", "r": "#FF4B4B"},
        {"faz": "2. Faz (Sınırlandırma)", "gun": 7, "h": "Belirli saatlerde uygulama limitleri koy.", "kh": "Limit Koy", "r": "#FACA2B"},
        {"faz": "3. Faz (Yeni Alışkanlık)", "gun": 11, "h": "Fiziksel hobilerle boşlukları doldur.", "kh": "Dönüşüm", "r": "#008751"}
    ]

# ==========================================
# 1. SAYFA AYARLARI VE CSS
# ==========================================
st.set_page_config(page_title="Kaydırma Arkeolojisi", layout="wide", initial_sidebar_state="collapsed")

css_yolu = os.path.join(".streamlit", "style.css")
if os.path.exists(css_yolu):
    with open(css_yolu) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ==========================================
# 2. DURUM YÖNETİMİ (SESSION STATE)
# ==========================================
if "adim" not in st.session_state:
    st.session_state.adim = 0
for k, v in {"veri": None, "takvim": [], "analiz": None, "analiz_yazildi": False, "takvim_yazildi": False}.items(): 
    st.session_state.setdefault(k, v)

# Üst Başlık
st.markdown("<h2 style='text-align: center; color: #008751; margin-bottom: 0;'>Kaydırma Arkeolojisi</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size:18px; margin-top: 5px;'>Dijital tüketim alışkanlıklarınızı keşfedin ve yönetin.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# ADIM 0: VERİ YÜKLEME
# ==========================================
st.markdown("### Adım 1: Veri Kaynağı")
st.write("Sosyal medya geçmişinizi (JSON) yükleyerek karanlıkta kalan alışkanlıklarınızı gün yüzüne çıkarın.")

col1, col2 = st.columns([1, 1])
with col1:
    yf = st.file_uploader("JSON Seçin", type=["json"], label_visibility="collapsed")
with col2:
    st.write("Veya test etmek için:")
    demo_btn = st.button("Hazır Demo Profilini Kullan", use_container_width=True)

if yf or demo_btn:
    if demo_btn:
        st.session_state.veri = {
            "schema_version": "1.0", "user_id": "anon_01", "generated_at": "2026-08-29T19:09:14Z", 
            "meta_interests": ["Ahşap İşçiliği", "Kendin Yap", "Doğa"], 
            "top_accounts": [
                {"account_hash": "A1", "view_count": 340, "category": "DIY/Hobi"}, 
                {"account_hash": "B2", "view_count": 210, "category": "DIY/Hobi"}, 
                {"account_hash": "C3", "view_count": 180, "category": "Eğlence"}, 
                {"account_hash": "D4", "view_count": 90, "category": "Haberler"}
            ], 
            "hourly_distribution": {"0": 80, "1": 40, "2": 20, "3": 0, "4": 0, "5": 0, "6": 5, "7": 15, "8": 30, "9": 45, "10": 20, "11": 25, "12": 60, "13": 50, "14": 40, "15": 30, "16": 35, "17": 50, "18": 75, "19": 90, "20": 110, "21": 130, "22": 150, "23": 120}, 
            "summary": {"total_views": 1220, "peak_hour": "22:00"}
        }
    else:
        st.session_state.veri = json.load(yf)
    
    if st.session_state.adim < 1:
        st.session_state.adim = 1
        st.rerun()

# ==========================================
# ADIM 1: PROFİL GÖRÜNÜMÜ
# ==========================================
if st.session_state.adim >= 1:
    st.divider()
    st.markdown("### Profilinle Yüzleş")
    
    d = st.session_state.veri
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div style='color:#64748b; font-size:14px; margin-bottom:10px;'>Özet Görünüm ({d.get('generated_at', '')[:10]})</div>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Toplam İçerik", f"{d['summary'].get('total_views', 0)} Kez", "-12% (Gecen Haftaya Gore)", "inverse")
        m2.metric("En Yoğun Saat", d['summary'].get('peak_hour', 'Bilinmiyor'))
        
        saatler = [f"{i:02d}:00" for i in range(24)]
        degerler = [d.get("hourly_distribution", {}).get(str(i), 0) for i in range(24)]
        st.plotly_chart(bar_ciz(saatler, degerler), use_container_width=True, config=NO_BAR)
    with c2:
        st.markdown("<div style='color:#64748b; font-size:14px; margin-bottom:10px;'>Kategori Analizi - Vaktinin dağılımı</div>", unsafe_allow_html=True)
        kat_sozluk = {}
        for acc in d.get("top_accounts", []): 
            kat_sozluk[acc.get("category", "Diger")] = kat_sozluk.get(acc.get("category", "Diger"), 0) + acc.get("view_count", 0)
        st.plotly_chart(donut_ciz(list(kat_sozluk.keys()), list(kat_sozluk.values())), use_container_width=True, config=NO_BAR)
    
    if st.session_state.adim == 1:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Bu Veriler Ne Anlama Geliyor? Analiz Et", type="primary", use_container_width=True):
            st.session_state.adim = 2
            st.rerun()

# ==========================================
# ADIM 2: DAVRANIŞ ANALİZİ (AI)
# ==========================================
if st.session_state.adim >= 2:
    st.divider()
    st.markdown("### Yapay Zeka Davranış Analizi")
    
    if st.session_state.analiz is None:
        lottie_alani = st.empty()
        with lottie_alani:
            ai_animasyon = lottie_yukle("https://lottie.host/809f69f2-2b6d-4ec3-ba92-b6ab74be3fcf/U432bH0l3k.json")
            if ai_animasyon:
                st_lottie(ai_animasyon, height=200, key="ai_loading")
            else:
                st.info("Yapay zeka verilerinizi inceliyor...")
            
            st.session_state.analiz = ai_analiz_cagrisi(st.session_state.veri)
            time.sleep(1.8)
        lottie_alani.empty()

    s = st.session_state.analiz
    
    if not st.session_state.analiz_yazildi:
        st.markdown("**Temel Bulgu:**")
        st.write_stream(daktilo_efekti(s.get('bulgu', '')))
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Tavsiye Edilen Eylem:**")
        st.write_stream(daktilo_efekti(s.get('eylem', '')))
        st.session_state.analiz_yazildi = True
    else:
        st.info(f"**Temel Bulgu:**\n\n{s.get('bulgu', '')}")
        st.success(f"**Tavsiye Edilen Eylem:**\n\n{s.get('eylem', '')}")
    
    if st.session_state.adim == 2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Değişim İçin 21 Günlük Programımı Oluştur", type="primary", use_container_width=True):
            st.session_state.adim = 3
            st.rerun()

# ==========================================
# ADIM 3: 21 GÜNLÜK TAKVİM
# ==========================================
if st.session_state.adim >= 3:
    st.divider()
    st.markdown("### 21 Günlük Yol Haritası")
    
    if not st.session_state.takvim:
        takvim_lottie_alani = st.empty()
        with takvim_lottie_alani:
            takvim_anim = lottie_yukle("https://lottie.host/e2d4d872-eb1e-4581-807d-07eaaf915c25/O4rO1s1yHw.json")
            if takvim_anim:
                st_lottie(takvim_anim, height=200, key="takvim_loading")
            else:
                st.info("Size özel program hazırlanıyor...")
            
            st.session_state.takvim = ai_takvim_cagrisi(st.session_state.veri)
            time.sleep(1.5)
        takvim_lottie_alani.empty()
    
    c1, c2, c3 = st.columns([2, 1, 2])
    kg = c3.slider("Zaman Simülasyonu", 1, 21, 1, label_visibility="collapsed")
    c3.markdown(f"<div style='text-align: right; color: #64748b; font-size: 13px; font-weight: bold;'>İlerleme: %{int(kg/21*100)}</div>", unsafe_allow_html=True)
    c3.progress(kg / 21.0)
    
    # Faz Başlıkları ve Daktilo Efekti
    gs = 1
    if not st.session_state.takvim_yazildi:
        for f in st.session_state.takvim:
            # HTML olan başlık kısmını tek seferde ekrana bas
            st.markdown(f"<h5 style='color: {f.get('r', '#000')}; margin-top: 15px;'>{gs}. Gün - {gs+f.get('gun', 0)-1}. Gün: {f.get('faz', '')}</h5>", unsafe_allow_html=True)
            # Sadece açıklamayı harf harf daktilo efektiyle yazdır
            st.write_stream(daktilo_efekti(f"*{f.get('h', '')}*", hiz=0.005))
            gs += f.get('gun', 0)
        st.session_state.takvim_yazildi = True
    else:
        for f in st.session_state.takvim:
            # Sayfa slider ile yenilendiğinde her şeyi statik olarak bas
            st.markdown(f"<h5 style='color: {f.get('r', '#000')}; margin-top: 15px;'>{gs}. Gün - {gs+f.get('gun', 0)-1}. Gün: {f.get('faz', '')}</h5>*{f.get('h', '')}*", unsafe_allow_html=True)
            gs += f.get('gun', 0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    ggi = 0
    for _ in range(3):
        cols = st.columns(7)
        for i in range(7):
            gn, gt = ggi + 1, BUGUN + datetime.timedelta(days=ggi)
            f_idx = 0 if gn <= 3 else 1 if gn <= 10 else 2
            takvim_faz = st.session_state.takvim[f_idx] if len(st.session_state.takvim) > f_idx else {"r": "#000", "kh": "-"}
            
            op, br = ("1.0", f"3px solid {takvim_faz.get('r', '#000')}") if gn == kg else ("0.3", "none") if gn < kg else ("0.8", "none")
            
            html = f"""
            <div style='background:{takvim_faz.get('r', '#000')}; color:white; border-radius:12px; padding:10px 4px; text-align:center; margin-bottom:12px; opacity:{op}; border:{br}; box-shadow: 0 4px 10px rgba(0,0,0,0.15); transition: all 0.3s ease;'>
                <div style='font-size:11px; opacity: 0.9;'>Gün {gn}</div>
                <div style='font-size:14px; font-weight:bold; margin:6px 0;'>{gt.day} {AYLAR[gt.month]}</div>
                <div style='font-size:11px; background:rgba(0,0,0,0.25); border-radius:6px; padding:4px; font-weight:bold;'>{takvim_faz.get('kh', '-')}</div>
            </div>
            """
            cols[i].markdown(html, unsafe_allow_html=True)
            ggi += 1