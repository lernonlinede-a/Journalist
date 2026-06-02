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
                "content": f"""Bugün {today} tarihli güncel haberleri web'de ara ve aşağıdaki formatta Türkçe bir haber bülteni hazırla.

BÖLGELER ve KATEGORİLER:
1. TÜRKİYE
   - Siyaset
   - 3. Sayfa
2. ABD
   - Siyaset
   - 3. Sayfa
3. İNGİLTERE
   - Siyaset
   - 3. Sayfa
4. ORTADOĞU
   - Siyaset
   - 3. Sayfa
5. AVRUPA
   - Siyaset
   - 3. Sayfa

Her alt kategori için 3-4 güncel haber başlığı bul.

Her haber için şunları yaz:
- Haber başlığı ve 2-3 cümle özet
- VTR ÖNERİSİ: Televizyon muhabiri olarak bu haber için nasıl bir muhabir haberi yapılabilir? (somut öneri)
- UZMAN ÖNERİSİ: Bu haber için kimlerle görüşülebilir? (isim, unvan, kurum olarak somut isimler ver)

Siyaset haberleri için: dış politika uzmanları, akademisyenler, eski diplomatlar, düşünce kuruluşu temsilcileri öner.

3. Sayfa haberleri için: olayın arka planına odaklanan yaratıcı muhabir önerileri sun. Örneğin bir okul saldırısı haberi için "çocuklarda şiddet eğilimi", "silah erişimi yaşı", "okul güvenliği" gibi bağlantılı konularda VTR fikirleri üret.

ÇIKTI FORMATI: Güzel HTML formatında, her bölge farklı renkte kart olarak, muhabir önerileri sarı kutucukta, uzman isimleri mavi kutucukta göster."""
            }
        ]
    )

    result = ""
    for block in message.content:
        if hasattr(block, "text"):
            result += block.text

    # HTML wrap
    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; background: #f5f5f5; padding: 20px; }}
        h1 {{ background: #1a1a2e; color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        h2 {{ color: #1a1a2e; border-left: 5px solid #e94560; padding-left: 10px; margin-top: 30px; }}
        h3 {{ color: #444; margin-left: 15px; }}
        .haber {{ background: white; border-radius: 8px; padding: 15px; margin: 10px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .vtr {{ background: #fff9c4; border-left: 4px solid #f9a825; padding: 10px; margin-top: 10px; border-radius: 5px; }}
        .uzman {{ background: #e3f2fd; border-left: 4px solid #1976d2; padding: 10px; margin-top: 8px; border-radius: 5px; }}
        .vtr-label {{ font-weight: bold; color: #f57f17; }}
        .uzman-label {{ font-weight: bold; color: #1565c0; }}
        .kategori-siyaset {{ border-top: 3px solid #c62828; }}
        .kategori-3sayfa {{ border-top: 3px solid #6a1b9a; }}
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
