
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8016305105:AAEJKHnSw8d30cpD155QCfYSQmnnSJjw68E"  

CURRENCIES = {
    'دلار': 'price_dollar_rl',
    'طلا': 'geram18',
    'بیت‌کوین': 'bitcoin'
}

def get_price(text):
    text = text.lower().strip()
    
    if text not in CURRENCIES:
        return "فقط دلار، طلا یا بیت‌کوین رو می‌فهمم!"
    
    coin = CURRENCIES[text]
    
    if coin == 'bitcoin':
        try:
            r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true", timeout=10)
            data = r.json()['bitcoin']
            price = data['usd']
            change = data['usd_24h_change']
            return f"بیت‌کوین: ${price:,.0f}\nتغییر ۲۴ ساعت: {change:+.2f}%"
        except:
            return "خطا در گرفتن قیمت بیت‌کوین "
    

    url = f"https://www.tgju.org/profile/{coin}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
 
        price_candidates = []
        for tag in soup.find_all(['span', 'div', 'td']):
            text = tag.get_text(strip=True)
       
            if text.isdigit() and len(text) > 6:
                price_candidates.append(int(text))
        
        if price_candidates:
            price = max(price_candidates) 
            change_tag = soup.find(lambda tag: tag.name in ['span', 'div'] and 'change' in tag.get('class', []))
            change = 0.0
            if change_tag:
                change_text = change_tag.get_text(strip=True).replace('%', '').replace('+', '').strip()
                try:
                    change = float(change_text)
                except:
                    pass
            
            return f"{text.capitalize()}: {price:,} تومان\nتغییر تقریبی: {change:+.2f}%"
        else:
            return f"قیمت {text} پیدا نشد (سایت ممکنه تغییر کرده باشه)"
    
    except Exception as e:
        return f"خطا در اتصال برای {text}: {str(e)}"
    

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    answer = get_price(text)
    await update.message.reply_text(answer)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من می‌تونم قیمت دلار، طلا و بیت‌کوین رو بگم!") 

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex(r"^/start$"), start))
    print("bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

