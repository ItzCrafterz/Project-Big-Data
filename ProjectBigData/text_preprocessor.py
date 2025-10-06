# text_preprocessor.py
import re
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import config

class TextPreprocessor:
    def __init__(self):
        # Inisialisasi Sastrawi stemmer
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()
        
        # Inisialisasi stopword remover
        stop_factory = StopWordRemoverFactory()
        self.stopword_remover = stop_factory.create_stop_word_remover()
        
        # Tambahkan stopwords domain-specific
        self.additional_stopwords = set(config.DOMAIN_STOPWORDS)
    
    def clean_text(self, text):
        """
        Membersihkan teks dari URL, mention, hashtag, angka, dan karakter spesial
        
        Args:
            text: Teks yang akan dibersihkan
        
        Returns:
            Teks yang sudah dibersihkan
        """
        if not isinstance(text, str):
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Hapus URL
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Hapus mention dan hashtag
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Hapus angka
        text = re.sub(r'\d+', '', text)
        
        # Hapus karakter spesial dan tanda baca, simpan hanya huruf dan spasi
        text = re.sub(r'[^a-z\s]', ' ', text)
        
        # Hapus whitespace berlebih
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_stopwords(self, text):
        """
        Menghapus stopwords bahasa Indonesia
        
        Args:
            text: Teks yang akan diproses
        
        Returns:
            Teks tanpa stopwords
        """
        # Gunakan Sastrawi stopword remover
        text = self.stopword_remover.remove(text)
        
        # Hapus stopwords tambahan
        words = text.split()
        words = [word for word in words if word not in self.additional_stopwords]
        
        return ' '.join(words)
    
    def stem_text(self, text):
        """
        Melakukan stemming dengan Sastrawi
        
        Args:
            text: Teks yang akan di-stem
        
        Returns:
            Teks hasil stemming
        """
        return self.stemmer.stem(text)
    
    def preprocess(self, text):
        """
        Pipeline preprocessing lengkap
        
        Args:
            text: Teks mentah
        
        Returns:
            Teks hasil preprocessing
        """
        # 1. Bersihkan teks
        text = self.clean_text(text)
        
        # 2. Hapus stopwords
        text = self.remove_stopwords(text)
        
        # 3. Stemming
        text = self.stem_text(text)
        
        return text
    
    def preprocess_dataframe(self, df):
        """
        Melakukan preprocessing pada DataFrame
        
        Args:
            df: DataFrame dengan kolom 'content'
        
        Returns:
            DataFrame dengan kolom 'processed_text' tambahan
        """
        print("[INFO] Memulai preprocessing teks...")
        
        if 'content' not in df.columns:
            print("[ERROR] Kolom 'content' tidak ditemukan!")
            return df
        
        # Apply preprocessing ke setiap baris
        df['processed_text'] = df['content'].apply(self.preprocess)
        
        # Hapus baris dengan teks kosong setelah preprocessing
        df = df[df['processed_text'].str.strip() != '']
        
        print(f"[SUCCESS] Preprocessing selesai untuk {len(df)} artikel")
        
        return df


def main():
    """Testing preprocessing"""
    # Contoh teks
    sample_text = """
    Naturalisasi pemain sepak bola untuk Timnas Indonesia menuai pro dan kontra! 
    Beberapa netizen mendukung keputusan ini karena dapat meningkatkan kualitas tim
    Link: https://example.com/berita @user123 #TimnasIndonesia
    """
    
    preprocessor = TextPreprocessor()
    
    print("Teks asli:")
    print(sample_text)
    print("\n" + "="*50 + "\n")
    
    print("Hasil preprocessing lengkap:")
    final = preprocessor.preprocess(sample_text)
    print(final)


if __name__ == "__main__":
    main()