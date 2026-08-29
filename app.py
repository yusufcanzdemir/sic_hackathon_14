import streamlit as st, json, datetime
import plotly.graph_objects as go

AYLAR = ["", "Ocak", "Subat", "Mart", "Nisan", "Mayis", "Haziran", "Temmuz", "Agustos", "Eylul", "Ekim", "Kasim", "Aralik"]
BUGUN = datetime.date(2026, 8, 29)
NO_BAR = {'displayModeBar': False}

def rb(d, m): return "#FF4B4B" if d/m >= 0.7 else "#FACA2B" if d/m >= 0.4 else "#008751"

def bar_ciz(x, y):
    m_val = max(y) if y else 1
    fig = go.Figure(go.Bar(x=x, y=y, marker=dict(color=[rb(v, m_val) for v in y], line=dict(width=0)), text=y, textposition='outside', textfont=dict(color='#64748b')))
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=20, b=0), xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#64748b", size=10)), yaxis=dict(showgrid=False, zeroline=False, visible=False), height=250, showlegend=False)
    return fig

def donut_ciz(isimler, degerler):
    renkler = ["#008751", "#34C759", "#FACA2B", "#FF4B4B", "#64748b"]
    fig = go.Figure(go.Pie(labels=isimler, values=degerler, hole=0.65, marker=dict(colors=renkler), textinfo='label+percent', textposition='outside', hoverinfo='label+value'))
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=20, b=0), showlegend=False, height=250)
    return fig

# ==========================================
# 2. AI ENTEGRASYON NOKTALARI
# ==========================================
# from ai_engine import get_behavioral_analysis, get_21_day_plan

def ai_analiz_cagrisi(json_verisi):
    """
    Girdi: Yuklenen JSON verisinin tamami (dict).
    Beklenen Cikti: {"bulgu": "Analiz metni...", "eylem": "Eylem metni..."}
    """
    # GERCEK KOD BURAYA GELECEK:
    # return get_behavioral_analysis(json_verisi)
    
    return {
        "bulgu": "Backend baglantisi bekleniyor... (Kisi A ve C'nin yazacagi model ciktisi buraya yansiyacak)",
        "eylem": "Backend baglantisi bekleniyor..."
    }

def ai_takvim_cagrisi(json_verisi):
    """
    Girdi: Yuklenen JSON verisinin tamami (dict).
    Beklenen Cikti: 3 elemanli liste. Format:
    [{"faz": "Faz Adi", "gun": KacGunSurecek, "h": "Uzun Aciklama", "kh": "Kisa Hedef", "r": "Renk Kodu"}, ...]
    """
    # GERCEK KOD BURAYA GELECEK:
    # return get_21_day_plan(json_verisi)
    
    return [
        {"faz": "1. Faz (Backend Bekleniyor)", "gun": 3, "h": "-", "kh": "-", "r": "#FF4B4B"},
        {"faz": "2. Faz (Backend Bekleniyor)", "gun": 7, "h": "-", "kh": "-", "r": "#FACA2B"},
        {"faz": "3. Faz (Backend Bekleniyor)", "gun": 11, "h": "-", "kh": "-", "r": "#008751"}
    ]

st.set_page_config(page_title="Kaydirma Arkeolojisi", layout="wide", initial_sidebar_state="collapsed")
for k, v in {"veri": None, "pa": False, "takvim": []}.items(): st.session_state.setdefault(k, v)

st.markdown("<h2 style='text-align: center; color: #008751;'>Kaydirma Arkeolojisi</h2><p style='text-align: center; color: #64748b;'>Dijital tuketim aliskanliklarinizi kesfedin ve yonetin.</p>", unsafe_allow_html=True)
st.divider()

t1, t2, t3, t4 = st.tabs(["Veri Kaynagi", "Profilim", "Davranis Analizi", "Aliskanlik Kurma"])

with t1:
    st.write("Sosyal medya gecmisinizi (JSON) yukleyin.")
    yf = st.file_uploader("JSON Secin", type=["json"])
    
    if yf or st.button("Hazir Demo Profilini Kullan", use_container_width=True):
        st.session_state.veri = json.load(yf) if yf else {"schema_version": "1.0", "user_id": "anon_01", "generated_at": "2026-08-29T19:09:14Z", "meta_interests": ["Ahsap Isciligi", "Kendin Yap", "Doga"], "top_accounts": [{"account_hash": "A1", "view_count": 340, "category": "DIY/Hobi"}, {"account_hash": "B2", "view_count": 210, "category": "DIY/Hobi"}, {"account_hash": "C3", "view_count": 180, "category": "Eglence"}, {"account_hash": "D4", "view_count": 90, "category": "Haberler"}], "hourly_distribution": {"0": 80, "1": 40, "2": 20, "3": 0, "4": 0, "5": 0, "6": 5, "7": 15, "8": 30, "9": 45, "10": 20, "11": 25, "12": 60, "13": 50, "14": 40, "15": 30, "16": 35, "17": 50, "18": 75, "19": 90, "20": 110, "21": 130, "22": 150, "23": 120}, "summary": {"total_views": 1220, "peak_hour": "22:00"}}
        st.success("Veri islendi. Diger sekmelere gecebilirsiniz.")

