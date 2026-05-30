# ==============================================================================
# 2. CUSTOM CSS INTERAKTIF (Digabung)
# ==============================================================================
st.markdown("""
    <style>
    /* Mengubah Latar Belakang Seluruh Aplikasi Menjadi Krem */
    .stApp {
        background-color: #fdfbf7;
        color: #2c3e50; /* Menjaga warna teks utama tetap kontras dan nyaman dibaca */
    }
    
    /* Mengubah Latar Belakang Sidebar agar Senada atau Tetap Terlihat Terpisah */
    [data-testid="stSidebar"] {
        background-color: #f5efe6;
    }

    /* Desain Kotak Hasil Analisis yang Unik & Modern */
    .kotak-analisis {
        border-left: 6px solid #2ecc71;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #ffffff; /* Mengubah ke putih murni agar kontras di atas latar krem */
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    }
    .label-analisis {
        font-weight: bold;
        color: #27ae60;
        font-size: 1.15em;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    /* Desain Banner Gradasi untuk Halaman Utama */
    .banner-utama {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        padding: 35px;
        border-radius: 12px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(56, 239, 125, 0.2);
    }
    /* CSS UNTUK TABUNG 2D */
    .tube-wrap { display: flex; justify-content: center; height: 350px; padding-top: 20px;}
    .tube-glass { 
        width: 80px; 
        height: 300px; 
        border: 4px solid #cbd5e1; 
        border-top: none; 
        border-radius: 0 0 40px 40px; 
        position: relative; 
        overflow: hidden;
        background: transparent;
    }
    .tube-liquid { 
        position: absolute; 
        bottom: 0; left: 0; right: 0; 
        transition: height 1.2s ease, background 1.2s ease; 
    }
    .precipitate-layer { position: absolute; bottom: 0; left: 0; right: 0; height: 40px; background-color: rgba(0,0,0,0.5); }
    .cloudy-layer { position: absolute; top: 0; bottom: 0; left: 0; right: 0; background-color: rgba(255,255,255,0.6); }
    .bubble-fx { position: absolute; background: rgba(0,0,0,0.2); border-radius: 50%; width: 8px; height: 8px; animation: floatUp 1.8s infinite ease-in; }
    @keyframes floatUp { 0% { bottom: 0px; opacity: 1; } 100% { bottom: 250px; opacity: 0; } }
    </style>
""", unsafe_allow_html=True)
