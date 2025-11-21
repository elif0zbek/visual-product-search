from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys # Bunu sadece body'yi bulmak için tutabiliriz ama asıl işi JS yapacak
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# --- 1. Adım: Firefox Tarayıcısını Ayarlama ---
print("Firefox tarayıcı ayarları yapılıyor...")
options = Options()
# options.add_argument("--headless") 
options.add_argument("--window-size=1920,1080")
options.set_preference("dom.webdriver.enabled", False)
options.set_preference('useAutomationExtension', False)
options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
print("Firefox tarayıcısı başlatılıyor...")

try:
    s = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=s, options=options)
    print("Firefox tarayıcısı başarıyla başlatıldı.")
except Exception as e:
    print(f"HATA: Firefox tarayıcısı başlatılamadı. {e}")
    exit()

# --- 2. Adım: Trendyol Veri Çekme (Yumuşak Kaydırma) ---
product_list = []
product_urls = set() 
target_count = 1000 # Hedef 1000
trendyol_base_url = "https://www.trendyol.com"
base_url = "https://www.trendyol.com/sr/ayakkabi-x-c109?order=BEST_SELLER"

try:
    print(f"Ana sayfaya gidiliyor: {base_url}")
    driver.get(base_url)
    print("Sayfa yüklendi. 5 saniye bekleniyor...")
    time.sleep(5) 
    
    try:
        cookie_button = driver.find_element("id", "onetrust-accept-btn-handler")
        if cookie_button:
            cookie_button.click()
            print("Çerez uyarısı kapatıldı.")
            time.sleep(2) 
    except Exception:
        print("Çerez uyarısı bulunamadı, devam ediliyor.")
    
    scroll_attempts = 0
    
    while len(product_list) < target_count:
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # İKİ TÜR KARTI DA SEÇ (Bu kod doğru)
        product_cards = soup.select("a.seller-store-product-card, a.product-card")
        
        if not product_cards and len(product_list) == 0:
            print("HİÇ ÜRÜN KARTI BULUNAMADI.")
            break

        new_products_found_in_this_scroll = 0
        for card in product_cards: 
            try:
                relative_url = card.get('href')
                if not relative_url:
                    continue
                
                site_url = trendyol_base_url + relative_url
                
                if site_url not in product_urls:
                    
                    product_name = 'N/A'
                    image_url = 'N/A'
                    
                    # TİP 1: "Sponsorlu" Kart (Bu kod doğru)
                    if 'seller-store-product-card' in card.get('class', []):
                        name_element = card.find('p', class_='product-name')
                        product_name = name_element.text.strip() if name_element else 'N/A'
                        img_element = card.find('img', class_='product-image')
                        image_url = img_element.get('src') if img_element else 'N/A'
                    
                    # TİP 2: "Normal" Kart (Bu kod doğru)
                    elif 'product-card' in card.get('class', []):
                        brand_span = card.find('span', class_='product-brand')
                        name_span = card.find('span', class_='product-name')
                        if brand_span and name_span:
                            product_name = f"{brand_span.text.strip()} {name_span.text.strip()}"
                        
                        img_element = card.find('img', class_='image')
                        image_url = img_element.get('src') if img_element else 'N/A'

                    if product_name != 'N/A' and image_url != 'N/A' and site_url:
                        product_list.append({
                            'product_name': product_name,
                            'image_url': image_url,
                            'site_url': site_url
                        })
                        product_urls.add(site_url) 
                        new_products_found_in_this_scroll += 1
                
            except Exception as e:
                pass 
        
        print(f"Bu kaydırmada {new_products_found_in_this_scroll} yeni ürün bulundu. Toplam: {len(product_list)} / {target_count}")

        if len(product_list) >= target_count:
            print(f"{target_count} hedefine ulaşıldı. Durduruluyor.")
            break
            
        if new_products_found_in_this_scroll == 0:
            scroll_attempts += 1
            print(f"Bu kaydırmada yeni ürün bulunamadı. Bekleniyor... (Deneme: {scroll_attempts}/5)")
            if scroll_attempts >= 5:
                print("5 denemedir yeni ürün bulunamıyor. Sayfanın sonu.")
                break
        else:
            scroll_attempts = 0 # Yeni ürün bulduysak sayacı sıfırla

        # --- NİHAİ DEĞİŞİKLİK: "YUMUŞAK" KAYDIRMA (JavaScript 'scrollBy') ---
        print("Yeni ürünler için 1000 piksel aşağı 'yumuşak' kaydırılıyor...")
        driver.execute_script("window.scrollBy(0, 1000);") # 'Keys.PAGE_DOWN' YERİNE
        # ----------------------------------------------------------------
        
        print("Yeni ürünlerin yüklenmesi için 5-8 saniye bekleniyor...")
        time.sleep(random.uniform(5.0, 8.0))
        
except Exception as e:
    print(f"Ana döngüde bir hata oluştu: {e}")

# --- 4. Adım: Kaydetme ---
print("\n--- Veri Çekme Tamamlandı ---")
driver.quit()
print("Tarayıcı kapatıldı.")

df = pd.DataFrame(product_list).head(target_count) 
print(f"Toplam {len(df)} adet benzersiz ürün bilgisi DataFrame'e yüklendi.")
print(df.head()) 

csv_filename = 'trendyol_ayakkabi.csv'
df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

print(f"\nBaşarılı! Veriler '{csv_filename}' dosyasına kaydedildi.")