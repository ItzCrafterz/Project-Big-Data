# Analisis Sentimen Naturalisasi Pemain Timnas Indonesia
**oleh: Gilang Gallan Indrana (5024231030)**

## Daftar Isi
1.  [Deskripsi Proyek](#1-deskripsi-proyek)
2.  [Fitur Utama](#2-fitur-utama)
3.  [Alur Kerja Sistem](#3-alur-kerja-sistem)
4.  [Teknologi & Tools](#4-teknologi--tools)
5.  [Struktur Folder](#5-struktur-folder)
6.  [Cara Menjalankan](#6-cara-menjalankan)
7.  [Penjelasan Modul](#7-penjelasan-modul)

---

## 1. Deskripsi Proyek
Proyek ini adalah sebuah sistem komprehensif untuk melakukan analisis sentimen terhadap isu **naturalisasi pemain untuk Tim Nasional (Timnas) Sepak Bola Indonesia**. Sistem ini secara otomatis mengumpulkan data dari berbagai sumber online (berita dan komentar YouTube), membersihkan dan memproses data teks tersebut, menganalisis sentimennya menggunakan metode berbasis leksikon, dan menyajikan hasilnya dalam bentuk ringkasan statistik, visualisasi data, serta menyimpannya ke dalam database MySQL untuk diakses oleh dashboard.

Tujuan utama proyek ini adalah untuk memahami bagaimana opini publik terbagi antara yang mendukung (sentimen positif) dan yang menolak (sentimen negatif) kebijakan naturalisasi pemain, serta membandingkan bagaimana sentimen ini berbeda di berbagai platform.

---

## 2. Fitur Utama
-   **Crawling Data Multi-Sumber**: Mampu mengumpulkan data dari **Google News** dan komentar **YouTube** secara otomatis berdasarkan kata kunci yang relevan.
-   **Pembersihan Data Tingkat Lanjut**: Dilengkapi modul `DataCleaner` untuk menghapus data duplikat, spam, dan teks yang tidak relevan (terlalu pendek/panjang).
-   **Preprocessing Teks Bahasa Indonesia**: Menggunakan library **Sastrawi** untuk proses *stemming* (mengubah kata ke bentuk dasar) dan *stopword removal* yang disesuaikan untuk Bahasa Indonesia.
-   **Analisis Sentimen Berbasis Leksikon**: Sentimen ditentukan dengan menghitung jumlah kata positif dan negatif dari kamus (leksikon) yang telah didefinisikan dalam `config.py`.
-   **Analisis Perbandingan**: Menganalisis dan memvisualisasikan perbedaan sentimen antara data yang berasal dari Berita dan komentar YouTube.
-   **Visualisasi Data Komprehensif**: Menghasilkan berbagai macam grafik untuk mempermudah pemahaman hasil analisis, seperti Pie Chart, Bar Chart, Word Cloud, dan Grafik Tren.
-   **Integrasi Database MySQL**: Menyimpan semua data mentah dan hasil analisis ke dalam database MySQL, memungkinkan data untuk digunakan oleh aplikasi lain seperti dashboard web.
-   **Pelatihan Model Machine Learning (Bonus)**: Sebagai fitur tambahan, sistem ini juga melatih model klasifikasi sentimen menggunakan **Naive Bayes** untuk evaluasi dan potensi penggunaan di masa depan.

---

## 3. Alur Kerja Sistem
Sistem bekerja melalui beberapa tahapan yang diatur secara berurutan oleh `main.py`:

1.  **Inisialisasi**: Sistem membuat folder `data` dan `output` jika belum ada, untuk menyimpan file CSV dan gambar hasil visualisasi.

2.  **Tahap 1: Pengumpulan Data (Crawling)**
    -   **Berita**: `news_crawler.py` menggunakan library `GoogleNews` untuk mencari artikel berita berdasarkan daftar kata kunci di `config.py`. Terdapat filter relevansi untuk memastikan artikel yang diambil benar-benar terkait Timnas Indonesia.
    -   **YouTube**: Jika diaktifkan, `youtube_scraper.py` (diimpor di `main.py`) akan menggunakan YouTube Data API untuk mencari video dan mengambil komentar dari video-video tersebut.
    -   **Penggabungan**: Data dari kedua sumber digabungkan menjadi satu DataFrame utama dan disimpan di `data/raw_data.csv`.

3.  **Tahap 2: Pembersihan Data (Cleaning)**
    -   `data_cleaner.py` dipanggil untuk membersihkan data mentah.
    -   Proses ini mencakup:
        -   Menghapus baris data dengan konten yang sama persis (duplikat).
        -   Menghapus konten yang terindikasi spam (misalnya, berisi ajakan "subscribe", "like", dll).
        -   Menghapus konten yang terlalu pendek atau terlalu panjang.

4.  **Tahap 3: Preprocessing Teks**
    -   `text_preprocessor.py` mengambil alih untuk memproses kolom teks (`content`).
    -   Langkah-langkahnya adalah:
        -   **Cleansing**: Menghapus URL, mention, hashtag, angka, dan tanda baca.
        -   **Case Folding**: Mengubah semua teks menjadi huruf kecil.
        -   **Stopword Removal**: Menghapus kata-kata umum yang tidak memiliki makna sentimen (misal: "yang", "di", "dan") menggunakan kamus dari Sastrawi dan kamus tambahan.
        -   **Stemming**: Mengubah setiap kata ke bentuk dasarnya (misal: "mendukung" -> "dukung") menggunakan Sastrawi.
    -   Hasilnya disimpan dalam kolom baru bernama `processed_text`.

5.  **Tahap 4: Analisis Sentimen**
    -   `lexicon_analyzer.py` menganalisis kolom `processed_text`.
    -   Untuk setiap teks, sistem menghitung **skor sentimen** dengan cara: `(jumlah kata positif) - (jumlah kata negatif)`.
    -   Berdasarkan skor tersebut, sentimen diklasifikasikan menjadi:
        -   **Positif** (jika skor > 0)
        -   **Negatif** (jika skor < 0)
        -   **Netral** (jika skor = 0)
    -   Hasil analisis disimpan di `data/processed_data.csv`.

6.  **Tahap 5: Ringkasan & Prediksi**
    -   Sistem menghitung ringkasan statistik (jumlah total, positif, negatif, netral, setuju, tidak setuju, dan persentasenya).
    -   `main.py` juga memberikan interpretasi dan prediksi tren sederhana berdasarkan dominasi sentimen.

7.  **Tahap 6: Visualisasi Data**
    -   `visualizer.py` (diimpor di `main.py`) membuat berbagai grafik dari data yang telah dianalisis dan menyimpannya di folder `output`.

8.  **Tahap 7: Integrasi Database**
    -   `mysql_integration.py` melakukan koneksi ke database MySQL.
    -   Data mentah (berita & youtube) dan data hasil sentimen dimasukkan ke dalam tabel-tabel yang sesuai.
    -   Sistem juga meng-update tabel statistik (`dashboard_stats`) yang bisa digunakan untuk menampilkan data agregat di dashboard.

9.  **Tahap 8: Analisis Perbandingan**
    -   `comparison_analyzer.py` secara khusus membandingkan hasil sentimen dari sumber Berita dan YouTube, lalu membuat visualisasi perbandingannya.

---

## 4. Teknologi & Tools
Berikut adalah daftar library Python utama yang digunakan dalam proyek ini:

| Kategori              | Library                 | Versi   | Kegunaan                                                    |
| --------------------- | ----------------------- | ------- | ----------------------------------------------------------- |
| **Web Crawling** | `GoogleNews`            | 1.6.13  | Mengambil data artikel dari Google News.                    |
|                       | `google-api-python-client`| -       | Mengakses YouTube Data API untuk mengambil data komentar.    |
| **Pemrosesan Teks** | `Sastrawi`              | 1.0.1   | Menyediakan fungsi *stemming* & *stopword removal* B. Indonesia.|
|                       | `nltk`                  | 3.8.1   | Digunakan untuk tokenisasi teks.                            |
| **Olah Data** | `pandas`                | 2.1.4   | Struktur data utama (DataFrame) untuk manipulasi data.      |
|                       | `numpy`                 | 1.26.2  | Digunakan untuk operasi numerik.                            |
| **Machine Learning** | `scikit-learn`          | 1.3.2   | Melatih dan mengevaluasi model Naive Bayes.                 |
| **Visualisasi** | `matplotlib`            | 3.8.2   | Membuat plot dan grafik statis.                             |
|                       | `seaborn`               | 0.13.0  | Membuat visualisasi data yang lebih menarik di atas Matplotlib.|
|                       | `wordcloud`             | 1.9.3   | Membuat visualisasi Word Cloud.                             |
| **Database** | `mysql-connector-python`| -       | Menghubungkan aplikasi Python dengan database MySQL.        |

---

## 5. Struktur Folder
` .
├── data/                 # Folder untuk menyimpan file CSV (data mentah & terproses)
├── output/               # Folder untuk menyimpan gambar hasil visualisasi
├── main.py               # File utama untuk menjalankan seluruh alur kerja
├── config.py             # File konfigurasi (keyword, leksikon, pengaturan)
├── requirements.txt      # Daftar library Python yang dibutuhkan
├── news_crawler.py       # Modul untuk crawling berita
├── youtube_scraper.py    # Modul untuk crawling komentar YouTube
├── data_cleaner.py       # Modul untuk membersihkan data mentah
├── text_preprocessor.py  # Modul untuk preprocessing teks
├── lexicon_analyzer.py   # Modul untuk analisis sentimen
├── visualizer.py         # Modul untuk membuat visualisasi
├── comparison_analyzer.py# Modul untuk analisis perbandingan
├── mysql_integration.py  # Modul untuk integrasi database MySQL
└── download_nltk_data.py # Skrip untuk mengunduh data NLTK `
---

## 6. Cara Menjalankan

1.  **Clone Repositori**
    ` git clone [URL_REPOSITORI_ANDA]
    cd [NAMA_FOLDER_PROYEK] `

2.  **Buat Virtual Environment (Sangat Direkomendasikan)**
    ` python -m venv venv
    venv\Scripts\activate  # Windows
    source venv/bin/activate  # MacOS/Linux `

3.  **Install Semua Kebutuhan Library**
    ` pip install -r requirements.txt `

4.  **Unduh Data NLTK**
    Jalankan skrip ini satu kali untuk mengunduh model yang dibutuhkan oleh NLTK.
    ` python download_nltk_data.py `

5.  **Konfigurasi**
    Buka file `config.py` dan sesuaikan pengaturannya:
    -   `YOUTUBE_API_KEY`: Masukkan API Key Anda dari Google Cloud Console agar bisa crawling data YouTube.
    -   Anda juga bisa menyesuaikan `SEARCH_KEYWORDS`, `POSITIVE_WORDS`, dan `NEGATIVE_WORDS`.

6.  **Setup Database MySQL**
    -   Pastikan server MySQL Anda (misalnya dari XAMPP) sudah berjalan.
    -   Buat sebuah database baru dengan nama `sentiment_analysis`.
    -   Impor skema tabel dari file `database_schema.sql` (jika ada) atau buat tabel secara manual sesuai yang dibutuhkan oleh `mysql_integration.py`.
    -   Sesuaikan detail koneksi (host, user, password) di dalam `main.py` pada bagian **TAHAP 7**.

7.  **Jalankan Program Utama**
    ` python main.py `
    Program akan menjalankan semua tahapan secara otomatis. Hasilnya akan ditampilkan di console, disimpan di folder `data` dan `output`, serta dimasukkan ke database MySQL.

---

## 7. Penjelasan Modul

-   `main.py`: Bertindak sebagai "otak" atau orkestrator yang memanggil dan menjalankan semua modul lain secara berurutan.
-   `config.py`: Pusat konfigurasi. Berisi semua pengaturan yang dapat diubah seperti kata kunci, kamus sentimen, dan API key.
-   `news_crawler.py`: Fokus pada tugas spesifik mengambil artikel dari Google News dan menyaringnya.
-   `youtube_scraper.py`: Fokus pada tugas mengambil komentar dari YouTube menggunakan API.
-   `data_cleaner.py`: Modul yang bertanggung jawab untuk memastikan kualitas data sebelum diproses lebih lanjut.
-   `text_preprocessor.py`: Berisi semua fungsi yang terkait dengan pengolahan bahasa alami (NLP) untuk teks berbahasa Indonesia.
-   `lexicon_analyzer.py`: Inti dari analisis sentimen, menerapkan logika berbasis kamus untuk mengklasifikasikan teks.
-   `visualizer.py`: Berisi semua kode untuk mengubah data numerik hasil analisis menjadi grafik yang mudah dipahami.
-   `comparison_analyzer.py`: Modul khusus untuk melakukan analisis perbandingan antar sumber data.
-   `mysql_integration.py`: Menangani semua interaksi dengan database MySQL, mulai dari koneksi hingga memasukkan data.