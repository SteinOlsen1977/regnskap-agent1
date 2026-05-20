import streamlit as st 
import requests 
from bs4 import BeautifulSoup 
import feedparser 
 
# ---------- DATA FUNKSJONER ---------- 
 
def get_brreg(name): 
    url = f"https://data.brreg.no/enhetsregisteret/api/enheter?navn={name}" 
    res = requests.get(url) 
 
    if res.status_code != 200: 
        return None 
 
    data = res.json() 
 
    if "_embedded" not in data: 
        return None 
 
    return data["_embedded"]["enheter"][0] 
 
 
def scrape_website(url): 
    try: 
        res = requests.get(url, timeout=5) 
        soup = BeautifulSoup(res.text, "html.parser") 
 
        for script in soup(["script", "style"]): 
            script.extract() 
 
        text = soup.get_text(separator=" ") 
 
        return text[:2000] 
    except: 
        return None 
 
 
def get_news(company): 
    url = f"https://news.google.com/rss/search?q={company}" 
    feed = feedparser.parse(url) 
 
    articles = [] 
 
    for entry in feed.entries[:5]: 
        articles.append({ 
            "title": entry.title, 
            "link": entry.link 
        }) 
 
    return articles 
 
 
def simple_analysis(brreg, news, website_text): 
    score = 0 
 
    ansatte = brreg.get("antallAnsatte") 
 
    if ansatte: 
        if ansatte > 1000: 
            score += 3 
        elif ansatte > 50: 
            score += 2 
 
    if news: 
        score += 2 
 
    if website_text: 
        score += 1 
 
    if score >= 5: 
        return "Sterkt selskap 💪" 
    elif score >= 3: 
        return "Stabilt selskap 📊" 
    else: 
        return "Lite datagrunnlag ⚠️" 
 
 
# ---------- UI ---------- 
 
st.set_page_config(page_title="Regnskapsagent", layout="wide") 
 
st.title("📊 AI Regnskapsagent Dashboard") 
 
query = st.text_input("🔍 Søk selskap", "Equinor") 
 
if st.button("Analyser"): 
 
    with st.spinner("Henter data..."): 
        brreg = get_brreg(query) 
 
        if not brreg: 
            st.error("Fant ikke selskap") 
        else: 
            orgnr = brreg["organisasjonsnummer"] 
            website = brreg.get("hjemmeside") 
 
            website_text = scrape_website(website) if website else None 
            news = get_news(query) 
 
            analysis = simple_analysis(brreg, news, website_text) 
 
    if brreg: 
 
        col1, col2 = st.columns(2) 
 
        with col1: 
            st.subheader("🏢 Selskapsinfo") 
            st.write(f"**Navn:** {brreg['navn']}") 
            st.write(f"**Org.nr:** {orgnr}") 
            st.write(f"**Ansatte:** {brreg.get('antallAnsatte')}") 
            st.write(f"**Nettside:** {website}") 
 
            st.subheader("🧠 Analyse") 
            st.success(analysis) 
 
        with col2: 
            st.subheader("📰 Nyheter") 
 
            for n in news: 
                st.markdown(f"{n['link']}") 
 
        st.subheader("🌐 Nettside-innhold") 
 
        if website_text: 
            st.text(website_text[:1000]) 
        else: 
            st.write("Ingen nettsidedata funnet") 
 