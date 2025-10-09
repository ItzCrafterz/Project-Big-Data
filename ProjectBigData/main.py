# main.py
# Program utama untuk analisis sentimen naturalisasi pemain timnas Indonesia
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score

# Import modules
try:
    from news_crawler import NewsCrawler
    from text_preprocessor import TextPreprocessor
    from indobert_analyzer import IndoBERTSentimentAnalyzer
    from visualizer import SentimentVisualizer
    from comparison_analyzer import ComparisonAnalyzer
    import config
except ImportError as e:
    print(f"[ERROR] Error importing modules: {str(e)}")
    print("\nPastikan semua file berikut ada di folder yang sama:")
    print("  - news_crawler.py")
    print("  - youtube_scraper.py")
    print("  - text_preprocessor.py")
    print("  - IndoBERT_analyzer.py")
    print("  - visualizer.py")
    print("  - comparison_analyzer.py")
    print("  - config.py")
    sys.exit(1)

def create_directories():
    """Membuat folder yang diperlukan"""
    directories = ['data', 'output']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[INFO] Folder '{directory}' dibuat")

def train_prediction_model(df):
    """
    Melatih model prediksi sentimen menggunakan Naive Bayes
    
    Args:
        df: DataFrame dengan kolom 'processed_text' dan 'sentiment'
    
    Returns:
        Model terlatih dan vectorizer
    """
    print("\n" + "="*70)
    print("TAHAP BONUS: TRAINING MODEL PREDIKSI")
    print("="*70)
    
    # Filter data yang valid
    df_clean = df[df['processed_text'].str.strip() != ''].copy()
    
    if len(df_clean) < 50:
        print("[WARNING] Data terlalu sedikit untuk training model")
        return None, None
    
    # Pisahkan fitur dan label
    X = df_clean['processed_text']
    y = df_clean['sentiment']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"[INFO] Data training: {len(X_train)} | Data testing: {len(X_test)}")
    
    # Vectorize text
    vectorizer = TfidfVectorizer(max_features=500, min_df=2)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Train model
    model = MultinomialNB()
    model.fit(X_train_vec, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n[RESULT] Akurasi Model: {accuracy*100:.2f}%")
    print("\n[RESULT] Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    return model, vectorizer

def predict_future_sentiment(summary):
    """
    Membuat prediksi dan interpretasi tren sentimen masa depan
    
    Args:
        summary: Dictionary hasil sentiment summary
    """
    print("\n" + "="*70)
    print("PREDIKSI & ANALISIS TREN")
    print("="*70)
    
    setuju_pct = summary['setuju_pct']
    tidak_setuju_pct = summary['tidak_setuju_pct']
    
    # Analisis sentiment dominan
    if setuju_pct > tidak_setuju_pct:
        dominan = "POSITIF (Setuju)"
        delta = setuju_pct - tidak_setuju_pct
    else:
        dominan = "NEGATIF (Tidak Setuju)"
        delta = tidak_setuju_pct - setuju_pct
    
    print(f"\n[ANALISIS] Sentimen Dominan: {dominan}")
    print(f"[ANALISIS] Selisih: {delta:.1f}%")
    
    # Prediksi berdasarkan dominasi
    print("\n[PREDIKSI] Tren Masa Depan:")
    if delta > 30:
        print(f"  >> Sentimen {dominan} sangat kuat dan stabil.")
        print(f"  >> Kemungkinan besar opini publik akan tetap {dominan.split()[0].lower()}.")
    elif delta > 15:
        print(f"  >> Sentimen {dominan} cukup kuat.")
        print(f"  >> Opini publik cenderung {dominan.split()[0].lower()}, namun masih ada ruang debat.")
    elif delta > 5:
        print(f"  >> Sentimen {dominan} sedikit lebih unggul.")
        print(f"  >> Opini publik masih terpolarisasi, bisa berubah tergantung perkembangan.")
    else:
        print(f"  >> Sentimen seimbang antara setuju dan tidak setuju.")
        print(f"  >> Opini publik sangat terbagi, situasi tidak menentu.")
    
    # Rekomendasi
    print("\n[REKOMENDASI]:")
    if setuju_pct > tidak_setuju_pct:
        print("  1. Mayoritas mendukung naturalisasi pemain.")
        print("  2. Stakeholder dapat melanjutkan kebijakan dengan lebih percaya diri.")
        print("  3. Perlu edukasi untuk kelompok yang masih ragu/menolak.")
    else:
        print("  1. Mayoritas menolak atau ragu terhadap naturalisasi pemain.")
        print("  2. Stakeholder perlu evaluasi dan komunikasi lebih baik.")
        print("  3. Penting untuk mendengarkan kekhawatiran masyarakat.")
    
    print("\n[INFO] Analisis ini berdasarkan data berita yang di-crawl.")
    print("[INFO] Hasil dapat berbeda jika menggunakan data dari platform lain.")

def main():
    """Fungsi utama program"""
    print("="*70)
    print("  ANALISIS SENTIMEN NATURALISASI PEMAIN TIMNAS INDONESIA")
    print("="*70)
    print()
    
    # Buat folder yang diperlukan
    create_directories()
    
    # ===== TAHAP 1: CRAWLING BERITA =====
    print("\n" + "="*70)
    print("TAHAP 1: CRAWLING DATA")
    print("="*70)
    
    # 1A. Crawl Berita
    print("\n[1A] CRAWLING BERITA ONLINE")
    print("-"*70)
    print(f"[INFO] Target: {config.NUM_ARTICLES} artikel per keyword")
    print(f"[INFO] Total keyword: {len(config.SEARCH_KEYWORDS)}")
    print(f"[INFO] Estimasi total artikel: ~{config.NUM_ARTICLES * len(config.SEARCH_KEYWORDS)}")

    df_news = pd.DataFrame()
    if config.NEWS_ENABLED:
        crawler = NewsCrawler()
        df_news = crawler.crawl_news(config.SEARCH_KEYWORDS, config.NUM_ARTICLES)

        if not df_news.empty:
            raw_news_path = 'data/raw_news.csv'
            crawler.save_to_csv(df_news, raw_news_path)
        else:
            # Load existing data if crawling failed
            raw_news_path = 'data/raw_news.csv'
            if os.path.exists(raw_news_path):
                print(f"[INFO] Loading existing news data from {raw_news_path}")
                df_news = pd.read_csv(raw_news_path, encoding='utf-8-sig')
                print(f"[INFO] Loaded {len(df_news)} existing news articles")
            else:
                print("[WARNING] No news data available")
    else:
        print("[INFO] News crawling disabled in config")
        # Load existing data
        raw_news_path = 'data/raw_news.csv'
        if os.path.exists(raw_news_path):
            print(f"[INFO] Loading existing news data from {raw_news_path}")
            df_news = pd.read_csv(raw_news_path, encoding='utf-8-sig')
            print(f"[INFO] Loaded {len(df_news)} existing news articles")
        else:
            print("[WARNING] No existing news data found")
    
    # 1B. Crawl YouTube (Optional)
    df_youtube = pd.DataFrame()
    if config.YOUTUBE_ENABLED and config.YOUTUBE_API_KEY != "YOUR_YOUTUBE_API_KEY_HERE":
        print("\n[1B] CRAWLING YOUTUBE COMMENTS")
        print("-"*70)
        print(f"[INFO] API Key: {config.YOUTUBE_API_KEY[:20]}...")
        print(f"[INFO] Target: {config.YOUTUBE_MAX_VIDEOS} video per keyword")
        print(f"[INFO] Target: {config.YOUTUBE_MAX_COMMENTS} komentar per video")
        print(f"[INFO] Estimasi total: ~{config.YOUTUBE_MAX_VIDEOS * len(config.YOUTUBE_KEYWORDS) * config.YOUTUBE_MAX_COMMENTS} komentar")
        
        try:
            from youtube_scraper import YouTubeScraper
            
            youtube_crawler = YouTubeScraper(api_key=config.YOUTUBE_API_KEY)
            df_youtube = youtube_crawler.crawl_comments(
                config.YOUTUBE_KEYWORDS, 
                max_videos=config.YOUTUBE_MAX_VIDEOS,
                max_comments_per_video=config.YOUTUBE_MAX_COMMENTS
            )
            
            if not df_youtube.empty:
                raw_youtube_path = 'data/raw_youtube.csv'
                youtube_crawler.save_to_csv(df_youtube, raw_youtube_path)

                print(f"\n[SUCCESS] Total YouTube comments: {len(df_youtube)}")
            else:
                print("\n[WARNING] Tidak ada YouTube comments yang berhasil di-crawl")
                # Load existing data if available
                raw_youtube_path = 'data/raw_youtube.csv'
                if os.path.exists(raw_youtube_path):
                    print(f"[INFO] Loading existing YouTube data from {raw_youtube_path}")
                    df_youtube = pd.read_csv(raw_youtube_path, encoding='utf-8-sig')
                    print(f"[INFO] Loaded {len(df_youtube)} existing YouTube comments")
                else:
                    print("[WARNING] No existing YouTube data found")
        
        except ImportError:
            print("[ERROR] google-api-python-client tidak terinstall")
            print("[INFO] Install dengan: pip install google-api-python-client")
        except Exception as e:
            print(f"[WARNING] Gagal crawl YouTube: {str(e)}")
            print("[INFO] Melanjutkan dengan data berita saja...")
    else:
        if not config.YOUTUBE_ENABLED:
            print("\n[1B] YouTube crawling DISABLED (config.YOUTUBE_ENABLED = False)")
        else:
            print("\n[1B] YouTube crawling SKIPPED (API Key tidak diset)")
    
    # Gabungkan data berita dan YouTube
    if not df_youtube.empty and not df_news.empty:
        # Standarisasi kolom
        df_youtube['title'] = df_youtube['content'].str[:100] + '...'

        # Kolom yang sama - dengan validasi
        required_columns = ['title', 'content', 'date', 'source', 'url', 'keyword', 'crawled_at']
        if all(col in df_news.columns for col in required_columns):
            df_news_std = df_news[required_columns]

            # YouTube: rename kolom untuk match
            df_youtube_std = df_youtube.copy()
            df_youtube_std['url'] = df_youtube_std['video_id']  # Pakai video_id sebagai URL
            df_youtube_std = df_youtube_std[['title', 'content', 'published_at', 'source', 'url', 'keyword', 'crawled_at']]
            df_youtube_std = df_youtube_std.rename(columns={'published_at': 'date'})

            df_raw = pd.concat([df_news_std, df_youtube_std], ignore_index=True)
            print(f"\n[INFO] Total data gabungan: {len(df_raw)} (Berita: {len(df_news)} + YouTube: {len(df_youtube)})")
        else:
            print(f"\n[WARNING] Kolom yang diperlukan tidak ada di df_news. Kolom tersedia: {list(df_news.columns)}")
            df_raw = df_youtube.copy()
            df_raw['title'] = df_raw['content'].str[:100] + '...'
            df_raw = df_raw.rename(columns={'published_at': 'date'})
            print(f"\n[INFO] Total data: {len(df_raw)} (YouTube saja)")
    elif not df_news.empty:
        # Validasi kolom df_news
        required_columns = ['title', 'content', 'date', 'source', 'url', 'keyword', 'crawled_at']
        if all(col in df_news.columns for col in required_columns):
            df_raw = df_news.copy()
            print(f"\n[INFO] Total data: {len(df_raw)} (Berita saja)")
        else:
            print(f"\n[ERROR] Kolom yang diperlukan tidak ada di df_news. Kolom tersedia: {list(df_news.columns)}")
            print("[ERROR] Tidak ada data yang valid. Program dihentikan.")
            return
    else:
        if not df_youtube.empty:
            df_raw = df_youtube.copy()
            df_raw['title'] = df_raw['content'].str[:100] + '...'
            df_raw = df_raw.rename(columns={'published_at': 'date'})
            print(f"\n[INFO] Total data: {len(df_raw)} (YouTube saja)")
        else:
            print("\n[ERROR] Tidak ada data berita atau YouTube yang berhasil di-crawl. Program dihentikan.")
            return
    
    if df_raw.empty:
        print("\n[ERROR] Tidak ada data yang berhasil di-crawl. Program dihentikan.")
        return
    
    # Simpan raw data gabungan
    raw_data_path = 'data/raw_data.csv'
    df_raw.to_csv(raw_data_path, index=False, encoding='utf-8-sig')
    print(f"[SAVE] Data mentah gabungan disimpan ke: {raw_data_path}")
    
    # ===== TAHAP 2: PREPROCESSING TEKS =====
    print("\n" + "="*70)
    print("TAHAP 2: DATA CLEANING & PREPROCESSING")
    print("="*70)
    
    # 2A. Data Cleaning (BARU!)
    from data_cleaner import DataCleaner
    
    cleaner = DataCleaner()
    df_cleaned = cleaner.clean_data(df_raw)
    
    # 2B. Text Preprocessing
    preprocessor = TextPreprocessor()
    df_processed = preprocessor.preprocess_dataframe(df_cleaned)
    
    # ===== TAHAP 3: ANALISIS SENTIMEN =====
    print("\n" + "="*70)
    print("TAHAP 3: ANALISIS SENTIMEN")
    print("="*70)
    
    analyzer = IndoBERTSentimentAnalyzer()
    df_final = analyzer.analyze_dataframe(df_processed)
    
    # Simpan processed data
    processed_data_path = 'data/processed_data.csv'
    df_final.to_csv(processed_data_path, index=False, encoding='utf-8-sig')
    print(f"[SAVE] Data hasil analisis disimpan ke: {processed_data_path}")
    
    # ===== TAHAP 4: RINGKASAN HASIL =====
    print("\n" + "="*70)
    print("RINGKASAN HASIL ANALISIS")
    print("="*70)
    
    summary = analyzer.get_sentiment_summary(df_final)
    
    if summary:
        print(f"\n{'='*70}")
        print("DISTRIBUSI SENTIMEN")
        print("="*70)
        print(f"Jumlah Positif : {summary['positive']}")
        print(f"Jumlah Negatif : {summary['negative']}")
        print(f"Jumlah Netral  : {summary['neutral']}")
        print(f"\nTotal Artikel  : {summary['total']}")
        
        print(f"\n{'='*70}")
        print("DISTRIBUSI OPINI (SETUJU vs TIDAK SETUJU)")
        print("="*70)
        print(f"Setuju (Mendukung)    : {summary['setuju']} ({summary['setuju_pct']:.1f}%)")
        print(f"Tidak Setuju (Menolak): {summary['tidak_setuju']} ({summary['tidak_setuju_pct']:.1f}%)")
        print(f"Netral                : {summary['neutral']} ({summary['neutral_pct']:.1f}%)")
        
        # Interpretasi
        print(f"\n{'='*70}")
        print("INTERPRETASI")
        print("="*70)
        
        if summary['setuju'] > summary['tidak_setuju']:
            print("[KESIMPULAN] Sentimen masyarakat cenderung POSITIF/SETUJU/MENDUKUNG")
            print("             naturalisasi pemain timnas Indonesia berdasarkan berita")
            print("             yang dianalisis.")
        elif summary['tidak_setuju'] > summary['setuju']:
            print("[KESIMPULAN] Sentimen masyarakat cenderung NEGATIF/TIDAK SETUJU/MENOLAK")
            print("             naturalisasi pemain timnas Indonesia berdasarkan berita")
            print("             yang dianalisis.")
        else:
            print("[KESIMPULAN] Sentimen masyarakat SEIMBANG antara setuju dan tidak setuju")
            print("             terhadap naturalisasi pemain timnas Indonesia.")
        
        # Prediksi tren
        predict_future_sentiment(summary)
    
    # ===== TAHAP 5: TRAINING MODEL PREDIKSI =====
    try:
        model, vectorizer = train_prediction_model(df_final)
    except Exception as e:
        print(f"[WARNING] Gagal training model: {str(e)}")
    
    # ===== TAHAP 6: VISUALISASI =====
    print("\n" + "="*70)
    print("TAHAP 6: VISUALISASI DATA")
    print("="*70)
    
    visualizer = SentimentVisualizer()
    visualizer.create_all_visualizations(df_final, show=True)
    
    # ===== TAHAP 7: SIMPAN KE MYSQL DATABASE (BARU!) =====
    print("\n" + "="*70)
    print("TAHAP 7: INTEGRASI DATABASE MYSQL")
    print("="*70)
    
    try:
        from mysql_integration import MySQLIntegration
        
        db = MySQLIntegration(
            host='localhost:8080',
            user='root',
            password='',  # Sesuaikan dengan password MySQL Anda
            database='sentiment_analysis'
        )
        
        if db.connect():
            # Insert raw data
            if not df_news.empty:
                db.insert_news_data(df_news)
            
            if not df_youtube.empty:
                db.insert_youtube_data(df_youtube)
            
            # Insert sentiment results
            db.insert_sentiment_results(df_final)
            
            # Update dashboard stats
            db.update_dashboard_stats() 
            db.update_sentiment_by_source()
            
            db.disconnect()
            
            print("\n[SUCCESS] Data berhasil disimpan ke MySQL!")
            print("[INFO] Buka browser: http://localhost:8080/sentiment_dashboard/")
        else:
            print("\n[WARNING] Gagal connect ke MySQL. Data hanya tersimpan di CSV.")
            print("[INFO] Pastikan XAMPP MySQL sudah running!")
    
    except ImportError:
        print("\n[WARNING] mysql-connector-python tidak terinstall.")
        print("[INFO] Install dengan: pip install mysql-connector-python")
    except Exception as e:
        print(f"\n[WARNING] Error MySQL integration: {str(e)}")
        print("[INFO] Data tetap tersimpan di CSV")
    
    # ===== TAHAP 8: ANALISIS PERBANDINGAN =====
    print("\n" + "="*70)
    print("TAHAP 8: ANALISIS PERBANDINGAN (BERITA vs YOUTUBE vs GABUNGAN)")
    print("="*70)

    if not df_youtube.empty:
        comparison_analyzer = ComparisonAnalyzer()
        comparison_result = comparison_analyzer.create_all_comparisons(df_final, show=True)

        # Simpan hasil perbandingan ke CSV
        comparison_df = pd.DataFrame(comparison_result).T
        comparison_csv_path = 'data/comparison_summary.csv'
        comparison_df.to_csv(comparison_csv_path, encoding='utf-8-sig')
        print(f"\n[SAVE] Ringkasan perbandingan disimpan ke: {comparison_csv_path}")
    else:
        print("[INFO] Hanya ada data berita, skip analisis perbandingan")
    
    # ===== SELESAI =====
    print("\n" + "="*70)
    print("PROSES SELESAI!")
    print("="*70)
    print("\n[OUTPUT] File yang dihasilkan:")
    print(f"  1. {raw_data_path} (Gabungan Berita + YouTube)")
    if not df_youtube.empty:
        print(f"  2. data/raw_news.csv (Berita saja)")
        print(f"  3. data/raw_youtube.csv (YouTube saja)")
        print(f"  4. {processed_data_path} (Data terproses)")
        print(f"  5. data/comparison_summary.csv (Ringkasan perbandingan)")
    else:
        print(f"  2. {processed_data_path} (Data terproses)")

    print(f"\n[VISUALISASI] Grafik yang dihasilkan:")
    print(f"  1. output/opinion_distribution.png (PIE: Setuju vs Tidak Setuju - Gabungan)")
    print(f"  2. output/sentiment_distribution.png (BAR: Distribusi sentimen)")
    print(f"  3. output/sentiment_by_source.png (BAR: Sentimen per media)")
    print(f"  4. output/sentiment_trend.png (LINE: Tren over time)")
    print(f"  5. output/wordcloud_positif.png (WORDCLOUD: Kata positif)")
    print(f"  6. output/wordcloud_negatif.png (WORDCLOUD: Kata negatif)")

    if not df_youtube.empty:
        print(f"\n[PERBANDINGAN] Grafik perbandingan YouTube vs Berita:")
        print(f"  7. output/comparison_bar_chart.png (BAR: Perbandingan jumlah)")
        print(f"  8. output/comparison_pie_charts.png (PIE: 3 pie side-by-side)")
        print(f"  9. output/comparison_percentage.png (STACKED BAR: Persentase)")
    print("\n[INFO] Terima kasih telah menggunakan program ini!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Program dihentikan oleh user.")
    except Exception as e:
        print(f"\n\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()