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
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""Bugün {today} tarihi için Türkiye ve dünya gündeminden önemli haberleri derle.
                
Şu kategorilerde özet hazırla:
- 🇹🇷 Türkiye Gündemi
- 🌍 Dünya Gündemi  
- 💰 Ekonomi
- 📱 Teknoloji

Her kategori için 3-4 önemli başlık ve kısa açıklama yaz.
HTML formatında, okunması kolay bir bülten olarak hazırla."""
            }
        ]
    )
    
    return message.content[0].text

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
