# youtube_scraper.py

import pandas as pd
from datetime import datetime
import time
import sys
import io

# FIX: Set stdout encoding ke UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("[WARNING] google-api-python-client tidak terinstall.")


class YouTubeScraper:
    def __init__(self, api_key):
        if not YOUTUBE_API_AVAILABLE:
            raise ImportError("google-api-python-client tidak terinstall")
        
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.comments = []
        
        # Filter keywords Indonesia
        self.must_contain = [
            'timnas indonesia', 'timnas garuda', 'garuda',
            'indonesia', 'pssi', 'naturalisasi'
        ]
        
        self.must_not_contain = [
            'timnas malaysia', 'timnas thailand', 'timnas vietnam'
        ]
    
    def clean_text(self, text):
        """Bersihkan text dari emoji dan karakter bermasalah"""
        if not text:
            return ""
        # Replace emoji dan unicode bermasalah dengan spasi
        return text.encode('ascii', 'ignore').decode('ascii')
    
    def is_relevant_comment(self, text):
        """Check apakah komentar relevan dengan Timnas Indonesia"""
        text_lower = text.lower()
        
        for keyword in self.must_not_contain:
            if keyword in text_lower:
                return False
        
        for keyword in self.must_contain:
            if keyword in text_lower:
                return True
        
        return False
    
    def search_videos(self, query, max_results=50):
        """Cari video berdasarkan keyword"""
        print(f"[SEARCH] Query: '{query}'")
        
        video_ids = []
        
        try:
            request = self.youtube.search().list(
                part='id,snippet',
                q=query,
                type='video',
                maxResults=max_results,
                order='relevance',
                relevanceLanguage='id',
                regionCode='ID'
            )
            
            response = request.execute()
            
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                title = self.clean_text(item['snippet']['title'])  # FIX: Clean title
                video_ids.append({
                    'video_id': video_id,
                    'title': title
                })
                
            print(f"[SUCCESS] Ditemukan {len(video_ids)} video")
            
        except HttpError as e:
            print(f"[ERROR] HTTP Error: {e}")
            if 'quotaExceeded' in str(e):
                print("[ERROR] Quota API habis!")
        except Exception as e:
            print(f"[ERROR] Error: {str(e)}")
        
        return video_ids
    
    def get_video_comments(self, video_id, max_comments=100):
        """Ambil komentar dari video"""
        comments = []
        
        try:
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(max_comments, 100),
                order='relevance',
                textFormat='plainText'
            )
            
            response = request.execute()
            
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                
                comment_text = self.clean_text(comment['textDisplay'])  # FIX: Clean comment
                author = self.clean_text(comment['authorDisplayName'])  # FIX: Clean author
                published_at = comment['publishedAt']
                like_count = comment['likeCount']
                
                # Filter relevansi
                if not self.is_relevant_comment(comment_text):
                    continue
                
                comments.append({
                    'comment_id': item['id'],
                    'video_id': video_id,
                    'author': author,
                    'content': comment_text,
                    'published_at': published_at,
                    'likes': like_count
                })
            
        except HttpError as e:
            if 'commentsDisabled' in str(e):
                print(f"[WARNING] Komentar disabled: {video_id}")
            elif 'quotaExceeded' in str(e):
                print(f"[ERROR] Quota API habis!")
                raise
            else:
                print(f"[WARNING] Error: {e}")
        
        return comments
    
    def crawl_comments(self, keywords, max_videos=20, max_comments_per_video=100):
        """Crawl komentar YouTube"""
        print("[INFO] Memulai crawling YouTube comments...")
        print(f"[INFO] Target: {max_videos} video per keyword")
        print(f"[INFO] Target: {max_comments_per_video} komentar per video\n")
        
        all_comments = []
        
        for keyword in keywords:
            print(f"[KEYWORD] Processing: '{keyword}'")
            
            videos = self.search_videos(keyword, max_videos)
            
            if not videos:
                continue
            
            for idx, video in enumerate(videos):
                video_id = video['video_id']
                video_title = video['title']
                
                # FIX: Print dengan safe encoding
                print(f"[VIDEO {idx+1}/{len(videos)}] {video_title[:50]}...")
                
                comments = self.get_video_comments(video_id, max_comments_per_video)
                
                for comment in comments:
                    comment['video_title'] = video_title
                    comment['keyword'] = keyword
                    comment['source'] = 'YouTube'
                    comment['crawled_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                all_comments.extend(comments)
                
                print(f"         Collected {len(comments)} comments")
                
                time.sleep(1)
            
            print(f"[SUCCESS] Total {len([c for c in all_comments if c['keyword'] == keyword])} komentar\n")
        
        df = pd.DataFrame(all_comments)
        
        if not df.empty:
            df = df.drop_duplicates(subset=['comment_id'], keep='first')
            print(f"[SUCCESS] Total {len(df)} komentar unik")
        else:
            print("[WARNING] Tidak ada komentar yang di-crawl")
        
        return df
    
    def save_to_csv(self, df, filename='data/raw_youtube.csv'):
        """Simpan ke CSV"""
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"[SAVE] Data YouTube disimpan ke: {filename}")
        except Exception as e:
            print(f"[ERROR] Error menyimpan file: {str(e)}")