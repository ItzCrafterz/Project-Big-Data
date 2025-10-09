# news_crawler.py
import pandas as pd
from GoogleNews import GoogleNews
from datetime import datetime
import time
import config

class NewsCrawler:
    def __init__(self):
        self.googlenews = GoogleNews(lang='id', region='ID', period='6m')
        self.articles = []
        
        # Keyword yang HARUS ada (Indonesia related)
        self.must_contain = [
            'indonesia', 'timnas indonesia', 'garuda', 'pssi', 
            'skuad garuda', 'shin tae-yong', 'sty'
        ]
        
        # Keyword yang TIDAK boleh ada (negara lain)
        self.must_not_contain = [
            'timnas malaysia', 'timnas thailand', 'timnas vietnam',
            'timnas singapura', 'timnas filipina', 'timnas jepang',
            'timnas korea', 'timnas china', 'timnas arab',
            'timnas inggris', 'timnas perancis', 'timnas spanyol',
            'timnas jerman', 'timnas brasil', 'timnas argentina'
        ]
    
    def is_relevant_article(self, title, content):
        """
        Check apakah artikel relevan dengan Timnas Indonesia
        
        Args:
            title: Judul artikel
            content: Isi artikel
        
        Returns:
            Boolean: True jika relevan, False jika tidak
        """
        text = f"{title} {content}".lower()
        
        # Cek keyword yang tidak boleh ada
        for keyword in self.must_not_contain:
            if keyword.lower() in text:
                return False
        
        # Cek minimal ada salah satu keyword Indonesia
        found_indonesia = False
        for keyword in self.must_contain:
            if keyword.lower() in text:
                found_indonesia = True
                break
        
        return found_indonesia
    
    def crawl_news(self, keywords, num_articles=50):
        """
        Crawl berita dari Google News
        
        Args:
            keywords: List keyword pencarian
            num_articles: Jumlah artikel per keyword
        
        Returns:
            DataFrame berisi artikel yang di-crawl
        """
        print("[INFO] Memulai crawling berita...")
        
        for keyword in keywords:
            print(f"\n[CRAWL] Mencari artikel dengan keyword: '{keyword}'")
            
            try:
                self.googlenews.clear()
                self.googlenews.search(keyword)
                
                # Ambil hasil pencarian dengan pagination
                page = 1
                total_collected = 0
                
                while total_collected < num_articles and page <= 10:
                    try:
                        if page > 1:
                            self.googlenews.get_page(page)
                        
                        results = self.googlenews.results()
                        
                        if not results:
                            break
                        
                        for idx, article in enumerate(results):
                            if total_collected >= num_articles:
                                break
                                
                            try:
                                # Ekstrak informasi artikel
                                title = article.get('title', '')
                                desc = article.get('desc', '')
                                date = article.get('date', '')
                                link = article.get('link', '')
                                media = article.get('media', 'Unknown')
                                
                                # Gabungkan title dan desc sebagai content
                                content = f"{title}. {desc}"
                                
                                # FILTER: Cek relevansi dengan Timnas Indonesia
                                if not self.is_relevant_article(title, content):
                                    continue  # Skip artikel yang tidak relevan
                                
                                self.articles.append({
                                    'title': title,
                                    'content': content,
                                    'date': date,
                                    'source': media,
                                    'url': link,
                                    'keyword': keyword,
                                    'crawled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                })
                                
                                total_collected += 1
                                
                            except Exception as e:
                                print(f"[WARNING] Error parsing artikel {idx+1}: {str(e)}")
                                continue
                        
                        page += 1
                        time.sleep(1)  # Delay antar halaman
                        
                    except Exception as e:
                        print(f"[WARNING] Error pada halaman {page}: {str(e)}")
                        break
                
                print(f"[SUCCESS] Berhasil crawl {total_collected} artikel untuk keyword '{keyword}'")
                
                # Delay untuk menghindari rate limit
                time.sleep(2)
                
            except Exception as e:
                print(f"[ERROR] Error crawling keyword '{keyword}': {str(e)}")
                continue
        
        # Konversi ke DataFrame
        df = pd.DataFrame(self.articles)
        
        if not df.empty:
            # PERBAIKAN: Hapus duplikat berdasarkan URL DAN title (lebih presisi)
            # Gunakan kombinasi URL + first 50 chars title untuk avoid false positive
            df['dedup_key'] = df['url'].astype(str) + '_' + df['title'].astype(str).str[:50]
            df = df.drop_duplicates(subset=['dedup_key'], keep='first')
            df = df.drop('dedup_key', axis=1)
            
            # Double check: Filter lagi untuk memastikan hanya Indonesia
            df['is_indonesia'] = df.apply(
                lambda row: self.is_relevant_article(row['title'], row['content']), 
                axis=1
            )
            df = df[df['is_indonesia'] == True]
            df = df.drop('is_indonesia', axis=1)
            
            print(f"\n[SUCCESS] Total {len(df)} artikel unik TIMNAS INDONESIA berhasil di-crawl")
        else:
            print("\n[WARNING] Tidak ada artikel yang berhasil di-crawl")
        
        return df
    
    def save_to_csv(self, df, filename='data/raw_data.csv'):
        """
        Simpan hasil crawling ke CSV
        
        Args:
            df: DataFrame hasil crawling
            filename: Nama file output
        """
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"[SAVE] Data mentah disimpan ke: {filename}")
        except Exception as e:
            print(f"[ERROR] Error menyimpan file: {str(e)}")


def main():
    """Testing crawling"""
    crawler = NewsCrawler()
    df = crawler.crawl_news(config.SEARCH_KEYWORDS, config.NUM_ARTICLES)
    
    if not df.empty:
        crawler.save_to_csv(df)
        print(f"\nContoh artikel pertama:")
        print(df.iloc[0]['content'][:200] + "...")
    

if __name__ == "__main__":
    main()