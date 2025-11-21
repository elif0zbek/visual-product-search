from flask import Flask, request, jsonify, render_template
import clip
import torch
import faiss
import pickle
from PIL import Image
import io
import os
import numpy as np

# İSTEK 3 İÇİN EKLENDİ
import webbrowser
from threading import Timer

app = Flask(__name__)

# --- 1. Model ve Index Yükleme ---
print("Sunucu başlatılıyor: CLIP modeli yükleniyor...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-L/14", device=device)
print("Model (ViT-L/14) yüklendi.")

index_path = "ayakkabi_index_L14.faiss"
payload_path = "ayakkabi_payload_L14.pkl"

print("Index ve payload yükleniyor...")
index_clip = faiss.read_index(index_path)
with open(payload_path, 'rb') as f:
    payload_map_clip = pickle.load(f)

print(f"Sunucu hazır. {index_clip.ntotal} ürün veritabanında.")


# --- 2. Arama Fonksiyonu (GÜNCELLENDİ) ---
# search_hybrid fonksiyonu sadeleştirildi, artık sadece resim arıyor (İstek 2)
def search_image(image_data, k=5):
    """
    Sadece görsel sorgu kullanarak arama yapar.
    Flask/FastAPI uyumlu, JSON listesi döndürür.
    """
    try:
        # 1. GÖRSEL İŞLEME
        img = Image.open(io.BytesIO(image_data)).convert("RGB")
        img_input = preprocess(img).unsqueeze(0).to(device)
        with torch.no_grad():
            img_vector = model.encode_image(img_input)
        img_vector /= img_vector.norm(dim=-1, keepdim=True) # Normalize et

        final_vector = img_vector # Artık sadece resim vektörü var
        print("Sadece görsel arama yapılıyor...")

        # 2. FAISS'te ARAMA
        query_np = final_vector.cpu().numpy().astype('float32')
        D, I = index_clip.search(query_np, k) # D=Mesafeler (Skorlar), I=Index'ler

        print("\n--- ARAMA SONUÇLARI ---")
        
        # 3. SONUÇLARI JSON LİSTESİNE ÇEVİRME
        results_list = []
        for i, idx in enumerate(I[0]):
            result = payload_map_clip[idx]
            score = D[0][i]
            results_list.append({
                "product_name": result['product_name'],
                "site_url": result['site_url'],
                "image_url": result['image_url'],
                "score": float(score) # Skoru float yap (JSON için önemli)
            })
        
        return results_list

    except Exception as e:
        import traceback
        print("Hata oluştu:")
        traceback.print_exc()
        return None

# --- 3. API Endpoints ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    if 'image' not in request.files:
        return jsonify({"error": "Resim dosyası eksik"}), 400
    
    image_file = request.files['image']
    image_data = image_file.read()

    # GÜNCELLENDİ: Metin sorgusu alma kısmı kaldırıldı (İstek 2)
    # text_query = request.form.get('text') 

    # GÜNCELLENDİ: search_image çağırılıyor (İstek 2)
    results = search_image(image_data, k=5)

    if results is not None:
        return jsonify(results)
    else:
        return jsonify({"error": "Arama sırasında hata"}), 500

# --- 4. Sunucuyu Başlatma (GÜNCELLENDİ) ---
# İSTEK 3 İÇİN GÜNCELLENDİ
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    
    # Sunucu başlamadan 1 saniye sonra tarayıcıyı açmak için zamanlayıcı
    def open_browser():
        webbrowser.open_new(f'http://127.0.0.1:{port}')

    Timer(1, open_browser).start()
    
    app.run(host='0.0.0.0', port=port)