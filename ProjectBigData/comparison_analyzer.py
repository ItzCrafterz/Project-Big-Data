# comparison_analyzer.py
"""
Analisis perbandingan antara Berita vs YouTube Comments
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


class ComparisonAnalyzer:
    def __init__(self, output_dir='output'):
        self.output_dir = output_dir
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (14, 8)
    
    def get_source_type_stats(self, df):
        """
        Ambil statistik per source type (News vs YouTube)
        
        Args:
            df: DataFrame dengan kolom 'source' dan 'sentiment'/'opinion'
        
        Returns:
            Dictionary berisi stats per source type
        """
        # Tentukan source_type
        df['source_type'] = df['source'].apply(
            lambda x: 'YouTube' if x == 'YouTube' else 'News'
        )
        
        stats = {}
        
        for source_type in ['News', 'YouTube']:
            df_filtered = df[df['source_type'] == source_type]
            
            if len(df_filtered) == 0:
                stats[source_type] = {
                    'total': 0,
                    'positif': 0,
                    'negatif': 0,
                    'netral': 0,
                    'setuju': 0,
                    'tidak_setuju': 0,
                    'positif_pct': 0,
                    'negatif_pct': 0,
                    'setuju_pct': 0,
                    'tidak_setuju_pct': 0
                }
                continue
            
            sentiment_counts = df_filtered['sentiment'].value_counts()
            opinion_counts = df_filtered['opinion'].value_counts()
            
            total = len(df_filtered)
            
            stats[source_type] = {
                'total': total,
                'positif': sentiment_counts.get('Positif', 0),
                'negatif': sentiment_counts.get('Negatif', 0),
                'netral': sentiment_counts.get('Netral', 0),
                'setuju': opinion_counts.get('Setuju', 0),
                'tidak_setuju': opinion_counts.get('Tidak Setuju', 0),
                'positif_pct': (sentiment_counts.get('Positif', 0) / total * 100),
                'negatif_pct': (sentiment_counts.get('Negatif', 0) / total * 100),
                'setuju_pct': (opinion_counts.get('Setuju', 0) / total * 100),
                'tidak_setuju_pct': (opinion_counts.get('Tidak Setuju', 0) / total * 100)
            }
        
        # Tambahkan gabungan
        stats['Gabungan'] = {
            'total': len(df),
            'positif': df['sentiment'].value_counts().get('Positif', 0),
            'negatif': df['sentiment'].value_counts().get('Negatif', 0),
            'netral': df['sentiment'].value_counts().get('Netral', 0),
            'setuju': df['opinion'].value_counts().get('Setuju', 0),
            'tidak_setuju': df['opinion'].value_counts().get('Tidak Setuju', 0)
        }
        
        total = len(df)
        stats['Gabungan']['positif_pct'] = stats['Gabungan']['positif'] / total * 100
        stats['Gabungan']['negatif_pct'] = stats['Gabungan']['negatif'] / total * 100
        stats['Gabungan']['setuju_pct'] = stats['Gabungan']['setuju'] / total * 100
        stats['Gabungan']['tidak_setuju_pct'] = stats['Gabungan']['tidak_setuju'] / total * 100
        
        return stats
    
    def plot_comparison_bar(self, stats, show=True):
        """
        Bar chart perbandingan jumlah absolut
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Chart 1: Sentimen
        categories = ['News', 'YouTube', 'Gabungan']
        positif_vals = [stats[cat]['positif'] for cat in categories]
        negatif_vals = [stats[cat]['negatif'] for cat in categories]
        netral_vals = [stats[cat]['netral'] for cat in categories]
        
        x = np.arange(len(categories))
        width = 0.25
        
        ax1.bar(x - width, positif_vals, width, label='Positif', color='#2ecc71', alpha=0.8)
        ax1.bar(x, negatif_vals, width, label='Negatif', color='#e74c3c', alpha=0.8)
        ax1.bar(x + width, netral_vals, width, label='Netral', color='#95a5a6', alpha=0.8)
        
        ax1.set_xlabel('Sumber', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Jumlah', fontsize=12, fontweight='bold')
        ax1.set_title('Perbandingan Sentimen (Jumlah Absolut)', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Chart 2: Opini
        setuju_vals = [stats[cat]['setuju'] for cat in categories]
        tidak_setuju_vals = [stats[cat]['tidak_setuju'] for cat in categories]
        
        ax2.bar(x - width/2, setuju_vals, width, label='Setuju', color='#2ecc71', alpha=0.8)
        ax2.bar(x + width/2, tidak_setuju_vals, width, label='Tidak Setuju', color='#e74c3c', alpha=0.8)
        
        ax2.set_xlabel('Sumber', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Jumlah', fontsize=12, fontweight='bold')
        ax2.set_title('Perbandingan Opini (Jumlah Absolut)', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, 'comparison_bar_chart.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"[SAVE] Grafik perbandingan bar disimpan ke: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_comparison_pie(self, stats, show=True):
        """
        3 Pie charts side-by-side untuk Setuju vs Tidak Setuju
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        categories = ['News', 'YouTube', 'Gabungan']
        colors = ['#2ecc71', '#e74c3c', '#95a5a6']
        
        for idx, cat in enumerate(categories):
            ax = axes[idx]
            
            setuju = stats[cat]['setuju']
            tidak_setuju = stats[cat]['tidak_setuju']
            netral = stats[cat]['netral']
            
            if setuju + tidak_setuju + netral == 0:
                ax.text(0.5, 0.5, 'Tidak ada data', ha='center', va='center', fontsize=14)
                ax.set_title(f'{cat}', fontsize=14, fontweight='bold')
                continue
            
            labels = ['Setuju', 'Tidak Setuju', 'Netral']
            sizes = [setuju, tidak_setuju, netral]
            
            # Filter size yang 0
            filtered_labels = []
            filtered_sizes = []
            filtered_colors = []
            for i, size in enumerate(sizes):
                if size > 0:
                    filtered_labels.append(labels[i])
                    filtered_sizes.append(size)
                    filtered_colors.append(colors[i])
            
            wedges, texts, autotexts = ax.pie(
                filtered_sizes,
                labels=filtered_labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=filtered_colors,
                explode=[0.05] * len(filtered_sizes),
                shadow=True,
                textprops={'fontsize': 11, 'weight': 'bold'}
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(12)
            
            ax.set_title(f'{cat}\n(Total: {stats[cat]["total"]})', 
                        fontsize=14, fontweight='bold', pad=20)
        
        plt.suptitle('Distribusi Opini: Setuju vs Tidak Setuju\n(Perbandingan News, YouTube, dan Gabungan)', 
                    fontsize=16, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, 'comparison_pie_charts.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"[SAVE] Grafik perbandingan pie disimpan ke: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def plot_comparison_percentage(self, stats, show=True):
        """
        Stacked bar chart persentase
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        categories = ['News', 'YouTube', 'Gabungan']
        
        setuju_pct = [stats[cat]['setuju_pct'] for cat in categories]
        tidak_setuju_pct = [stats[cat]['tidak_setuju_pct'] for cat in categories]
        netral_pct = [100 - stats[cat]['setuju_pct'] - stats[cat]['tidak_setuju_pct'] for cat in categories]
        
        x = np.arange(len(categories))
        width = 0.6
        
        p1 = ax.bar(x, setuju_pct, width, label='Setuju', color='#2ecc71', alpha=0.9)
        p2 = ax.bar(x, tidak_setuju_pct, width, bottom=setuju_pct, 
                   label='Tidak Setuju', color='#e74c3c', alpha=0.9)
        p3 = ax.bar(x, netral_pct, width, 
                   bottom=[setuju_pct[i] + tidak_setuju_pct[i] for i in range(len(categories))],
                   label='Netral', color='#95a5a6', alpha=0.9)
        
        # Tambahkan label persentase
        for i, cat in enumerate(categories):
            if setuju_pct[i] > 5:
                ax.text(i, setuju_pct[i]/2, f'{setuju_pct[i]:.1f}%', 
                       ha='center', va='center', fontweight='bold', color='white', fontsize=12)
            
            if tidak_setuju_pct[i] > 5:
                ax.text(i, setuju_pct[i] + tidak_setuju_pct[i]/2, f'{tidak_setuju_pct[i]:.1f}%',
                       ha='center', va='center', fontweight='bold', color='white', fontsize=12)
            
            if netral_pct[i] > 5:
                ax.text(i, setuju_pct[i] + tidak_setuju_pct[i] + netral_pct[i]/2, f'{netral_pct[i]:.1f}%',
                       ha='center', va='center', fontweight='bold', color='white', fontsize=12)
        
        ax.set_ylabel('Persentase (%)', fontsize=12, fontweight='bold')
        ax.set_title('Perbandingan Opini (Persentase)\nNews vs YouTube vs Gabungan', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', fontsize=11)
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, 'comparison_percentage.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"[SAVE] Grafik perbandingan persentase disimpan ke: {filepath}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def print_comparison_summary(self, stats):
        """
        Print ringkasan perbandingan ke console
        """
        print("\n" + "="*80)
        print("RINGKASAN PERBANDINGAN: NEWS vs YOUTUBE vs GABUNGAN")
        print("="*80)
        
        for cat in ['News', 'YouTube', 'Gabungan']:
            print(f"\n{cat.upper()}")
            print("-" * 80)
            print(f"Total Data        : {stats[cat]['total']}")
            print(f"\nSentimen:")
            print(f"  Positif         : {stats[cat]['positif']} ({stats[cat]['positif_pct']:.1f}%)")
            print(f"  Negatif         : {stats[cat]['negatif']} ({stats[cat]['negatif_pct']:.1f}%)")
            print(f"  Netral          : {stats[cat]['netral']}")
            print(f"\nOpini:")
            print(f"  Setuju          : {stats[cat]['setuju']} ({stats[cat]['setuju_pct']:.1f}%)")
            print(f"  Tidak Setuju    : {stats[cat]['tidak_setuju']} ({stats[cat]['tidak_setuju_pct']:.1f}%)")
        
        # Analisis perbedaan
        print("\n" + "="*80)
        print("ANALISIS PERBEDAAN")
        print("="*80)
        
        if stats['News']['total'] > 0 and stats['YouTube']['total'] > 0:
            diff_setuju = stats['News']['setuju_pct'] - stats['YouTube']['setuju_pct']
            diff_tidak_setuju = stats['News']['tidak_setuju_pct'] - stats['YouTube']['tidak_setuju_pct']
            
            print(f"\nSelisih Opini Setuju (News - YouTube): {diff_setuju:+.1f}%")
            print(f"Selisih Opini Tidak Setuju (News - YouTube): {diff_tidak_setuju:+.1f}%")
            
            if abs(diff_setuju) < 5:
                print("\n[KESIMPULAN] Sentimen News dan YouTube relatif SEIMBANG")
            elif diff_setuju > 0:
                print(f"\n[KESIMPULAN] News lebih POSITIF/SETUJU dibanding YouTube ({abs(diff_setuju):.1f}% lebih tinggi)")
            else:
                print(f"\n[KESIMPULAN] YouTube lebih POSITIF/SETUJU dibanding News ({abs(diff_setuju):.1f}% lebih tinggi)")
        else:
            if stats['News']['total'] == 0:
                print("\n[WARNING] Tidak ada data News untuk dibandingkan")
            if stats['YouTube']['total'] == 0:
                print("\n[WARNING] Tidak ada data YouTube untuk dibandingkan")
        
        print("="*80 + "\n")
    
    def create_all_comparisons(self, df, show=True):
        """
        Buat semua visualisasi perbandingan
        
        Args:
            df: DataFrame dengan kolom 'source', 'sentiment', 'opinion'
            show: Apakah menampilkan plot
        
        Returns:
            Dictionary statistik perbandingan
        """
        print("\n[INFO] Membuat analisis perbandingan...")
        
        # Get stats
        stats = self.get_source_type_stats(df)
        
        # Print summary
        self.print_comparison_summary(stats)
        
        # Create visualizations
        self.plot_comparison_bar(stats, show=show)
        self.plot_comparison_pie(stats, show=show)
        self.plot_comparison_percentage(stats, show=show)
        
        print("[SUCCESS] Semua visualisasi perbandingan berhasil dibuat!")
        
        return stats


def main():
    """Testing comparison analyzer"""
    # Buat dummy data
    np.random.seed(42)
    
    dummy_news = pd.DataFrame({
        'source': ['Detik'] * 100,
        'sentiment': np.random.choice(['Positif', 'Negatif', 'Netral'], 100, p=[0.5, 0.3, 0.2]),
        'opinion': np.random.choice(['Setuju', 'Tidak Setuju', 'Netral'], 100, p=[0.5, 0.3, 0.2])
    })
    
    dummy_youtube = pd.DataFrame({
        'source': ['YouTube'] * 100,
        'sentiment': np.random.choice(['Positif', 'Negatif', 'Netral'], 100, p=[0.3, 0.5, 0.2]),
        'opinion': np.random.choice(['Setuju', 'Tidak Setuju', 'Netral'], 100, p=[0.3, 0.5, 0.2])
    })
    
    df_combined = pd.concat([dummy_news, dummy_youtube], ignore_index=True)
    
    analyzer = ComparisonAnalyzer()
    stats = analyzer.create_all_comparisons(df_combined, show=True)


if __name__ == "__main__":
    main()