# visualizer.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os
import numpy as np

class SentimentVisualizer:
    def __init__(self, output_dir='output'):
        self.output_dir = output_dir
        
        # Buat folder output jika belum ada
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Set style untuk visualisasi
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
    
    def plot_opinion_distribution(self, df, show=True):
        """
        Membuat diagram PIE untuk distribusi opini Setuju vs Tidak Setuju
        
        Args:
            df: DataFrame dengan kolom 'opinion'
            show: Apakah menampilkan plot
        """
        if 'opinion' not in df.columns:
            print("[ERROR] Kolom 'opinion' tidak ditemukan!")
            return
        
        opinion_counts = df['opinion'].value_counts()
        
        # Filter hanya Setuju dan Tidak Setuju
        filtered_counts = {}
        if 'Setuju' in opinion_counts.index:
            filtered_counts['Setuju'] = opinion_counts['Setuju']
        if 'Tidak Setuju' in opinion_counts.index:
            filtered_counts['Tidak Setuju'] = opinion_counts['Tidak Setuju']
        
        if not filtered_counts:
            print("[WARNING] Tidak ada data opini untuk divisualisasikan")
            return
        
        # Buat plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = ['#2ecc71', '#e74c3c']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(
            filtered_counts.values(),
            labels=filtered_counts.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=explode,
            shadow=True,
            textprops={'fontsize': 14, 'weight': 'bold'}
        )
        
        # Styling
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(16)
            autotext.set_weight('bold')
        
        ax.set_title('Distribusi Opini Masyarakat:\nSetuju vs Tidak Setuju Naturalisasi Pemain Timnas', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Tambahkan legend dengan jumlah
        legend_labels = [f"{label}: {count}" for label, count in filtered_counts.items()]
        ax.legend(legend_labels, loc='best', fontsize=12)
        
        plt.tight_layout()
        
        # Simpan plot
        filepath = os.path.join(self.output_dir, 'opinion_distribution.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"[SAVE] Grafik distribusi opini disimpan ke: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_sentiment_distribution(self, df, show=True):
        """
        Membuat diagram batang distribusi sentimen
        
        Args:
            df: DataFrame dengan kolom 'sentiment'
            show: Apakah menampilkan plot
        """
        if 'sentiment' not in df.columns:
            print("[ERROR] Kolom 'sentiment' tidak ditemukan!")
            return
        
        sentiment_counts = df['sentiment'].value_counts()
        
        # Urutkan: Positif, Netral, Negatif
        order = ['Positif', 'Netral', 'Negatif']
        sentiment_counts = sentiment_counts.reindex(order, fill_value=0)
        
        # Buat plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['#2ecc71', '#95a5a6', '#e74c3c']
        bars = ax.bar(sentiment_counts.index, sentiment_counts.values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
        
        # Tambahkan label pada batang
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}\n({height/len(df)*100:.1f}%)',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax.set_xlabel('Kategori Sentimen', fontsize=12, fontweight='bold')
        ax.set_ylabel('Jumlah Artikel', fontsize=12, fontweight='bold')
        ax.set_title('Distribusi Sentimen Berita Naturalisasi Pemain Timnas Indonesia', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Simpan plot
        filepath = os.path.join(self.output_dir, 'sentiment_distribution.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"[SAVE] Grafik distribusi sentimen disimpan ke: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_sentiment_by_source(self, df, show=True, top_n=10):
        """
        Membuat diagram batang sentimen berdasarkan sumber berita
        
        Args:
            df: DataFrame dengan kolom 'source' dan 'sentiment'
            show: Apakah menampilkan plot
            top_n: Jumlah sumber teratas yang ditampilkan
        """
        if 'source' not in df.columns or 'sentiment' not in df.columns:
            print("[ERROR] Kolom 'source' atau 'sentiment' tidak ditemukan!")
            return
        
        # Ambil top N sumber dengan artikel terbanyak
        top_sources = df['source'].value_counts().head(top_n).index
        df_filtered = df[df['source'].isin(top_sources)]
        
        # Hitung sentimen per sumber
        sentiment_by_source = pd.crosstab(df_filtered['source'], df_filtered['sentiment'])
        
        # Urutkan berdasarkan total artikel
        sentiment_by_source['total'] = sentiment_by_source.sum(axis=1)
        sentiment_by_source = sentiment_by_source.sort_values('total', ascending=False)
        sentiment_by_source = sentiment_by_source.drop('total', axis=1)
        
        # Pastikan kolom dalam urutan yang benar
        for col in ['Positif', 'Netral', 'Negatif']:
            if col not in sentiment_by_source.columns:
                sentiment_by_source[col] = 0
        
        sentiment_by_source = sentiment_by_source[['Positif', 'Netral', 'Negatif']]
        
        # Buat plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        sentiment_by_source.plot(kind='barh', stacked=False, ax=ax, 
                                color=['#2ecc71', '#95a5a6', '#e74c3c'], alpha=0.8, width=0.7)
        
        ax.set_xlabel('Jumlah Artikel', fontsize=12, fontweight='bold')
        ax.set_ylabel('Sumber Berita', fontsize=12, fontweight='bold')
        ax.set_title(f'Distribusi Sentimen Berdasarkan Sumber Berita (Top {top_n})', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(title='Sentimen', loc='best', fontsize=10)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        # Simpan plot
        filepath = os.path.join(self.output_dir, 'sentiment_by_source.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"[SAVE] Grafik sentimen per sumber disimpan ke: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_sentiment_trend(self, df, show=True):
        """
        Membuat grafik tren sentimen berdasarkan waktu
        
        Args:
            df: DataFrame dengan kolom 'date' dan 'sentiment'
            show: Apakah menampilkan plot
        """
        if 'date' not in df.columns or 'sentiment' not in df.columns:
            print("[WARNING] Kolom 'date' atau 'sentiment' tidak ditemukan, skip tren")
            return
        
        try:
            # Convert date to datetime
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
            df_with_date = df.dropna(subset=['date_parsed'])
            
            if len(df_with_date) < 10:
                print("[WARNING] Data tanggal terlalu sedikit untuk membuat tren")
                return
            
            # Group by date and sentiment
            df_with_date['date_only'] = df_with_date['date_parsed'].dt.date
            sentiment_over_time = df_with_date.groupby(['date_only', 'sentiment']).size().unstack(fill_value=0)
            
            # Plot
            fig, ax = plt.subplots(figsize=(14, 6))
            
            if 'Positif' in sentiment_over_time.columns:
                ax.plot(sentiment_over_time.index, sentiment_over_time['Positif'], 
                       marker='o', label='Positif', color='#2ecc71', linewidth=2)
            if 'Negatif' in sentiment_over_time.columns:
                ax.plot(sentiment_over_time.index, sentiment_over_time['Negatif'], 
                       marker='s', label='Negatif', color='#e74c3c', linewidth=2)
            if 'Netral' in sentiment_over_time.columns:
                ax.plot(sentiment_over_time.index, sentiment_over_time['Netral'], 
                       marker='^', label='Netral', color='#95a5a6', linewidth=2)
            
            ax.set_xlabel('Tanggal', fontsize=12, fontweight='bold')
            ax.set_ylabel('Jumlah Artikel', fontsize=12, fontweight='bold')
            ax.set_title('Tren Sentimen Berita Naturalisasi Pemain Timnas Over Time', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            
            # Simpan plot
            filepath = os.path.join(self.output_dir, 'sentiment_trend.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"[SAVE] Grafik tren sentimen disimpan ke: {filepath}")
            
            if show:
                plt.show()
            else:
                plt.close()
        
        except Exception as e:
            print(f"[ERROR] Gagal membuat grafik tren: {str(e)}")
    
    def create_wordcloud(self, df, sentiment_type, show=True):
        """
        Membuat wordcloud untuk sentimen tertentu
        
        Args:
            df: DataFrame dengan kolom 'sentiment' dan 'processed_text'
            sentiment_type: 'Positif' atau 'Negatif'
            show: Apakah menampilkan plot
        """
        if 'sentiment' not in df.columns or 'processed_text' not in df.columns:
            print("[ERROR] Kolom 'sentiment' atau 'processed_text' tidak ditemukan!")
            return
        
        # Filter berdasarkan sentimen
        df_filtered = df[df['sentiment'] == sentiment_type]
        
        if len(df_filtered) == 0:
            print(f"[WARNING] Tidak ada artikel dengan sentimen {sentiment_type}")
            return
        
        # Gabungkan semua teks
        text = ' '.join(df_filtered['processed_text'].astype(str))
        
        if not text.strip():
            print(f"[WARNING] Tidak ada teks untuk sentimen {sentiment_type}")
            return
        
        # Buat wordcloud
        wordcloud = WordCloud(
            width=1600, 
            height=800, 
            background_color='white',
            colormap='Greens' if sentiment_type == 'Positif' else 'Reds',
            max_words=100,
            relative_scaling=0.5,
            min_font_size=10
        ).generate(text)
        
        # Plot
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f'Word Cloud - Sentimen {sentiment_type}', 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Simpan plot
        filename = f'wordcloud_{sentiment_type.lower()}.png'
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"[SAVE] Word cloud {sentiment_type} disimpan ke: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def create_all_visualizations(self, df, show=True):
        """
        Membuat semua visualisasi sekaligus
        
        Args:
            df: DataFrame hasil analisis sentimen
            show: Apakah menampilkan plot
        """
        print("\n[INFO] Membuat visualisasi...")
        
        # 1. Distribusi opini (Setuju vs Tidak Setuju) - PRIORITAS
        self.plot_opinion_distribution(df, show=show)
        
        # 2. Distribusi sentimen
        self.plot_sentiment_distribution(df, show=show)
        
        # 3. Sentimen per sumber
        self.plot_sentiment_by_source(df, show=show)
        
        # 4. Tren sentimen
        self.plot_sentiment_trend(df, show=show)
        
        # 5. Word cloud positif
        self.create_wordcloud(df, 'Positif', show=show)
        
        # 6. Word cloud negatif
        self.create_wordcloud(df, 'Negatif', show=show)
        
        print("[SUCCESS] Semua visualisasi berhasil dibuat!")


def main():
    """Testing visualizer"""
    # Buat data dummy untuk testing
    import numpy as np
    
    np.random.seed(42)
    
    dummy_data = {
        'title': [f'Artikel {i}' for i in range(100)],
        'sentiment': np.random.choice(['Positif', 'Negatif', 'Netral'], 100, p=[0.4, 0.3, 0.3]),
        'opinion': np.random.choice(['Setuju', 'Tidak Setuju', 'Netral'], 100, p=[0.45, 0.35, 0.2]),
        'source': np.random.choice(['Detik', 'Kompas', 'Tribun', 'CNN Indonesia', 'Bola.com'], 100),
        'processed_text': [
            'dukung natural kuat tingkat prestasi bagus' if s == 'Positif' 
            else 'tolak kontra lemah gagal masalah' if s == 'Negatif'
            else 'main bola latih fisik teknik'
            for s in np.random.choice(['Positif', 'Negatif', 'Netral'], 100, p=[0.4, 0.3, 0.3])
        ]
    }
    
    df = pd.DataFrame(dummy_data)
    
    visualizer = SentimentVisualizer()
    visualizer.create_all_visualizations(df, show=True)


if __name__ == "__main__":
    main()