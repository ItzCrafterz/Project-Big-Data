# app.py - Dashboard dengan Tema Merah Putih Indonesia
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Sentimen Timnas Indonesia",
    page_icon="🇮🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS dengan Tema Merah Putih Indonesia
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Background - Gradasi Merah Putih */
    .main {
        background: linear-gradient(180deg, 
            #DC143C 0%,      /* Merah Indonesia */
            #E63946 15%,     /* Merah Terang */
            #FFFFFF 35%,     /* Putih */
            #F8F9FA 50%,     /* Abu Sangat Terang */
            #FFFFFF 65%,     /* Putih */
            #E63946 85%,     /* Merah Terang */
            #DC143C 100%     /* Merah Indonesia */
        );
        background-attachment: fixed;
    }
    
    /* Header Container - Merah Putih */
    .header-container {
        background: linear-gradient(135deg, #DC143C 0%, #FF4458 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(220, 20, 60, 0.4);
        border: 3px solid #FFFFFF;
    }
    
    .header-title {
        color: #FFFFFF;
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        letter-spacing: 1px;
    }
    
    .header-subtitle {
        color: #FFE5E5;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 0;
        font-weight: 300;
    }
    
    /* Metric Cards - Warna Berbeda Jelas */
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        border-left: 6px solid;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
    }
    
    /* Sidebar - Merah Indonesia */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #DC143C 0%, #A01020 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    [data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 600;
    }
    
    /* Tabs - Warna Jelas dan Kontras */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: white;
        border-radius: 15px;
        padding: 0.8rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 1rem 2rem;
        font-weight: 600;
        background-color: #F8F9FA;
        color: #333;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #FFE5E5;
        border-color: #DC143C;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #DC143C 0%, #FF4458 100%) !important;
        color: white !important;
        border-color: #FFFFFF !important;
        box-shadow: 0 5px 15px rgba(220, 20, 60, 0.4);
    }
    
    /* Button Styling - Merah Indonesia */
    .stButton>button {
        background: linear-gradient(135deg, #DC143C 0%, #FF4458 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2.5rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(220, 20, 60, 0.3);
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(220, 20, 60, 0.5);
    }
    
    /* Progress Bar - Merah Indonesia */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #DC143C 0%, #FF4458 100%);
    }
    
    /* Info/Warning Boxes */
    .info-box {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #2196F3;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #FF9800;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 15px !important;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #DC143C 0%, #FF4458 100%);
        color: white;
        border-radius: 15px;
        margin-top: 3rem;
        box-shadow: 0 10px 30px rgba(220, 20, 60, 0.3);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Select Box */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 10px;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background-color: white;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNGSI VISUALISASI DENGAN WARNA JELAS ---
def create_sentiment_pie(df):
    """Pie chart dengan warna yang jelas dan kontras"""
    opinion_counts = df['opinion'].value_counts()
    
    # Warna yang sangat kontras
    colors = {
        'Setuju': '#2ECC71',      # Hijau Terang
        'Tidak Setuju': '#E74C3C', # Merah Terang
        'Netral': '#95A5A6'        # Abu-abu
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=opinion_counts.index,
        values=opinion_counts.values,
        hole=0.45,
        marker=dict(
            colors=[colors.get(label, '#BDC3C7') for label in opinion_counts.index],
            line=dict(color='white', width=4)
        ),
        textinfo='label+percent',
        textfont=dict(size=16, color='white', family='Poppins'),
        hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>',
        pull=[0.1, 0.1, 0]  # Highlight slice
    )])
    
    fig.update_layout(
        title={
            'text': '📊 Distribusi Opini: Setuju vs Tidak Setuju',
            'font': {'size': 24, 'color': '#2C3E50', 'family': 'Poppins', 'weight': 700},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
            font=dict(size=14, family='Poppins'),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#DC143C',
            borderwidth=2
        ),
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig

def create_trend_chart(df):
    """Line chart tren dengan warna kontras"""
    df_trend = df.dropna(subset=['date']).copy()
    
    if df_trend.empty:
        return None
    
    df_trend['date_only'] = df_trend['date'].dt.date
    daily_sentiment = df_trend.groupby(['date_only', 'sentiment']).size().reset_index(name='count')
    
    # Warna yang sangat jelas
    color_map = {
        'Positif': '#2ECC71',   # Hijau Terang
        'Negatif': '#E74C3C',   # Merah Terang
        'Netral': '#3498DB'     # Biru Terang
    }
    
    fig = px.line(
        daily_sentiment,
        x='date_only',
        y='count',
        color='sentiment',
        title='📈 Tren Sentimen dari Waktu ke Waktu',
        labels={'date_only': 'Tanggal', 'count': 'Jumlah', 'sentiment': 'Sentimen'},
        color_discrete_map=color_map
    )
    
    fig.update_traces(
        mode='lines+markers',
        line=dict(width=4),
        marker=dict(size=10, line=dict(width=2, color='white'))
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Poppins', size=13),
        title_font=dict(size=24, color='#2C3E50', family='Poppins', weight=700),
        height=500,
        legend=dict(
            title=dict(text='Sentimen', font=dict(size=16, weight=700)),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#DC143C',
            borderwidth=2,
            font=dict(size=14)
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#ECF0F1',
            showline=True,
            linewidth=2,
            linecolor='#DC143C'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#ECF0F1',
            showline=True,
            linewidth=2,
            linecolor='#DC143C'
        )
    )
    
    return fig

def create_comparison_chart(df):
    """Comparison chart dengan warna jelas"""
    df['source_type'] = df['source'].apply(lambda x: 'YouTube' if x == 'YouTube' else 'News')
    
    comparison = df.groupby(['source_type', 'opinion']).size().reset_index(name='count')
    
    # Warna yang sangat kontras
    color_map = {
        'Setuju': '#2ECC71',
        'Tidak Setuju': '#E74C3C',
        'Netral': '#95A5A6'
    }
    
    fig = px.bar(
        comparison,
        x='source_type',
        y='count',
        color='opinion',
        title='⚖️ Perbandingan Opini: Berita vs YouTube',
        labels={'source_type': 'Sumber Data', 'count': 'Jumlah', 'opinion': 'Opini'},
        color_discrete_map=color_map,
        barmode='group',
        text='count'
    )
    
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        textfont=dict(size=14, family='Poppins', weight=700)
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Poppins', size=13),
        title_font=dict(size=24, color='#2C3E50', family='Poppins', weight=700),
        height=500,
        legend=dict(
            title=dict(text='Opini', font=dict(size=16, weight=700)),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#DC143C',
            borderwidth=2,
            font=dict(size=14)
        ),
        xaxis=dict(showgrid=False, linewidth=2, linecolor='#DC143C'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#ECF0F1', linewidth=2, linecolor='#DC143C')
    )
    
    return fig

def create_source_distribution(df):
    """Bar chart dengan gradasi warna"""
    top_sources = df['source'].value_counts().head(10)
    
    fig = go.Figure(go.Bar(
        y=top_sources.index,
        x=top_sources.values,
        orientation='h',
        marker=dict(
            color=top_sources.values,
            colorscale=[[0, '#FFE5E5'], [0.5, '#FF6B7A'], [1, '#DC143C']],
            showscale=True,
            colorbar=dict(title="Jumlah", thickness=20)
        ),
        text=top_sources.values,
        textposition='outside',
        textfont=dict(size=14, weight=700),
        hovertemplate='<b>%{y}</b><br>Jumlah: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '📰 Top 10 Sumber Berita/Komentar',
            'font': {'size': 24, 'color': '#2C3E50', 'family': 'Poppins', 'weight': 700},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Jumlah Data",
        yaxis_title="Sumber",
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=550,
        showlegend=False,
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#ECF0F1'),
        yaxis=dict(showgrid=False)
    )
    
    return fig

@st.cache_data
def load_data(path):
    """Memuat data dari CSV"""
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, encoding='utf-8-sig')
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            return df
        except Exception as e:
            st.error(f"❌ Gagal memuat data: {e}")
            return None
    else:
        return None

# --- HEADER ---
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🇮🇩 Analisis Sentimen Naturalisasi Pemain Timnas Indonesia 🇮🇩</h1>
        <p class="header-subtitle">📊 Dashboard Interaktif | Gilang Gallan Indrana - 5024231030</p>
    </div>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
DATA_PATH = 'data/processed_data.csv'
df = load_data(DATA_PATH)

if df is not None and not df.empty:
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("### 🎛️ Filter & Pengaturan")
        st.markdown("---")
        
        # Filter Sumber
        st.markdown("#### 📊 **Sumber Data**")
        all_sources = df['source'].unique().tolist()
        selected_sources = st.multiselect(
            "Pilih Sumber:",
            options=all_sources,
            default=all_sources,
            help="Filter data berdasarkan sumber"
        )
        
        st.markdown("---")
        
        # Filter Sentimen
        st.markdown("#### 😊 **Sentimen**")
        all_sentiments = df['sentiment'].unique().tolist()
        selected_sentiments = st.multiselect(
            "Pilih Sentimen:",
            options=all_sentiments,
            default=all_sentiments,
            help="Filter data berdasarkan sentimen"
        )
        
        st.markdown("---")
        
        # Date range
        if 'date' in df.columns and df['date'].notna().any():
            st.markdown("#### 📅 **Rentang Tanggal**")
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            
            date_range = st.date_input(
                "Pilih Periode:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Filter berdasarkan rentang tanggal"
            )
        
        st.markdown("---")
        
        # Info
        st.markdown("### ℹ️ **Tentang Dashboard**")
        st.info("""
        Dashboard ini menampilkan hasil analisis sentimen menggunakan **IndoBERT** terhadap isu naturalisasi pemain Timnas Indonesia.
        
        **Sumber Data:**
        - 📰 Portal berita online
        - 🎥 Komentar YouTube
        
        **Model:** IndoBERT (Transformer)
        
        **Update:** {}
        """.format(datetime.now().strftime("%d %B %Y, %H:%M")))
    
    # Terapkan filter
    df_filtered = df.copy()
    if selected_sources:
        df_filtered = df_filtered[df_filtered['source'].isin(selected_sources)]
    if selected_sentiments:
        df_filtered = df_filtered[df_filtered['sentiment'].isin(selected_sentiments)]
    if 'date' in df.columns and len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered['date'].dt.date >= date_range[0]) &
            (df_filtered['date'].dt.date <= date_range[1])
        ]
    
    # --- METRICS ---
    st.markdown("## 📊 Ringkasan Statistik")
    
    total_data = len(df_filtered)
    setuju_count = len(df_filtered[df_filtered['opinion'] == 'Setuju'])
    tidak_setuju_count = len(df_filtered[df_filtered['opinion'] == 'Tidak Setuju'])
    netral_count = len(df_filtered[df_filtered['opinion'] == 'Netral'])
    
    setuju_pct = (setuju_count / total_data * 100) if total_data > 0 else 0
    tidak_setuju_pct = (tidak_setuju_count / total_data * 100) if total_data > 0 else 0
    netral_pct = (netral_count / total_data * 100) if total_data > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Data",
            value=f"{total_data:,}",
            delta="100%",
            help="Total data yang dianalisis"
        )
    
    with col2:
        st.metric(
            label="✅ Setuju (Mendukung)",
            value=f"{setuju_count:,}",
            delta=f"{setuju_pct:.1f}%",
            delta_color="normal",
            help="Mendukung naturalisasi"
        )
    
    with col3:
        st.metric(
            label="❌ Tidak Setuju (Menolak)",
            value=f"{tidak_setuju_count:,}",
            delta=f"{tidak_setuju_pct:.1f}%",
            delta_color="inverse",
            help="Menolak naturalisasi"
        )
    
    with col4:
        st.metric(
            label="😐 Netral",
            value=f"{netral_count:,}",
            delta=f"{netral_pct:.1f}%",
            delta_color="off",
            help="Opini netral"
        )
    
    # Progress bars dengan warna yang jelas
    st.markdown("### 📈 Distribusi Persentase")
    col_prog1, col_prog2, col_prog3 = st.columns(3)
    
    with col_prog1:
        st.markdown(f"**✅ Setuju: {setuju_pct:.1f}%**")
        st.progress(setuju_pct / 100)
    
    with col_prog2:
        st.markdown(f"**❌ Tidak Setuju: {tidak_setuju_pct:.1f}%**")
        st.progress(tidak_setuju_pct / 100)
    
    with col_prog3:
        st.markdown(f"**😐 Netral: {netral_pct:.1f}%**")
        st.progress(netral_pct / 100)
    
    st.markdown("---")
    
    # --- TABS DENGAN WARNA JELAS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Distribusi Opini",
        "📈 Tren Waktu",
        "⚖️ Perbandingan",
        "☁️ Word Clouds",
        "📋 Data Explorer"
    ])
    
    with tab1:
        st.markdown("### 📊 Visualisasi Distribusi Opini")
        
        col_viz1, col_viz2 = st.columns([1, 1])
        
        with col_viz1:
            fig_pie = create_sentiment_pie(df_filtered)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_viz2:
            st.markdown("#### 🎯 Insight Sentimen")
            
            # Dominant sentiment
            dominant = 'Setuju' if setuju_pct > tidak_setuju_pct else 'Tidak Setuju' if tidak_setuju_pct > setuju_pct else 'Seimbang'
            
            if dominant == 'Setuju':
                st.success(f"""
                **✅ Sentimen Dominan: MENDUKUNG**
                
                - {setuju_pct:.1f}% masyarakat **SETUJU** dengan naturalisasi
                - Selisih {abs(setuju_pct - tidak_setuju_pct):.1f}% lebih tinggi dari yang menolak
                - Indikasi dukungan kuat terhadap kebijakan
                """)
            elif dominant == 'Tidak Setuju':
                st.error(f"""
                **❌ Sentimen Dominan: MENOLAK**
                
                - {tidak_setuju_pct:.1f}% masyarakat **TIDAK SETUJU** dengan naturalisasi
                - Selisih {abs(tidak_setuju_pct - setuju_pct):.1f}% lebih tinggi dari yang mendukung
                - Perlu evaluasi kebijakan lebih lanjut
                """)
            else:
                st.warning("""
                **😐 Sentimen SEIMBANG**
                
                - Opini publik terbagi rata
                - Diperlukan dialog lebih lanjut
                """)
        
        # Source distribution
        st.markdown("---")
        fig_source = create_source_distribution(df_filtered)
        st.plotly_chart(fig_source, use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 Tren Sentimen dari Waktu ke Waktu")
        
        fig_trend = create_trend_chart(df_filtered)
        if fig_trend:
            st.plotly_chart(fig_trend, use_container_width=True)
            
            st.markdown("""
            <div class="info-box">
            <strong>💡 Cara Membaca Grafik:</strong><br>
            • <span style="color: #2ECC71;">●</span> <strong>Garis Hijau</strong> = Sentimen Positif (Mendukung)<br>
            • <span style="color: #E74C3C;">●</span> <strong>Garis Merah</strong> = Sentimen Negatif (Menolak)<br>
            • <span style="color: #3498DB;">●</span> <strong>Garis Biru</strong> = Sentimen Netral<br><br>
            Perhatikan pola kenaikan/penurunan untuk memahami dinamika opini publik.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Data tanggal tidak memadai untuk membuat grafik tren")
    
    with tab3:
        st.markdown("### ⚖️ Perbandingan Berita vs YouTube")
        
        if 'YouTube' in df['source'].values:
            fig_comparison = create_comparison_chart(df_filtered)
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Stats comparison
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                news_data = df_filtered[df_filtered['source'] != 'YouTube']
                if not news_data.empty:
                    news_setuju = len(news_data[news_data['opinion'] == 'Setuju'])
                    news_total = len(news_data)
                    news_pct = (news_setuju / news_total * 100) if news_total > 0 else 0
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%); 
                                padding: 2rem; border-radius: 15px; color: white; 
                                box-shadow: 0 8px 20px rgba(46, 204, 113, 0.3);">
                    <h3>📰 Portal Berita</h3>
                    <p style="font-size: 3rem; font-weight: bold; margin: 1rem 0;">{news_pct:.1f}%</p>
                    <p style="font-size: 1.2rem;">Mendukung Naturalisasi</p>
                    <p style="opacity: 0.9;">Total: {news_total:,} data</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_comp2:
                youtube_data = df_filtered[df_filtered['source'] == 'YouTube']
                if not youtube_data.empty:
                    youtube_setuju = len(youtube_data[youtube_data['opinion'] == 'Setuju'])
                    youtube_total = len(youtube_data)
                    youtube_pct = (youtube_setuju / youtube_total * 100) if youtube_total > 0 else 0
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%); 
                                padding: 2rem; border-radius: 15px; color: white;
                                box-shadow: 0 8px 20px rgba(231, 76, 60, 0.3);">
                    <h3>🎥 YouTube Comments</h3>
                    <p style="font-size: 3rem; font-weight: bold; margin: 1rem 0;">{youtube_pct:.1f}%</p>
                    <p style="font-size: 1.2rem;">Mendukung Naturalisasi</p>
                    <p style="opacity: 0.9;">Total: {youtube_total:,} data</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Data YouTube tidak tersedia untuk perbandingan")
    
    with tab4:
        st.markdown("### ☁️ Word Clouds - Kata Populer")
        
        col_wc1, col_wc2 = st.columns(2)
        
        with col_wc1:
            st.markdown("#### ✅ Sentimen Positif")
            if os.path.exists("output/wordcloud_positif.png"):
                st.image("output/wordcloud_positif.png", use_column_width=True,
                        caption="Kata-kata yang sering muncul pada komentar/berita positif")
            else:
                st.warning("⚠️ File wordcloud positif tidak ditemukan")
        
        with col_wc2:
            st.markdown("#### ❌ Sentimen Negatif")
            if os.path.exists("output/wordcloud_negatif.png"):
                st.image("output/wordcloud_negatif.png", use_column_width=True,
                        caption="Kata-kata yang sering muncul pada komentar/berita negatif")
            else:
                st.warning("⚠️ File wordcloud negatif tidak ditemukan")
        
        st.markdown("""
        <div class="info-box">
        <strong>💡 Cara Membaca Word Cloud:</strong><br>
        • Semakin <strong>BESAR</strong> ukuran kata = semakin <strong>SERING</strong> muncul<br>
        • Word cloud membantu mengidentifikasi <strong>tema utama</strong> dalam diskusi<br>
        • Perhatikan kata-kata dominan untuk memahami fokus pembahasan
        </div>
        """, unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### 📋 Eksplorasi Data Detail")
        
        # Search functionality
        search_term = st.text_input("🔍 Cari dalam konten:", placeholder="Masukkan kata kunci...")
        
        if search_term:
            df_search = df_filtered[df_filtered['content'].str.contains(search_term, case=False, na=False)]
            st.info(f"Ditemukan {len(df_search)} hasil untuk '{search_term}'")
            display_df = df_search
        else:
            display_df = df_filtered
        
        # Column selector
        all_columns = display_df.columns.tolist()
        default_columns = ['source', 'content', 'sentiment', 'opinion']
        available_defaults = [col for col in default_columns if col in all_columns]
        
        selected_columns = st.multiselect(
            "Pilih kolom yang ditampilkan:",
            options=all_columns,
            default=available_defaults
        )
        
        if selected_columns:
            st.dataframe(
                display_df[selected_columns].head(100),
                use_container_width=True,
                height=400
            )
            
            # Download button
            csv = display_df[selected_columns].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Data (CSV)",
                data=csv,
                file_name=f'sentiment_data_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                help="Download data yang ditampilkan dalam format CSV"
            )
    
    # --- FOOTER ---
    st.markdown("---")
    st.markdown("""
        <div class="footer">
            <h3>🇮🇩 Dashboard Analisis Sentimen Naturalisasi Pemain Timnas Indonesia 🇮🇩</h3>
            <p style="font-size: 1.1rem; margin: 1rem 0;">
                Dibuat dengan ❤️ menggunakan <strong>Streamlit</strong> & <strong>IndoBERT</strong>
            </p>
            <p style="font-size: 0.9rem; opacity: 0.9;">
                Data diupdate berkala melalui crawling otomatis | Model: IndoBERT Transformer
            </p>
            <p style="font-size: 0.9rem; margin-top: 1rem;">
                © 2024 Big Data Analytics Project | <strong>Gilang Gallan Indrana - 5024231030</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

else:
    # Jika tidak ada data
    st.error("❌ Data tidak ditemukan!")
    st.markdown("""
    <div class="warning-box">
    <h3>⚠️ Langkah-langkah untuk memulai:</h3>
    <ol>
        <li>Pastikan file <code>data/processed_data.csv</code> ada</li>
        <li>Jalankan <code>python main.py</code> untuk melakukan crawling dan analisis</li>
        <li>Tunggu proses selesai (bisa memakan waktu untuk IndoBERT)</li>
        <li>Refresh halaman ini setelah proses selesai</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)