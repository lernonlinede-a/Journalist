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

ANA KATEGORİLER:

1. TÜRKİYE
   a) İÇ SİYASET HABERLERİ → EN AZ 5 haber
      - Cumhurbaşkanı, Cumhurbaşkanı Yardımcısı, Bakanlar, CHP, MHP, İYİ Parti, HDP/DEM Parti açıklamaları ve ziyaretleri
      - Eğer bir lider bugün bir ziyaret veya etkinliğe katılacaksa, o ziyaretin YAKIN TARİHSEL ARKA PLANINI yaz. Örn: "Erdoğan bugün Sayıştay'ın 164. Kuruluş Yıl Dönümü Töreni'ne katılacak. Erdoğan geçen hafta yaptığı kabine toplantısı sonrası CHP'deki tartışmalara 'Ana muhalefet içindeki tartışmalar bizi ilgilendirmiyor' demişti."
      - Meclis gündemi, ekonomi kararları, iç gelişmeler

   b) 3. SAYFA HABERLERİ → EN AZ 8 haber
      - Suç, kaza, yangın, cinayet, sosyal olaylar
      - Her haber için yaratıcı VTR önerisi: olayın arka planına odaklan
      - Örn: okul saldırısı → "çocuklarda şiddet psikolojisi", "poligonda silah kullanma yaşı sınırı" gibi bağlantılı haberler öner

2. DIŞ SİYASET GÜNDEMİ → EN AZ 5 haber
   - Dünya liderlerinin temasları, ziyaretler, açıklamalar
   - ABD, Avrupa, Ortadoğu, Asya gelişmeleri
   - Türkiye'nin dış politikasını etkileyen gelişmeler
   - Her haber için uzman ve VTR önerisi

Her haber için şu HTML yapısını kullan:

<div class="haber">
  <h3 class="haber-baslik">HABER BAŞLIĞI</h3>
  <p class="haber-ozet">Haberin 2-3 cümle özeti. Lider haberleri için yakın tarihsel arka plan da ekle.</p>
  <div class="vtr">
    <span class="vtr-label">📹 VTR ÖNERİSİ:</span> Somut ve yaratıcı muhabir haberi önerisi.
  </div>
  <div class="uzman">
    <span class="uzman-label">👤 UZMAN ÖNERİSİ:</span>
    <ul>
      <li>İsim Soyisim - Unvan - Kurum</li>
      <li>İsim Soyisim - Unvan - Kurum</li>
    </ul>
  </div>
</div>

Ana kategori başlıkları:
<h2 class="bolge turkiye">🇹🇷 TÜRKİYE</h2>
<h2 class="bolge dis-siyaset">🌍 DIŞ SİYASET GÜNDEMİ</h2>

Alt kategori başlıkları:
<h3 class="alt-kat ic-siyaset">⚖️ İÇ SİYASET HABERLERİ</h3>
<h3 class="alt-kat uc-sayfa">📋 3. SAYFA HABERLERİ</h3>

SADECE HTML içeriği döndür, başka açıklama yazma."""
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
        .dis-siyaset {{ background: #1E3A8A; }}

        h3.alt-kat {{
            font-size: 15px;
            padding: 7px 15px;
            border-radius: 5px;
            margin: 15px 0 8px 0;
            color: #FAF8F4;
            display: inline-block;
        }}
        .ic-siyaset {{ background: #6B7280; }}
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
        .arka-plan {{
            background: #fef3c7;
            border-left: 4px solid #F4B400;
            padding: 10px 14px;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 14px;
            color: #1A1A1A;
            line-height: 1.6;
        }}
        .arka-plan-label {{
            font-weight: bold;
            color: #b38a00;
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
    recipients = os.environ["RECIPIENT_EMAIL"].split(",")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📰 Günlük Haber Bülteni - {datetime.now().strftime('%d.%m.%Y')}"
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
