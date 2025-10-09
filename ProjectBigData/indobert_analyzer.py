# indobert_analyzer.py

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from tqdm import tqdm

class IndoBERTSentimentAnalyzer:
    def __init__(self, model_name='indolem/indobert-base-uncased'):
        """
        Initialize IndoBERT model untuk sentiment analysis
        
        Args:
            model_name: Nama model Hugging Face
        """
        print("[INFO] Loading IndoBERT model...")
        print(f"[INFO] Model: {model_name}")
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"[INFO] Using device: {self.device}")
        
        # Load tokenizer dan model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Kita akan membuat classifier sederhana
        # Atau gunakan model pre-trained sentiment jika ada
        try:
            # Coba load model sentiment yang sudah di-fine-tune
            self.model = AutoModelForSequenceClassification.from_pretrained(
                'w11wo/indonesian-roberta-base-sentiment-classifier'
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                'w11wo/indonesian-roberta-base-sentiment-classifier'
            )
            print("[INFO] Loaded pre-trained sentiment model")
        except:
            # Fallback ke IndoBERT base
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=3  # Positif, Negatif, Netral
            )
            print("[INFO] Using base IndoBERT model")
        
        self.model.to(self.device)
        self.model.eval()
        
        # Label mapping
        self.label_map = {0: 'Negatif', 1: 'Netral', 2: 'Positif'}
        
        print("[SUCCESS] Model loaded successfully!")
    
    def predict_sentiment(self, text, max_length=512):
        """
        Prediksi sentimen untuk satu teks
        
        Args:
            text: Teks yang akan dianalisis
            max_length: Panjang maksimal token
        
        Returns:
            dict dengan sentiment, confidence, dan probabilities
        """
        if not isinstance(text, str) or not text.strip():
            return {
                'sentiment': 'Netral',
                'confidence': 0.0,
                'probabilities': {'Positif': 0.33, 'Negatif': 0.33, 'Netral': 0.34}
            }
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            max_length=max_length,
            padding='max_length'
        ).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        
        # Get prediction
        pred_label = np.argmax(probs)
        sentiment = self.label_map.get(pred_label, 'Netral')
        confidence = float(probs[pred_label])
        
        # Probabilities dict
        probabilities = {
            'Positif': float(probs[2]) if len(probs) > 2 else float(probs[1]),
            'Negatif': float(probs[0]),
            'Netral': float(probs[1]) if len(probs) > 2 else 0.0
        }
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'probabilities': probabilities
        }
    
    def analyze_dataframe(self, df, text_column='content', batch_size=16):
        """
        Analisis sentimen untuk DataFrame
        
        Args:
            df: DataFrame dengan kolom text
            text_column: Nama kolom yang berisi teks
            batch_size: Ukuran batch untuk processing
        
        Returns:
            DataFrame dengan kolom sentimen tambahan
        """
        print("[INFO] Memulai analisis sentimen dengan IndoBERT...")
        print(f"[INFO] Total data: {len(df)}")
        
        if text_column not in df.columns:
            print(f"[ERROR] Kolom '{text_column}' tidak ditemukan!")
            return df
        
        results = []
        
        # Process dengan progress bar
        for idx, text in tqdm(enumerate(df[text_column]), total=len(df), desc="Analyzing"):
            result = self.predict_sentiment(str(text))
            results.append(result)
        
        # Tambahkan hasil ke DataFrame
        df['sentiment'] = [r['sentiment'] for r in results]
        df['sentiment_confidence'] = [r['confidence'] for r in results]
        df['prob_positif'] = [r['probabilities']['Positif'] for r in results]
        df['prob_negatif'] = [r['probabilities']['Negatif'] for r in results]
        df['prob_netral'] = [r['probabilities']['Netral'] for r in results]
        
        # Tentukan opinion berdasarkan sentimen
        df['opinion'] = df['sentiment'].apply(self.get_opinion_label)
        
        # Print distribusi
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
        
        print(f"\n[SUCCESS] Analisis selesai untuk {len(df)} data")
        
        return df
    
    def get_opinion_label(self, sentiment):
        """Konversi sentimen ke opini"""
        if sentiment == 'Positif':
            return 'Setuju'
        elif sentiment == 'Negatif':
            return 'Tidak Setuju'
        else:
            return 'Netral'
    
    def get_sentiment_summary(self, df):
        """Dapatkan ringkasan statistik sentimen"""
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
        
        # Hitung average confidence
        avg_confidence = df['sentiment_confidence'].mean() if 'sentiment_confidence' in df.columns else 0
        
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
            'tidak_setuju_pct': (tidak_setuju / total * 100) if total > 0 else 0,
            'avg_confidence': avg_confidence
        }


def main():
    """Testing IndoBERT analyzer"""
    print("="*70)
    print("TESTING INDOBERT SENTIMENT ANALYZER")
    print("="*70)
    
    # Initialize
    analyzer = IndoBERTSentimentAnalyzer()
    
    # Test texts
    test_texts = [
        "Naturalisasi pemain timnas Indonesia sangat bagus untuk meningkatkan prestasi!",
        "Saya tidak setuju dengan naturalisasi pemain asing untuk timnas",
        "Pemain timnas Indonesia berlatih di stadion"
    ]
    
    print("\n[TEST] Testing sentimen analysis:\n")
    
    for text in test_texts:
        result = analyzer.predict_sentiment(text)
        print(f"Teks: {text}")
        print(f"Sentimen: {result['sentiment']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Probabilities: {result['probabilities']}")
        print("-" * 70)


if __name__ == "__main__":
    main()