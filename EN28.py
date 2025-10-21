import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from scipy import stats
import uuid
import logging
import time
import requests
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="EasyNatorics - Jelajah Kombinatorika",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLORS = {
    'primary': '#00D4FF',
    'secondary': '#FF0080',
    'accent1': '#7928CA',
    'accent2': '#FF6B35',
    'dark': '#0A0A0A',
    'darker': '#111111',
    'light': '#1A1A1A',
}

# Pre-generated explanations for demo mode to avoid API calls
PRE_GENERATED_EXPLANATIONS = {
    "prinsip_perkalian": {
        "beginner": """
**🔢 PRINSIP PERKALIAN**

**Konsep Inti**: Jika ada beberapa tahap dalam suatu proses dan setiap tahap punya beberapa pilihan, jumlah kombinasi total dihitung dengan mengalikan jumlah pilihan di setiap tahap.

**Analogi Sederhana**: Bayangkan kamu pilih menu di restoran: 3 makanan, 2 minuman. Kamu bisa pilih 1 makanan dan 1 minuman. Total kombinasi? 3 × 2 = 6 cara.

**Contoh**: Di toko ada 4 jenis baju dan 3 ukuran. Berapa banyak kombinasi baju dan ukuran?  
Jawab: 4 × 3 = 12 kombinasi.

**Tips**: Gambar diagram pohon untuk visualisasi. Latihan dengan soal sederhana dulu!
        """,
        "intermediate": """
**🔢 PRINSIP PERKALIAN**

**Konsep Inti**: Prinsip perkalian digunakan untuk menghitung total cara saat ada beberapa langkah independen, masing-masing dengan pilihan tertentu.

**Analogi Sederhana**: Bayangin bikin password: 1 huruf (26 pilihan) dan 1 angka (10 pilihan). Total? 26 × 10 = 260 password.

**Contoh**: Ada 5 rute dari kota A ke B, 3 rute dari B ke C. Berapa rute total dari A ke C via B?  
Jawab: 5 × 3 = 15 rute.

**Tips**: Pastikan langkah-langkah independen. Cek ulang apakah urutan penting (kalau iya, mungkin permutasi).
        """,
        "advanced": """
**🔢 PRINSIP PERKALIAN**

**Konsep Inti**: Jumlah total kombinasi dari beberapa langkah independen adalah hasil kali jumlah pilihan di setiap langkah.

**Analogi Sederhana**: Kamu desain kode: 2 slot huruf (26 pilihan per slot), 2 slot angka (10 pilihan per slot). Total? 26 × 26 × 10 × 10 = 67,600 kode.

**Contoh**: Sebuah tim punya 4 proyek, 3 anggota per proyek, 2 jadwal. Berapa kombinasi?  
Jawab: 4 × 3 × 2 = 24 kombinasi.

**Tips**: Bedakan dengan permutasi (urutan penting). Gunakan kalkulator untuk angka besar!
        """
    },
    "permutasi": {
        "beginner": """
**🔄 PERMUTASI**

**Konsep Inti**: Permutasi adalah cara menyusun objek di mana urutan penting.

**Analogi Sederhana**: Bayangin susun 3 buku di rak. Urutan beda = susunan beda. Total? 3 × 2 × 1 = 6 cara.

**Contoh**: Berapa cara susun 3 siswa di baris?  
Jawab: 3! = 6 cara.

**Tips**: Mulai dengan jumlah kecil. Tulis semua kemungkinan untuk paham!
        """,
        "intermediate": """
**🔄 PERMUTASI**

**Konsep Inti**: Permutasi menghitung cara menyusun r objek dari n objek, urutan penting. Rumus: P(n,r) = n!/(n-r)!.

**Analogi Sederhana**: Susun 3 dari 5 buku di rak. Total? 5 × 4 × 3 = 60 cara.

**Contoh**: Dari 6 orang, pilih 3 untuk jabatan berbeda. Berapa cara?  
Jawab: P(6,3) = 6 × 5 × 4 = 120 cara.

**Tips**: Gunakan kalkulator faktorial. Cek apakah semua objek berbeda.
        """,
        "advanced": """
**🔄 PERMUTASI**

**Konsep Inti**: Permutasi menghitung susunan r objek dari n objek dengan urutan penting, termasuk kasus siklik atau pengulangan.

**Analogi Sederhana**: Susun 4 orang di meja bundar. Total? (4-1)! = 6 cara.

**Contoh**: Berapa susunan 5 huruf berbeda untuk kode?  
Jawab: 5! = 120 cara.

**Tips**: Pahami kasus khusus (siklik, pengulangan). Latihan soal variasi!
        """
    },
    "kombinasi": {
        "beginner": """
**👥 KOMBINASI**

**Konsep Inti**: Kombinasi adalah cara memilih objek tanpa peduli urutan.

**Analogi Sederhana**: Pilih 2 temen dari 4 untuk tim. Urutan nggak penting. Total? C(4,2) = 6 cara.

**Contoh**: Dari 5 buku, pilih 2 untuk dibaca. Berapa cara?  
Jawab: C(5,2) = 5!/(2!×3!) = 10 cara.

**Tips**: Gunakan rumus C(n,r). Gambar kombinasi untuk visualisasi!
        """,
        "intermediate": """
**👥 KOMBINASI**

**Konsep Inti**: Kombinasi menghitung cara memilih r objek dari n tanpa urutan. Rumus: C(n,r) = n!/(r!×(n-r)!).

**Analogi Sederhana**: Pilih 3 dari 6 topping pizza. Total? C(6,3) = 20 cara.

**Contoh**: Dari 8 siswa, pilih 4 untuk panitia. Berapa cara?  
Jawab: C(8,4) = 8!/(4!×4!) = 70 cara.

**Tips**: Bedakan dengan permutasi. Cek ulang perhitungan faktorial!
        """,
        "advanced": """
**👥 KOMBINASI**

**Konsep Inti**: Kombinasi digunakan untuk memilih r objek dari n tanpa urutan, dengan aplikasi seperti probabilitas.

**Analogi Sederhana**: Pilih 3 dari 7 warna untuk logo. Total? C(7,3) = 35 cara.

**Contoh**: Dari 10 orang, pilih 5 untuk tim. Berapa cara?  
Jawab: C(10,5) = 10!/(5!×5!) = 252 cara.

**Tips**: Gunakan kalkulator untuk n besar. Pahami aplikasi di probabilitas!
        """
    }
}

