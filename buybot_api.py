# buybot_api.py

import time
import random
import requests

# === CONFIG ===
TELEGRAM_TOKEN = "7920670641:AAH1zlG8hwW0Hj_QCz0NnsXOs5in7nVVRw4"
TELEGRAM_CHAT_ID = "@BullxOnSei"
BUY_LINK = "https://kame.ag/SEI-BULLX?ref=BULLX"
PAIR_URLS = [
    ("DragonSwap", "https://api.dexscreener.com/latest/dex/pairs/seiv2/0xaf14f09ff79cde9e0df21ec9c9f95144232bddb8"),
    ("Yaka", "https://api.dexscreener.com/latest/dex/pairs/seiv2/0x9079b022824b931d294eccc66ac9a83aa575edb3")
]
IMAGE_URLS = [
    "https://www.bullionx.xyz/wp-content/uploads/2025/06/early.jpg",
    "https://www.bullionx.xyz/wp-content/uploads/2025/06/BullX-Rumo-a-Lua.png",
    "https://www.bullionx.xyz/wp-content/uploads/2025/06/ChatGPT-Image-22_06_2025-12_15_32.png",
    "https://www.bullionx.xyz/wp-content/uploads/2025/06/ChatGPT-Image-4_06_2025-19_16_09.png",
    "https://www.bullionx.xyz/wp-content/uploads/2025/06/ChatGPT-Image-10_05_2025-13_16_24.png"
]

last_txns = {}


def get_latest_buy(pair_name, url):
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        pair = data["pair"]
        txns = pair["txns"]
        volume = pair["volume"]
        liquidity = pair["liquidity"]["usd"]
        marketcap = pair["marketCap"]
        price = float(pair["priceUsd"])
        buys = txns["m5"]["buys"]

        if buys == 0:
            return None

        key = f"{pair_name}_{buys}"
        if key == last_txns.get(pair_name):
            return None

        last_txns[pair_name] = key

        spent = float(volume["m5"])             # SEI
        amount = spent / price                  # Quantidade $BULLX
        usd = spent * price                     # Valor estimado em USD

        return {
            "pair": pair_name,
            "buys": buys,
            "volume": spent,
            "price_usd": price,
            "liquidity": liquidity,
            "marketcap": marketcap,
            "spent": spent,
            "usd": usd,
            "amount": amount
        }

    except Exception as e:
        print(f"[ERROR] {pair_name}:", e)
        return None




def send_telegram_message(text, image_url):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": text,
        "photo": image_url,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [[{
                "text": "🐂 Buy $BULLX Now – Don’t Miss It",
                "url": BUY_LINK
            }]]
        }
    }
    try:
        res = requests.post(url, json=payload)
        print("[INFO] Sent:", res.status_code, res.text)
    except Exception as e:
        print("[ERROR] Telegram:", e)

def calculate_rocket_icons(sei_spent, ratio=1):
    """
    Gera a string de ícones 🚀 com base no valor de SEI gasto.
    ratio = 1 -> 1 ícone por cada X SEI.
    """
    try:
        sei_float = float(sei_spent)
        count = int(sei_float // ratio)
        return "🚀" * count
    except Exception as e:
        print("[ERRO] Ícones:", e)
        return ""

def main():
    print("🐂 BuyBot API started...")
    while True:
        try:
            for name, url in PAIR_URLS:
                buy = get_latest_buy(name, url)
                if buy:
                    image = random.choice(IMAGE_URLS)
                    intro = random.choice([
                        f"🐂 Someone just joined the herd on {buy['pair']}!",
                        f"🔥 Another Bullx believer just bought in via {buy['pair']}!",
                        f"💣 New $BULLX buy exploded on {buy['pair']}!",
                        f"🚨 Bullx-ish hard on {buy['pair']} — another buy just landed!",
                        f"👀 A degen just went Bullx mode on {buy['pair']}!"
                    ])

                    print(f"[DEBUG] SEI gasto: {buy['spent']}")
                    rockets = calculate_rocket_icons(buy['spent'], ratio=1)

                    msg = (
                        f"{intro}\n\n"
                        f"{rockets}\n\n"
                        f"💰 Got: {buy['amount']:,.0f} $BULLX\n"
                        f"💲 Spent: {buy['spent']:,.3f} $USD\n"
                        f"✅ Dex: {buy['pair']}\n"
                        f"🏦 Liquidity: ${buy['liquidity']:,.2f}\n"
                        f"📊 Market Cap: ${buy['marketcap']:,.0f}\n\n"
                        f"[📈 Chart](https://dexscreener.com/seiv2/0xaf14f09ff79cde9e0df21ec9c9f95144232bddb8) | "
                        f"[🌐 Website](https://www.bullionx.xyz/) | "
                        f"[📌 Portal](https://stampede.bullionx.xyz/) | "
                        f"[✖️ Twitter](https://x.com/BullxOnSei)"
                    )

                    send_telegram_message(msg, image)

            time.sleep(3)
        except Exception as e:
            print("[ERROR in main loop]:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()