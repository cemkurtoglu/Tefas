from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

import cloudscraper

app = Flask(__name__)

@app.route('/fon')
def get_fon_fiyat():
    fon_kodu = request.args.get('kod', '').upper()
    if not fon_kodu:
        return "Kod girilmedi", 400
    
    url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fon_kodu}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
    
    try:
        session = cloudscraper.create_scraper()
        response = session.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"TEFAS Hatası: {response.status_code}", 500
        
        soup = BeautifulSoup(response.text, 'html.parser')
        panel = soup.find(id="MainContent_PanelInfo")
        
        if not panel:
            return f"Panel bulunamadı. Sayfa Başlığı: {soup.title.string if soup.title else 'Yok'} | HTML Özeti: {response.text[:300]}", 404
            
        # "Son Fiyat" metnini içeren etiketi bulup içindeki sayıya odaklanıyoruz
        text = panel.get_text()
        match = re.search(r"Son Fiyat[\s\S]*?([\d.,]+)", text)
        
        if match:
            fiyat_str = match.group(1).replace(".", "").replace(",", ".")
            return str(float(fiyat_str))
        return "Fiyat bulunamadı", 404
        
    except Exception as e:
        return f"Hata: {str(e)}", 500

if __name__ == "__main__":
    app.run()
