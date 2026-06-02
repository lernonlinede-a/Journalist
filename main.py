import os
import smtplib
import anthropic
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def get_news_brief():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now().strftime("%d %B %Y")

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": f"""Bugün {today} tarihli güncel haberleri web'de ara ve aşağıdaki formatta Türkçe HTML haber bülteni hazırla.

KATEGORİLER VE HABER SAYILARI:
- TÜRKİYE / Siyaset → EN AZ 5 haber
- TÜRKİYE / 3. Sayfa → EN AZ 5 haber
- ABD / Siyaset → 3 haber
- ABD / 3. Sayfa → 3 haber
- İNGİLTERE / Siyaset → 3 haber
- İNGİLTERE / 3. Sayfa → 3 haber
- ORTADOĞU / Siyaset → 3 haber
- ORTADOĞU / 3. Sayfa → 3 haber
- AVRUPA / Siyaset → 3 haber
- AVRUPA / 3. Sayfa → 3 haber

Her haber için şu HTML yapısını kullan:

<div class="haber">
  <h3 class="haber-baslik">HABER BAŞLIĞI</h3>
  <p class="haber-ozet">Haberin 2-3 cümle özeti. Net ve okunaklı.</p>
  <div class="vtr">
    <span class="vtr-label">📹 VTR ÖNERİSİ:</span> Muhabir haberi önerisi buraya.
  </div>
  <div class="uzman">
    <span class="uzman-label">👤 UZMAN ÖNERİSİ:</span>
    <ul>
      <li>İsim Soyisim - Unvan - Kurum</li>
      <li>İsim Soyisim - Unvan - Kurum</li>
    </ul>
  </div>
</div>

Bölge başlıkları için şu class yapısını kullan:
- Türkiye: <h2 class="bolge turkiye">🇹🇷 TÜRKİYE</h2>
- ABD: <h2 class="bolge abd">🇺🇸 ABD</h2>
- İngiltere: <h2 class="bolge ingiltere">🇬🇧 İNGİLTERE</h2>
- Ortadoğu: <h2 class="bolge ortadogu">🌙 ORTADOĞU</h2>
- Avrupa: <h2 class="bolge avrupa">🇪🇺 AVRUPA</h2>

Alt kategori başlıkları:
- Siyaset: <h3 class="alt-kat siyaset">⚖️ SİYASET</h3>
- 3. Sayfa: <h3 class="alt-kat uc-sayfa">📋 3. SAYFA</h3>

Türkiye 3. Sayfa haberleri için VTR önerileri yaratıcı olsun — olayın arka planına odaklanan haberler öner.
Siyaset haberlerinde somut uzman isimleri ver.
SADECE HTML içeriği döndür."""
            }
        ]
    )

    result = ""
    for block in message.content:
        if hasattr(block, "text"):
            result += block.text

    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            max-width: 950px;
            margin: 0 auto;
            background: #FAF8F4;
            padding: 20px;
            color: #1A1A1A;
        }}
        h1 {{
            background: #1A1A1A;
            color: #FAF8F4;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            font-size: 26px;
            margin-bottom: 30px;
            letter-spacing: 1px;
        }}
        h2.bolge {{
            color: #FAF8F4;
            padding: 14px 20px;
            border-radius: 8px;
            font-size: 22px;
            margin-top: 40px;
            margin-bottom: 5px;
        }}
        .turkiye {{ background: #C8102E; }}
        .abd {{ background: #1E3A8A; }}
        .ingiltere {{ background: #012169; }}
        .ortadogu {{ background: #b38a00; color: #1A1A1A !important; }}
        .avrupa {{ background: #F87171; color: #1A1A1A !important; }}

        h3.alt-kat {{
            font-size: 15px;
            padding: 7px 15px;
            border-radius: 5px;
            margin: 12px 0 8px 0;
            color: #FAF8F4;
            display: inline-block;
        }}
        .siyaset {{ background: #6B7280; }}
        .uc-sayfa {{ background: #1A1A1A; }}

        .haber {{
            background: #ffffff;
            border-radius: 8px;
            padding: 20px 22px;
            margin: 10px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.10);
            border-left: 5px solid #1A1A1A;
        }}
        .haber-baslik {{
            color: #1A1A1A;
            font-size: 17px;
            font-weight: bold;
            margin: 0 0 10px 0;
            line-height: 1.4;
        }}
        .haber-ozet {{
            color: #1A1A1A;
            font-size: 15px;
            line-height: 1.75;
            margin: 0 0 14px 0;
        }}
        .vtr {{
            background: #f0fce0;
            border-left: 5px solid #84CC16;
            padding: 12px 15px;
            margin-top: 12px;
            border-radius: 5px;
            color: #1A1A1A;
            font-size: 14px;
            line-height: 1.6;
        }}
        .vtr-label {{
            font-weight: bold;
            color: #3d6b00;
            font-size: 15px;
        }}
        .uzman {{
            background: #f3f4f6;
            border-left: 5px solid #6B7280;
            padding: 12px 15px;
            margin-top: 10px;
            border-radius: 5px;
            color: #1A1A1A;
            font-size: 14px;
        }}
        .uzman-label {{
            font-weight: bold;
            color: #374151;
            font-size: 15px;
        }}
        .uzman ul {{
            margin: 8px 0 0 0;
            padding-left: 20px;
        }}
        .uzman ul li {{
            margin: 5px 0;
            color: #1A1A1A;
        }}
    </style>
    </head>
    <body>
    <h1>📰 Günlük Haber Bülteni — {today}</h1>
    {result}
    </body>
    </html>
    """
    return html

def send_email(content):
    sender = os.environ["GMAIL_SENDER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📰 Günlük Haber Bülteni - {datetime.now().strftime('%d.%m.%Y')}"
    msg["From"] = sender
    msg["To"] = recipient

    part = MIMEText(content, "html")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print("Email gönderildi!")

if __name__ == "__main__":
    print("Haberler derleniyor...")
    content = get_news_brief()
    print("Email gönderiliyor...")
    send_email(content)
    print("Tamamlandı!")
