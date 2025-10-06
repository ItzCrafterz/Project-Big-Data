# lexicon_analyzer.py
import pandas as pd
import config

class LexiconSentimentAnalyzer:
    def __init__(self):
        # Load kamus kata positif dan negatif
        self.positive_words = set([word.lower() for word in config.POSITIVE_WORDS])
        self.negative_words = set([word.lower() for word in config.NEGATIVE_WORDS])
        
        print(f"[INFO] Loaded {len(self.positive_words)} kata positif")
        print(f"[INFO] Loaded {len(self.negative_words)} kata negatif")
    
    def calculate_sentiment_score(self, text):
        """
        Menghitung skor sentimen berdasarkan jumlah kata positif dan negatif
        
        Args:
            text: Teks yang sudah di-preprocessing
        
        Returns:
            dict dengan positive_count, negative_count, dan sentiment_score
        """
        if not isinstance(text, str) or text.strip() == '':
            return {
                'positive_count': 0,
                'negative_count': 0,
                'sentiment_score': 0
            }
        
        words = text.lower().split()
        
        # Hitung kata positif dan negatif
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Skor sentimen = jumlah positif - jumlah negatif
        sentiment_score = positive_count - negative_count
        
        return {
            'positive_count': positive_count,
            'negative_count': negative_count,
            'sentiment_score': sentiment_score
        }
    
    def classify_sentiment(self, sentiment_score):
        """
        Klasifikasi sentimen berdasarkan skor
        
        Args:
            sentiment_score: Skor sentimen (positif - negatif)
        
        Returns:
            Label sentimen: 'Positif', 'Negatif', atau 'Netral'
        """
        if sentiment_score > 0:
            return 'Positif'
        elif sentiment_score < 0:
            return 'Negatif'
        else:
            return 'Netral'
    
    def get_opinion_label(self, sentiment):
        """
        Konversi sentimen ke label opini (Setuju/Tidak Setuju)
        
        Args:
            sentiment: Label sentimen
        
        Returns:
            'Setuju' atau 'Tidak Setuju'
        """
        if sentiment == 'Positif':
            return 'Setuju'
        elif sentiment == 'Negatif':
            return 'Tidak Setuju'
        else:
            return 'Netral'
    
    def analyze_dataframe(self, df):
        """
        Melakukan analisis sentimen pada DataFrame
        
        Args:
            df: DataFrame dengan kolom 'processed_text'
        
        Returns:
            DataFrame dengan kolom sentimen tambahan
        """
        print("[INFO] Memulai analisis sentimen...")
        
        if 'processed_text' not in df.columns:
            print("[ERROR] Kolom 'processed_text' tidak ditemukan!")
            return df
        
        # Hitung skor sentimen untuk setiap baris
        sentiment_data = df['processed_text'].apply(self.calculate_sentiment_score)
        
        # Ekstrak hasil ke kolom terpisah
        df['positive_count'] = sentiment_data.apply(lambda x: x['positive_count'])
        df['negative_count'] = sentiment_data.apply(lambda x: x['negative_count'])
        df['sentiment_score'] = sentiment_data.apply(lambda x: x['sentiment_score'])
        
        # Klasifikasi sentimen
        df['sentiment'] = df['sentiment_score'].apply(self.classify_sentiment)
        
        # Tambahkan label opini (Setuju/Tidak Setuju)
        df['opinion'] = df['sentiment'].apply(self.get_opinion_label)
        
        # Hitung distribusi sentimen
        sentiment_dist = df['sentiment'].value_counts()
        opinion_dist = df['opinion'].value_counts()
        
        print("\n[RESULT] Distribusi Sentimen:")
        print(f"   Positif: {sentiment_dist.get('Positif', 0)}")
        print(f"   Negatif: {sentiment_dist.get('Negatif', 0)}")
        print(f"   Netral : {sentiment_dist.get('Netral', 0)}")
        
        print("\n[RESULT] Distribusi Opini:")
        print(f"   Setuju      : {opinion_dist.get('Setuju', 0)}")
        print(f"   Tidak Setuju: {opinion_dist.get('Tidak Setuju', 0)}")
        print(f"   Netral      : {opinion_dist.get('Netral', 0)}")
        
        print(f"\n[SUCCESS] Analisis sentimen selesai untuk {len(df)} artikel")
        
        return df
    
    def get_sentiment_summary(self, df):
        """
        Mendapatkan ringkasan sentimen
        
        Args:
            df: DataFrame hasil analisis
        
        Returns:
            Dictionary berisi statistik sentimen
        """
        if 'sentiment' not in df.columns or 'opinion' not in df.columns:
            return None
        
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        opinion_counts = df['opinion'].value_counts().to_dict()
        
        total = len(df)
        positive = sentiment_counts.get('Positif', 0)
        negative = sentiment_counts.get('Negatif', 0)
        neutral = sentiment_counts.get('Netral', 0)
        
        setuju = opinion_counts.get('Setuju', 0)
        tidak_setuju = opinion_counts.get('Tidak Setuju', 0)
        
        return {
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_pct': (positive / total * 100) if total > 0 else 0,
            'negative_pct': (negative / total * 100) if total > 0 else 0,
            'neutral_pct': (neutral / total * 100) if total > 0 else 0,
            'setuju': setuju,
            'tidak_setuju': tidak_setuju,
            'setuju_pct': (setuju / total * 100) if total > 0 else 0,
            'tidak_setuju_pct': (tidak_setuju / total * 100) if total > 0 else 0
        }


def main():
    """Testing sentiment analysis"""
    analyzer = LexiconSentimentAnalyzer()
    
    # Contoh teks setelah preprocessing
    test_texts = [
        "dukung natural kuat tingkat prestasi tanding",  # Positif
        "tolak kontra lemah gagal masalah kekalahan",      # Negatif
        "main bola latih fisik teknik"                     # Netral
    ]
    
    print("\n[TEST] Testing Analisis Sentimen:\n")
    
    for text in test_texts:
        result = analyzer.calculate_sentiment_score(text)
        sentiment = analyzer.classify_sentiment(result['sentiment_score'])
        opinion = analyzer.get_opinion_label(sentiment)
        
        print(f"Teks: {text}")
        print(f"Positif: {result['positive_count']}, Negatif: {result['negative_count']}")
        print(f"Skor: {result['sentiment_score']}")
        print(f"Sentimen: {sentiment} | Opini: {opinion}")
        print("-" * 50)


if __name__ == "__main__":
    main()