with t2:
    if st.session_state.veri:
        d = st.session_state.veri
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("#### Genel Istatistikler")
                st.markdown(f"<div style='text-align: center; margin-top: 5px; font-weight: bold;'>Ozet Gorunum ({d.get('generated_at', '')[:10]})</div><hr style='margin:10px 0'>", unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("Toplam Icerik", f"{d['summary'].get('total_views', 0)} Kez", "-12% (Gecen Haftaya Gore)", "inverse")
                m2.metric("En Yogun Saat", d['summary'].get('peak_hour', 'Bilinmiyor'))
                
                saatler = [f"{i:02d}:00" for i in range(24)]
                degerler = [d.get("hourly_distribution", {}).get(str(i), 0) for i in range(24)]
                st.plotly_chart(bar_ciz(saatler, degerler), use_container_width=True, config=NO_BAR)
        with c2:
            with st.container(border=True):
                st.markdown("#### Kategori Analizi<br><span style='font-size:14px; color:#64748b;'>Vaktinizin dagilimi</span><hr style='margin:10px 0'>", unsafe_allow_html=True)
                kat_sozluk = {}
                for acc in d.get("top_accounts", []): kat_sozluk[acc.get("category", "Diger")] = kat_sozluk.get(acc.get("category", "Diger"), 0) + acc.get("view_count", 0)
                st.plotly_chart(donut_ciz(list(kat_sozluk.keys()), list(kat_sozluk.values())), use_container_width=True, config=NO_BAR)
    else: st.info("Veri yukleyin.")

with t3:
    if st.session_state.veri:
        if st.button("Analizi Baslat", type="primary", use_container_width=True):
            with st.spinner("AI Modeli calisiyor..."):
                s = ai_analiz_cagrisi(st.session_state.veri)
                
            st.markdown("<br>", unsafe_allow_html=True)
            for t, v in [("Bulgu", s.get('bulgu', '')), ("Tavsiye Edilen Eylem", s.get('eylem', ''))]:
                with st.container(border=True):
                    st.markdown(f"<h4 style='color: #008751;'>{t}</h4><p>{v}</p>", unsafe_allow_html=True)
    else: st.info("Veri yukleyin.")

with t4:
    if st.session_state.veri:
        if not st.session_state.pa and st.button("21 Gunluk Programimi Olustur", type="primary", use_container_width=True):
            with st.spinner("Takvim olusturuluyor..."):
                st.session_state.takvim = ai_takvim_cagrisi(st.session_state.veri)
                st.session_state.pa = True
                st.rerun()
            
        if st.session_state.pa:
            c1, c2, c3 = st.columns([2, 1, 2])
            c1.markdown("<h3 style='margin-bottom: 0;'>Takvim ve Ilerleme</h3>", unsafe_allow_html=True)
            kg = c3.slider("Zaman Simulasyonu", 1, 21, 1, label_visibility="collapsed")
            c3.markdown(f"<div style='text-align: right; color: #64748b; font-size: 13px; font-weight: bold;'>Ilerleme: %{int(kg/21*100)}</div>", unsafe_allow_html=True)
            c3.progress(kg / 21.0)
            st.divider()
            
            gs = 1
            for f in st.session_state.takvim:
                with st.container(border=True):
                    st.markdown(f"<h5 style='color: {f.get('r', '#000')}; margin: 0;'>{gs}. Gun - {gs+f.get('gun', 0)-1}. Gun: {f.get('faz', '')}</h5><p style='margin:0;'>{f.get('h', '')}</p>", unsafe_allow_html=True)
                gs += f.get('gun', 0)
                
            st.markdown("<br>", unsafe_allow_html=True)
            ggi = 0
            for _ in range(3):
                cols = st.columns(7)
                for i in range(7):
                    gn, gt = ggi + 1, BUGUN + datetime.timedelta(days=ggi)
                    f_idx = 0 if gn <= 3 else 1 if gn <= 10 else 2
                    takvim_faz = st.session_state.takvim[f_idx] if len(st.session_state.takvim) > f_idx else {"r": "#000", "kh": "-"}
                    
                    op, br = ("1.0", "3px solid #1E293B") if gn == kg else ("0.4", "none") if gn < kg else ("0.8", "none")
                    html = f"<div style='background:{takvim_faz.get('r', '#000')}; color:white; border-radius:8px; padding:8px 4px; text-align:center; margin-bottom:12px; opacity:{op}; border:{br};'><div style='font-size:11px;'>Gun {gn}</div><div style='font-size:13px; font-weight:bold; margin:4px 0;'>{gt.day} {AYLAR[gt.month]}</div><div style='font-size:10px; background:rgba(0,0,0,0.2); border-radius:4px; padding:3px; font-weight:bold;'>{takvim_faz.get('kh', '-')}</div></div>"
                    cols[i].markdown(html, unsafe_allow_html=True)
                    ggi += 1
    else: st.info("Veri yukleyin.")