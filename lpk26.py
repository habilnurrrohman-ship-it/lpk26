import streamlit as st
import time

# ==============================================================================
# 1. KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(
    page_title="OrganicChem | Edu-Lab Platform",
    page_icon="🧪",
    layout="wide"
)

# ==============================================================================
# 2. CUSTOM CSS INTERAKTIF
# ==============================================================================
st.markdown("""
    <style>
    .stApp {
        background-color: #fdfbf7;
        color: #2c3e50;
    }
    [data-testid="stSidebar"] {
        background-color: #f5efe6;
    }
    .banner-utama {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        padding: 35px;
        border-radius: 12px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(56, 239, 125, 0.2);
    }
    .kartu-materi {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #11998e;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
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
    .precipitate-layer { position: absolute; bottom: 0; left: 0; right: 0; height: 40px; background-color: rgba(0,0,0,0.4); }
    .cloudy-layer { position: absolute; top: 0; bottom: 0; left: 0; right: 0; background-color: rgba(255,255,255,0.6); }
    .bubble-fx { position: absolute; background: rgba(0,0,0,0.2); border-radius: 50%; width: 8px; height: 8px; animation: floatUp 1.8s infinite ease-in; }
    @keyframes floatUp { 0% { bottom: 0px; opacity: 1; } 100% { bottom: 250px; opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. FUNGSI HELPER & ENGINE DETEKSI GOLONGAN
# ==============================================================================
def force_rerun():
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()

def render_tube(tinggi, warna, efek):
    e_html = ""
    if efek == "precipitate":
        e_html = "<div class='precipitate-layer'></div>"
    elif efek == "cloudy":
        e_html = "<div class='cloudy-layer'></div>"
    elif efek == "bubbles":
        e_html = "<div class='bubble-fx' style='left:20px;'></div><div class='bubble-fx' style='left:50px; animation-delay:0.5s;'></div>"
    return f"<div class='tube-wrap'><div class='tube-glass'><div class='tube-liquid' style='height:{tinggi}; background:{warna};'>{e_html}</div></div></div>"

def deteksi_golongan_senyawa(nama_senyawa):
    nama_lower = nama_senyawa.lower().strip()
    proper_name = nama_senyawa.strip()
    if not nama_lower:
        return "Alkana / Hidrokarbon Jenuh", "Alkana / Hidrokarbon Jenuh", proper_name
        
    if any(k in nama_lower for k in ["1-butil", "1-butanol", "metanol", "etanol", "propanol", "primer"]):
        return "Alkohol Primer", "Alkohol Primer", proper_name
    elif any(k in nama_lower for k in ["2-butanol", "2-propanol", "isopropanol", "sekunder"]):
        return "Alkohol Sekunder", "Alkohol Sekunder", proper_name
    elif any(k in nama_lower for k in ["tersier", "t-butil", "2-metil-2-propanol"]):
        return "Alkohol Tersier", "Alkohol Tersier", proper_name
    elif any(k in nama_lower for k in ["aldehid", "al", "formaldehida", "metanal", "etanal"]):
        return "Aldehid", "Aldehid", proper_name
    elif any(k in nama_lower for k in ["on", "aseton", "keton", "propanon"]):
        return "Keton", "Keton", proper_name
    elif any(k in nama_lower for k in ["asetat", "ester", "at"]):
        return "Ester", "Ester", proper_name
    elif any(k in nama_lower for k in ["asam", "karboksilat", "oat"]):
        return "Asam Karboksilat", "Asam Karboksilat", proper_name
    else:
        return "Alkana / Hidrokarbon Jenuh", "Alkana / Hidrokarbon Jenuh", proper_name

# ==============================================================================
# 4. DATABASE REAKSI & ALUR FLOWCHART
# ==============================================================================
reagen_colors = {
    "Ceric Nitrat": "#facc15", "Pereaksi Jones": "#f97316", "Pereaksi Lucas": "#f8fafc", 
    "Pereaksi Lucas (Panas)": "#f8fafc", "Na-Bisulfit": "#f8fafc", "Pereaksi Fehling": "#3b82f6", 
    "Pereaksi Schiff": "#f8fafc", "Uji Iodoform": "#f8fafc", "Hidroksilamin (Uji Ester)": "#f8fafc",
    "Uji Barit (NaHCO3)": "#f8fafc"
}

flowchart_paths = {
    "Alkohol Primer": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas (Panas)"],
    "Alkohol Sekunder": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas (Panas)", "Uji Iodoform"],
    "Alkohol Tersier": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas"],
    "Aldehid": ["Ceric Nitrat", "Na-Bisulfit", "Pereaksi Fehling", "Pereaksi Schiff"],
    "Keton": ["Ceric Nitrat", "Na-Bisulfit", "Pereaksi Fehling", "Uji Iodoform"],
    "Ester": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)"],
    "Asam Karboksilat": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)", "Uji Barit (NaHCO3)"],
    "Alkana / Hidrokarbon Jenuh": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)", "Uji Barit (NaHCO3)"]
}

def dapatkan_data_reaksi(golongan, nama_spesifik):
    database = {
        "Alkohol Primer": {
            "Ceric Nitrat": {"hasil": "(+) Merah Ceri", "reaksi": r"R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3", "alasan": f"Gugus -OH bebas pada {nama_spesifik} bereaksi menggantikan ligan nitrat pada ion Cerium(IV) membentuk senyawa kompleks koordinasi berwarna merah ceri sehingga merupakan golongan alkohol primer.", "warna_akhir": "#ef4444", "efek": "none"},
            "Pereaksi Jones": {"hasil": "(+) Hijau", "reaksi": r"3 R-CH_2OH + 2 CrO_3 + 3 H_2SO_4 \rightarrow 3 R-CHO + Cr_2(SO_4)_3 + 6 H_2O", "alasan": f"{nama_spesifik} merupakan golongan alkohol primer yang memiliki atom hidrogen alfa. Dioksidasi kuat menjadi asam karboksilat, sedangkan Kromium(VI) jingga tereduksi menjadi Kromium(III) hijau.", "warna_akhir": "#10b981", "efek": "none"},
            "Pereaksi Lucas (Panas)": {"hasil": "(-) Bening", "reaksi": r"R-CH_2OH + HCl \xrightarrow{ZnCl_2, \Delta} \text{Tidak terjadi endapan}", "alasan": f"Karbokation dari {nama_spesifik} sangat tidak stabil karena strukturnya sebagai alkohol primer. Reaksi tidak berjalan membentuk alkil klorida yang tak larut meski dipanaskan.", "warna_akhir": "#f8fafc", "efek": "none"}
        },
        "Alkohol Sekunder": {
            "Ceric Nitrat": {"hasil": "(+) Merah Ceri", "reaksi": r"R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3", "alasan": f"Ikatan koordinasi terbentuk antara atom oksigen pada gugus hidroksil sekunder milik {nama_spesifik} dengan logam Cerium yang mengonfirmasi sifat alkohol sekunder.", "warna_akhir": "#ef4444", "efek": "none"},
            "Pereaksi Jones": {"hasil": "(+) Hijau", "reaksi": r"3 R_2CH-OH + 2 CrO_3 + 3 H_2SO_4 \rightarrow 3 R_2C=O + Cr_2(SO_4)_3 + 6 H_2O", "alasan": f"Sebagai alkohol sekunder, {nama_spesifik} dioksidasi oleh reagen Jones menjadi senyawa keton. Cr(VI) jingga tereduksi ke Cr(III) hijau.", "warna_akhir": "#10b981", "efek": "none"},
            "Pereaksi Lucas (Panas)": {"hasil": "(+) Emulsi Putih", "reaksi": r"R_2CH-OH + HCl \xrightarrow{ZnCl_2} R_2CH-Cl \downarrow + H_2O", "alasan": f"Karbokation sekunder dari {nama_spesifik} memiliki stabilitas menengah. Dibutuhkan pemanasan untuk mempercepat pembentukan cairan alkil klorida yang mengemulsi.", "warna_akhir": "#e2e8f0", "efek": "cloudy"},
            "Uji Iodoform": {"hasil": "(+) Endapan Kuning", "reaksi": r"R-CH(OH)-CH_3 + 4 I_2 + 6 NaOH \rightarrow CHI_3 \downarrow + R-COONa + 5 NaI + 5 H_2O", "alasan": f"{nama_spesifik} memiliki struktur metil karbinol khas alkohol sekunder tertentu yang dapat dioksidasi iodin menjadi metil keton, lalu membentuk kristal iodoform kuning.", "warna_akhir": "#fef08a", "efek": "precipitate"}
        },
        "Alkohol Tersier": {
            "Ceric Nitrat": {"hasil": "(+) Merah Ceri", "reaksi": r"R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3", "alasan": f"Terdapat gugus -OH bebas pada {nama_spesifik} yang dapat berikatan koordinasi membentuk kompleks merah, membuktikan senyawa ini adalah alkohol tersier.", "warna_akhir": "#ef4444", "efek": "none"},
            "Pereaksi Jones": {"hasil": "(-) Tetap Jingga", "reaksi": r"R_3C-OH + CrO_3 + H^+ \rightarrow \text{Tidak bereaksi}", "alasan": f"{nama_spesifik} bertindak sebagai alkohol tersier yang tidak memiliki atom hidrogen alfa, sehingga strukturnya sangat stabil dan tidak dapat dioksidasi.", "warna_akhir": "#f97316", "efek": "none"},
            "Pereaksi Lucas": {"hasil": "(+) Emulsi Putih (Seketika)", "reaksi": r"R_3C-OH + HCl \xrightarrow{ZnCl_2} R_3C-Cl \downarrow + H_2O", "alasan": f"{nama_spesifik} membentuk karbokation tersier yang sangat stabil. Reaksi substitusi dengan klorida terjadi seketika menghasilkan kabut emulsi alkil klorida.", "warna_akhir": "#94a3b8", "efek": "cloudy"}
        },
        "Aldehid": {
            "Ceric Nitrat": {"hasil": "(-) Kuning", "reaksi": r"\text{Aldehid} + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", "alasan": f"{nama_spesifik} merupakan senyawa golongan aldehid dan tidak memiliki gugus hidroksil bebas alkoholik.", "warna_akhir": "#facc15", "efek": "none"},
            "Na-Bisulfit": {"hasil": "(+) Endapan Putih", "reaksi": r"R-CHO + NaHSO_3 \rightarrow R-CH(OH)SO_3Na \downarrow", "alasan": f"Nukleofil bisulfit menyerang gugus karbonil {nama_spesifik} yang miskin elektron, membentuk produk adisi berupa garam padatan kristal putih.", "warna_akhir": "#ffffff", "efek": "precipitate"},
            "Pereaksi Fehling": {"hasil": "(+) Merah Bata", "reaksi": r"R-CHO + 2 Cu^{2+} + 5 OH^- \rightarrow R-COO^- + Cu_2O \downarrow + 3 H_2O", "alasan": f"Gugus aldehid pada {nama_spesifik} bersifat sebagai reduktor kuat. Ia mereduksi Tembaga(II) biru menjadi endapan Tembaga(I) oksida merah bata.", "warna_akhir": "#b91c1c", "efek": "precipitate"},
            "Pereaksi Schiff": {"hasil": "(+) Ungu / Magenta", "reaksi": r"\text{Aldehid} + \text{Reagen Schiff} \rightarrow \text{Kompleks warna magenta}", "alasan": f"Terjadi reaksi adisi spesifik antara gugus aldehid {nama_spesifik} yang memulihkan kembali pewarna p-rosanilin hidroklorida menjadi magenta.", "warna_akhir": "#d946ef", "efek": "none"}
        },
        "Keton": {
            "Ceric Nitrat": {"hasil": "(-) Kuning", "reaksi": r"\text{Keton} + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}", "alasan": f"Senyawa {nama_spesifik} tergolong dalam kelompok keton sehingga tidak memiliki gugus fungsi hidroksil.", "warna_akhir": "#facc15", "efek": "none"},
            "Na-Bisulfit": {"hasil": "(+) Endapan Putih", "reaksi": r"R-CO-CH_3 + NaHSO_3 \rightarrow R-C(OH)(SO_3Na)CH_3 \downarrow", "alasan": f"Gugus keton pada {nama_spesifik} memiliki halangan sterik rendah sehingga dapat mengalami adisi nukleofilik membentuk garam bisulfit berbentuk kristal.", "warna_akhir": "#ffffff", "efek": "precipitate"},
            "Pereaksi Fehling": {"hasil": "(-) Tetap Biru", "reaksi": r"\text{Keton} + Cu^{2+} \rightarrow \text{Tidak direduksi}", "alasan": f"Keton seperti {nama_spesifik} tidak memiliki atom hidrogen langsung pada karbonil sehingga tidak bersifat reduktor terhadap pereaksi Fehling.", "warna_akhir": "#3b82f6", "efek": "none"},
            "Uji Iodoform": {"hasil": "(+) Endapan Kuning", "reaksi": r"R-CO-CH_3 + 3 I_2 + 4 NaOH \rightarrow CHI_3 \downarrow + R-COONa + 3 NaI + 3 H_2O", "alasan": f"{nama_spesifik} memiliki gugus metil keton. Hidrogen alfa digantikan oleh Iodin dalam suasana basa lalu putus membentuk haloform (iodoform kuning).", "warna_akhir": "#fef08a", "efek": "precipitate"}
        },
        "Ester": {
            "Ceric Nitrat": {"hasil": "(-) Kuning", "reaksi": r"\text{Ester} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}", "alasan": f"Gugus fungsi ester pada {nama_spesifik} tidak responsif terhadap uji reagen Ceric Nitrat.", "warna_akhir": "#facc15", "efek": "none"},
            "Na-Bisulfit": {"hasil": "(-) Bening", "reaksi": r"\text{Ester} + NaHSO_3 \rightarrow \text{Tidak bereaksi}", "alasan": f"Resonansi pasangan elektron bebas dari gugus alkoksi menstabilkan karbon karbonil pada {nama_spesifik} sehingga tidak reaktif terhadap bisulfit.", "warna_akhir": "#f8fafc", "efek": "none"},
            "Hidroksilamin (Uji Ester)": {"hasil": "(+) Merah Violet", "reaksi": r"\text{1. } R-COOR' + NH_2OH \rightarrow R-CONHOH + R'OH \quad \text{2. } 3 R-CONHOH + FeCl_3 \rightarrow Fe(R-CONHO)_3 + 3 HCl", "alasan": f"Senyawa {nama_spesifik} diubah oleh hidroksilamin menjadi asam hidroksamat, yang kemudian mengkelat ion Fe3+ membentuk senyawa kompleks koordinasi warna violet khas golongan ester.", "warna_akhir": "#c026d3", "efek": "none"}
        },
        "Asam Karboksilat": {
            "Ceric Nitrat": {"hasil": "(-) Kuning", "reaksi": r"\text{Asam Karboksilat} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}", "alasan": f"Oksigen karboksil pada {nama_spesifik} kurang nukleofilik akibat terjadinya resonansi ikatan rangkap karbonil.", "warna_akhir": "#facc15", "efek": "none"},
            "Na-Bisulfit": {"hasil": "(-) Bening", "reaksi": r"\text{Asam Karboksilat} + NaHSO_3 \rightarrow \text{Tidak bereaksi}", "alasan": f"{nama_spesifik} merupakan asam karboksilat, bukan golongan aldehid ataupun keton.", "warna_akhir": "#f8fafc", "efek": "none"},
            "Hidroksilamin (Uji Ester)": {"hasil": "(-) Bening", "reaksi": r"\\text{Asam Karboksilat} + NH_2OH \\rightarrow \\text{Tidak bereaksi}", "alasan": f"Asam karboksilat bebas pada {nama_spesifik} tidak memicu pembentukan asam hidroksamat dalam uji ester.", "warna_akhir": "#f8fafc", "efek": "none"},
            "Uji Barit (NaHCO3)": {"hasil": "(+) Gelembung & Keruh", "reaksi": r"\text{1. } R-COOH + NaHCO_3 \rightarrow R-COONa + H_2O + CO_2 \uparrow \quad \text{2. } CO_2 + Ba(OH)_2 \rightarrow BaCO_3 \downarrow + H_2O", "alasan": f"Gugus asam pada {nama_spesifik} mendonasikan proton untuk mengurai bikarbonat menjadi gas CO2. Mengonfirmasi sifat senyawa sebagai asam karboksilat.", "warna_akhir": "#f8fafc", "efek": "bubbles"}
        },
        "Alkana / Hidrokarbon Jenuh": {
            "Ceric Nitrat": {"hasil": "(-) Kuning", "reaksi": r"\text{Alkana} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}", "alasan": f"{nama_spesifik} merupakan senyawa hidrokarbon jenuh dan tidak memiliki gugus fungsi reaktif.", "warna_akhir": "#facc15", "efek": "none"},
            "Na-Bisulfit": {"hasil": "(-) Bening", "reaksi": r"\text{Alkana} + NaHSO_3 \rightarrow \text{Tidak bereaksi}", "alasan": f"{nama_spesifik} tidak memiliki gugus karbonil aktif.", "warna_akhir": "#f8fafc", "efek": "none"},
            "Hidroksilamin (Uji Ester)": {"hasil": "(-) Bening", "reaksi": r"\text{Alkana} + NH_2OH \rightarrow \text{Tidak bereaksi}", "alasan": f"{nama_spesifik} bukan merupakan golongan ester.", "warna_akhir": "#f8fafc", "efek": "none"},
            "Uji Barit (NaHCO3)": {"hasil": "(-) Bening", "reaksi": r"\text{Alkana} + NaHCO_3 \rightarrow \text{Tidak bereaksi}", "alasan": f"Senyawa {nama_spesifik} bersifat non-polar dan inert. Karena secara beruntun gagal bereaksi di seluruh uji eliminasi, ini mengonfirmasi sampel adalah alkana.", "warna_akhir": "#f8fafc", "efek": "none"}
        }
    }
    return database.get(golongan, database["Alkana / Hidrokarbon Jenuh"])

# ==============================================================================
# 5. STATE MANAGEMENT
# ==============================================================================
if 'test_started' not in st.session_state: st.session_state.test_started = False
if 'nama_input_user' not in st.session_state: st.session_state.nama_input_user = ""
if 'senyawa_model' not in st.session_state: st.session_state.senyawa_model = ""
if 'golongan_terdeteksi' not in st.session_state: st.session_state.golongan_terdeteksi = ""
if 'current_step' not in st.session_state: st.session_state.current_step = 0
if 'log_history' not in st.session_state: st.session_state.log_history = []
if 'trigger_animation' not in st.session_state: st.session_state.trigger_animation = False

# ==============================================================================
# 6. SIDEBAR NAVIGASI
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022607.png", width=70)
    st.title("OrganicChem Pro")
    st.write("🔬 *Interactive Learning Platform*")
    st.markdown("---")
    
    pilihan_halaman = st.radio(
        "Pilih Modul Pembelajaran:", 
        ["🏠 HALAMAN UTAMA", "📖 MODUL MATERI GUGUS FUNGSI", "🕵️ CASUS STUDY (PROBLEM SOLVING)", "🔬 SMART LAB SIMULATOR"]
    )
    st.markdown("---")
    st.caption("E-Learning Kimia Organik | © 2026")

# ==============================================================================
# 7. KONTEN HALAMAN
# ==============================================================================

# --- HALAMAN UTAMA ---
if pilihan_halaman == "🏠 HALAMAN UTAMA":
    st.markdown("""
        <div class="banner-utama">
            <h1 style='color: white; margin-bottom: 5px; font-weight: 700;'>Selamat Datang di OrganicChem! 👋</h1>
            <p style='font-size: 1.2em; opacity: 0.95;'>Platform Integrasi Teori, Studi Kasus, dan Simulasi Reaksi Identifikasi Senyawa Organik</p>
        </div>
    """, unsafe_allow_html=True)
    st.subheader("💡 Fitur Utama Aplikasi:")
    st.markdown("""
    *   **📖 Modul Materi Gugus Fungsi**: Berisi rangkuman materi ringkas mengenai prinsip reaksi uji kimia kualitatif.
    *   **🕵️ Case Study (Problem Solving)**: Latihan pemecahan masalah analitis komprehensif berdasarkan data eksperimen nyata.
    *   **🔬 Smart Lab Simulator**: Fitur mutakhir untuk menginput nama senyawa secara bebas untuk mendeteksi golongan serta mensimulasikan uji eliminasi visual secara runtut.
    """)

# --- MODUL MATERI ---
elif pilihan_halaman == "📖 MODUL MATERI GUGUS FUNGSI":
    st.title("📖 Teori Dasar Identifikasi Gugus Fungsi")
    st.write("Pelajari prinsip dasar uji kualitatif eliminasi yang digunakan di laboratorium kimia organik.")
    st.divider()
    tabs = st.tabs(["🧪 Uji Alkohol", "🍊 Uji Karbonil", "💎 Uji Ester & Asam"])
    
    with tabs[0]:
        st.markdown("""
        <div class='kartu-materi'>
            <h3>1. Uji Ceric Amonium Nitrat</h3>
            <p>Digunakan untuk mendeteksi keberadaan gugus <b>hidroksil (-OH)</b> alkoholik bebas. Hasil positif ditunjukkan dengan perubahan warna larutan dari kuning menjadi <b>merah ceri</b>.</p>
        </div>
        <div class='kartu-materi'>
            <h3>2. Pereaksi Lucas (ZnCl₂ dalam HCl)</h3>
            <p>Membedakan struktur alkohol berdasarkan kecepatan pembentukan emulsi keruh (alkil klorida): Tersier (seketika), Sekunder (5-10 menit/hangat), Primer (tidak bereaksi).</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tabs[1]:
        st.markdown("""
        <div class='kartu-materi'>
            <h3>1. Uji Natrium Bisulfit (NaHSO₃)</h3>
            <p>Uji umum untuk mendeteksi gugus <b>karbonil (C=O)</b> rendah halangan sterik (aldehid & metil keton). Membentuk kristal padat putih.</p>
        </div>
        <div class='kartu-materi'>
            <h3>2. Pereaksi Fehling</h3>
            <p>Membedakan aldehid dengan keton. Aldehid bertindak sebagai reduktor kuat menghasilkan endapan <b>merah bata (Cu₂O)</b>.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with tabs[2]:
        st.markdown("""
        <div class='kartu-materi'>
            <h3>1. Uji Hidroksamat (Untuk Ester)</h3>
            <p>Ester diubah menjadi asam hidroksamat yang mengkelat ion Fe³⁺ menghasilkan kompleks berwarna <b>merah violet</b>.</p>
        </div>
        <div class='kartu-materi'>
            <h3>2. Uji Bikarbonat (Asam Karboksilat)</h3>
            <p>Asam karboksilat membebaskan gas CO₂ saat direaksikan dengan NaHCO₃, yang kemudian mengeruhkan larutan air barit.</p>
        </div>
        """, unsafe_allow_html=True)

# --- CASE STUDY ---
elif pilihan_halaman == "🕵️ CASUS STUDY (PROBLEM SOLVING)":
    st.title("🕵️ Studi Kasus: Detektif Laboratorium Kimia")
    st.divider()
    st.info("📋 **PROBLEM:** Sebuah botol sampel kehilangan labelnya. Hasil uji kualitatif:\n1. Uji Ceric Nitrat ➔ (-) Tetap Kuning\n2. Uji Na-Bisulfit ➔ (+) Terbentuk endapan kristal putih\n3. Pereaksi Fehling ➔ (-) Larutan tetap biru jernih\n4. Uji Iodoform ➔ (+) Terbentuk endapan kuning pekat")
    
    jawaban = st.radio("Berdasarkan data eliminasi di atas, senyawa apakah yang berada di dalam botol tersebut?", [
        "A. 1-Butanol (Alkohol Primer)",
        "B. Formaldehida (Aldehid)",
        "C. Aseton (Keton / Metil Keton)",
        "D. Asam Asetat (Asam Karboksilat)"
    ])
    
    if st.button("Kirim Jawaban Analisis 📑", type="primary"):
        if "Aseton" in jawaban:
            st.success("🎉 **JAWABAN ANDA BENAR!**\n\n**Analisis:**\n* Bukan alkohol (Ceric -), punya karbonil (Bisulfit +), bukan aldehid (Fehling -), dan merupakan jenis metil keton (Iodoform +). Maka senyawa tersebut adalah **Aseton**.")
        else:
            st.error("❌ **JAWABAN KURANG TEPAT.** Perhatikan uji Fehling (negatif) dan Iodoform (positif) untuk menemukan jenis keton yang spesifik.")

# --- SMART LAB SIMULATOR ---
elif pilihan_halaman == "🔬 SMART LAB SIMULATOR":
    st.title("🔀 Smart Flowchart Auto-Analyzer Lab")
    st.write("Ketikkan nama senyawa organik secara bebas. Sistem akan memicu skema analisis eliminasi gugus fungsi.")

    if not st.session_state.test_started:
        st.divider()
        input_user = st.text_input("✍️ Masukkan Nama Senyawa Kimia:", placeholder="Misal: Metanol, Propanon, Etil Asetat, Asam Butanoat, Heksana...")
        
        if st.button("Mulai Identifikasi Golongan & Reaksi 🚀", type="primary"):
            if not input_user.strip():
                st.warning("⚠️ Harap ketikkan nama senyawa terlebih dahulu!")
            else:
                golongan, model_key, proper_name = deteksi_golongan_senyawa(input_user)
                
                st.session_state.test_started = True
                st.session_state.nama_input_user = proper_name
                st.session_state.golongan_terdeteksi = golongan
                st.session_state.senyawa_model = model_key
                st.session_state.current_step = 0
                st.session_state.log_history = []
                st.session_state.trigger_animation = True
                force_rerun()

    else:
        st.write("---")
        input_user = st.session_state.nama_input_user
        golongan = st.session_state.golongan_terdeteksi
        model_key = st.session_state.senyawa_model
        
        urutan = flowchart_paths.get(model_key, flowchart_paths["Alkana / Hidrokarbon Jenuh"])
        db_reaksi_dinamis = dapatkan_data_reaksi(model_key, input_user)

        col_visual, col_log = st.columns([1, 2.5])
        
        with col_visual:
            st.markdown("<h4 style='text-align: center;'>Visual Lab</h4>", unsafe_allow_html=True)
            tube_placeholder = st.empty() 
            status_placeholder = st.empty()
            
        with col_log:
            st.markdown("#### 📑 Logbook & Analisis Gugus Fungsi")
            log_container = st.container()

        with log_container:
            for log in st.session_state.log_history:
                if "(+)" in log["hasil"]:
                    st.success(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**")
                else:
                    st.error(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**")
                st.latex(log['reaksi'])
                st.write(f"**Mekanisme & Alasan:**\n{log['alasan']}")
                st.divider()

        # Logika Simulasi Animasi Interaktif
        if st.session_state.trigger_animation and st.session_state.current_step < len(urutan):
            pereaksi = urutan[st.session_state.current_step]
            
            # Efek menuangkan sampel
            tube_placeholder.markdown(render_tube("30%", "#f1f5f9", "none"), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center;'><em>Menyiapkan sampel {input_user}...</em></div>", unsafe_allow_html=True)
            time.sleep(0.6)
            
            # Efek menambahkan reagen
            warna_reagen = reagen_colors.get(pereaksi, "#f8fafc")
            tube_placeholder.markdown(render_tube("65%", warna_reagen, "none"), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center;'><em>Mereaksikan dengan {pereaksi}...</em></div>", unsafe_allow_html=True)
            time.sleep(0.7)
            
            # Perubahan hasil visual akhir
            res = db_reaksi_dinamis.get(pereaksi, {"hasil": "(-) Tidak bereaksi", "reaksi": r"\text{Tidak Bereaksi}", "alasan": "Senyawa inert.", "warna_akhir": "#f8fafc", "efek": "none"})
            tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
            status_placeholder.markdown("<div style='text-align:center; font-weight:bold;'>Perubahan visual terdeteksi!</div>", unsafe_allow_html=True)
            time.sleep(0.5)
            
            # Simpan ke histori logbook
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
                res = db_reaksi_dinamis.get(last_pereaksi, {"warna_akhir": "#f8fafc", "efek": "none"})
                tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
            
            if st.session_state.current_step < len(urutan):
                next_pereaksi = urutan[st.session_state.current_step]
                status_placeholder.markdown("<div style='text-align:center; color:#475569;'>Menunggu instruksi uji lanjutan...</div>", unsafe_allow_html=True)
                
                with col_visual:
                    st.write("") 
                    if st.button(f"Lanjutkan ke Uji {next_pereaksi} ⏭️", use_container_width=True, type="primary"):
                        st.session_state.trigger_animation = True
                        force_rerun()
            else:
                # Bagian penampilan mutlak identifikasi golongan dari senyawa yang diinputkan pengguna
                status_placeholder.markdown("<div style='text-align:center; font-weight:bold; color:#10b981;'>Selesai!</div>", unsafe_allow_html=True)
                with log_container:
                    st.info(f"🎉 **KESIMPULAN AKHIR IDENTIFIKASI GOLONGAN:**\n\nBerdasarkan rangkaian uji penapisan/eliminasi bertahap di atas, sampel senyawa **'{input_user}'** yang Anda inputkan secara valid teridentifikasi masuk ke dalam golongan senyawa organik: **{golongan.upper()}**.")
                
                with col_visual:
                    st.write("")
                    if st.button("🔄 Uji Senyawa Baru", use_container_width=True):
                        st.session_state.test_started = False
                        force_rerun()