# ==================== CSS STYLING ====================
def apply_futuristic_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp {
        background: linear-gradient(135deg, #0A0A0A 0%, #111111 100%);
        color: white;
        font-family: 'Orbitron', sans-serif;
    }
    .main-title {
        font-weight: 900;
        background: linear-gradient(90deg, #00D4FF, #FF6B35);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3.5rem;
        margin-bottom: 2rem;
    }
    .card {
        background: linear-gradient(145deg, #1A1A1A, #111111);
        border: 1px solid #00D4FF33;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
    }
    .metric-card {
        background: linear-gradient(145deg, #1A1A1A, #111111);
        border: 1px solid #00D4FF33;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00D4FF, #FF6B35);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton>button {
        border-radius: 10px;
        font-family: 'Orbitron', sans-serif;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
    .stRadio > label {
        font-family: 'Orbitron', sans-serif;
        margin-bottom: 0.5rem;
    }
    .stTextInput > div > input {
        font-family: 'Orbitron', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== DATABASE SYSTEM ====================
class RealTimeDatabase:
    def __init__(self):
        self.data_dir = "research_data"
        os.makedirs(self.data_dir, exist_ok=True)

    def save_participant(self, participant_id: str, data: Dict) -> bool:
        try:
            file_path = os.path.join(self.data_dir, f"{participant_id}.json")
            data['last_updated'] = datetime.now().isoformat()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved participant data for {participant_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving participant {participant_id}: {e}")
            st.error(f"Error saving data: {e}")
            return False

    def load_participant(self, participant_id: str) -> Optional[Dict]:
        try:
            file_path = os.path.join(self.data_dir, f"{participant_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded participant data for {participant_id}")
                    return data
            logger.warning(f"No data found for participant {participant_id}")
            return None
        except Exception as e:
            logger.error(f"Error loading participant {participant_id}: {e}")
            st.error(f"Error loading data: {e}")
            return None

    def get_all_participants(self) -> Dict[str, Dict]:
        participants = {}
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    pid = filename.replace('.json', '')
                    data = self.load_participant(pid)
                    if data:
                        participants[pid] = data
            logger.info(f"Retrieved {len(participants)} participants")
        except Exception as e:
            logger.error(f"Error retrieving participants: {e}")
            st.error(f"Error retrieving data: {e}")
        return participants

# ==================== AI INTEGRATION ====================
class DeepSeekAI:
    def __init__(self):
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-chat"
        self.demo_mode = not bool(self.api_key)
        if self.demo_mode:
            st.info("🔧 Running in Demo Mode - Using pre-generated content for faster response")
        else:
            st.success("✅ Connected to DeepSeek AI")

    def _call_api(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 800) -> Optional[str]:
        if self.demo_mode:
            return None
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://easynatorics.streamlit.app",
                "X-Title": "EasyNatorics"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10  # Timeout 10 detik
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.Timeout:
            logger.error("API request timed out")
            st.warning("Connection to AI service timed out. Using fallback content.")
            return None
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            st.warning(f"Failed to connect to AI service: {e}. Using fallback content.")
            return None

    @st.cache_data(show_spinner=False)
    def get_explanation(_self, concept: str, level: str) -> str:
        if _self.demo_mode:
            return PRE_GENERATED_EXPLANATIONS.get(concept, {}).get(level, "Explanation not available")
        prompt = f"""Jelaskan {concept} untuk siswa SMA level {level} dalam bahasa Indonesia.
        Format: judul, konsep inti, analogi sederhana, contoh, tips. Maksimal 400 kata."""
        messages = [
            {"role": "system", "content": "Anda tutor matematika yang sabar dan jelas."},
            {"role": "user", "content": prompt}
        ]
        response = _self._call_api(messages, temperature=0.7, max_tokens=800)
        return response if response else PRE_GENERATED_EXPLANATIONS.get(concept, {}).get(level, "Explanation not available")

    @st.cache_data(show_spinner=False)
    def ask_tutor(_self, question: str, context: str = "") -> str:
        if _self.demo_mode:
            return f"🤖 **AI Tutor:** In demo mode, full responses require an API key. Contoh jawaban: Coba gambarkan soal sebagai diagram pohon untuk memahami {context}."
        prompt = f"""Konteks: {context}\nPertanyaan: {question}
        Berikan penjelasan mudah, analogi, contoh konkret, langkah sederhana.
        Format markdown dengan emoji. Maksimal 300 kata."""
        messages = [
            {"role": "system", "content": "Anda tutor matematika ramah dan jelas."},
            {"role": "user", "content": prompt}
        ]
        response = _self._call_api(messages, temperature=0.7, max_tokens=600)
        return f"🤖 **AI Tutor:**\n\n{response}" if response else f"🤖 **AI Tutor:** Tidak dapat menghubungi AI. Contoh: Untuk {context}, coba buat diagram pohon."

    @st.cache_data(show_spinner=False)
    def generate_questions(_self, concept: str, difficulty: str, count: int = 3) -> List[Dict]:
        if _self.demo_mode:
            return _self._demo_questions(concept, count)
        prompt = f"""Buat {count} soal {concept} tingkat {difficulty} untuk SMA dalam bahasa Indonesia.
        Format JSON:
        {{
            "questions": [
                {{
                    "question": "teks soal",
                    "options": ["A", "B", "C", "D"],
                    "answer": "jawaban benar",
                    "explanation": "penjelasan",
                    "hint": "petunjuk"
                }}
            ]
        }}
        Soal kontekstual, menarik, dan jelas."""
        messages = [
            {"role": "system", "content": "Guru matematika kreatif. Kembalikan JSON valid."},
            {"role": "user", "content": prompt}
        ]
        response = _self._call_api(messages, temperature=0.8, max_tokens=2000)
        if response:
            try:
                cleaned = response.strip()
                if '```json' in cleaned:
                    cleaned = cleaned.split('```json')[1].split('```')[0].strip()
                result = json.loads(cleaned)
                return result.get('questions', [])
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                st.warning("Failed to generate questions. Using fallback questions.")
        return _self._demo_questions(concept, count)

    def _demo_questions(self, concept: str, count: int) -> List[Dict]:
        demo = {
            "prinsip_perkalian": [
                {
                    "question": "Restoran punya 4 makanan, 3 minuman, 2 dessert. Berapa kombinasi menu?",
                    "options": ["9", "12", "24", "36"],
                    "answer": "24",
                    "explanation": "4 × 3 × 2 = 24 kombinasi",
                    "hint": "Kalikan semua pilihan"
                },
                {
                    "question": "Ada 5 warna baju dan 3 ukuran. Berapa kombinasi baju?",
                    "options": ["8", "15", "20", "25"],
                    "answer": "15",
                    "explanation": "5 × 3 = 15 kombinasi",
                    "hint": "Hitung jumlah pilihan per kategori"
                },
                {
                    "question": "Seorang siswa pilih 1 dari 4 buku dan 1 dari 3 waktu. Berapa kombinasi?",
                    "options": ["7", "12", "16", "20"],
                    "answer": "12",
                    "explanation": "4 × 3 = 12 kombinasi",
                    "hint": "Gunakan prinsip perkalian"
                }
            ],
            "permutasi": [
                {
                    "question": "Dari 8 peserta, berapa susunan juara 1, 2, 3?",
                    "options": ["56", "336", "512", "40320"],
                    "answer": "336",
                    "explanation": "P(8,3) = 8 × 7 × 6 = 336",
                    "hint": "Urutan penting, pakai permutasi"
                },
                {
                    "question": "Berapa cara susun 3 buku di rak?",
                    "options": ["6", "9", "12", "18"],
                    "answer": "6",
                    "explanation": "3! = 3 × 2 × 1 = 6 cara",
                    "hint": "Hitung faktorial"
                },
                {
                    "question": "Pilih 2 dari 5 huruf untuk kode. Berapa susunan?",
                    "options": ["10", "20", "25", "60"],
                    "answer": "20",
                    "explanation": "P(5,2) = 5 × 4 = 20 cara",
                    "hint": "Urutan penting"
                }
            ],
            "kombinasi": [
                {
                    "question": "Dari 10 orang, pilih 4 untuk panitia. Berapa cara?",
                    "options": ["40", "210", "5040", "10000"],
                    "answer": "210",
                    "explanation": "C(10,4) = 10!/(4!×6!) = 210 cara",
                    "hint": "Urutan tidak penting"
                },
                {
                    "question": "Pilih 2 dari 5 topping pizza. Berapa cara?",
                    "options": ["5", "10", "20", "25"],
                    "answer": "10",
                    "explanation": "C(5,2) = 5!/(2!×3!) = 10 cara",
                    "hint": "Gunakan rumus kombinasi"
                },
                {
                    "question": "Dari 7 warna, pilih 3 untuk logo. Berapa cara?",
                    "options": ["21", "35", "49", "343"],
                    "answer": "35",
                    "explanation": "C(7,3) = 7!/(3!×4!) = 35 cara",
                    "hint": "Pilih tanpa urutan"
                }
            ]
        }
        return demo.get(concept, [])[:count]

# ==================== RESEARCH SYSTEM ====================
class ResearchSystem:
    def __init__(self):
        self.db = RealTimeDatabase()
        self._initialize_session_state()

    def _initialize_session_state(self):
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.current_participant = None
            st.session_state.participant_data = self._create_template()

    def _create_template(self) -> Dict:
        return {
            'participant_id': None,
            'demographics': {},
            'pre_test': {'score': None, 'answers': [], 'completion_time': None},
            'post_test': {'score': None, 'answers': [], 'completion_time': None},
            'anxiety_survey': {'pre_score': None, 'post_score': None, 'responses': []},
            'satisfaction_survey': {'testimonial': ''},
            'learning_progress': {
                'problems_attempted': 0,
                'problems_correct': 0,
                'module_progress': {
                    'prinsip_perkalian': {'completed': False},
                    'permutasi': {'completed': False},
                    'kombinasi': {'completed': False}
                }
            },
            'adaptive_learning': {
                'current_levels': {
                    'prinsip_perkalian': 'beginner',
                    'permutasi': 'beginner',
                    'kombinasi': 'beginner'
                },
                'performance_history': {
                    'prinsip_perkalian': {'attempts': 0, 'correct': 0},
                    'permutasi': {'attempts': 0, 'correct': 0},
                    'kombinasi': {'attempts': 0, 'correct': 0}
                }
            },
            'registration_time': datetime.now().isoformat()
        }

    def register(self, demographics: Dict) -> Optional[str]:
        try:
            all_p = self.db.get_all_participants()
            pid = f"P{len(all_p) + 1:03d}"
            new_data = self._create_template()
            new_data['participant_id'] = pid
            new_data['demographics'] = demographics
            if self.db.save_participant(pid, new_data):
                st.session_state.current_participant = pid
                st.session_state.participant_data = new_data
                logger.info(f"Registered participant {pid}")
                return pid
            return None
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            st.error("Failed to register participant.")
            return None

    def load(self, pid: str) -> bool:
        data = self.db.load_participant(pid)
        if data:
            st.session_state.current_participant = pid
            st.session_state.participant_data = data
            logger.info(f"Loaded participant {pid}")
            return True
        return False

    def save_current(self) -> bool:
        if st.session_state.current_participant:
            return self.db.save_participant(
                st.session_state.current_participant,
                st.session_state.participant_data
            )
        logger.warning("No current participant to save")
        return False

    def update_progress(self, concept: str, is_correct: bool) -> bool:
        data = st.session_state.participant_data
        data['learning_progress']['problems_attempted'] += 1
        if is_correct:
            data['learning_progress']['problems_correct'] += 1
        perf = data['adaptive_learning']['performance_history'][concept]
        perf['attempts'] += 1
        if is_correct:
            perf['correct'] += 1
        if perf['attempts'] >= 3:
            acc = perf['correct'] / perf['attempts']
            if acc >= 0.8:
                data['adaptive_learning']['current_levels'][concept] = 'advanced'
            elif acc >= 0.6:
                data['adaptive_learning']['current_levels'][concept] = 'intermediate'
        return self.save_current()

    def complete_module(self, module: str) -> bool:
        data = st.session_state.participant_data
        data['learning_progress']['module_progress'][module]['completed'] = True
        return self.save_current()

    def get_level(self, concept: str) -> str:
        try:
            return st.session_state.participant_data['adaptive_learning']['current_levels'].get(concept, 'beginner')
        except Exception as e:
            logger.error(f"Error getting level for {concept}: {e}")
            return 'beginner'

# ==================== INSTRUMENTS ====================
class Instruments:
    def __init__(self):
        self.amas_questions = [
            {"q": "Mengerjakan soal matematika yang diberikan guru", "cat": "Learning"},
            {"q": "Mengerjakan soal di papan tulis", "cat": "Learning"},
            {"q": "Mengerjakan ujian matematika", "cat": "Evaluation"},
            {"q": "Mempersiapkan ujian matematika", "cat": "Evaluation"},
            {"q": "Mendengar pelajaran matematika", "cat": "Learning"},
            {"q": "Mengerjakan PR matematika", "cat": "Learning"},
            {"q": "Membaca soal di buku", "cat": "Learning"},
            {"q": "Mendapat nilai matematika buruk", "cat": "Evaluation"},
            {"q": "Memikirkan pelajaran besok", "cat": "Evaluation"}
        ]
        self.pre_test_questions = [
            # Prinsip Perkalian (4)
            {
                "id": 1,
                "question": "Sebuah restoran menawarkan 4 jenis makanan utama, 3 jenis minuman, dan 2 jenis dessert. Berapa banyak kombinasi menu yang berbeda yang dapat dipilih pelanggan?",
                "options": ["9", "12", "24", "36"],
                "correct_answer": "24",
                "concept": "prinsip_perkalian",
                "explanation": "Menggunakan prinsip perkalian: 4 makanan × 3 minuman × 2 dessert = 24 kombinasi"
            },
            {
                "id": 2,
                "question": "Ada 5 jalur bus dari kota A ke B, dan 3 jalur dari B ke C. Berapa banyak rute dari A ke C melalui B?",
                "options": ["8", "15", "20", "25"],
                "correct_answer": "15",
                "concept": "prinsip_perkalian",
                "explanation": "5 jalur A→B × 3 jalur B→C = 15 rute"
            },
            {
                "id": 3,
                "question": "Menu cafe: 5 jenis kopi, 4 jenis kue. Berapa banyak kombinasi kopi + kue?",
                "options": ["9", "20", "25", "30"],
                "correct_answer": "20",
                "concept": "prinsip_perkalian",
                "explanation": "5 kopi × 4 kue = 20 kombinasi"
            },
            {
                "id": 4,
                "question": "Seorang siswa memilih 1 dari 3 mata pelajaran dan 1 dari 4 waktu les. Berapa banyak kombinasi pilihan?",
                "options": ["7", "12", "16", "20"],
                "correct_answer": "12",
                "concept": "prinsip_perkalian",
                "explanation": "3 mata pelajaran × 4 waktu les = 12 kombinasi"
            },
            # Permutasi (3)
            {
                "id": 5,
                "question": "Dari 8 peserta, berapa banyak kemungkinan susunan juara 1, 2, dan 3?",
                "options": ["56", "336", "512", "40320"],
                "correct_answer": "336",
                "concept": "permutasi",
                "explanation": "Menggunakan permutasi P(8,3) = 8 × 7 × 6 = 336 susunan"
            },
            {
                "id": 6,
                "question": "Berapa banyak kata 4 huruf yang dapat disusun dari huruf-huruf pada kata 'MAJU'?",
                "options": ["16", "24", "256", "12"],
                "correct_answer": "24",
                "concept": "permutasi",
                "explanation": "Menyusun 4 huruf berbeda: 4! = 4 × 3 × 2 × 1 = 24 kata"
            },
            {
                "id": 7,
                "question": "Dalam sebuah rapat, 7 orang duduk melingkar. Berapa banyak susunan duduk yang mungkin?",
                "options": ["5040", "720", "120", "2520"],
                "correct_answer": "720",
                "concept": "permutasi",
                "explanation": "Permutasi siklik: (7-1)! = 6! = 720 susunan"
            },
            # Kombinasi (3)
            {
                "id": 8,
                "question": "Dari 10 orang, akan dipilih 4 orang untuk menjadi panitia. Berapa banyak cara memilih panitia tersebut?",
                "options": ["40", "210", "5040", "10000"],
                "correct_answer": "210",
                "concept": "kombinasi",
                "explanation": "Menggunakan kombinasi C(10,4) = 10!/(4!×6!) = 210 cara"
            },
            {
                "id": 9,
                "question": "Sebuah tim bola basket terdiri dari 5 pemain. Jika ada 12 pemain yang tersedia, berapa banyak tim berbeda yang dapat dibentuk?",
                "options": ["60", "792", "95040", "248832"],
                "correct_answer": "792",
                "concept": "kombinasi",
                "explanation": "Menggunakan kombinasi C(12,5) = 12!/(5!×7!) = 792 tim"
            },
            {
                "id": 10,
                "question": "Dari 6 buku berbeda, berapa cara memilih 2 buku untuk dibaca?",
                "options": ["12", "15", "30", "36"],
                "correct_answer": "15",
                "concept": "kombinasi",
                "explanation": "C(6,2) = 6!/(2!×4!) = 15 cara"
            }
        ]
        self.post_test_questions = [
            # Prinsip Perkalian (4)
            {
                "id": 1,
                "question": "Sebuah kode akses terdiri dari 2 huruf vokal (A,I,U,E,O) diikuti 3 angka. Berapa banyak kode yang mungkin?",
                "options": ["1250", "2500", "5000", "10000"],
                "correct_answer": "1250",
                "concept": "prinsip_perkalian",
                "explanation": "5 huruf vokal × 5 huruf vokal × 5 huruf vokal × 10 angka × 10 angka = 1250"
            },
            {
                "id": 2,
                "question": "Ada 4 rute dari rumah ke kampus, dan 3 rute dari kampus ke perpustakaan. Berapa banyak perjalanan berbeda dari rumah ke perpustakaan via kampus?",
                "options": ["7", "12", "16", "20"],
                "correct_answer": "12",
                "concept": "prinsip_perkalian",
                "explanation": "4 rute × 3 rute = 12 perjalanan"
            },
            {
                "id": 3,
                "question": "Seorang pelanggan memilih 1 dari 6 rasa es krim dan 1 dari 3 topping. Berapa banyak kombinasi es krim yang mungkin?",
                "options": ["9", "18", "24", "30"],
                "correct_answer": "18",
                "concept": "prinsip_perkalian",
                "explanation": "6 rasa × 3 topping = 18 kombinasi"
            },
            {
                "id": 4,
                "question": "Seorang siswa memilih 1 dari 5 buku dan 1 dari 4 waktu baca. Berapa banyak kombinasi pilihan?",
                "options": ["9", "15", "20", "25"],
                "correct_answer": "20",
                "concept": "prinsip_perkalian",
                "explanation": "5 buku × 4 waktu = 20 kombinasi"
            },
            # Permutasi (3)
            {
                "id": 5,
                "question": "Dari 9 orang, akan dipilih ketua, sekretaris, dan bendahara. Berapa banyak cara memilih?",
                "options": ["84", "504", "729", "362880"],
                "correct_answer": "504",
                "concept": "permutasi",
                "explanation": "P(9,3) = 9 × 8 × 7 = 504 cara"
            },
            {
                "id": 6,
                "question": "Berapa banyak bilangan 3 digit yang dapat dibentuk dari angka 1,2,3,4,5,6 tanpa pengulangan?",
                "options": ["120", "216", "256", "720"],
                "correct_answer": "120",
                "concept": "permutasi",
                "explanation": "P(6,3) = 6 × 5 × 4 = 120 bilangan"
            },
            {
                "id": 7,
                "question": "Berapa banyak cara menyusun 5 buku berbeda di rak?",
                "options": ["25", "120", "625", "3125"],
                "correct_answer": "120",
                "concept": "permutasi",
                "explanation": "5! = 5 × 4 × 3 × 2 × 1 = 120 cara"
            },
            # Kombinasi (3)
            {
                "id": 8,
                "question": "Dalam sebuah komite yang terdiri dari 8 orang, dipilih 3 orang sebagai tim inti. Berapa banyak tim yang mungkin?",
                "options": ["56", "336", "512", "40320"],
                "correct_answer": "56",
                "concept": "kombinasi",
                "explanation": "C(8,3) = 8!/(3!×5!) = 56 tim"
            },
            {
                "id": 9,
                "question": "Dari 15 siswa, akan dipilih 5 siswa untuk lomba cerdas cermat. Berapa banyak cara memilih?",
                "options": ["3003", "3600", "1500", "32760"],
                "correct_answer": "3003",
                "concept": "kombinasi",
                "explanation": "C(15,5) = 15!/(5!×10!) = 3003 cara"
            },
            {
                "id": 10,
                "question": "Sebuah pizza dapat dipilih dengan 3 topping dari 8 topping yang tersedia. Berapa banyak kombinasi pizza?",
                "options": ["24", "56", "336", "512"],
                "correct_answer": "56",
                "concept": "kombinasi",
                "explanation": "C(8,3) = 8!/(3!×5!) = 56 kombinasi"
            }
        ]

    def render_amas(self, survey_type: str) -> List[Dict]:
        st.markdown(f"""
        <div class='card'>
            <h2>📊 Survey Kecemasan Matematika ({'Awal' if survey_type == 'pre' else 'Akhir'})</h2>
            <p>Silakan jawab dengan jujur untuk membantu penelitian.</p>
        </div>
        """, unsafe_allow_html=True)
        responses = []
        pid = st.session_state.participant_data.get('participant_id', 'unknown')
        for i, item in enumerate(self.amas_questions, 1):
            st.markdown(f"**{i}. {item['q']}**")
            response = st.radio(
                f"Tingkat kecemasan untuk '{item['q']}'",
                [1, 2, 3, 4, 5],
                format_func=lambda x: ["Tidak Cemas", "Sedikit", "Cukup", "Cemas", "Sangat Cemas"][x-1],
                key=f"{pid}_amas_{survey_type}_{i}",
                horizontal=True
            )
            responses.append({"question": item['q'], "response": response})
        return responses

    def render_test(self, test_type: str) -> tuple[List[Dict], int]:
        st.markdown(f"""
        <div class='card'>
            <h2>🎯 {'Pre-Test' if test_type == 'pre' else 'Post-Test'}</h2>
            <p>Jawab 10 pertanyaan berikut dengan cermat.</p>
        </div>
        """, unsafe_allow_html=True)
        questions = self.pre_test_questions if test_type == 'pre' else self.post_test_questions
        answers = []
        score = 0
        pid = st.session_state.participant_data.get('participant_id', 'unknown')
        for i, q in enumerate(questions, 1):
            st.markdown(f"### Soal {i}")
            st.markdown(f"**{q['question']}**")
            answer = st.radio(
                f"Pilih jawaban untuk soal {i}",
                q['options'],
                key=f"{pid}_{test_type}_q{i}",
                index=None
            )
            is_correct = (answer == q['correct_answer']) if answer else False
            if is_correct:
                score += 1
            answers.append({
                "question_id": q['id'],
                "answer": answer,
                "correct": is_correct
            })
        return answers, score

# ==================== LEARNING MODULES ====================
# ==================== LEARNING MODULES ====================
class LearningModules:
    def __init__(self, ai: DeepSeekAI, research: ResearchSystem):
        self.ai = ai
        self.research = research
        self.modules = {
            'prinsip_perkalian': {
                'title': '🔢 Prinsip Perkalian',
                'desc': 'Seni Menghitung Kemungkinan',
                'color': COLORS['secondary']
            },
            'permutasi': {
                'title': '🔄 Permutasi',
                'desc': 'Seni Menyusun dengan Presisi',
                'color': COLORS['primary']
            },
            'kombinasi': {
                'title': '👥 Kombinasi',
                'desc': 'Power of Team Selection',
                'color': COLORS['accent1']
            }
        }

    def render(self, module_key: str):
        module = self.modules[module_key]
        level = self.research.get_level(module_key)
        st.markdown(f"""
        <div class='card' style='background: linear-gradient(135deg, {module['color']} 0%, {module['color']}77 100%); color: white;'>
            <h1>{module['title']}</h1>
            <h3>{module['desc']}</h3>
            <p>Level Anda: {level.title()}</p>
        </div>
        """, unsafe_allow_html=True)

        # Explanation section
        with st.spinner("Memuat penjelasan... (Pertama kali mungkin 10-20 detik, selanjutnya cepat)"):
            explanation = self.ai.get_explanation(module_key, level)
            st.markdown(f"<div class='card'>{explanation}</div>", unsafe_allow_html=True)

        # AI Tutor
        st.markdown("### 🤖 AI Tutor")
        question = st.text_input(
            "Tanya apa saja tentang konsep ini:",
            placeholder="Ketik pertanyaan...",
            key=f"tutor_{module_key}"
        )
        if question:
            with st.spinner("AI sedang menjawab..."):
                response = self.ai.ask_tutor(question, f"Konsep: {module['title']}")
                st.markdown(f"<div class='card'>{response}</div>", unsafe_allow_html=True)

        # Practice
        st.markdown("### 🎯 Latihan Adaptif")
        
        # Initialize session state untuk soal jika belum ada
        if f'practice_questions_{module_key}' not in st.session_state:
            with st.spinner("Memuat soal adaptif..."):
                questions = self.ai.generate_questions(module_key, level, 3)
                st.session_state[f'practice_questions_{module_key}'] = questions
                st.session_state[f'practice_answers_{module_key}'] = [None] * len(questions)
                st.session_state[f'practice_checked_{module_key}'] = [False] * len(questions)
        
        questions = st.session_state[f'practice_questions_{module_key}']
        answers = st.session_state[f'practice_answers_{module_key}']
        checked = st.session_state[f'practice_checked_{module_key}']
        
        for i, prob in enumerate(questions):
            st.markdown(f"#### Soal {i+1}")
            st.markdown(f"**{prob['question']}**")
            
            # Gunakan key yang konsisten
            answer_key = f"practice_{module_key}_{i}"
            
            # Radio button untuk memilih jawaban
            selected_answer = st.radio(
                f"Pilih jawaban untuk soal {i+1}",
                prob['options'],
                key=answer_key,
                index=prob['options'].index(answers[i]) if answers[i] in prob['options'] else None
            )
            
            # Simpan jawaban yang dipilih
            if selected_answer != answers[i]:
                answers[i] = selected_answer
                st.session_state[f'practice_answers_{module_key}'] = answers
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                # Tombol cek jawaban
                if st.button("✅ Cek Jawaban", key=f"check_{module_key}_{i}", use_container_width=True):
                    if answers[i]:
                        correct = (answers[i] == prob['answer'])
                        checked[i] = True
                        st.session_state[f'practice_checked_{module_key}'] = checked
                        
                        if correct:
                            st.success("🎉 Benar!")
                            self.research.update_progress(module_key, True)
                        else:
                            st.error("❌ Belum tepat")
                            self.research.update_progress(module_key, False)
                    else:
                        st.warning("Pilih jawaban terlebih dahulu!")
            
            with col2:
                # Tombol lihat hint
                if st.button("💡 Hint", key=f"hint_{module_key}_{i}", use_container_width=True):
                    st.info(f"**Hint:** {prob['hint']}")
            
            with col3:
                # Tampilkan penjelasan jika sudah dicek
                if checked[i]:
                    if answers[i] == prob['answer']:
                        st.success(f"**Penjelasan:** {prob['explanation']}")
                    else:
                        st.error(f"**Jawaban benar:** {prob['answer']}")
                        st.info(f"**Penjelasan:** {prob['explanation']}")
            
            st.markdown("---")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎲 Soal Baru", key=f"refresh_{module_key}", use_container_width=True):
                # Clear cache dan state untuk soal baru
                st.cache_data.clear()
                if f'practice_questions_{module_key}' in st.session_state:
                    del st.session_state[f'practice_questions_{module_key}']
                if f'practice_answers_{module_key}' in st.session_state:
                    del st.session_state[f'practice_answers_{module_key}']
                if f'practice_checked_{module_key}' in st.session_state:
                    del st.session_state[f'practice_checked_{module_key}']
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset Jawaban", key=f"reset_{module_key}", use_container_width=True):
                # Reset hanya jawaban, pertanyaan tetap sama
                st.session_state[f'practice_answers_{module_key}'] = [None] * len(questions)
                st.session_state[f'practice_checked_{module_key}'] = [False] * len(questions)
                st.rerun()
                
        with col3:
            if st.button("✅ Selesai Modul", key=f"complete_{module_key}", use_container_width=True, type="primary"):
                if self.research.complete_module(module_key):
                    st.success(f"🎊 Modul {module['title']} selesai!")
                    st.balloons()
                    # Clear state modul
                    if f'practice_questions_{module_key}' in st.session_state:
                        del st.session_state[f'practice_questions_{module_key}']
                    if f'practice_answers_{module_key}' in st.session_state:
                        del st.session_state[f'practice_answers_{module_key}']
                    if f'practice_checked_{module_key}' in st.session_state:
                        del st.session_state[f'practice_checked_{module_key}']
                    st.session_state.current_module = None
                    st.rerun()
# ==================== ANALYTICS ====================
def render_analytics():
    st.markdown("<div class='card'><h1>📈 Analisis Data</h1></div>", unsafe_allow_html=True)
    data = st.session_state.participant_data
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pre = data['pre_test'].get('score', 0) or 0
        post = data['post_test'].get('score', 0) or 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='stat-value'>{post - pre}</div>
            <div>Peningkatan Nilai</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        pre_anx = data['anxiety_survey'].get('pre_score', 0) or 0
        post_anx = data['anxiety_survey'].get('post_score', 0) or 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='stat-value'>{pre_anx - post_anx:.1f}</div>
            <div>Penurunan Kecemasan</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        progress = data['learning_progress']
        attempted = progress['problems_attempted']
        correct = progress['problems_correct']
        acc = (correct / attempted * 100) if attempted > 0 else 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='stat-value'>{acc:.1f}%</div>
            <div>Akurasi</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='stat-value'>{attempted}</div>
            <div>Soal Dikerjakan</div>
        </div>
        """, unsafe_allow_html=True)
    testimonial = data['satisfaction_survey'].get('testimonial', '')
    if testimonial:
        st.markdown(f"""
        <div class='card' style='background: linear-gradient(135deg, {COLORS['accent1']}, {COLORS['secondary']}); color: white;'>
            <h3>💬 Testimoni Anda</h3>
            <p>"{testimonial}"</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("### 🌍 Data Global Partisipan")
    all_participants = research.db.get_all_participants()
    if all_participants:
        df_data = []
        pre_anx_list, post_anx_list, pre_test_list, post_test_list = [], [], [], []
        for pid, pdata in all_participants.items():
            pre_anx = pdata.get('anxiety_survey', {}).get('pre_score', 0) or 0
            post_anx = pdata.get('anxiety_survey', {}).get('post_score', 0) or 0
            pre_score = pdata.get('pre_test', {}).get('score', 0) or 0
            post_score = pdata.get('post_test', {}).get('score', 0) or 0
            if isinstance(pre_anx, (int, float)):
                pre_anx_list.append(pre_anx)
            if isinstance(post_anx, (int, float)):
                post_anx_list.append(post_anx)
            if isinstance(pre_score, (int, float)):
                pre_test_list.append(pre_score)
            if isinstance(post_score, (int, float)):
                post_test_list.append(post_score)
            df_data.append({
                'ID': pid,
                'Nama': pdata.get('demographics', {}).get('nama', 'Unknown'),
                'Kelas': pdata.get('demographics', {}).get('kelas', 'Unknown'),
                'Usia': pdata.get('demographics', {}).get('usia', 0),
                'Pengalaman': pdata.get('demographics', {}).get('pengalaman', 'Unknown'),
                'Skor Anxiety Pre': round(pre_anx, 2),
                'Skor Anxiety Post': round(post_anx, 2),
                'Skor Pre-Test': pre_score,
                'Skor Post-Test': post_score,
                'Problems Attempted': pdata.get('learning_progress', {}).get('problems_attempted', 0),
                'Problems Correct': pdata.get('learning_progress', {}).get('problems_correct', 0),
                'Testimonial': pdata.get('satisfaction_survey', {}).get('testimonial', '')
            })
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        if len(pre_anx_list) > 1 and len(post_anx_list) > 1:
            mean_pre_anx = np.mean(pre_anx_list)
            mean_post_anx = np.mean(post_anx_list)
            decrease = mean_pre_anx - mean_post_anx
            t_anx, p_anx = stats.ttest_rel(pre_anx_list, post_anx_list)
            st.markdown("### Table 1: Perbandingan Skor Kecemasan Matematika")
            summary_anx = pd.DataFrame({
                'Metric': ['Mean Pre', 'Mean Post', 'Penurunan', 't-value', 'p-value'],
                'Value': [round(mean_pre_anx, 2), round(mean_post_anx, 2), round(decrease, 2), 
                         round(t_anx, 2), '<0.001' if p_anx < 0.001 else round(p_anx, 4)]
            })
            st.table(summary_anx)
        if len(pre_test_list) > 1 and len(post_test_list) > 1:
            mean_pre_test = np.mean(pre_test_list)
            mean_post_test = np.mean(post_test_list)
            increase = mean_post_test - mean_pre_test
            t_test, p_test = stats.ttest_rel(pre_test_list, post_test_list)
            st.markdown("### Table 2: Perbandingan Nilai Pre-test dan Post-test")
            summary_test = pd.DataFrame({
                'Metric': ['Mean Pre', 'Mean Post', 'Peningkatan', 't-value', 'p-value'],
                'Value': [round(mean_pre_test, 1), round(mean_post_test, 1), round(increase, 2), 
                         round(t_test, 2), '<0.001' if p_test < 0.001 else round(p_test, 4)]
            })
            st.table(summary_test)

# ==================== MAIN APP ====================
def main():
    apply_futuristic_style()
    global research, ai, instruments, modules
    research = ResearchSystem()
    ai = DeepSeekAI()
    instruments = Instruments()
    modules = LearningModules(ai, research)
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if 'current_module' not in st.session_state:
        st.session_state.current_module = None
    st.markdown("<div class='main-title'>EasyNatorics</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #00D4FF; font-size: 1.2rem; margin-bottom: 2rem;'>Platform Pembelajaran Kombinatorika Berbasis AI</div>", unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("### 🧭 Navigasi")
        if st.session_state.current_participant:
            st.success(f"Selamat datang, {st.session_state.current_participant}!")
        pages = ["Dashboard", "Pendaftaran", "Survey Awal", "Pre-Test", "Belajar", "Post-Test", "Survey Akhir", "Hasil"]
        st.session_state.current_page = st.selectbox(
            "Pilih Halaman:",
            pages,
            index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0
        )
        if st.session_state.current_participant and st.button("🚪 Logout", use_container_width=True):
            st.session_state.current_participant = None
            st.session_state.participant_data = research._create_template()
            st.session_state.current_page = "Dashboard"
            st.rerun()
    page = st.session_state.current_page
    if page == "Dashboard":
        st.markdown("""
        <div class='card'>
            <h1>🎯 Selamat Datang di EasyNatorics!</h1>
            <p>Platform pembelajaran kombinatorika interaktif dengan teknologi AI.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.current_participant:
            st.success(f"Halo, {st.session_state.participant_data['demographics'].get('nama', 'Peserta')}!")
            if st.button("📚 Mulai Belajar", use_container_width=True, type="primary"):
                st.session_state.current_page = "Belajar"
                st.rerun()
        else:
            if st.button("🚀 Daftar Sekarang", use_container_width=True, type="primary"):
                st.session_state.current_page = "Pendaftaran"
                st.rerun()
    elif page == "Pendaftaran":
        st.markdown("""
        <div class='card'>
            <h1>📝 Pendaftaran Peserta</h1>
            <p>Isi data diri untuk memulai perjalanan belajar Anda.</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("registration_form"):
            col1, col2 = st.columns(2)
            with col1:
                nama = st.text_input("Nama Lengkap*", placeholder="Masukkan nama lengkap")
                kelas = st.selectbox("Kelas*", ["10", "11", "12"], index=None, placeholder="Pilih kelas")
            with col2:
                usia = st.number_input("Usia*", min_value=15, max_value=18, value=16)
                pengalaman = st.selectbox("Pengalaman Matematika*", ["Pemula", "Menengah", "Lanjutan"], index=None, placeholder="Pilih tingkat")
            consent = st.checkbox("Saya setuju berpartisipasi dalam penelitian ini*")
            if st.form_submit_button("🚀 Daftar Sekarang", type="primary"):
                if nama and kelas and pengalaman and consent:
                    demographics = {
                        'nama': nama.strip(),
                        'kelas': st.session_state.get(f"registration_form_kelas", kelas),
                        'usia': int(usia),
                        'pengalaman': st.session_state.get(f"registration_form_pengalaman", pengalaman)
                    }
                    pid = research.register(demographics)
                    if pid:
                        st.success(f"🎉 Pendaftaran berhasil! ID Anda: **{pid}**")
                        st.balloons()
                        time.sleep(1)
                        st.session_state.current_page = "Survey Awal"
                        st.rerun()
                else:
                    st.error("❌ Harap isi semua field dan setujui persetujuan penelitian.")
    elif page == "Survey Awal":
        if not st.session_state.current_participant:
            st.warning("⚠️ Silakan daftar terlebih dahulu.")
            st.stop()
        responses = instruments.render_amas("pre")
        if st.button("📨 Submit Survey & Lanjut", type="primary", use_container_width=True):
            if all(r['response'] is not None for r in responses):
                amas_score = np.mean([r['response'] for r in responses])
                st.session_state.participant_data['anxiety_survey']['pre_score'] = amas_score
                st.session_state.participant_data['anxiety_survey']['responses'] = responses
                research.save_current()
                anxiety_level = "Rendah" if amas_score <= 2.0 else "Sedang" if amas_score <= 3.5 else "Tinggi"
                st.success(f"""
                ✅ Survey berhasil disimpan!
                **Skor Kecemasan Awal:** {amas_score:.2f}
                **Tingkat Kecemasan:** {anxiety_level}
                """)
                time.sleep(2)
                st.session_state.current_page = "Pre-Test"
                st.rerun()
            else:
                st.error("Harap jawab semua pertanyaan sebelum submit.")
    elif page == "Pre-Test":
        if not st.session_state.current_participant:
            st.warning("⚠️ Silakan daftar terlebih dahulu.")
            st.stop()
        answers, score = instruments.render_test("pre")
        if st.button("📊 Lihat Hasil & Lanjut", type="primary", use_container_width=True):
            if all(a['answer'] is not None for a in answers):
                st.session_state.participant_data['pre_test']['answers'] = answers
                st.session_state.participant_data['pre_test']['score'] = score
                st.session_state.participant_data['pre_test']['completion_time'] = datetime.now().isoformat()
                research.save_current()
                st.markdown(f"""
                <div class='card' style='background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent1']}); color: white;'>
                    <h2>📊 Hasil Pre-Test</h2>
                    <h1>{score}/10</h1>
                    <h3>{round(score/10*100)}%</h3>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(2)
                st.session_state.current_page = "Belajar"
                st.rerun()
            else:
                st.error("Harap jawab semua soal sebelum submit.")
    elif page == "Belajar":
        if not st.session_state.current_participant:
            st.warning("⚠️ Silakan daftar terlebih dahulu.")
            st.stop()
        st.markdown("""
        <div class='card'>
            <h1>📚 Pusat Pembelajaran</h1>
            <p>Pilih modul untuk memulai belajar kombinatorika.</p>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.current_module:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔢 Prinsip Perkalian", use_container_width=True, type="primary"):
                    st.session_state.current_module = 'prinsip_perkalian'
                    st.rerun()
            with col2:
                if st.button("🔄 Permutasi", use_container_width=True, type="primary"):
                    st.session_state.current_module = 'permutasi'
                    st.rerun()
            with col3:
                if st.button("👥 Kombinasi", use_container_width=True, type="primary"):
                    st.session_state.current_module = 'kombinasi'
                    st.rerun()
            progress = st.session_state.participant_data['learning_progress']
            completed = sum(1 for m in progress['module_progress'].values() if m['completed'])
            st.markdown("---")
            st.progress(completed / 3, text=f"Progres: {completed}/3 Modul Selesai")
            if completed >= 2:
                if st.button("🎯 Lanjut ke Post-Test", type="primary", use_container_width=True):
                    st.session_state.current_page = "Post-Test"
                    st.rerun()
        else:
            modules.render(st.session_state.current_module)
            if st.button("🏠 Kembali ke Menu", use_container_width=True):
                st.session_state.current_module = None
                st.rerun()
    elif page == "Post-Test":
        if not st.session_state.current_participant:
            st.warning("⚠️ Silakan daftar terlebih dahulu.")
            st.stop()
        answers, score = instruments.render_test("post")
        if st.button("📊 Lihat Hasil", type="primary", use_container_width=True):
            if all(a['answer'] is not None for a in answers):
                st.session_state.participant_data['post_test']['answers'] = answers
                st.session_state.participant_data['post_test']['score'] = score
                st.session_state.participant_data['post_test']['completion_time'] = datetime.now().isoformat()
                research.save_current()
                pre_score = st.session_state.participant_data['pre_test'].get('score', 0) or 0
                improvement = score - pre_score
                st.markdown(f"""
                <div class='card' style='background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent1']}); color: white;'>
                    <h2>📊 Hasil Post-Test</h2>
                    <h1>{score}/10</h1>
                    <h3>{round(score/10*100)}%</h3>
                    <h4>📈 Peningkatan: +{improvement} poin</h4>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(2)
                st.session_state.current_page = "Survey Akhir"
                st.rerun()
            else:
                st.error("Harap jawab semua soal sebelum submit.")
    elif page == "Survey Akhir":
        if not st.session_state.current_participant:
            st.warning("⚠️ Silakan daftar terlebih dahulu.")
            st.stop()
        st.markdown("### 📊 Survey Kecemasan Akhir")
        post_responses = instruments.render_amas("post")
        st.markdown("### 💬 Testimoni")
        testimonial = st.text_area(
            "Bagikan pengalaman belajar Anda:",
            placeholder="Apa yang paling Anda sukai? Saran untuk perbaikan?",
            height=150
        )
        if st.button("📨 Submit & Lihat Hasil", type="primary", use_container_width=True):
            if all(r['response'] is not None for r in post_responses):
                post_amas = np.mean([r['response'] for r in post_responses])
                st.session_state.participant_data['anxiety_survey']['post_score'] = post_amas
                st.session_state.participant_data['satisfaction_survey']['testimonial'] = testimonial.strip()
                research.save_current()
                st.success("✅ Semua data berhasil disimpan! Terima kasih atas partisipasi Anda!")
                time.sleep(2)
                st.session_state.current_page = "Hasil"
                st.rerun()
            else:
                st.error("Harap jawab semua pertanyaan sebelum submit.")
    elif page == "Hasil":
        if not st.session_state.current_participant:
            st.warning("⚠️ Silakan daftar terlebih dahulu.")
            st.stop()
        render_analytics()

if __name__ == "__main__":
    main()
