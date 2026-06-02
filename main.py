import os
import smtplib
import anthropic
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def get_news_brief():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now().strftime("%d %B %Y, %A")

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": f"""Bugün {today} tarihli güncel haberleri web'de ara.

Aşağıdaki kategorilerde haber bul:
- TÜRKİYE / İÇ SİYASET → EN AZ 5 haber
- TÜRKİYE / 3. SAYFA → EN AZ 8 haber
- DIŞ SİYASET GÜNDEMİ → EN AZ 5 haber (dünya liderleri temasları, ABD, Avrupa, Ortadoğu, Asya gelişmeleri, Türkiye'yi etkileyen dış gelişmeler)

Her haber için JSON formatında döndür:
{{
  "haberler": [
    {{
      "kategori": "Türkiye › İç Siyaset",
      "renk": "#C8102E",
      "baslik": "Haber başlığı",
      "kaynak": "Kaynak adı",
      "saat": "HH:MM",
      "ozet": "2 cümle özet. Lider haberleri için yakın tarihsel arka plan ekle. Örn: Erdoğan bugün X törenine katılacak. Erdoğan geçen hafta Y konusunda Z açıklamasını yapmıştı.",
      "vtr": ["VTR önerisi 1", "VTR önerisi 2", "VTR önerisi 3"],
      "uzmanlar": [
        {{"isim": "Ad Soyad", "unvan": "Unvan", "kurum": "Ankara merkezli kurum"}},
        {{"isim": "Ad Soyad", "unvan": "Unvan", "kurum": "Ankara merkezli kurum"}}
      ],
      "link": "https://kaynak-url.com"
    }}
  ]
}}

KATEGORİ ve RENK KURALLARI:
- "Türkiye › İç Siyaset" → renk: "#C8102E"
- "Türkiye › 3. Sayfa" → renk: "#7b2d00"
- "Dış Siyaset Gündemi" → renk: "#1E3A8A"

ÖNEMLİ KURALLAR:
- Tüm uzmanlar Ankara merkezli olsun (Ankara Üniversitesi, Hacettepe, ODTÜ, Bilkent, TBMM çevresi, Dışişleri Bakanlığı bağlantılı kurumlar, SETA, TEPAV, EDAM vb.)
- Türkiye İç Siyaset: lider açıklamaları ve ziyaretler için yakın tarihsel arka plan ekle
- Türkiye 3. Sayfa: VTR önerileri yaratıcı olsun, olayın arka planına odaklan (psikoloji, yasal boyut, sosyal bağlam)
- Dış Siyaset: dünya liderlerinin temaslarını, ziyaretleri ve Türkiye'yi etkileyen gelişmeleri dahil et
- SADECE geçerli JSON döndür, başka hiçbir şey yazma"""
            }
        ]
    )

    raw = ""
    for block in message.content:
        if hasattr(block, "text"):
            raw += block.text

    import json, re
    match = re.search(r'\{[\s\S]*\}', raw)
    if match:
        try:
            data = json.loads(match.group())
            haberler = data.get("haberler", [])
        except:
            haberler = []
    else:
        haberler = []

    kategoriler = {}
    kat_sira = ["Türkiye › İç Siyaset", "Türkiye › 3. Sayfa", "Dış Siyaset Gündemi"]
    for h in haberler:
        kat = h.get("kategori", "Diğer")
        if kat not in kategoriler:
            kategoriler[kat] = []
        kategoriler[kat].append(h)

    kat_ikon = {
        "Türkiye › İç Siyaset": "🇹🇷",
        "Türkiye › 3. Sayfa": "🇹🇷",
        "Dış Siyaset Gündemi": "🌍"
    }

    sections_html = ""
    for kat in kat_sira:
        if kat not in kategoriler:
            continue
        haberler_list = kategoriler[kat]
        ikon = kat_ikon.get(kat, "📰")
        sections_html += f'<div class="section-title">{ikon} {kat}</div>\n<div class="cards">\n'

        for h in haberler_list:
            baslik = h.get("baslik", "")
            kaynak = h.get("kaynak", "")
            saat = h.get("saat", "")
            ozet = h.get("ozet", "")
            vtr_list = h.get("vtr", [])
            uzmanlar = h.get("uzmanlar", [])
            link = h.get("link", "#")
            kart_renk = h.get("renk", "#1a3a5c")

            vtr_items = ""
            for v in vtr_list:
                vtr_items += f'<div class="vtr-item">{v}</div>\n'

            uzman_items = ""
            for u in uzmanlar:
                uzman_items += f'<div class="expert"><strong>{u.get("isim","")}</strong> — {u.get("unvan","")}, {u.get("kurum","")}</div>\n'

            sections_html += f"""
<div class="card" style="border-top-color:{kart_renk}">
  <span class="card-badge" style="background:{kart_renk}">{kat}</span>
  <div class="card-title">{baslik}</div>
  <div class="card-meta">{kaynak} · {saat}</div>
  <p style="font-size:13px;color:#333;line-height:1.6;margin:0 0 12px 0">{ozet}</p>
  <div class="vtr-block" style="border-left-color:{kart_renk}">
    <h4 style="color:{kart_renk}">▶ VTR Önerileri</h4>
    {vtr_items}
  </div>
  <div class="expert-block">
    <h4>Uzman Önerileri</h4>
    {uzman_items}
  </div>
  <a class="card-link" href="{link}" target="_blank">🔗 Haberin kaynağına git</a>
</div>
"""
        sections_html += "</div>\n"

    toplam = sum(len(v) for v in kategoriler.values())

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Günlük Haber Brifing — {today}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#FAF8F4; color:#222; margin:0; padding:0; }}
  .header {{ background:#1A1A1A; color:#fff; padding:28px 32px; }}
  .header h1 {{ margin:0; font-size:22px; letter-spacing:1px; }}
  .header p {{ margin:6px 0 0; color:#aac; font-size:13px; }}
  .section-title {{ background:#1A1A1A; color:#F4B400; padding:10px 32px;
                    font-size:13px; font-weight:700; letter-spacing:2px;
                    text-transform:uppercase; margin-top:28px; }}
  .cards {{ display:flex; flex-wrap:wrap; gap:18px; padding:16px 28px; }}
  .card {{ background:#fff; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,.10);
           width:calc(50% - 18px); min-width:300px; box-sizing:border-box;
           border-top:4px solid #1a3a5c; padding:18px 20px; }}
  .card-badge {{ display:inline-block; font-size:10px; font-weight:700;
                 padding:2px 8px; border-radius:12px; margin-bottom:10px;
                 color:#fff; letter-spacing:1px; }}
  .card-title {{ font-size:15px; font-weight:700; line-height:1.4; margin-bottom:6px; color:#111; }}
  .card-meta {{ font-size:11px; color:#888; margin-bottom:12px; }}
  .vtr-block {{ background:#f0fce0; border-left:3px solid #84CC16;
                padding:10px 14px; border-radius:0 6px 6px 0; margin-bottom:12px; }}
  .vtr-block h4 {{ margin:0 0 8px; font-size:11px; text-transform:uppercase; letter-spacing:1px; }}
  .vtr-item {{ font-size:13px; line-height:1.6; margin-bottom:6px;
               padding-left:12px; position:relative; color:#1A1A1A; }}
  .vtr-item::before {{ content:"▶"; position:absolute; left:0; color:#84CC16; font-size:10px; }}
  .expert-block {{ margin-top:10px; }}
  .expert-block h4 {{ margin:0 0 6px; font-size:11px; color:#555;
                      text-transform:uppercase; letter-spacing:1px; }}
  .expert {{ font-size:12px; line-height:1.6; margin-bottom:4px;
             padding-left:16px; position:relative; color:#1A1A1A; }}
  .expert::before {{ content:"👤"; position:absolute; left:0; font-size:10px; }}
  .expert strong {{ color:#1A1A1A; }}
  .card-link {{ display:block; margin-top:12px; font-size:11px; color:#3a7bd5;
                text-decoration:none; word-break:break-all; }}
  .footer {{ background:#1A1A1A; color:#aac; text-align:center;
             padding:18px; font-size:12px; margin-top:32px; }}
  @media(max-width:700px) {{ .card {{ width:100%; }} .cards {{ padding:12px; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>📺 Günlük Haber Brifing</h1>
  <p>{today} · Otomatik olarak oluşturuldu · {toplam} haber</p>
</div>
{sections_html}
<div class="footer">Gazeteci Asistanı · Claude AI ile oluşturuldu</div>
</body>
</html>"""

    return html

def send_email(content):
    sender = os.environ["GMAIL_SENDER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipients = os.environ["RECIPIENT_EMAIL"].split(",")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📺 Günlük Haber Brifing - {datetime.now().strftime('%d.%m.%Y')}"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    part = MIMEText(content, "html")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())

    print(f"Email gönderildi: {', '.join(recipients)}")

if __name__ == "__main__":
    print("Haberler derleniyor...")
    content = get_news_brief()
    print("Email gönderiliyor...")
    send_email(content)
    print("Tamamlandı!")
