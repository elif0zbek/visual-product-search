import clip
import torch
import faiss
import pickle
import pandas as pd
from PIL import Image
import io
import requests
import numpy as np
import os

print("Script başlatıldı...")

# --- 1. Gerekli Değişkenler ve Dosya Yolları ---

# Sunucuyla (app.py) aynı modeli (ViT-L/14) kullanıyoruz
MODEL_ADI = "ViT-L/14"
EMBEDDING_DIM = 768  # ViT-L/14'ün embedding boyutu

# Dosya yolları lokal klasör yapısına göre güncellendi
# ../data/ -> bir üst klasördeki 'data' klasörüne git
CSV_PATH = os.path.join('..', 'data', 'trendyol_ayakkabi.csv')

# ../ -> bir üst klasöre kaydet
INDEX_PATH = os.path.join('..', 'ayakkabi_index_L14.faiss')
PAYLOAD_PATH = os.path.join('..', 'ayakkabi_payload_L14.pkl')

# --- 2. CLIP Modeli ---
print(f"CLIP modeli ({MODEL_ADI}) yükleniyor...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load(MODEL_ADI, device=device)
print(f"Model {device} üzerine yüklendi.")

# --- 3. CSV’den Ürün Veritabanını Oku ---
print(f"Veri tabanı şuradan okunuyor: {CSV_PATH}")
if not os.path.exists(CSV_PATH):
    print(f"HATA: {CSV_PATH} dosyası bulunamadı. Lütfen önce 1_scrape_data.py script'ini çalıştırın.")
    exit()
    
df = pd.read_csv(CSV_PATH)
print(f"Toplam {len(df)} ürün yüklendi.")

# --- 4. FAISS Index ve Payload Hazırlığı ---
index_clip = faiss.IndexFlatIP(EMBEDDING_DIM)
payload_map_clip = []

print(f"Toplam {len(df)} ürün işlenecek ve embedding'leri oluşturulacak...")

for idx, row in df.iterrows():
    # CSV dosya isimlerinin 'image_url', 'product_name', 'site_url' olduğunu varsayıyoruz
    image_url = row['image_url']
    product_name = row['product_name']
    site_url = row['site_url']

    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code != 200:
            print(f"Hata: {image_url} indirilemedi.")
            continue

        img_data = response.content
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
        img_input = preprocess(img).unsqueeze(0).to(device)

        with torch.no_grad():
            embedding = model.encode_image(img_input)

        # L2 Normalize
        embedding /= embedding.norm(dim=-1, keepdim=True)

        # FAISS'e ekle
        index_clip.add(embedding.cpu().numpy().astype('float32'))

        # Payload ekle
        payload_map_clip.append({
            "product_name": product_name,
            "site_url": site_url,
            "image_url": image_url
        })

        if (idx + 1) % 50 == 0:
            print(f"{idx + 1}/{len(df)} ürün işlendi.")

    except Exception as e:
        print(f"Hata [{idx}]: {image_url} işlenirken {e}")

print(f"\n--- İşlem Tamamlandı ---")
print(f"FAISS index toplam {index_clip.ntotal} embedding içeriyor.")

# --- 5. Index ve Payload'u kaydet ---
faiss.write_index(index_clip, INDEX_PATH)
with open(PAYLOAD_PATH, 'wb') as f:
    pickle.dump(payload_map_clip, f)

print(f"Index kaydedildi: {INDEX_PATH}")
print(f"Payload kaydedildi: {PAYLOAD_PATH}")
print("Tüm işlemler tamamlandı.")