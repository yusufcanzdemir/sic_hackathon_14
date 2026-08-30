import streamlit as st
import json
import datetime
import plotly.graph_objects as go
import time
import requests
import os
from streamlit_lottie import st_lottie

from ai.api import ai_analiz_sohbeti_baslat, ai_analizi_revize_et, ai_takvim_cagrisi

AYLAR = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
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

st.set_page_config(page_title="Find your offline joy instead.", layout="wide", initial_sidebar_state="collapsed")

css_yolu = os.path.join(".streamlit", "style.css")
if os.path.exists(css_yolu):
    with open(css_yolu) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "adim" not in st.session_state:
    st.session_state.adim = 0
    
varsayilan_stateler = {
    "veri": None, "takvim": [], "analiz": None, 
    "analiz_yazildi": False, "takvim_yazildi": False, 
    "tercihler": {}, "chat_history": []
}

for k, v in varsayilan_stateler.items(): 
    st.session_state.setdefault(k, v)

st.markdown("<h2 style='text-align: center; color: #008751; margin-bottom: 0;'>Find your offline joy instead.</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size:18px; margin-top: 5px;'>Discover and manage your digital consumption habits.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("### Step 1: Data Source")
st.write("Shed light on your hidden habits by uploading your social media history (JSON).")

col1, col2 = st.columns([1, 1])
with col1:
    yf = st.file_uploader("Select JSON (profile.json)", type=["json"], label_visibility="collapsed")

if yf:
    st.session_state.veri = json.load(yf)
    if st.session_state.adim < 1:
        st.session_state.adim = 1
        st.rerun()

if st.session_state.adim >= 1:
    st.divider()
    st.markdown("### Face Your Profile")
    
    d = st.session_state.veri
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div style='color:#64748b; font-size:14px; margin-bottom:10px;'>Summary View</div>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Total Content", f"{d.get('summary', {}).get('total_posts', 0)} Times", "-12% (Compared to Last Week)", "inverse")
        m2.metric("Peak Hour", f"{d.get('summary', {}).get('peak_hour', 'Unknown')}:00")
        
        saatler = [f"{i:02d}:00" for i in range(24)]
        degerler = [d.get("hourly_distribution", {}).get(str(i), 0) for i in range(24)]
        st.plotly_chart(bar_ciz(saatler, degerler), use_container_width=True, config=NO_BAR)
    with c2:
        st.markdown("<div style='color:#64748b; font-size:14px; margin-bottom:10px;'>Category Analysis - Time distribution</div>", unsafe_allow_html=True)
        kat_sozluk = {}
        for h in d.get("top_hashtags", [])[:5]: 
            kat_sozluk[h["tag"]] = h["count"]
        st.plotly_chart(donut_ciz(list(kat_sozluk.keys()), list(kat_sozluk.values())), use_container_width=True, config=NO_BAR)
    
    if st.session_state.adim == 1:
        st.markdown("<br><hr>", unsafe_allow_html=True)
        st.markdown("### 🎯 Your Activity Preferences")
        st.write("Set the filters so the AI can give you a pinpoint recommendation:")
        
        pref_c1, pref_c2, pref_c3 = st.columns(3)
        with pref_c1:
            sos_ortam = st.selectbox("Social Environment", ["Solo (By myself)", "With Family", "With Friends"])
        with pref_c2:
            butce_tipi = st.radio("Budget Status", ["Completely Free", "Paid / Set a Budget"])
        with pref_c3:
            butce_mik = 0
            if butce_tipi == "Paid / Set a Budget":
                butce_mik = st.number_input("Maximum Budget (TRY)", min_value=0, value=500, step=50)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Analyze with These Preferences", type="primary", use_container_width=True):
            st.session_state.tercihler = {
                "sosyal_ortam": sos_ortam, 
                "butce_tipi": butce_tipi, 
                "butce_miktari": butce_mik
            }
            st.session_state.adim = 2
            st.rerun()

if st.session_state.adim >= 2:
    st.divider()
    st.markdown("### AI Behavior Analysis")
    
    if st.session_state.analiz is None:
        lottie_alani = st.empty()
        with lottie_alani:
            ai_animasyon = lottie_yukle("https://lottie.host/809f69f2-2b6d-4ec3-ba92-b6ab74be3fcf/U432bH0l3k.json")
            if ai_animasyon: st_lottie(ai_animasyon, height=200, key="ai_loading")
            else: st.info("Gemini AI is analyzing your data...")
            
            sonuc, gecmis = ai_analiz_sohbeti_baslat(st.session_state.veri, st.session_state.tercihler)
            st.session_state.analiz = sonuc
            st.session_state.chat_history = gecmis
        lottie_alani.empty()

    s = st.session_state.analiz
    
    if not st.session_state.analiz_yazildi:
        st.markdown("**Core Finding:**")
        st.write_stream(daktilo_efekti(s.get('bulgu', '')))
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Recommended Action:**")
        st.write_stream(daktilo_efekti(s.get('eylem', '')))
        st.session_state.analiz_yazildi = True
    else:
        st.info(f"**Core Finding:**\n\n{s.get('bulgu', '')}")
        st.success(f"**Recommended Action:**\n\n{s.get('eylem', '')}")
    
    st.markdown("#### How did you find the recommendation?")
    sentiment_mapping = ["Terrible (1 Star)", "Bad (2 Stars)", "Okay (3 Stars)", "Good (4 Stars)", "Excellent! (5 Stars)"]
    selected = st.feedback("stars", key="star_feedback")
    
    if selected is not None:
        st.markdown(f"**Your Rating:** {sentiment_mapping[selected]}")
        
        if selected < 3:
            st.warning("It looks like you didn't quite embrace this action. The AI can find you a new action without forgetting what was said before.")
            revize_talebi = st.text_input("What kind of thing would you like? (e.g., I don't want to go out, suggest an indoor activity)")
            
            if st.button("Request New Recommendation Using Memory"):
                with st.spinner("Recalling past conversation, preparing new recommendation..."):
                    yeni_sonuc, yeni_gecmis = ai_analizi_revize_et(st.session_state.chat_history, revize_talebi)
                    
                    st.session_state.analiz = yeni_sonuc
                    st.session_state.chat_history = yeni_gecmis
                    
                    del st.session_state["star_feedback"]
                    st.session_state.analiz_yazildi = False 
                    st.rerun()

    if st.session_state.adim == 2 and st.session_state.analiz is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("I Chose This Action, Create My 21-Day Program", type="primary", use_container_width=True):
            st.session_state.adim = 3
            st.rerun()

if st.session_state.adim >= 3:
    st.divider()
    st.markdown("### 21-Day Roadmap")
    
    if not st.session_state.takvim:
        takvim_lottie_alani = st.empty()
        with takvim_lottie_alani:
            takvim_anim = lottie_yukle("https://lottie.host/e2d4d872-eb1e-4581-807d-07eaaf915c25/O4rO1s1yHw.json")
            if takvim_anim: st_lottie(takvim_anim, height=200, key="takvim_loading")
            else: st.info("Preparing your personalized program...")
            
            st.session_state.takvim = ai_takvim_cagrisi(st.session_state.veri, st.session_state.analiz)
        takvim_lottie_alani.empty()
    
    c1, c2, c3 = st.columns([2, 1, 2])
    kg = c3.slider("Time Simulation", 1, 21, 1, label_visibility="collapsed")
    c3.markdown(f"<div style='text-align: right; color: #64748b; font-size: 13px; font-weight: bold;'>Progress: %{int(kg/21*100)}</div>", unsafe_allow_html=True)
    c3.progress(kg / 21.0)
    
    gs = 1
    if not st.session_state.takvim_yazildi:
        for f in st.session_state.takvim:
            st.markdown(f"<h5 style='color: {f.get('r', '#000')}; margin-top: 15px;'>Day {gs} - Day {gs+f.get('gun', 0)-1}: {f.get('faz', '')}</h5>", unsafe_allow_html=True)
            st.write_stream(daktilo_efekti(f"*{f.get('h', '')}*", hiz=0.005))
            gs += f.get('gun', 0)
        st.session_state.takvim_yazildi = True
    else:
        for f in st.session_state.takvim:
            st.markdown(f"<h5 style='color: {f.get('r', '#000')}; margin-top: 15px;'>Day {gs} - Day {gs+f.get('gun', 0)-1}: {f.get('faz', '')}</h5>*{f.get('h', '')}*", unsafe_allow_html=True)
            gs += f.get('gun', 0)
    
    st.markdown("<br>", unsafe_allow_html=True)

    faz_bitisleri = []
    kumulatif = 0
    for f in st.session_state.takvim:
        kumulatif += f.get("gun", 0)
        faz_bitisleri.append(kumulatif)

    def gun_to_faz_idx(gn):
        for idx, bitis in enumerate(faz_bitisleri):
            if gn <= bitis:
                return idx
        return max(0, len(faz_bitisleri) - 1)

    ggi = 0
    for _ in range(3):
        cols = st.columns(7)
        for i in range(7):
            gn, gt = ggi + 1, BUGUN + datetime.timedelta(days=ggi)
            f_idx = gun_to_faz_idx(gn)
            takvim_faz = st.session_state.takvim[f_idx] if len(st.session_state.takvim) > f_idx else {"r": "#000", "kh": "-"}
            op, br = ("1.0", f"3px solid {takvim_faz.get('r', '#000')}") if gn == kg else ("0.3", "none") if gn < kg else ("0.8", "none")
            html = f"""
            <div style='background:{takvim_faz.get('r', '#000')}; color:white; border-radius:12px; padding:10px 4px; text-align:center; margin-bottom:12px; opacity:{op}; border:{br}; box-shadow: 0 4px 10px rgba(0,0,0,0.15); transition: all 0.3s ease;'>
                <div style='font-size:11px; opacity: 0.9;'>Day {gn}</div>
                <div style='font-size:14px; font-weight:bold; margin:6px 0;'>{gt.day} {AYLAR[gt.month]}</div>
                <div style='font-size:11px; background:rgba(0,0,0,0.25); border-radius:6px; padding:4px; font-weight:bold;'>{takvim_faz.get('kh', '-')}</div>
            </div>
            """
            cols[i].markdown(html, unsafe_allow_html=True)
            ggi += 1