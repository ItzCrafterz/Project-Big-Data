# config.py
# Konfigurasi dan leksikon sentimen

# Keyword pencarian (fokus ke Timnas Indonesia)
SEARCH_KEYWORDS = [
    "naturalisasi pemain timnas indonesia garuda",
    "pemain naturalisasi timnas garuda indonesia",
    "pemain asing timnas indonesia skuad garuda",
    "wna masuk timnas indonesia",
    "naturalisasi pemain sepak bola indonesia",
    "pemain keturunan timnas indonesia garuda",
    "naturalisasi sandy walsh ivar jenner",
    "naturalisasi elkan baggott jay idzes",
    "rafael struick timnas indonesia",
    "pemain naturalisasi STY pssi"
]

# News Crawling Settings
NEWS_ENABLED = True  # Set False jika tidak ingin crawl berita
NUM_ARTICLES = 1000  # Total target: 150 x 10 keyword = 1500 artikel Indonesia

# YouTube Crawling Settings
YOUTUBE_ENABLED = True  # Set False jika tidak ingin crawl YouTube
YOUTUBE_API_KEY = "AIzaSyB_cmM0taTMRmrP7xUFQrKFN067M2vybUU"  # API Key Anda
YOUTUBE_MAX_VIDEOS = 100  # 100 video per keyword untuk dapat 10K comments
YOUTUBE_MAX_COMMENTS = 100  # 100 komentar per video
YOUTUBE_DAYS = 1800  # 5 thn ke belakang untuk lebih banyak data

YOUTUBE_KEYWORDS = SEARCH_KEYWORDS  # Gunakan keyword yang sama dengan berita

# Twitter Crawling Settings (DISABLED)
TWITTER_ENABLED = False  # Disabled karena snscrape diblokir

# Twitter Keywords (lebih spesifik untuk Twitter)
TWITTER_KEYWORDS = []  # Kosongkan karena disabled

# Kamus kata positif bahasa Indonesia (diperluas)
POSITIVE_WORDS = [
    'baik', 'bagus', 'hebat', 'luar biasa', 'sempurna', 'positif', 
    'senang', 'gembira', 'bangga', 'mendukung', 'setuju', 'optimis',
    'sukses', 'berhasil', 'cemerlang', 'gemilang', 'juara', 'menang',
    'prestasi', 'berprestasi', 'berkualitas', 'unggul', 'terbaik',
    'mendukung', 'dukungan', 'apresiasi', 'mengapresiasi', 'pujian',
    'memuji', 'tepat', 'cocok', 'sesuai', 'layak', 'pantas', 
    'profesional', 'kompeten', 'potensial', 'berbakat', 'talenta',
    'kuat', 'tangguh', 'solid', 'strategis', 'cerdas', 'brilian',
    'efektif', 'efisien', 'produktif', 'kontribusi', 'berkontribusi',
    'membantu', 'bermanfaat', 'menguntungkan', 'profit', 'untung',
    'maju', 'berkembang', 'meningkat', 'progress', 'peningkatan',
    'harapan', 'berharap', 'optimisme', 'yakin', 'percaya', 'aman',
    'nyaman', 'stabil', 'mantap', 'solid', 'kokoh', 'keren',
    'wow', 'dahsyat', 'fantastis', 'luar', 'biasa', 'spektakuler',
    'memperkuat', 'menguatkan', 'boost', 'dongkrak', 'tingkatkan',
    'solutif', 'solusi', 'jalan keluar', 'jawaban', 'inovasi', 'inovatif',
    'kreatif', 'produktif', 'efektif', 'hasil', 'dampak', 'positif',
    'support', 'dukung', 'backing', 'sokongan', 'pro', 'memihak',
    'setuju', 'sepakat', 'seia', 'sekata', 'sejalan', 'sependapat'
]

# Kamus kata negatif bahasa Indonesia (diperluas)
NEGATIVE_WORDS = [
    'buruk', 'jelek', 'tidak', 'gagal', 'salah', 'negatif', 'sedih',
    'kecewa', 'menolak', 'tolak', 'menentang', 'tentang', 'protes',
    'demo', 'demonstrasi', 'kontra', 'anti', 'kritik', 'mengkritik',
    'lemah', 'payah', 'loyo', 'kalah', 'kekalahan', 'hancur',
    'ambruk', 'roboh', 'rusak', 'kerusakan', 'masalah', 'problem',
    'problematik', 'rumit', 'sulit', 'susah', 'berat', 'bingung',
    'khawatir', 'was', 'pesimis', 'pesimisme', 'ragu', 'keraguan',
    'meragukan', 'diragukan', 'tidak setuju', 'kurang', 'minus',
    'cacat', 'celah', 'kesalahan', 'error', 'keliru', 'kacau',
    'chaos', 'anarkis', 'brutal', 'kasar', 'keras', 'ekstrim',
    'radikal', 'berbahaya', 'bahaya', 'ancaman', 'mengancam',
    'merugikan', 'rugi', 'kerugian', 'loss', 'defisit', 'minus',
    'turun', 'menurun', 'penurunan', 'jatuh', 'anjlok', 'merosot',
    'mundur', 'kemunduran', 'stagnan', 'macet', 'mandek', 'buntu',
    'tak', 'kurang', 'minim', 'sedikit', 'lemah', 'payah',
    'kontroversial', 'kontradiksi', 'konflik', 'bentrok', 'ricuh',
    'menghancurkan', 'merusak', 'memperburuk', 'memperlemah', 'melemahkan',
    'tidak adil', 'curang', 'unfair', 'diskriminasi', 'bias', 'pilih kasih',
    'merampas', 'mengambil', 'rebut', 'slot', 'kesempatan', 'peluang',
    'asing', 'luar', 'bukan', 'asli', 'palsu', 'tiruan', 'impor',
    'menolak', 'reject', 'refuse', 'tidak mau', 'tidak suka', 'benci',
    'prihatin', 'miris', 'menyedihkan', 'mengecewakan', 'menyesal'
]

# Stopwords tambahan khusus domain
DOMAIN_STOPWORDS = [
    'timnas', 'indonesia', 'sepak', 'bola', 'pemain', 'naturalisasi',
    'jakarta', 'surabaya', 'bandung', 'artikel', 'berita', 'news',
    'com', 'detik', 'kompas', 'tribun', 'cnn', 'republika'
]