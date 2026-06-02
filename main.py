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
                "content": f"""Bugün {today} tarihli güncel haberleri web'de ara ve Türkçe HTML haber bülteni hazırla.

ÖNEMLİ KISITLAMALAR:
- Her haber özeti MAX 2 cümle olsun (kısa ve öz)
- VTR önerisi MAX 1 cümle
- Uzman önerisi MAX 2 isim
- Tüm uzmanlar Ankara merkezli olsun (Ankara üniversiteleri, Ankara'daki düşünce kuruluşları, Ankara'daki eski bürokratlar)

KATEGORİLER:

1. TÜRKİYE / İÇ SİYASET → EN AZ 5 haber
- Lider haberleri için 1 cümle yakın tarihsel arka plan ekle
- Meclis, hükümet, muhalefet gelişmeleri

2. TÜRKİYE / 3. SAYFA → EN AZ 8 haber
- Suç, kaza, sosyal olaylar
- Yaratıcı VTR önerisi: olayın arka planına odaklan

3. DIŞ SİYASET GÜNDEMİ → EN AZ 5 haber
- Dünya liderleri temasları
- Türkiye'yi etkileyen dış gelişmeler

Her haber için HTML:
<div class="haber">
  <h3 class="haber-baslik">BAŞLIK</h3>
  <p class="haber-ozet">Max 2 cümle özet.</p>
  <div class="vtr"><span class="vtr-label">📹 VTR:</span> Max 1 cümle öneri.</div>
  <div class="uzman"><span class="uzman-label">👤 UZMAN:</span><ul><li>İsim - Unvan - Ankara'daki Kurum</li><li>İsim - Unvan - Ankara'daki Kurum</li></ul></div>
</div>

Bölge başlıkları:
<h2 class="bolge turkiye">🇹🇷 TÜRKİYE</h2>
<h2 class="bolge dis-siyaset">🌍 DIŞ SİYASET GÜNDEMİ</h2>

Alt kategoriler:
<h3 class="alt-kat ic-siyaset">⚖️ İÇ SİYASET HABERLERİ</h3>
<h3 class="alt-kat uc-sayfa">📋 3. SAYFA HABERLERİ</h3>

SADECE HTML içeriği döndür."""
            }
        ]
    )

    result = ""
    for block in message.content:
        if hasattr(block, "text"):
            result += block.text

    html = f"""<html>
<head><meta charset="UTF-8">
<style>
body{{font-family:Arial,sans-serif;max-width:900px;margin:0 auto;background:#FAF8F4;padding:15px;color:#1A1A1A;}}
h1{{background:#1A1A1A;color:#FAF8F4;padding:20px;border-radius:8px;text-align:center;font-size:22px;margin-bottom:25px;}}
h2.bolge{{color:#FAF8F4;padding:12px 18px;border-radius:6px;font-size:19px;margin-top:30px;margin-bottom:4px;}}
.turkiye{{background:#C8102E;}}.dis-siyaset{{background:#1E3A8A;}}
h3.alt-kat{{font-size:13px;padding:6px 12px;border-radius:4px;margin:12px 0 6px 0;color:#FAF8F4;display:inline-block;}}
.ic-siyaset{{background:#6B7280;}}.uc-sayfa{{background:#1A1A1A;}}
.haber{{background:#fff;border-radius:6px;padding:14px 18px;margin:8px 0;box-shadow:0 1px 5px rgba(0,0,0,0.08);border-left:4px solid #1A1A1A;}}
.haber-baslik{{color:#1A1A1A;font-size:15px;font-weight:bold;margin:0 0 8px 0;line-height:1.4;}}
.haber-ozet{{color:#1A1A1A;font-size:13px;line-height:1.65;margin:0 0 10px 0;}}
.vtr{{background:#f0fce0;border-left:4px solid #84CC16;padding:8px 12px;margin-top:8px;border-radius:4px;color:#1A1A1A;font-size:12px;}}
.vtr-label{{font-weight:bold;color:#3d6b00;}}
.uzman{{background:#f3f4f6;border-left:4px solid #6B7280;padding:8px 12px;margin-top:6px;border-radius:4px;font-size:12px;}}
.uzman-label{{font-weight:bold;color:#374151;}}
.uzman ul{{margin:5px 0 0 0;padding-left:16px;}}.uzman ul li{{margin:3px 0;color:#1A1A1A;}}
</style></head>
<body>
<h1>📰 Günlük Haber Bülteni — {today}</h1>
{result}
</body></html>"""
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
