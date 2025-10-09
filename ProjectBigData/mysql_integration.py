# mysql_integration.py
"""
Integrasi data ke MySQL database untuk dashboard
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime


class MySQLIntegration:
    def __init__(self, host='localhost', user='root', password='', database='sentiment_analysis'):
        """
        Initialize MySQL connection
        
        Args:
            host: MySQL host (default: localhost untuk XAMPP)
            user: MySQL username (default: root)
            password: MySQL password (default: kosong untuk XAMPP)
            database: Database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """Buat koneksi ke MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                use_unicode=True
            )
            
            if self.connection.is_connected():
                print(f"[MySQL] Berhasil connect ke database '{self.database}'")
                return True
        except Error as e:
            print(f"[MySQL ERROR] Gagal connect: {e}")
            print("[INFO] Pastikan XAMPP MySQL sudah running!")
            print("[INFO] Buat database dengan: mysql -u root < database_schema.sql")
            return False
        
        return False
    
    def disconnect(self):
        """Tutup koneksi"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[MySQL] Koneksi ditutup")
    
    def insert_news_data(self, df):
        """
        Insert data berita ke tabel raw_news
        
        Args:
            df: DataFrame hasil crawling berita
        """
        if df.empty:
            print("[MySQL] Tidak ada data berita untuk diinsert")
            return
        
        print(f"[MySQL] Inserting {len(df)} data berita...")
        
        cursor = self.connection.cursor()
        
        insert_query = """
        INSERT INTO raw_news (title, content, date, source, url, keyword, crawled_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        for _, row in df.iterrows():
            try:
                values = (
                    row.get('title', ''),
                    row.get('content', ''),
                    row.get('date', ''),
                    row.get('source', ''),
                    row.get('url', ''),
                    row.get('keyword', ''),
                    row.get('crawled_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
                cursor.execute(insert_query, values)
                success_count += 1
            except Error as e:
                print(f"[MySQL WARNING] Error insert: {e}")
                continue
        
        self.connection.commit()
        cursor.close()
        print(f"[MySQL SUCCESS] {success_count}/{len(df)} data berita berhasil diinsert")
    
    def insert_youtube_data(self, df):
        """Insert data YouTube comments ke tabel youtube_comments"""
        if df.empty:
            print("[MySQL] Tidak ada data YouTube untuk diinsert")
            return
        
        print(f"[MySQL] Inserting {len(df)} YouTube comments...")
        
        cursor = self.connection.cursor()
        
        insert_query = """
        INSERT INTO youtube_comments (comment_id, video_id, video_title, author, content, 
                                     published_at, likes, keyword, source, crawled_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            likes = VALUES(likes)
        """
        
        success_count = 0
        for _, row in df.iterrows():
            try:
                values = (
                    row.get('comment_id', ''),
                    row.get('video_id', ''),
                    row.get('video_title', ''),
                    row.get('author', ''),
                    row.get('content', ''),
                    row.get('published_at', ''),
                    int(row.get('likes', 0)),
                    row.get('keyword', ''),
                    row.get('source', 'YouTube'),
                    row.get('crawled_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
                cursor.execute(insert_query, values)
                success_count += 1
            except Error as e:
                print(f"[MySQL WARNING] Error insert: {e}")
                continue
        
        self.connection.commit()
        cursor.close()
        print(f"[MySQL SUCCESS] {success_count}/{len(df)} YouTube comments berhasil diinsert")
    
    def insert_sentiment_results(self, df):
        """Insert hasil analisis sentimen"""
        if df.empty:
            print("[MySQL] Tidak ada hasil sentimen untuk diinsert")
            return
        
        print(f"[MySQL] Inserting {len(df)} sentiment results...")
        
        cursor = self.connection.cursor()
        
        insert_query = """
        INSERT INTO sentiment_results (source_type, original_text, processed_text, 
                                      positive_count, negative_count, sentiment_score,
                                      sentiment, opinion, source_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        for _, row in df.iterrows():
            try:
                # Tentukan source_type
                source = row.get('source', '')
                source_type = 'YouTube' if source == 'YouTube' else 'News'
                
                values = (
                    source_type,
                    row.get('content', ''),
                    row.get('processed_text', ''),
                    int(row.get('positive_count', 0)),
                    int(row.get('negative_count', 0)),
                    int(row.get('sentiment_score', 0)),
                    row.get('sentiment', 'Netral'),
                    row.get('opinion', 'Netral'),
                    source
                )
                cursor.execute(insert_query, values)
                success_count += 1
            except Error as e:
                print(f"[MySQL WARNING] Error insert: {e}")
                continue
        
        self.connection.commit()
        cursor.close()
        print(f"[MySQL SUCCESS] {success_count}/{len(df)} sentiment results berhasil diinsert")
    
    def update_dashboard_stats(self):
        """Update statistik dashboard"""
        print("[MySQL] Updating dashboard stats...")
        
        cursor = self.connection.cursor()
        
        # Hitung statistik dari sentiment_results
        stats_query = """
        INSERT INTO dashboard_stats (stat_date, total_data, total_news, total_youtube,
                                    positive_count, negative_count, neutral_count,
                                    setuju_count, tidak_setuju_count,
                                    positive_pct, negative_pct, setuju_pct, tidak_setuju_pct)
        SELECT 
            CURDATE() as stat_date,
            COUNT(*) as total_data,
            SUM(CASE WHEN source_type = 'News' THEN 1 ELSE 0 END) as total_news,
            SUM(CASE WHEN source_type = 'YouTube' THEN 1 ELSE 0 END) as total_youtube,
            SUM(CASE WHEN sentiment = 'Positif' THEN 1 ELSE 0 END) as positive_count,
            SUM(CASE WHEN sentiment = 'Negatif' THEN 1 ELSE 0 END) as negative_count,
            SUM(CASE WHEN sentiment = 'Netral' THEN 1 ELSE 0 END) as neutral_count,
            SUM(CASE WHEN opinion = 'Setuju' THEN 1 ELSE 0 END) as setuju_count,
            SUM(CASE WHEN opinion = 'Tidak Setuju' THEN 1 ELSE 0 END) as tidak_setuju_count,
            ROUND(SUM(CASE WHEN sentiment = 'Positif' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as positive_pct,
            ROUND(SUM(CASE WHEN sentiment = 'Negatif' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as negative_pct,
            ROUND(SUM(CASE WHEN opinion = 'Setuju' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as setuju_pct,
            ROUND(SUM(CASE WHEN opinion = 'Tidak Setuju' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as tidak_setuju_pct
        FROM sentiment_results
        ON DUPLICATE KEY UPDATE
            total_data = VALUES(total_data),
            total_news = VALUES(total_news),
            total_youtube = VALUES(total_youtube),
            positive_count = VALUES(positive_count),
            negative_count = VALUES(negative_count),
            neutral_count = VALUES(neutral_count),
            setuju_count = VALUES(setuju_count),
            tidak_setuju_count = VALUES(tidak_setuju_count),
            positive_pct = VALUES(positive_pct),
            negative_pct = VALUES(negative_pct),
            setuju_pct = VALUES(setuju_pct),
            tidak_setuju_pct = VALUES(tidak_setuju_pct)
        """
        
        try:
            cursor.execute(stats_query)
            self.connection.commit()
            print("[MySQL SUCCESS] Dashboard stats updated")
        except Error as e:
            print(f"[MySQL ERROR] Failed to update stats: {e}")
        
        cursor.close()
    
    def update_sentiment_by_source(self):
        """Update sentiment by source"""
        print("[MySQL] Updating sentiment by source...")
        
        cursor = self.connection.cursor()
        
        # Delete old data
        cursor.execute("TRUNCATE TABLE sentiment_by_source")
        
        # Insert new aggregated data
        aggregate_query = """
        INSERT INTO sentiment_by_source (source_name, source_type, positive, negative, neutral, total)
        SELECT 
            source_name,
            source_type,
            SUM(CASE WHEN sentiment = 'Positif' THEN 1 ELSE 0 END) as positive,
            SUM(CASE WHEN sentiment = 'Negatif' THEN 1 ELSE 0 END) as negative,
            SUM(CASE WHEN sentiment = 'Netral' THEN 1 ELSE 0 END) as neutral,
            COUNT(*) as total
        FROM sentiment_results
        GROUP BY source_name, source_type
        """
        
        try:
            cursor.execute(aggregate_query)
            self.connection.commit()
            print("[MySQL SUCCESS] Sentiment by source updated")
        except Error as e:
            print(f"[MySQL ERROR] Failed to update: {e}")
        
        cursor.close()
    
    def get_dashboard_data(self):
        """Ambil data untuk dashboard"""
        cursor = self.connection.cursor(dictionary=True)
        
        # Get latest stats
        cursor.execute("SELECT * FROM dashboard_stats WHERE stat_date = CURDATE()")
        stats = cursor.fetchone()
        
        # Get comparison
        cursor.execute("SELECT * FROM v_comparison_summary")
        comparison = cursor.fetchall()
        
        # Get sentiment by source
        cursor.execute("SELECT * FROM sentiment_by_source ORDER BY total DESC LIMIT 10")
        by_source = cursor.fetchall()
        
        cursor.close()
        
        return {
            'stats': stats,
            'comparison': comparison,
            'by_source': by_source
        }


def main():
    """Testing MySQL integration"""
    print("="*70)
    print("TESTING MYSQL INTEGRATION")
    print("="*70)
    
    # Initialize
    db = MySQLIntegration(
        host='localhost',
        user='root',
        password='',  # Kosongkan untuk XAMPP default
        database='sentiment_analysis'
    )
    
    # Connect
    if not db.connect():
        return
    
    # Test dengan sample data
    sample_news = pd.DataFrame([
        {
            'title': 'Naturalisasi Pemain Timnas Menuai Pro Kontra',
            'content': 'Kebijakan naturalisasi pemain timnas indonesia mendapat respon beragam',
            'date': '2024-10-01',
            'source': 'Detik',
            'url': 'http://example.com/1',
            'keyword': 'naturalisasi',
            'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ])
    
    # Insert test data
    db.insert_news_data(sample_news)
    
    # Update stats
    db.update_dashboard_stats()
    
    # Get dashboard data
    data = db.get_dashboard_data()
    print("\n[INFO] Dashboard data:")
    print(data)
    
    # Disconnect
    db.disconnect()


if __name__ == "__main__":
    main()