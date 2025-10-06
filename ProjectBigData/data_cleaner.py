# data_cleaner.py
import pandas as pd
import re

class DataCleaner:
    def __init__(self):
        # Kata-kata spam/irrelevant
        self.spam_keywords = [
            'subscribe', 'like', 'comment', 'share', 'link in bio',
            'check description', 'visit my channel', 'follow me',
            'giveaway', 'promo', 'diskon', 'beli sekarang',
            'jual', 'jualan', 'iklan', 'advertisement'
        ]
        
        # Minimum panjang text (karakter)
        self.min_length = 10
        
        # Maximum panjang text (untuk filter spam)
        self.max_length = 5000
    
    def is_spam(self, text):
        """
        Check apakah text adalah spam
        
        Args:
            text: Text yang akan dicek
        
        Returns:
            Boolean
        """
        if not isinstance(text, str):
            return True
        
        text_lower = text.lower()
        
        # Cek spam keywords
        spam_count = sum(1 for keyword in self.spam_keywords if keyword in text_lower)
        if spam_count >= 2:  # Jika ada 2+ spam keyword
            return True
        
        # Cek jika terlalu banyak emoji (spam)
        emoji_count = len(re.findall(r'[^\w\s,.]', text))
        if emoji_count > len(text) * 0.3:  # Jika >30% emoji
            return True
        
        # Cek jika terlalu banyak uppercase (SPAM)
        if len(re.findall(r'[A-Z]', text)) > len(text) * 0.7:
            return True
        
        # Cek jika terlalu banyak angka
        if len(re.findall(r'\d', text)) > len(text) * 0.5:
            return True
        
        return False
    
    def is_valid_length(self, text):
        """Check panjang text valid"""
        if not isinstance(text, str):
            return False
        
        length = len(text.strip())
        return self.min_length <= length <= self.max_length
    
    def remove_duplicates_advanced(self, df):
        """
        Hapus duplikat dengan metode advanced
        - Exact duplicate
        - Near duplicate (similarity >90%)
        """
        print("[CLEAN] Menghapus duplikat...")
        
        initial_count = len(df)
        
        # 1. Hapus exact duplicate
        df = df.drop_duplicates(subset=['content'], keep='first')
        
        # 2. Hapus near duplicate (optional, lambat untuk data besar)
        # Untuk sekarang skip, bisa ditambah nanti jika perlu
        
        removed = initial_count - len(df)
        print(f"[CLEAN] Dihapus {removed} duplikat")
        
        return df
    
    def remove_spam(self, df):
        """Hapus spam content"""
        print("[CLEAN] Menghapus spam...")

        initial_count = len(df)

        df = df.copy()
        df['is_spam'] = df['content'].apply(self.is_spam)
        df = df[df['is_spam'] == False]
        df = df.drop('is_spam', axis=1)

        removed = initial_count - len(df)
        print(f"[CLEAN] Dihapus {removed} spam")

        return df
    
    def remove_invalid_length(self, df):
        """Hapus content dengan panjang tidak valid"""
        print("[CLEAN] Menghapus content dengan panjang tidak valid...")

        initial_count = len(df)

        df = df.copy()
        df['is_valid_length'] = df['content'].apply(self.is_valid_length)
        df = df[df['is_valid_length'] == True]
        df = df.drop('is_valid_length', axis=1)

        removed = initial_count - len(df)
        print(f"[CLEAN] Dihapus {removed} content (terlalu pendek/panjang)")

        return df
    
    def remove_empty_processed(self, df):
        """Hapus row dengan processed_text kosong"""
        if 'processed_text' not in df.columns:
            return df
        
        print("[CLEAN] Menghapus row dengan processed_text kosong...")
        
        initial_count = len(df)
        
        df = df[df['processed_text'].notna()]
        df = df[df['processed_text'].str.strip() != '']
        
        removed = initial_count - len(df)
        print(f"[CLEAN] Dihapus {removed} row kosong")
        
        return df
    
    def clean_data(self, df):
        """
        Pipeline cleaning lengkap
        
        Args:
            df: DataFrame raw data
        
        Returns:
            DataFrame yang sudah bersih
        """
        print("\n" + "="*70)
        print("DATA CLEANING")
        print("="*70)
        
        initial_count = len(df)
        print(f"[INFO] Data awal: {initial_count} rows")
        
        # 1. Hapus duplikat
        df = self.remove_duplicates_advanced(df)
        
        # 2. Hapus spam
        df = self.remove_spam(df)
        
        # 3. Hapus invalid length
        df = self.remove_invalid_length(df)
        
        # 4. Reset index
        df = df.reset_index(drop=True)
        
        final_count = len(df)
        removed_total = initial_count - final_count
        removal_pct = (removed_total / initial_count * 100) if initial_count > 0 else 0
        
        print(f"\n[SUMMARY] Data akhir: {final_count} rows")
        print(f"[SUMMARY] Total dihapus: {removed_total} rows ({removal_pct:.1f}%)")
        print(f"[SUMMARY] Data retention: {100 - removal_pct:.1f}%")
        print("="*70 + "\n")
        
        return df


def main():
    """Testing data cleaner"""
    # Buat sample data dengan spam
    sample_data = {
        'content': [
            'Naturalisasi pemain timnas indonesia bagus untuk prestasi',
            'SUBSCRIBE MY CHANNEL NOW!!! LINK IN BIO!!!',
            'abc',  # Terlalu pendek
            'Naturalisasi pemain timnas indonesia bagus untuk prestasi',  # Duplicate
            'Saya setuju dengan naturalisasi pemain',
            '123456789012345678901234567890' * 100,  # Terlalu panjang
            'follow me instagram @spam link bio check',  # Spam
            'Pemain naturalisasi seperti Jay Idzes bagus'
        ],
        'source': ['News'] * 8
    }
    
    df = pd.DataFrame(sample_data)
    print(f"Data awal:\n{df}\n")
    
    cleaner = DataCleaner()
    df_clean = cleaner.clean_data(df)
    
    print(f"\nData setelah cleaning:\n{df_clean}")


if __name__ == "__main__":
    main()