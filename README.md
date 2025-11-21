#  Visual Product Search Engine (Görsel Ürün Arama Motoru)

Bu proje, kullanıcıların yüklediği bir ayakkabı fotoğrafını analiz ederek, veritabanındaki en benzer ürünleri bulan yapay zeka tabanlı bir web uygulamasıdır.

## Özellikler

* **Derin Öğrenme Tabanlı:** ResNet50 modeli kullanılarak görsellerden öznitelik vektörleri (feature extraction) çıkarılır.
* **Hızlı Arama:** FAISS (Facebook AI Similarity Search) kütüphanesi ve Kosinüs Benzerliği (Cosine Similarity) kullanılarak milisaniyeler içinde arama yapılır.
* **Kullanıcı Dostu Arayüz:** Streamlit ile geliştirilmiş modern ve responsive web arayüzü.
* **Gerçek Veri:** Trendyol üzerinden toplanan gerçek ayakkabı veri seti üzerinde çalışır.

## Kullanılan Teknolojiler

* **Python 3.x**
* **TensorFlow / Keras:** ResNet50 modeli için.
* **FAISS (Facebook AI Similarity Search):** Vektör veritabanı ve hızlı benzerlik araması için.
* **Streamlit:** Web arayüzü (UI) için.
* **Pandas & NumPy:** Veri işleme için.

## Kurulum

Bu projeyi kendi bilgisayarınızda çalıştırmak için adımları takip edin:

1.  **Projeyi Klonlayın:**
    ```bash
    git clone [https://github.com/KULLANICI_ADIN/REPO_ADIN.git](https://github.com/KULLANICI_ADIN/REPO_ADIN.git)
    cd REPO_ADIN
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Uygulamayı Başlatın:**
    ```bash
    streamlit run app.py
    ```

## Proje Yapısı

* `app.py`: Streamlit ana uygulama dosyası.
* `ayakkabi_index_cosine.faiss`: FAISS vektör veritabanı dosyası.
* `ayakkabi_payload_cosine.pkl`: Ürün bilgilerini (link, resim url, isim) tutan dosya.
* `requirements.txt`: Gerekli kütüphane listesi.
