#!/usr/bin/env python3
"""
Notification service for breakfast reminders.
Sends daily notifications via Email and/or WhatsApp.
"""

import os
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), 'breakfast.db')


def get_tomorrow_date():
    """Get tomorrow's date string."""
    return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')


def get_tomorrow_meal():
    """Get the confirmed meal for tomorrow from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    tomorrow = get_tomorrow_date()
    
    cursor.execute('''
        SELECT r.*, n.calories, n.protein, n.carbohydrate, n.fat, n.fiber
        FROM draw_history dh
        JOIN recipes r ON dh.recipe_id = r.id
        LEFT JOIN nutrition n ON r.id = n.recipe_id
        WHERE dh.draw_date = ? AND dh.confirmed = 1
    ''', (tomorrow,))
    
    result = cursor.fetchone()
    if not result:
        conn.close()
        return None
    
    meal = dict(result)
    
    # Get ingredients
    cursor.execute('''
        SELECT ingredient_name, quantity, unit, notes
        FROM ingredients WHERE recipe_id = ?
    ''', (meal['id'],))
    meal['ingredients'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return meal


def format_meal_message(meal):
    """Format meal info for notification."""
    if not meal:
        return "🍳 还没有确认明天的早餐！\n快去网站抽取一个吧！"
    
    ingredients_text = "\n".join([
        f"  • {ing['ingredient_name']} - {ing['quantity'] or ''} {ing['unit'] or ''}"
        for ing in meal['ingredients']
    ])
    
    message = f"""
🍳 明日早餐提醒 🍳

📅 {get_tomorrow_date()}

🥘 菜品: {meal['recipe_name']} ({meal['recipe_name_en']})
⏱️ 烹饪时间: {meal['cooking_time']} 分钟
📊 难度: {'⭐' * meal['difficulty']}

📊 营养信息:
  • 热量: {meal['calories']} kcal
  • 蛋白质: {meal['protein']}g
  • 碳水: {meal['carbohydrate']}g
  • 脂肪: {meal['fat']}g

🛒 准备食材:
{ingredients_text}

祝你明天早餐愉快！🌟
"""
    return message


def send_email_notification(meal):
    """Send email notification."""
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')
    to_email = os.getenv('NOTIFICATION_EMAIL')
    
    if not all([smtp_email, smtp_password, to_email]):
        print("⚠️ Email configuration incomplete. Skipping email notification.")
        return False
    
    try:
        message = MIMEMultipart('alternative')
        message['Subject'] = f'🍳 明日早餐提醒 - {meal["recipe_name"] if meal else "快去选择吧"}'
        message['From'] = smtp_email
        message['To'] = to_email
        
        text_content = format_meal_message(meal)
        
        # Create HTML version
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h1>🍳 明日早餐提醒</h1>
                <p>{get_tomorrow_date()}</p>
            </div>
            
            {"<div style='padding: 20px; background: #f8f9fa; border-radius: 10px; margin-top: 20px;'>" + f'''
                <h2 style="color: #333;">{meal['recipe_name']}</h2>
                <p style="color: #888;">{meal['recipe_name_en']}</p>
                
                <div style="display: flex; gap: 20px; margin: 15px 0;">
                    <span>⏱️ {meal['cooking_time']} 分钟</span>
                    <span>📊 难度 {'⭐' * meal['difficulty']}</span>
                </div>
                
                <h3>🛒 准备食材</h3>
                <ul>
                    {"".join(f"<li>{ing['ingredient_name']} - {ing['quantity'] or ''} {ing['unit'] or ''}</li>" for ing in meal['ingredients'])}
                </ul>
                
                <h3>📊 营养信息</h3>
                <p>热量: {meal['calories']} kcal | 蛋白质: {meal['protein']}g | 碳水: {meal['carbohydrate']}g</p>
            ''' + "</div>" if meal else "<p style='text-align: center; padding: 40px;'>还没有确认明天的早餐！<br>快去网站抽取一个吧！</p>"}
            
            <p style="text-align: center; color: #888; margin-top: 20px;">
                祝你明天早餐愉快！🌟
            </p>
        </body>
        </html>
        """
        
        message.attach(MIMEText(text_content, 'plain'))
        message.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(message)
        
        print(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def send_whatsapp_notification(meal):
    """Send WhatsApp notification via Twilio."""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_whatsapp = os.getenv('TWILIO_WHATSAPP_FROM')
    to_whatsapp = os.getenv('WHATSAPP_TO')
    
    if not all([account_sid, auth_token, from_whatsapp, to_whatsapp]):
        print("⚠️ WhatsApp configuration incomplete. Skipping WhatsApp notification.")
        return False
    
    try:
        from twilio.rest import Client
        
        client = Client(account_sid, auth_token)
        
        message_body = format_meal_message(meal)
        
        message = client.messages.create(
            body=message_body,
            from_=from_whatsapp,
            to=to_whatsapp
        )
        
        print(f"✅ WhatsApp message sent: {message.sid}")
        return True
        
    except ImportError:
        print("⚠️ Twilio library not installed. Run: pip install twilio")
        return False
    except Exception as e:
        print(f"❌ Failed to send WhatsApp: {e}")
        return False


def send_notifications():
    """Send all configured notifications."""
    print(f"\n📬 Sending notifications at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    meal = get_tomorrow_meal()
    
    if meal:
        print(f"📋 Tomorrow's meal: {meal['recipe_name']}")
    else:
        print("⚠️ No meal confirmed for tomorrow")
    
    # Send email
    send_email_notification(meal)
    
    # Send WhatsApp
    send_whatsapp_notification(meal)
    
    print("✅ Notification process complete\n")


if __name__ == '__main__':
    send_notifications()
