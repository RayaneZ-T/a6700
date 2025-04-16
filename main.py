import os
import requests
from bs4 import BeautifulSoup

# Configuration
URL = "https://ledenicheur.fr/product.php?p=11403019"
SEUIL = 1200  # Seuil d'alerte

# 🔐 Récupération des secrets depuis les variables d'environnement
TELEGRAM_BOT_TOKEN = os.environ.get("7735919437:AAEnVqTSdtL52LMqBHmtLYQFn_4WXYrcq6c")
TELEGRAM_CHAT_ID = os.environ.get("8132587274")

def envoyer_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Les variables d'environnement Telegram ne sont pas définies.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("✅ Message Telegram envoyé")
    else:
        print("❌ Erreur lors de l'envoi Telegram :", response.text)

def get_best_offer_with_link():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    offer_blocks = soup.find_all("a", href=True, attrs={
        "class": lambda x: x and ("go-to-shop" in x or "CardActionArea" in x)
    })

    offers = []
    for block in offer_blocks:
        link = block['href']
        full_link = "https://ledenicheur.fr" + link if link.startswith("/") else link

        price_els = block.find_all("h4", attrs={"data-test": "PriceLabel"})
        if not price_els:
            continue

        for price_el in price_els:
            price_text = price_el.get_text(strip=True).replace('\xa0', '').replace('€', '').replace(',', '.')
            try:
                price = float(price_text)
                offers.append((price, full_link))
            except ValueError:
                continue

    if not offers:
        print("❌ Aucune offre trouvée avec lien.")
        return None

    best_offer = min(offers, key=lambda x: x[0])
    print(f"✅ Meilleure offre avec lien : {best_offer[0]} €")
    print(f"🔗 Lien d'achat : {best_offer[1]}")
    return best_offer

# Exécution
offer = get_best_offer_with_link()
if offer and offer[0] < SEUIL:
    message = f"📉 Offre détectée à {offer[0]} € !\n👉 {offer[1]}"
    envoyer_telegram(message)
else:
    print("🔕 Aucun bon plan pour le moment.")
