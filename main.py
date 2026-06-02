import os
import smtplib
import anthropic
import json
import re
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
                "content": f"""Bugün {today} tarihli güncel haberleri web'de ara ve aşağıdaki HTML bölümlerini doldur.

KATEGORİLER:
1. Türkiye İç Siyaset → EN AZ 5 haber (lider haberleri için yakın tarihsel arka plan ekle)
2. Türkiye 3. Sayfa → EN AZ 8 haber (yaratıcı VTR önerileri: olayın arka planına odaklan)
3. Dış Siyaset Gündemi → EN AZ 5 haber (dünya liderleri temasları, Türkiye'yi etkileyen gelişmeler)

Türkiye İç Siyaset kartları (border #C8102E):
<div class="card" style="border-top-color:#C8102E">
  <span class="card-badge" style="background:#C8102E">Türkiye › İç Siyaset</span>
  <div class="card-title">GERÇEK HABER BAŞLIĞI</div>
  <div class="card-meta">KAYNAK · SAAT</div>
  <p class="ozet">2 cümle özet. Lider haberleri için yakın tarihsel arka plan ekle.</p>
  <div class="vtr-block" style="border-left-color:#84CC16">
    <h4 style="color:#3d6b00">▶ VTR Önerileri</h4>
    <div class="vtr-item">VTR önerisi 1</div>
    <div class="vtr-item">VTR önerisi 2</div>
    <div class="vtr-item">VTR önerisi 3</div>
  </div>
  <div class="expert-block">
    <h4>Uzman Önerileri (Ankara merkezli)</h4>
    <div class="expert"><strong>İsim Soyisim</strong> — Unvan, Kurum</div>
    <div class="expert"><strong>İsim Soyisim</strong> — Unvan, Kurum</div>
  </div>
</div>

Türkiye 3. Sayfa kartları (border #7b2d00):
<div class="card" style="border-top-color:#7b2d00">
  <span class="card-badge" style="background:#7b2d00">Türkiye › 3. Sayfa</span>
  ...aynı yapı...
</div>

Dış Siyaset kartları (border #1E3A8A):
<div class="card" style="border-top-color:#1E3A8A">
  <span class="card-badge" style="background:#1E3A8A">Dış Siyaset Gündemi</span>
  ...aynı yapı...
</div>

ÇIKTI:
<section data-kat="ic-siyaset">[kartlar]</section>
<section data-kat="uc-sayfa">[kartlar]</section>
<section data-kat="dis-siyaset">[kartlar]</section>

Uzmanlar Ankara merkezli olsun. SADECE HTML döndür."""
            }
        ]
    )

    raw = ""
    for block in message.content:
        if hasattr(block, "text"):
            raw += block.text

    ic_siyaset = ""
    uc_sayfa = ""
    dis_siyaset = ""

    m = re.search(r'<section data-kat="ic-siyaset">([\s\S]*?)</section>', raw)
    if m: ic_siyaset = m.group(1)
    m = re.search(r'<section data-kat="uc-sayfa">([\s\S]*?)</section>', raw)
    if m: uc_sayfa = m.group(1)
    m = re.search(r'<section data-kat="dis-siyaset">([\s\S]*?)</section>', raw)
    if m: dis_siyaset = m.group(1)

    if not ic_siyaset and not uc_sayfa and not dis_siyaset:
        content_html = raw
    else:
        content_html = f"""
<div class="section-title">🇹🇷 Türkiye › İç Siyaset</div>
<div class="cards">{ic_siyaset}</div>
<div class="section-title">🇹🇷 Türkiye › 3. Sayfa</div>
<div class="cards">{uc_sayfa}</div>
<div class="section-title">🌍 Dış Siyaset Gündemi</div>
<div class="cards">{dis_siyaset}</div>
"""

    today_display = datetime.now().strftime("%d %B %Y, %A")
    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Günlük Haber Brifing — {today_display}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#FAF8F4; color:#1A1A1A; margin:0; padding:0; }}
  .header {{ background:#1A1A1A; color:#fff; padding:28px 32px; }}
  .header h1 {{ margin:0; font-size:22px; letter-spacing:1px; }}
  .header p {{ margin:6px 0 0; color:#aac; font-size:13px; }}
  .section-title {{ background:#1A1A1A; color:#F4B400; padding:10px 32px; font-size:13px; font-weight:700; letter-spacing:2px; text-transform:uppercase; margin-top:28px; }}
  .cards {{ display:flex; flex-wrap:wrap; gap:18px; padding:16px 28px; }}
  .card {{ background:#fff; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,.10); width:calc(50% - 18px); min-width:300px; box-sizing:border-box; border-top:4px solid #1a3a5c; padding:18px 20px; }}
  .card-badge {{ display:inline-block; font-size:10px; font-weight:700; padding:2px 8px; border-radius:12px; margin-bottom:10px; color:#fff; letter-spacing:1px; }}
  .card-title {{ font-size:15px; font-weight:700; line-height:1.4; margin-bottom:6px; color:#111; }}
  .card-meta {{ font-size:11px; color:#888; margin-bottom:12px; }}
  .ozet {{ font-size:13px; color:#1A1A1A; line-height:1.65; margin:0 0 12px 0; }}
  .vtr-block {{ background:#f0fce0; border-left:3px solid #84CC16; padding:10px 14px; border-radius:0 6px 6px 0; margin-bottom:12px; }}
  .vtr-block h4 {{ margin:0 0 8px; font-size:11px; text-transform:uppercase; letter-spacing:1px; }}
  .vtr-item {{ font-size:13px; line-height:1.6; margin-bottom:6px; padding-left:14px; position:relative; color:#1A1A1A; }}
  .vtr-item::before {{ content:"▶"; position:absolute; left:0; color:#84CC16; font-size:10px; top:3px; }}
  .expert-block {{ margin-top:10px; }}
  .expert-block h4 {{ margin:0 0 6px; font-size:11px; color:#555; text-transform:uppercase; letter-spacing:1px; }}
  .expert {{ font-size:12px; line-height:1.6; margin-bottom:4px; padding-left:16px; position:relative; color:#1A1A1A; }}
  .expert::before {{ content:"👤"; position:absolute; left:0; font-size:10px; }}
  .expert strong {{ color:#1A1A1A; }}
  .footer {{ background:#1A1A1A; color:#aac; text-align:center; padding:18px; font-size:12px; margin-top:32px; }}
  @media(max-width:700px) {{ .card {{ width:100%; }} .cards {{ padding:12px; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>📺 Günlük Haber Brifing</h1>
  <p>{today_display} · Otomatik olarak oluşturuldu</p>
</div>
{content_html}
<div class="footer">Gazeteci Asistanı · Claude AI ile oluşturuldu</div>
</body>
</html>"""

    return html

def upload_to_drive(html_content, filename):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaInMemoryUpload

    sa_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]

    creds = service_account.Credentials.from_service_account_info(
        sa_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": filename,
        "parents": [folder_id],
        "mimeType": "text/html"
    }

    media = MediaInMemoryUpload(
        html_content.encode("utf-8"),
        mimetype="text/html"
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    file_id = file.get("id")

    # Herkese açık yap
    service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"}
    ).execute()

    return f"https://drive.google.com/file/d/{file_id}/view"

def send_email(drive_link, today_str):
    sender = os.environ["GMAIL_SENDER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipients = os.environ["RECIPIENT_EMAIL"].split(",")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📺 Günlük Haber Brifing - {today_str}"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;background:#FAF8F4;padding:30px;">
    <div style="max-width:600px;margin:0 auto;background:#1A1A1A;border-radius:12px;padding:30px;text-align:center;">
      <h1 style="color:#F4B400;margin:0 0 10px 0;">📺 Günlük Haber Brifing</h1>
      <p style="color:#aac;font-size:14px;margin:0 0 25px 0;">{today_str}</p>
      <a href="{drive_link}" style="background:#C8102E;color:white;padding:14px 30px;border-radius:8px;text-decoration:none;font-weight:bold;font-size:16px;">
        📰 Brifingimi Aç
      </a>
      <p style="color:#666;font-size:12px;margin-top:20px;">Gazeteci Asistanı · Claude AI ile oluşturuldu</p>
    </div>
    </body></html>
    """

    part = MIMEText(html_body, "html")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())

    print(f"Email gönderildi: {', '.join(recipients)}")

if __name__ == "__main__":
    today_str = datetime.now().strftime("%d.%m.%Y")
    filename = f"brifing_{today_str}.html"

    print("Haberler derleniyor...")
    html_content = get_news_brief()

    print("Google Drive'a yükleniyor...")
    drive_link = upload_to_drive(html_content, filename)
    print(f"Drive linki: {drive_link}")

    print("Email gönderiliyor...")
    send_email(drive_link, today_str)
    print("Tamamlandı!")
