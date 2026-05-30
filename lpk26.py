import streamlit as st
import time

# ==============================================================================
# 1. KONFIGURASI HALAMAN (Harus diletakkan di baris paling atas)
# ==============================================================================
st.set_page_config(
    page_title="OrganicChem | Edu-Lab Platform",
    page_icon="🧪",
    layout="wide"
)

# ==============================================================================
# 2. CUSTOM CSS INTERAKTIF (Tema Krem)
# ==============================================================================
st.markdown("""
    <style>
    /* Mengubah Latar Belakang Seluruh Aplikasi Menjadi Krem */
    .stApp {
        background-color: #fdfbf7;
        color: #2c3e50;
    }
    
    /* Mengubah Latar Belakang Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f5efe6;
    }

    /* Kotak Hasil Analisis */
    .kotak-analisis {
        border-left: 6px solid #2ecc71;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #ffffff;
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
    /* Banner Gradasi Halaman Utama */
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

# ==============================================================================
# 3. FUNGSI HELPER & DATABASE
# ==============================================================================
def force_rerun():
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        st.warning("⚠️ Versi Streamlit usang. Silakan refresh halaman secara manual (F5).")

def render_tube(tinggi, warna, efek):
    e_html = ""
    if efek == "precipitate":
        e_html = "<div class='precipitate-layer'></div>"
    elif efek == "cloudy":
        e_html = "<div class='cloudy-layer'></div>"
    elif efek == "bubbles":
        e_html = "<div class='bubble-fx' style='left:20px;'></div><div class='bubble-fx' style='left:50px; animation-delay:0.5s;'></div>"
        
    return f"<div class='tube-wrap'><div class='tube-glass'><div class='tube-liquid' style='height:{tinggi}; background:{warna};'>{e_html}</div></div></div>"

# --- ENGINE LOGIKA DETEKSI JAUH LEBIH AKURAT & TERSENTRALISASI ---
def deteksi_golongan_dari_teks(nama_input):
    nama_lower = nama_input.lower().strip()
    proper_name = nama_input.strip()
    
    # 1. PERIKSA ASAM KARBOKSILAT & ESTER TERLEBIH DAHULU (Menghindari tabrakan akhiran -oat/-at)
    if any(k in nama_lower for k in ["asam", "karboksilat", "oat"]):
        return "Asam Karboksilat", "Asam Asetat", proper_name, "memiliki gugus fungsi karboksil (-COOH) yang memberikan sifat asam organik."
    elif any(k in nama_lower for k in ["asetat", "ester", "at", "propionat"]):
        return "Ester", "Etil Asetat", proper_name, "memiliki gugus fungsi alkoksi karbonil (-COOR)."
        
    # 2. PERIKSA ALDEHID & KETON (Menghindari tabrakan akhiran -al/-on)
    elif any(k in nama_lower for k in ["aldehid", "al", "formaldehida", "metanal", "etanal", "propanal"]):
        return "Aldehid", "Formaldehida", proper_name, "memiliki gugus fungsi karbonil di ujung rantai dengan satu hidrogen bebas (-CHO)."
    elif any(k in nama_lower for k in ["on", "aseton", "keton", "propanon", "butanon"]):
        return "Keton", "Aseton", proper_name, "memiliki gugus fungsi karbonil (C=O) yang diapit oleh dua gugus alkil/karbon."
    
    # 3. PERIKSA ALKOHOL TERSIER (Urutan paling atas di golongan alkohol agar 't-butil' tidak tertangkap 'butil')
    elif any(k in nama_lower for k in ["tersier", "t-butil", "2-metil-2-propanol", "2-metil-2-butanol"]):
        return "Alkohol Tersier", "t-butil alkohol", proper_name, "memiliki gugus fungsi hidroksil (-OH) yang terikat pada karbon alfa, di mana karbon alfa tersebut mengikat 3 atom karbon lain secara langsung."
    
    # 4. PERIKSA ALKOHOL SEKUNDER
    elif any(k in nama_lower for k in ["2-butanol", "2-propanol", "isopropanol", "sekunder", "3-pentanol", "2-pentanol"]):
        return "Alkohol Sekunder", "2-butanol", proper_name, "memiliki gugus fungsi hidroksil (-OH) yang terikat pada karbon alfa, di mana karbon alfa tersebut mengikat 2 atom karbon lain."
    
    # 5. PERIKSA ALKOHOL PRIMER (Menggunakan jaring pengaman akhiran 'ol' dan pencarian kata 'butanol')
    elif any(k in nama_lower for k in ["1-butanol", "metanol", "etanol", "propanol", "butil alkohol", "primer"]) or nama_lower.endswith("ol") or "butanol" in nama_lower:
        return "Alkohol Primer", "1-butanol", proper_name, "memiliki gugus fungsi hidroksil (-OH) yang terikat pada karbon alfa, di mana karbon alfa tersebut hanya mengikat 1 atom karbon lain."
    
    # 6. JIKA SEMUA FILTER GAGAL, BARU DIANGGAP ALKANA
    else:
        return "Alkana / Hidrokarbon Jenuh", "Heksana", proper_name, "tidak menunjukkan gugus fungsi reaktif oksigen, melainkan tersusun atas ikatan tunggal C-H dan C-C yang jenuh."

reagen_colors = {
    "Ceric Nitrat": "#facc15", 
    "Pereaksi Jones": "#f97316", 
    "Pereaksi Lucas": "#f8fafc", 
    "Pereaksi Lucas (Panas)": "#f8fafc", 
    "Na-Bisulfit": "#f8fafc", 
    "Pereaksi Fehling": "#3b82f6", 
    "Pereaksi Schiff": "#f8fafc",
    "Uji Iodoform": "#f8fafc",
    "Hidroksilamin (Uji Ester)": "#f8fafc",
    "Uji Barit (NaHCO3)": "#f8fafc"
}

flowchart_paths = {
    "1-butanol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas (Panas)"],
    "2-butanol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas (Panas)", "Uji Iodoform"],
    "t-butil alkohol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas"],
    "Formaldehida": ["Ceric Nitrat", "Na-Bisulfit", "Pereaksi Fehling", "Pereaksi Schiff"],
    "Aseton": ["Ceric Nitrat", "Na-Bisulfit", "Pereaksi Fehling", "Uji Iodoform"],
    "Etil Asetat": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)"],
    "Asam Asetat": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)", "Uji Barit (NaHCO3)"],
    "Heksana": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)", "Uji Barit (NaHCO3)"]
}

database_reaksi = {
    "1-butanol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3", 
            "alasan": "Keberadaan gugus hidroksil (-OH) bebas yang terikat pada karbon alfa membuat sampel ini dapat berinteraksi menggantikan ligan nitrat pada ion Cerium(IV), membentuk kompleks koordinasi berwarna merah ceri.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Pereaksi Jones": {
            "hasil": "(+) Hijau", 
            "reaksi": r"3 R-CH_2OH + 2 CrO_3 + 3 H_2SO_4 \rightarrow 3 R-CHO + Cr_2(SO_4)_3 + 6 H_2O", 
            "alasan": "Karena karbon alfa yang mengikat gugus -OH hanya berikatan dengan 1 atom karbon lain (alkohol primer), ia masih memiliki 2 hidrogen alfa bebas. Hal ini memungkinkannya dioksidasi kuat menjadi asam karboksilat, mereduksi Kromium(VI) jingga menjadi Kromium(III) hijau.", 
            "warna_akhir": "#10b981", "efek": "none"
        },
        "Pereaksi Lucas (Panas)": {
            "hasil": "(-) Bening", 
            "reaksi": r"R-CH_2OH + HCl \xrightarrow{ZnCl_2, \Delta} \text{Tidak terjadi endapan}", 
            "alasan": "Karena gugus -OH terikat pada karbon alfa yang hanya mengikat 1 atom karbon lain, pembentukan karbokation primer sangat tidak stabil. Akibatnya, reaksi substitusi nukleofilik tidak berjalan meski dibantu pemanasan.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        }
    },
    "2-butanol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3", 
            "alasan": "Adanya gugus -OH yang terikat pada struktur molekulnya memicu pembentukan ikatan koordinasi dengan logam Cerium pusat, menghasilkan warna kompleks merah.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Pereaksi Jones": {
            "hasil": "(+) Hijau", 
            "reaksi": r"3 R_2CH-OH + 2 CrO_3 + 3 H_2SO_4 \rightarrow 3 R_2C=O + Cr_2(SO_4)_3 + 6 H_2O", 
            "alasan": "Sampel adalah alkohol sekunder karena gugus -OH berada di karbon alfa yang mengikat 2 atom karbon lain. Karbon alfa ini masih memiliki 1 hidrogen bebas sehingga bisa dioksidasi oleh reagen Jones menjadi keton, disertai perubahan warna reagen menjadi hijau.", 
            "warna_akhir": "#10b981", "efek": "none"
        },
        "Pereaksi Lucas (Panas)": {
            "hasil": "(+) Emulsi Putih Kabur", 
            "reaksi": r"R_2CH-OH + HCl \xrightarrow{ZnCl_2} R_2CH-Cl \downarrow + H_2O", 
            "alasan": "Karena gugus -OH terikat pada karbon alfa yang memegang 2 atom karbon lain, ia membentuk karbokation sekunder dengan stabilitas sedang. Substitusi berjalan agak lambat dan membutuhkan bantuan panas untuk memisahkan alkil klorida cair yang mengeruhkan larutan menjadi emulsi kabur.", 
            "warna_akhir": "#e2e8f0", "efek": "cloudy"
        },
        "Uji Iodoform": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": r"R-CH(OH)-CH_3 + 4 I_2 + 6 NaOH \rightarrow CHI_3 \downarrow + R-COONa + 5 NaI + 5 H_2O", 
            "alasan": "Struktur alkohol sekunder ini memiliki gugus metil yang terikat langsung pada karbon alfa pengikat -OH (metil karbinol). Gugus metil tersebut dipotong oleh iodin dalam kondisi basa menjadi kristal iodoform kuning.", 
            "warna_akhir": "#fef08a", "efek": "precipitate"
        }
    },
    "t-butil alkohol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3", 
            "alasan": "Deteksi positif merah ceri terjadi karena adanya ligan aktif berupa gugus fungsi -OH yang berikatan langsung ke ion Cerium.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Pereaksi Jones": {
            "hasil": "(-) Tetap Jingga", 
            "reaksi": r"R_3C-OH + CrO_3 + H^+ \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Gugus -OH terikat pada karbon alfa yang sudah mengikat 3 atom karbon lain (alkohol tersier). Hal ini membuat karbon alfa tidak memiliki hidrogen sisa sama sekali, sehingga tidak dapat dioksidasi oleh reagen Jones.", 
            "warna_akhir": "#f97316", "efek": "none"
        },
        "Pereaksi Lucas": {
            "hasil": "(+) Emulsi Putih Kabur (Seketika)", 
            "reaksi": r"R_3C-OH + HCl \xrightarrow{ZnCl_2} R_3C-Cl \downarrow + H_2O", 
            "alasan": "Karena gugus -OH terikat pada karbon alfa yang mengikat 3 atom karbon lain, lepasnya gugus fungsi ini menghasilkan karbokation tersier yang sangat stabil. Reaksi substitusi berjalan seketika menghasilkan lapisan emulsi kabur dari cairan alkil klorida tanpa bantuan pemanasan.", 
            "warna_akhir": "#94a3b8", "efek": "cloudy"
        }
    },
    "Formaldehida": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", "reaksi": r"HCHO + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Sampel merupakan aldehid dan tidak memiliki gugus hidroksil bebas untuk bereaksi dengan Cerium.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(+) Endapan Putih", "reaksi": r"H-CHO + NaHSO_3 \rightarrow H_2C(OH)SO_3Na \downarrow", 
            "alasan": "Nukleofil bisulfit menyerang karbonil yang miskin elektron, membentuk garam padatan kristal.", "warna_akhir": "#ffffff", "efek": "precipitate"
        },
        "Pereaksi Fehling": {
            "hasil": "(+) Merah Bata", "reaksi": r"H-CHO + 2 Cu^{2+} + 5 OH^- \rightarrow H-COO^- + Cu_2O \downarrow + 3 H_2O", 
            "alasan": "Aldehid adalah reduktor kuat. Ia mereduksi Tembaga(II) sulfat biru menjadi endapan Tembaga(I) oksida (merah bata).", "warna_akhir": "#b91c1c", "efek": "precipitate"
        },
        "Pereaksi Schiff": {
            "hasil": "(+) Ungu / Magenta", "reaksi": r"\text{Aldehid} + \text{Reagen Schiff} \rightarrow \text{Kompleks warna magenta}", 
            "alasan": "Reaksi adisi spesifik yang memulihkan pewarna p-rosanilin hidroklorida.", "warna_akhir": "#d946ef", "efek": "none"
        }
    },
    "Aseton": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", "reaksi": r"CH_3COCH_3 + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Keton tidak memiliki gugus hidroksil alkoholik.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(+) Endapan Putih", "reaksi": r"CH_3-CO-CH_3 + NaHSO_3 \rightarrow (CH_3)_2C(OH)SO_3Na \downarrow", 
            "alasan": "Sampel masih memiliki halangan sterik rendah, sehingga bisa mengalami reaksi adisi membentuk garam bisulfit.", "warna_akhir": "#ffffff", "efek": "precipitate"
        },
        "Pereaksi Fehling": {
            "hasil": "(-) Tetap Biru", "reaksi": r"CH_3-CO-CH_3 + Cu^{2+} \rightarrow \text{Tidak direduksi}", 
            "alasan": "Keton tidak memiliki atom hidrogen pada karbon pengikat oksigen sehingga tidak memiliki sifat reduktor.", "warna_akhir": "#3b82f6", "efek": "none"
        },
        "Uji Iodoform": {
            "hasil": "(+) Endapan Kuning", "reaksi": r"CH_3-CO-CH_3 + 3 I_2 + 4 NaOH \rightarrow CHI_3 \downarrow + CH_3COONa + 3 NaI + 3 H_2O", 
            "alasan": "Atom hidrogen alfa pada metil keton sangat asam, tersubstitusi oleh Iodin lalu putus membentuk Iodoform kuning.", "warna_akhir": "#fef08a", "efek": "precipitate"
        }
    },
    "Etil Asetat": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", "reaksi": r"\text{Ester} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Gugus ester tidak bereaksi dengan uji alkohol.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", "reaksi": r"\text{Ester} + NaHSO_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Resonansi pasangan elektron bebas dari gugus alkoksi menstabilkan karbon karbonil, menjadikannya tidak reaktif terhadap nukleofil lemah.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(+) Merah Violet", 
            "reaksi": r"\text{1. } R-COOR' + NH_2OH \rightarrow R-CONHOH + R'OH \quad \text{2. } 3 R-CONHOH + FeCl_3 \rightarrow Fe(R-CONHO)_3 + 3 HCl", 
            "alasan": "Ester diubah oleh hidroksilamin menjadi asam hidroksamat yang dapat mengikat ion besi(III) menghasilkan kompleks berwarna violet.", 
            "warna_akhir": "#c026d3", "efek": "none"
        }
    },
    "Asam Asetat": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", "reaksi": r"CH_3COOH + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Oksigen karboksil ditarik oleh resonansi ikatan rangkap karbonil, menjadikannya kurang nukleofilik untuk berikatan dengan Cerium.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", "reaksi": r"CH_3COOH + NaHSO_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Bukan senyawa golongan aldehid atau keton.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(-) Bening", "reaksi": r"CH_3COOH + NH_2OH + FeCl_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Bukan ester. Asam karboksilat tidak memicu pembentukan asam hidroksamat reaktif di kondisi ini.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Barit (NaHCO3)": {
            "hasil": "(+) Gelembung & Keruh", 
            "reaksi": r"\text{1. } CH_3COOH + NaHCO_3 \rightarrow CH_3COONa + H_2O + CO_2 \uparrow \quad \text{2. } CO_2 + Ba(OH)_2 \rightarrow BaCO_3 \downarrow + H_2O", 
            "alasan": "Asam karboksilat mendonasikan proton untuk mengurai bikarbonat. Gas karbon dioksida yang terlepas bereaksi dengan air barit membentuk barium karbonat yang keruh.", 
            "warna_akhir": "#f8fafc", "efek": "bubbles"
        }
    },
    "Heksana": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", "reaksi": r"\text{Heksana} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}", "alasan": "Tidak ada gugus fungsi -OH.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", "reaksi": r"\text{Heksana} + NaHSO_3 \rightarrow \text{Tidak bereaksi}", "alasan": "Tidak ada gugus karbonil.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(-) Bening", "reaksi": r"\text{Heksana} + NH_2OH \rightarrow \text{Tidak bereaksi}", "alasan": "Bukan gugus ester.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Barit (NaHCO3)": {
            "hasil": "(-) Bening", "reaksi": r"\text{Heksana} + NaHCO_3 \rightarrow \text{Tidak bereaksi}", 
            "alasan": "Senyawa hidrokarbon alifatik (jenuh) bersifat non-polar dan inert. Karena secara berturut-turut gagal bereaksi di seluruh uji fungsional, ini membuktikan senyawanya adalah alkana.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        }
    }
}

# Inisialisasi State Management
if 'test_started' not in st.session_state:
    st.session_state.test_started = False
if 'senyawa_uji' not in st.session_state:
    st.session_state.senyawa_uji = ""
if 'golongan_terdeteksi' not in st.session_state:
    st.session_state.golongan_terdeteksi = ""
if 'alasan_golongan' not in st.session_state:
    st.session_state.alasan_golongan = ""
if 'senyawa_model' not in st.session_state:
    st.session_state.senyawa_model = ""
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'log_history' not in st.session_state:
    st.session_state.log_history = []
if 'trigger_animation' not in st.session_state:
    st.session_state.trigger_animation = False

# ==============================================================================
# 4. SIDEBAR NAVIGASI
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022607.png", width=75)
    st.title("OrganicChem v1.0")
    st.write("🔬 *E-Learning & Lab Simulator*")
    st.markdown("---")
    
    pilihan_halaman = st.sidebar.radio(
        "Navigasi Menu:",
        [
            "🏠 HALAMAN UTAMA", 
            "📘 BAB I. HIDROKARBON", 
            "📙 BAB II. ALKOHOL, ETER, DAN FENOL", 
            "📗 BAB III. ALDEHID DAN KETON", 
            "📕 BAB IV. ASAM KARBOKSILAT DAN DERIVATNYA", 
            "🔬 POST TEST"
        ]
    )
    st.markdown("---")
    st.caption("E-Learning Kimia Organik | © 2026")

# ==============================================================================
# 5. LOGIKA KONTEN TIAP HALAMAN
# ==============================================================================

# --- HALAMAN UTAMA ---
if pilihan_halaman == "🏠 HALAMAN UTAMA":
    st.markdown("""
        <div class="banner-utama">
            <h1 style='color: white; margin-bottom: 5px; font-weight: 700;'>Selamat Datang di OrganicChem! 👋</h1>
            <p style='font-size: 1.2em; opacity: 0.95;'>Platform Media Pembelajaran Mandiri & Simulasi Identifikasi Gugus Fungsi</p>
        </div>
    """, unsafe_allow_html=True)
    st.subheader("💡 Tentang Platform Ini")
    st.write("Platform ini dirancang untuk membantu pemahaman materi praktikum Kimia Organik secara interaktif.")

# --- BAB I ---
elif pilihan_halaman == "📘 BAB I. HIDROKARBON":
    st.title("📘 BAB I. HIDROKARBON")
    st.write("Materi Hidrokarbon Jenuh, Tidak Jenuh, dan Aromatik.")

# --- BAB II ---
elif pilihan_halaman == "📙 BAB II. ALKOHOL, ETER, DAN FENOL":
    st.title("📙 BAB II. ALKOHOL, ETER, DAN FENOL")
    st.write("Materi Karakteristik Kimia Golongan Alkohol Primer, Sekunder, Tersier, dan Fenol.")

# --- BAB III ---
elif pilihan_halaman == "📗 BAB III. ALDEHID DAN KETON":
    st.title("📗 BAB III. ALDEHID DAN KETON")
    st.write("Materi Gugus Fungsi Karbonil, Uji Fehling, Tollens, dan Adisi Bisulfit.")

# --- BAB IV ---
elif pilihan_halaman == "📕 BAB IV. ASAM KARBOKSILAT DAN DERIVATNYA":
    st.title("📕 BAB IV. ASAM KARBOKSILAT DAN DERIVATNYA")
    st.write("Materi Asam Karboksilat dan Uji Reaktivitas Derivat Ester Hidroksamat.")

# --- 🔬 POST TEST ---
elif pilihan_halaman == "🔬 POST TEST":
    st.title("🔀 Smart Flowchart Auto-Analyzer (Step-by-Step)")
    st.write("Ketikkan nama senyawa organik secara bebas. Sistem akan mengidentifikasi golongannya secara instan berdasarkan struktur kata kunci yang valid.")

    if not st.session_state.test_started:
        st.divider()
        input_senyawa_user = st.text_input("✍️ Masukkan Nama Senyawa Kimia Organik:", placeholder="Misal: 2-metilbutanol, t-butil alkohol, propanon...")
        
        if st.button("Mulai Identifikasi 🚀", type="primary"):
            if not input_senyawa_user.strip():
                st.warning("⚠️ Harap ketikkan nama senyawa terlebih dahulu!")
            else:
                golongan, model_key, proper_name, alasan = deteksi_golongan_dari_teks(input_senyawa_user)
                
                st.session_state.test_started = True
                st.session_state.senyawa_uji = proper_name
                st.session_state.golongan_terdeteksi = golongan
                st.session_state.alasan_golongan = alasan
                st.session_state.senyawa_model = model_key
                st.session_state.current_step = 0
                st.session_state.log_history = []
                st.session_state.trigger_animation = True
                force_rerun()

    else:
        st.write("---")
        senyawa = st.session_state.senyawa_uji
        golongan = st.session_state.golongan_terdeteksi
        alasan_golongan = st.session_state.alasan_golongan
        model_key = st.session_state.senyawa_model
        
        st.markdown(f"""
        <div class="kotak-analisis">
            <div class="label-analisis">🔍 HASIL DETEKSI GOLONGAN AWAL</div>
            Senyawa <b>"{senyawa}"</b> terdeteksi masuk ke dalam golongan <b>{golongan.upper()}</b>.<br>
            <span style='color:#555;'><b>Alasan:</b> {alasan_golongan}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        urutan = flowchart_paths[model_key]

        col_visual, col_log = st.columns([1, 2.5])
        
        with col_visual:
            st.markdown("<h4 style='text-align: center;'>Visual Lab</h4>", unsafe_allow_html=True)
            tube_placeholder = st.empty() 
            status_placeholder = st.empty()
            
        with col_log:
            st.markdown("#### 📑 Logbook & Analisis Teoritis")
            log_container = st.container()

        with log_container:
            for log in st.session_state.log_history:
                if "(+)" in log["hasil"]:
                    st.success(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Reaksi:**")
                    st.latex(log['reaksi'])
                    st.write(f"**Pembahasan:**\n{log['alasan']}")
                else:
                    st.error(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Reaksi:**")
                    st.latex(log['reaksi'])
                    st.write(f"**Pembahasan:**\n{log['alasan']}")

        # ---------------- LOGIKA ANIMASI & TOMBOL NEXT ----------------
        if st.session_state.trigger_animation and st.session_state.current_step < len(urutan):
            pereaksi = urutan[st.session_state.current_step]
            
            tube_placeholder.markdown(render_tube("30%", "#f1f5f9", "none"), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center;'><em>Menyiapkan sampel untuk {pereaksi}...</em></div>", unsafe_allow_html=True)
            time.sleep(1.0)
            
            warna_reagen = reagen_colors[pereaksi]
            tube_placeholder.markdown(render_tube("65%", warna_reagen, "none"), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center;'><em>Meneteskan {pereaksi}...</em></div>", unsafe_allow_html=True)
            time.sleep(1.5)
            
            res = database_reaksi[model_key][pereaksi]
            tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
            status_placeholder.markdown("<div style='text-align:center; font-weight:bold;'>Melihat hasil reaksi...</div>", unsafe_allow_html=True)
            time.sleep(1.2)
            
            st.session_state.log_history.append({
                "step": st.session_state.current_step + 1,
                "pereaksi": pereaksi,
                "hasil": res["hasil"],
                "reaksi": res["reaksi"],
                "alasan": res["alasan"]
            })
            
            st.session_state.current_step += 1
            st.session_state.trigger_animation = False
            force_rerun()

        elif not st.session_state.trigger_animation:
            if st.session_state.current_step > 0:
                last_pereaksi = urutan[st.session_state.current_step - 1]
                res = database_reaksi[model_key][last_pereaksi]
                tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
            
            if st.session_state.current_step < len(urutan):
                next_pereaksi = urutan[st.session_state.current_step]
                status_placeholder.markdown("<div style='text-align:center; color:#475569;'>Menunggu konfirmasi pembacaan...</div>", unsafe_allow_html=True)
                
                with col_visual:
                    st.write("") 
                    if st.button(f"Lanjutkan ke Uji {next_pereaksi} ⏭️", use_container_width=True, type="primary"):
                        st.session_state.trigger_animation = True
                        force_rerun()
                        
            else:
                status_placeholder.markdown("<div style='text-align:center; font-weight:bold; color:#10b981;'>Seluruh tahap identifikasi selesai!</div>", unsafe_allow_html=True)
                with log_container:
                    st.info(f"🎉 **KESIMPULAN:** Berdasarkan alur eliminasi dan uji spesifik, senyawa yang Anda input ({senyawa}) terkonfirmasi sah memiliki karakteristik reaktivitas golongan **{golongan.upper()}**.")
                
                with col_visual:
                    st.write("")
                    if st.button("🔄 Uji Senyawa Lain", use_container_width=True):
                        st.session_state.test_started = False
                        force_rerun()
