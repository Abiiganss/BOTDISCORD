import discord
from discord.ext import commands, tasks
import json
import os
import random
import time
import asyncio
from datetime import datetime, timedelta
from flask import Flask
import threading

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Flask app untuk UptimeRobot monitoring
app = Flask(__name__)

@app.route('/')
def health_check():
    return {
        "status": "online",
        "bot_ready": bot.is_ready(),
        "uptime": time.time() - bot.start_time if hasattr(bot, 'start_time') else 0,
        "timestamp": int(time.time())
    }

@app.route('/stats')
def bot_stats():
    total_users = len([u for u in data.keys() if u.isdigit()])
    total_commands = len(bot.commands)
    return {
        "total_users": total_users,
        "total_commands": total_commands,
        "guilds": len(bot.guilds),
        "status": "healthy"
    }

@app.route('/webhook-alert', methods=['POST'])
def webhook_alert():
    """Endpoint untuk menerima alert dari UptimeRobot"""
    # Kirim notifikasi ke Discord channel tertentu
    # Implementasi sesuai kebutuhan
    return {"status": "received"}

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# Start Flask server di thread terpisah
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Load database
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return {}

# Save database
def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# Konstanta untuk sistem pinjaman
PINJAMAN_BATAS_HARI = 7  # batas waktu utang 7 hari

def cek_jatuh_tempo(utang_data):
    sekarang = int(time.time())
    jatuh_tempo = utang_data.get("jatuh_tempo", 0)
    if jatuh_tempo == 0:
        return "Tidak ada batas waktu pembayaran."

    sisa_detik = jatuh_tempo - sekarang
    if sisa_detik < 0:
        return f"Utang sudah melewati jatuh tempo sejak {-sisa_detik // 86400} hari yang lalu!"
    else:
        hari = sisa_detik // 86400
        return f"Sisa waktu pembayaran: {hari} hari."

# Database kota dan building
cities = {
    "jakarta": {
        "nama": "Jakarta",
        "buildings": {
            "pengadilan_negeri_jkt": {
                "nama": "Pengadilan Negeri Jakarta Pusat",
                "alamat": "Jl. Gajah Mada No. 17, Jakarta Pusat",
                "kapasitas": 50,
                "jam_operasional": "08:00 - 16:00",
                "jobs": ["hakim", "pengacara", "jaksa"],
                "facilities": ["Ruang Sidang", "Perpustakaan Hukum", "Kantin", "Parkir"],
                "biaya_transport": 15000
            },
            "rumah_sakit_cipto": {
                "nama": "RSUPN Dr. Cipto Mangunkusumo",
                "alamat": "Jl. Diponegoro No. 71, Jakarta Pusat",
                "kapasitas": 200,
                "jam_operasional": "24 jam",
                "jobs": ["dokter umum", "dokter anak", "dokter bedah"],
                "facilities": ["IGD", "Laboratorium", "Apotek", "Kantin", "Parkir"],
                "biaya_transport": 20000
            },
            "universitas_indonesia": {
                "nama": "Universitas Indonesia",
                "alamat": "Kampus UI Depok, Jakarta",
                "kapasitas": 100,
                "jam_operasional": "07:00 - 17:00",
                "jobs": ["dosen", "guru sma"],
                "facilities": ["Perpustakaan", "Lab Komputer", "Kantin", "Auditorium"],
                "biaya_transport": 25000
            },
            "plaza_indonesia": {
                "nama": "Plaza Indonesia IT Center",
                "alamat": "Jl. MH Thamrin, Jakarta Pusat",
                "kapasitas": 80,
                "jam_operasional": "09:00 - 18:00",
                "jobs": ["programmer", "data analyst"],
                "facilities": ["Coworking Space", "Meeting Room", "Food Court", "Gym"],
                "biaya_transport": 18000
            }
        }
    },
    "bandung": {
        "nama": "Bandung",
        "buildings": {
            "pengadilan_negeri_bdg": {
                "nama": "Pengadilan Negeri Bandung",
                "alamat": "Jl. Veteran No. 4, Bandung",
                "kapasitas": 30,
                "jam_operasional": "08:00 - 16:00",
                "jobs": ["hakim", "pengacara", "jaksa"],
                "facilities": ["Ruang Sidang", "Perpustakaan", "Kantin"],
                "biaya_transport": 10000
            },
            "rumah_sakit_hasan_sadikin": {
                "nama": "RS Hasan Sadikin",
                "alamat": "Jl. Pasteur No. 38, Bandung",
                "kapasitas": 150,
                "jam_operasional": "24 jam", 
                "jobs": ["dokter umum", "dokter gigi", "dokter anak"],
                "facilities": ["IGD", "Laboratorium", "Apotek", "Kantin"],
                "biaya_transport": 12000
            },
            "itb_campus": {
                "nama": "Institut Teknologi Bandung",
                "alamat": "Jl. Ganesha No. 10, Bandung",
                "kapasitas": 60,
                "jam_operasional": "07:00 - 17:00",
                "jobs": ["dosen", "guru sma"],
                "facilities": ["Lab Teknik", "Perpustakaan", "Kantin", "Auditorium"],
                "biaya_transport": 8000
            }
        }
    },
    "surabaya": {
        "nama": "Surabaya",
        "buildings": {
            "pengadilan_negeri_sby": {
                "nama": "Pengadilan Negeri Surabaya",
                "alamat": "Jl. Jenderal Basuki Rachmat, Surabaya",
                "kapasitas": 40,
                "jam_operasional": "08:00 - 16:00",
                "jobs": ["hakim", "pengacara", "jaksa"],
                "facilities": ["Ruang Sidang", "Perpustakaan", "Kantin"],
                "biaya_transport": 12000
            },
            "rumah_sakit_soetomo": {
                "nama": "RS Dr. Soetomo",
                "alamat": "Jl. Mayjend Prof. Dr Moestopo, Surabaya",
                "kapasitas": 180,
                "jam_operasional": "24 jam",
                "jobs": ["dokter umum", "dokter bedah", "dokter anak"],
                "facilities": ["IGD", "Laboratorium", "Apotek", "Kantin"],
                "biaya_transport": 15000
            },
            "its_campus": {
                "nama": "Institut Teknologi Sepuluh Nopember",
                "alamat": "Jl. Raya ITS, Surabaya",
                "kapasitas": 70,
                "jam_operasional": "07:00 - 17:00",
                "jobs": ["dosen", "programmer", "data analyst"],
                "facilities": ["Lab IT", "Perpustakaan", "Kantin", "Auditorium"],
                "biaya_transport": 14000
            }
        }
    },
    "yogyakarta": {
        "nama": "Yogyakarta",
        "buildings": {
            "pengadilan_negeri_jogja": {
                "nama": "Pengadilan Negeri Yogyakarta",
                "alamat": "Jl. Kenari No. 1, Yogyakarta",
                "kapasitas": 25,
                "jam_operasional": "08:00 - 16:00",
                "jobs": ["hakim", "pengacara", "jaksa"],
                "facilities": ["Ruang Sidang", "Perpustakaan", "Kantin"],
                "biaya_transport": 8000
            },
            "rumah_sakit_sardjito": {
                "nama": "RS Dr. Sardjito",
                "alamat": "Jl. Kesehatan No. 1, Yogyakarta",
                "kapasitas": 120,
                "jam_operasional": "24 jam",
                "jobs": ["dokter umum", "dokter gigi", "dokter anak"],
                "facilities": ["IGD", "Laboratorium", "Apotek", "Kantin"],
                "biaya_transport": 10000
            },
            "ugm_campus": {
                "nama": "Universitas Gadjah Mada",
                "alamat": "Bulaksumur, Yogyakarta",
                "kapasitas": 90,
                "jam_operasional": "07:00 - 17:00",
                "jobs": ["dosen", "guru sma"],
                "facilities": ["Perpustakaan", "Lab", "Kantin", "Auditorium"],
                "biaya_transport": 7000
            },
            "malioboro_mall": {
                "nama": "Malioboro Mall",
                "alamat": "Jl. Malioboro, Yogyakarta",
                "kapasitas": 50,
                "jam_operasional": "10:00 - 22:00",
                "jobs": ["pegawai toko", "kasir", "barista"],
                "facilities": ["Food Court", "ATM", "Parkir", "Cinema"],
                "biaya_transport": 5000
            }
        }
    },
    "medan": {
        "nama": "Medan",
        "buildings": {
            "rumah_sakit_haji": {
                "nama": "RS Haji Adam Malik",
                "alamat": "Jl. Bunga Lau No. 17, Medan",
                "kapasitas": 100,
                "jam_operasional": "24 jam",
                "jobs": ["dokter umum", "dokter gigi", "dokter anak"],
                "facilities": ["IGD", "Laboratorium", "Apotek", "Kantin"],
                "biaya_transport": 12000
            },
            "usu_campus": {
                "nama": "Universitas Sumatera Utara",
                "alamat": "Jl. Universitas No. 9, Medan",
                "kapasitas": 80,
                "jam_operasional": "07:00 - 17:00",

# Simple work system without shifts


                "jobs": ["dosen", "guru smp"],
                "facilities": ["Perpustakaan", "Lab", "Kantin", "Auditorium"],
                "biaya_transport": 10000
            },
            "plaza_medan_fair": {
                "nama": "Plaza Medan Fair",
                "alamat": "Jl. Gatot Subroto, Medan",
                "kapasitas": 60,
                "jam_operasional": "10:00 - 22:00",
                "jobs": ["pegawai toko", "kasir", "barista"],
                "facilities": ["Food Court", "ATM", "Parkir", "Cinema"],
                "biaya_transport": 8000
            }
        }
    }
}

# Database pekerjaan dengan building assignment - Gaji disesuaikan dengan dunia nyata Indonesia
jobs = {
    # === PROFESI HUKUM ===
    "hakim": {
        "gaji": 18000000,
        "xp": 30,
        "deskripsi": "Menangani perkara hukum di pengadilan dan memutuskan keadilan",
        "lokasi": "Pengadilan Negeri",
        "jam_kerja": "08:00 - 16:00",
        "requirement_level": 15,
        "buildings": ["pengadilan_negeri_jkt", "pengadilan_negeri_bdg", "pengadilan_negeri_sby", "pengadilan_negeri_jogja"],
        "skill": {
            "name": "Vonis Keadilan",
            "command": "vonis",
            "description": "Memberikan vonis keadilan untuk menyelesaikan konflik",
            "cooldown": 21600,  # 6 jam
            "effect": "resolve_conflict"
        }
    },
    "notaris": {
        "gaji": 20000000,
        "xp": 28,
        "deskripsi": "Membuat akta otentik dan legalisasi dokumen penting",
        "lokasi": "Kantor Notaris",
        "jam_kerja": "09:00 - 17:00",
        "requirement_level": 18,
        "buildings": ["general_office"],
        "skill": {
            "name": "Legalisasi Dokumen",
            "command": "legalisasi",
            "description": "Mengesahkan dokumen penting dengan biaya premium",
            "cooldown": 14400,  # 4 jam
            "effect": "legal_document"
        }
    },
    "polisi": {
        "gaji": 8000000,
        "xp": 22,
        "deskripsi": "Menjaga keamanan dan ketertiban masyarakat",
        "lokasi": "Kantor Polisi",
        "jam_kerja": "Shift 24/7",
        "requirement_level": 10,
        "buildings": ["kantor_polisi"],
        "skill": {
            "name": "Patroli Keamanan",
            "command": "patroli",
            "description": "Melakukan patroli untuk mencegah kejahatan",
            "cooldown": 10800,  # 3 jam
            "effect": "security_boost"
        }
    },
    "pengacara": {
        "gaji": 15000000,
        "xp": 25,
        "deskripsi": "Memberikan bantuan hukum dan mewakili klien di pengadilan",
        "lokasi": "Kantor Hukum",
        "jam_kerja": "09:00 - 17:00",
        "requirement_level": 12,
        "buildings": ["pengadilan_negeri_jkt", "pengadilan_negeri_bdg", "pengadilan_negeri_sby", "pengadilan_negeri_jogja"],
        "skill": {
            "name": "Konsultasi Hukum",
            "command": "konsultasi",
            "description": "Memberikan konsultasi hukum untuk menyelesaikan masalah legal",
            "cooldown": 14400,  # 4 jam
            "effect": "legal_advice"
        }
    },
    "jaksa": {
        "gaji": 16000000,
        "xp": 28,
        "deskripsi": "Menuntut terdakwa dalam proses peradilan pidana",
        "lokasi": "Kejaksaan",
        "jam_kerja": "08:00 - 16:00",
        "requirement_level": 14,
        "buildings": ["pengadilan_negeri_jkt", "pengadilan_negeri_bdg", "pengadilan_negeri_sby", "pengadilan_negeri_jogja"],
        "skill": {
            "name": "Investigasi Kriminal",
            "command": "investigasi",
            "description": "Melakukan investigasi untuk mengungkap kejahatan (DM only)",
            "cooldown": 18000,  # 5 jam
            "effect": "investigate_crime",
            "dm_only": True
        }
    },
    
    # === PROFESI MEDIS & KESEHATAN ===
    "bidan": {
        "gaji": 5500000,
        "xp": 20,
        "deskripsi": "Membantu persalinan dan perawatan ibu hamil",
        "lokasi": "Klinik Bersalin",
        "jam_kerja": "On-call 24/7",
        "requirement_level": 8,
        "buildings": ["rumah_sakit_cipto", "rumah_sakit_hasan_sadikin", "rumah_sakit_soetomo"],
        "skill": {
            "name": "Assist Persalinan",
            "command": "assist",
            "description": "Membantu proses persalinan dengan aman",
            "cooldown": 18000,  # 5 jam
            "effect": "birth_assistance"
        }
    },
    "perawat": {
        "gaji": 4500000,
        "xp": 18,
        "deskripsi": "Merawat pasien dan membantu dokter dalam pelayanan medis",
        "lokasi": "Rumah Sakit",
        "jam_kerja": "Shift 8 jam",
        "requirement_level": 6,
        "buildings": ["rumah_sakit_cipto", "rumah_sakit_hasan_sadikin", "rumah_sakit_soetomo", "rumah_sakit_sardjito", "rumah_sakit_haji"],
        "skill": {
            "name": "Perawatan Intensif",
            "command": "rawat",
            "description": "Memberikan perawatan intensif untuk pemulihan",
            "cooldown": 12600,  # 3.5 jam
            "effect": "intensive_care"
        }
    },
    "apoteker": {
        "gaji": 7000000,
        "xp": 22,
        "deskripsi": "Meracik dan menyediakan obat-obatan sesuai resep dokter",
        "lokasi": "Apotek",
        "jam_kerja": "08:00 - 20:00",
        "requirement_level": 12,
        "buildings": ["apotek_guardian", "apotek_kimia_farma"],
        "skill": {
            "name": "Racik Obat",
            "command": "racikobat",
            "description": "Meracik obat custom dengan efek khusus",
            "cooldown": 14400,  # 4 jam
            "effect": "custom_medicine"
        }
    },
    "fisioterapis": {
        "gaji": 6500000,
        "xp": 20,
        "deskripsi": "Memberikan terapi fisik untuk rehabilitasi pasien",
        "lokasi": "Klinik Fisioterapi",
        "jam_kerja": "08:00 - 17:00",
        "requirement_level": 10,
        "buildings": ["klinik_fisioterapi"],
        "skill": {
            "name": "Terapi Rehabilitasi",
            "command": "terapi",
            "description": "Memberikan terapi untuk mempercepat pemulihan",
            "cooldown": 16200,  # 4.5 jam
            "effect": "physical_therapy"
        }
    },
    "psikolog": {
        "gaji": 8500000,
        "xp": 24,
        "deskripsi": "Memberikan konseling dan terapi psikologis",
        "lokasi": "Klinik Psikologi",
        "jam_kerja": "09:00 - 17:00",
        "requirement_level": 15,
        "buildings": ["klinik_psikologi"],
        "skill": {
            "name": "Konseling Mental",
            "command": "konseling",
            "description": "Memberikan terapi mental untuk kesehatan jiwa",
            "cooldown": 18000,  # 5 jam
            "effect": "mental_therapy"
        }
    },
    "dokter umum": {
        "gaji": 25000000,
        "xp": 35,
        "deskripsi": "Memberikan pelayanan kesehatan dasar kepada pasien",
        "lokasi": "Rumah Sakit/Puskesmas",
        "jam_kerja": "08:00 - 14:00",
        "requirement_level": 18,
        "buildings": ["rumah_sakit_cipto", "rumah_sakit_hasan_sadikin", "rumah_sakit_soetomo", "rumah_sakit_sardjito", "rumah_sakit_haji"],
        "skill": {
            "name": "Pengobatan Medis",
            "command": "obati",
            "description": "Mengobati diri sendiri atau orang lain secara gratis",
            "cooldown": 10800,  # 3 jam
            "effect": "medical_treatment"
        }
    },
    "dokter spesialis": {
        "gaji": 45000000,
        "xp": 40,
        "deskripsi": "Dokter spesialis dengan keahlian khusus di bidang tertentu",
        "lokasi": "Rumah Sakit Khusus",
        "jam_kerja": "08:00 - 16:00",
        "requirement_level": 25,
        "buildings": ["rumah_sakit_cipto", "rumah_sakit_soetomo"],
        "skill": {
            "name": "Diagnosa Spesialis",
            "command": "diagnosa",
            "description": "Memberikan diagnosa dan pengobatan spesialis",
            "cooldown": 21600,  # 6 jam
            "effect": "specialist_treatment"
        }
    },
    "dokter gigi": {
        "gaji": 30000000,
        "xp": 32,
        "deskripsi": "Merawat kesehatan gigi dan mulut pasien",
        "lokasi": "Klinik Gigi",
        "jam_kerja": "09:00 - 17:00",
        "requirement_level": 16,
        "buildings": ["rumah_sakit_hasan_sadikin", "rumah_sakit_sardjito", "rumah_sakit_haji"],
        "skill": {
            "name": "Perawatan Gigi",
            "command": "rawatgigi",
            "description": "Memberikan perawatan gigi untuk kesehatan optimal",
            "cooldown": 12600,  # 3.5 jam
            "effect": "dental_care"
        }
    },
    "dokter anak": {
        "gaji": 35000000,
        "xp": 38,
        "deskripsi": "Memberikan perawatan medis khusus untuk anak-anak",
        "lokasi": "Rumah Sakit Anak",
        "jam_kerja": "08:00 - 15:00",
        "requirement_level": 20,
        "buildings": ["rumah_sakit_cipto", "rumah_sakit_hasan_sadikin", "rumah_sakit_soetomo", "rumah_sakit_sardjito", "rumah_sakit_haji"],
        "skill": {
            "name": "Terapi Anak",
            "command": "terapianak",
            "description": "Memberikan terapi khusus dan vitamin untuk kesehatan",
            "cooldown": 14400,  # 4 jam
            "effect": "child_therapy"
        }
    },
    "dokter bedah": {
        "gaji": 50000000,
        "xp": 42,
        "deskripsi": "Melakukan operasi bedah untuk mengatasi penyakit",
        "lokasi": "Rumah Sakit",
        "jam_kerja": "07:00 - 19:00",
        "requirement_level": 25,
        "buildings": ["rumah_sakit_cipto", "rumah_sakit_soetomo"],
        "skill": {
            "name": "Operasi Darurat",
            "command": "operasi",
            "description": "Melakukan operasi untuk menyembuhkan kondisi kritis",
            "cooldown": 21600,  # 6 jam
            "effect": "emergency_surgery"
        }
    },
    "guru sd": {
        "gaji": 3500000,
        "xp": 15,
        "deskripsi": "Mengajar siswa sekolah dasar kelas 1-6",
        "lokasi": "Sekolah Dasar",
        "jam_kerja": "07:00 - 13:00",
        "requirement_level": 5,
        "buildings": ["general_schools"],  # Sekolah tersebar di semua kota
        "skill": {
            "name": "Bimbingan Belajar",
            "command": "bimbingan",
            "description": "Memberikan bimbingan belajar untuk meningkatkan XP",
            "cooldown": 14400,  # 4 jam
            "effect": "tutoring"
        }
    },
    "guru smp": {
        "gaji": 4000000,
        "xp": 17,
        "deskripsi": "Mengajar siswa sekolah menengah pertama",
        "lokasi": "SMP",
        "jam_kerja": "07:00 - 14:00",
        "requirement_level": 7,
        "buildings": ["general_schools", "usu_campus"],
        "skill": {
            "name": "Mentoring Remaja",
            "command": "mentoring",
            "description": "Memberikan mentoring untuk pengembangan karakter",
            "cooldown": 16200,  # 4.5 jam
            "effect": "character_development"
        }
    },
    "guru sma": {
        "gaji": 4500000,
        "xp": 18,
        "deskripsi": "Mengajar siswa sekolah menengah atas",
        "lokasi": "SMA",
        "jam_kerja": "07:00 - 15:00",
        "requirement_level": 8,
        "buildings": ["universitas_indonesia", "ugm_campus"],
        "skill": {
            "name": "Konseling Karir",
            "command": "konseling",
            "description": "Memberikan konseling karir dan motivasi",
            "cooldown": 18000,  # 5 jam
            "effect": "career_counseling"
        }
    },
    "dosen": {
        "gaji": 12000000,
        "xp": 22,
        "deskripsi": "Mengajar dan meneliti di perguruan tinggi",
        "lokasi": "Universitas",
        "jam_kerja": "08:00 - 16:00",
        "requirement_level": 10,
        "buildings": ["universitas_indonesia", "itb_campus", "its_campus", "ugm_campus", "usu_campus"],
        "skill": {
            "name": "Riset Akademik",
            "command": "riset",
            "description": "Melakukan penelitian untuk mendapat insight dan bonus",
            "cooldown": 21600,  # 6 jam
            "effect": "academic_research"
        }
    },
    "programmer": {
        "gaji": 8000000,
        "xp": 25,
        "deskripsi": "Membuat dan mengembangkan aplikasi software",
        "lokasi": "Kantor IT/Remote",
        "jam_kerja": "09:00 - 18:00",
        "requirement_level": 12,
        "buildings": ["plaza_indonesia", "its_campus"],
        "skill": {
            "name": "Coding Session",
            "command": "coding",
            "description": "Melakukan sesi coding untuk membuat program dan bonus uang",
            "cooldown": 12600,  # 3.5 jam
            "effect": "programming_bonus"
        }
    },
    "data analyst": {
        "gaji": 9000000,
        "xp": 28,
        "deskripsi": "Menganalisis data untuk insight bisnis",
        "lokasi": "Kantor Perusahaan",
        "jam_kerja": "09:00 - 17:00",
        "requirement_level": 14,
        "buildings": ["plaza_indonesia", "its_campus"],
        "skill": {
            "name": "Analisis Data",
            "command": "analisis",
            "description": "Menganalisis data untuk mendapat insight bisnis dan prediksi",
            "cooldown": 14400,  # 4 jam
            "effect": "data_insights"
        }
    },
    "pilot": {
        "gaji": 40000000,
        "xp": 45,
        "deskripsi": "Menerbangkan pesawat untuk transportasi penumpang",
        "lokasi": "Bandara",
        "jam_kerja": "Shift 24/7",
        "requirement_level": 30,
        "buildings": ["bandara_soekarno_hatta", "bandara_juanda", "bandara_kualanamu"],
        "skill": {
            "name": "Penerbangan Cepat",
            "command": "terbang",
            "description": "Melakukan penerbangan express untuk perjalanan super cepat",
            "cooldown": 18000,  # 5 jam
            "effect": "fast_travel"
        }
    },
    "pramugari": {
        "gaji": 8000000,
        "xp": 30,
        "deskripsi": "Melayani penumpang pesawat selama penerbangan",
        "lokasi": "Pesawat",
        "jam_kerja": "Shift 24/7",
        "requirement_level": 15,
        "buildings": ["bandara_soekarno_hatta", "bandara_juanda", "bandara_kualanamu"],
        "skill": {
            "name": "Pelayanan Prima",
            "command": "layani",
            "description": "Memberikan pelayanan prima untuk meningkatkan mood dan tips",
            "cooldown": 10800,  # 3 jam
            "effect": "premium_service"
        }
    },
    "sopir truk": {
        "gaji": 4500000,
        "xp": 18,
        "deskripsi": "Mengangkut barang dengan truk jarak jauh",
        "lokasi": "Jalan Raya",
        "jam_kerja": "06:00 - 18:00",
        "requirement_level": 8,
        "buildings": ["depot_logistik"],  # Depot tersebar di semua kota
        "skill": {
            "name": "Ekspedisi Barang",
            "command": "ekspedisi",
            "description": "Melakukan pengiriman barang dengan bonus ongkir",
            "cooldown": 16200,  # 4.5 jam
            "effect": "cargo_delivery"
        }
    },
    "pegawai toko": {
        "gaji": 3000000,
        "xp": 12,
        "deskripsi": "Melayani pelanggan dan mengatur barang di toko",
        "lokasi": "Toko Retail",
        "jam_kerja": "08:00 - 20:00",
        "requirement_level": 3,
        "buildings": ["malioboro_mall", "plaza_medan_fair", "grand_city_surabaya"],
        "skill": {
            "name": "Manajemen Stok",
            "command": "stok",
            "description": "Mengelola inventory dengan lebih efisien dan dapat diskon",
            "cooldown": 21600,  # 6 jam
            "effect": "inventory_management"
        }
    },
    "kasir": {
        "gaji": 3000000,
        "xp": 12,
        "deskripsi": "Melayani pembayaran pelanggan di kasir",
        "lokasi": "Supermarket/Toko",
        "jam_kerja": "08:00 - 20:00",
        "requirement_level": 3,
        "buildings": ["malioboro_mall", "plaza_medan_fair", "grand_city_surabaya"],
        "skill": {
            "name": "Transaksi Cepat",
            "command": "kasir",
            "description": "Melakukan transaksi super cepat dengan bonus cashback",
            "cooldown": 14400,  # 4 jam
            "effect": "fast_transaction"
        }
    },
    "barista": {
        "gaji": 3500000,
        "xp": 15,
        "deskripsi": "Membuat dan menyajikan kopi kepada pelanggan",
        "lokasi": "Cafe",
        "jam_kerja": "06:00 - 22:00",
        "requirement_level": 4,
        "buildings": ["malioboro_mall", "plaza_medan_fair", "plaza_indonesia"],
        "skill": {
            "name": "Racik Kopi",
            "command": "racikkopi",
            "description": "Meracik kopi special untuk energy boost dan bonus",
            "cooldown": 10800,  # 3 jam
            "effect": "coffee_brewing"
        }
    },
    "montir": {
        "gaji": 4000000,
        "xp": 17,
        "deskripsi": "Memperbaiki dan merawat kendaraan bermotor",
        "lokasi": "Bengkel",
        "jam_kerja": "08:00 - 17:00",
        "requirement_level": 6,
        "buildings": ["bengkel_resmi"],  # Bengkel tersebar di semua kota
        "skill": {
            "name": "Servis Kendaraan",
            "command": "servis",
            "description": "Melakukan servis kendaraan dengan diskon besar",
            "cooldown": 18000,  # 5 jam
            "effect": "vehicle_service"
        }
    },
    
    # === PROFESI TEKNOLOGI & IT ===
    "web developer": {
        "gaji": 9500000,
        "xp": 26,
        "deskripsi": "Mengembangkan website dan aplikasi web",
        "lokasi": "Software House",
        "jam_kerja": "09:00 - 18:00",
        "requirement_level": 12,
        "buildings": ["plaza_indonesia", "its_campus"],
        "skill": {
            "name": "Deploy Website",
            "command": "deploy",
            "description": "Deploy website dan dapatkan passive income",
            "cooldown": 21600,  # 6 jam
            "effect": "web_deployment"
        }
    },
    "mobile developer": {
        "gaji": 10500000,
        "xp": 28,
        "deskripsi": "Mengembangkan aplikasi mobile Android dan iOS",
        "lokasi": "Tech Company",
        "jam_kerja": "09:00 - 18:00",
        "requirement_level": 14,
        "buildings": ["plaza_indonesia"],
        "skill": {
            "name": "Publish App",
            "command": "publishapp",
            "description": "Publish aplikasi dan dapatkan download revenue",
            "cooldown": 28800,  # 8 jam
            "effect": "app_revenue"
        }
    },
    "system administrator": {
        "gaji": 8500000,
        "xp": 24,
        "deskripsi": "Mengelola server dan infrastruktur IT perusahaan",
        "lokasi": "Data Center",
        "jam_kerja": "Shift 24/7",
        "requirement_level": 10,
        "buildings": ["data_center"],
        "skill": {
            "name": "Backup System",
            "command": "backup",
            "description": "Melakukan backup data dengan recovery guarantee",
            "cooldown": 14400,  # 4 jam
            "effect": "data_backup"
        }
    },
    "cybersecurity specialist": {
        "gaji": 15000000,
        "xp": 32,
        "deskripsi": "Mengamankan sistem dari ancaman cyber dan hacker",
        "lokasi": "Security Operations Center",
        "jam_kerja": "Shift 24/7",
        "requirement_level": 18,
        "buildings": ["soc_center"],
        "skill": {
            "name": "Penetration Test",
            "command": "pentest",
            "description": "Melakukan security testing dan audit",
            "cooldown": 21600,  # 6 jam
            "effect": "security_audit"
        }
    },
    "ui ux designer": {
        "gaji": 7500000,
        "xp": 22,
        "deskripsi": "Mendesain antarmuka dan pengalaman pengguna",
        "lokasi": "Design Studio",
        "jam_kerja": "09:00 - 17:00",
        "requirement_level": 8,
        "buildings": ["design_studio"],
        "skill": {
            "name": "Design Portfolio",
            "command": "design",
            "description": "Membuat design portfolio dan dapatkan client",
            "cooldown": 18000,  # 5 jam
            "effect": "design_portfolio"
        }
    },
    
    # === PROFESI KEUANGAN & PERBANKAN ===
    "akuntan": {
        "gaji": 7000000,
        "xp": 20,
        "deskripsi": "Mengelola pembukuan dan laporan keuangan perusahaan",
        "lokasi": "Kantor Akuntan",
        "jam_kerja": "08:00 - 17:00",
        "requirement_level": 10,
        "buildings": ["kantor_akuntan"],
        "skill": {
            "name": "Audit Keuangan",
            "command": "audit",
            "description": "Melakukan audit dan optimasi keuangan",
            "cooldown": 21600,  # 6 jam
            "effect": "financial_audit"
        }
    },
    "financial advisor": {
        "gaji": 12000000,
        "xp": 28,
        "deskripsi": "Memberikan konsultasi investasi dan perencanaan keuangan",
        "lokasi": "Bank/Sekuritas",
        "jam_kerja": "09:00 - 17:00",
        "requirement_level": 15,
        "buildings": ["bank_bca", "bank_mandiri"],
        "skill": {
            "name": "Investment Plan",
            "command": "invest",
            "description": "Buat portfolio investasi dengan return premium",
            "cooldown": 21600,  # 6 jam
            "effect": "investment_portfolio"
        }
    },
    "teller bank": {
        "gaji": 4500000,
        "xp": 15,
        "deskripsi": "Melayani nasabah untuk transaksi perbankan",
        "lokasi": "Bank",
        "jam_kerja": "08:00 - 15:00",
        "requirement_level": 5,
        "buildings": ["bank_bca", "bank_mandiri", "bank_bni"],
        "skill": {
            "name": "Express Transfer",
            "command": "transfer",
            "description": "Transfer uang dengan fee minimal",
            "cooldown": 7200,  # 2 jam
            "effect": "bank_transfer"
        }
    },
    "ekonom": {
        "gaji": 15000000,
        "xp": 30,
        "deskripsi": "Menganalisis kondisi ekonomi dan memberikan prediksi",
        "lokasi": "Lembaga Riset",
        "jam_kerja": "09:00 - 17:00",
        "requirement_level": 20,
        "buildings": ["lembaga_riset"],
        "skill": {
            "name": "Economic Forecast",
            "command": "forecast",
            "description": "Prediksi trend ekonomi dan market timing",
            "cooldown": 28800,  # 8 jam
            "effect": "economic_prediction"
        }
    },
    
    # === PROFESI INDUSTRI KREATIF ===
    "graphic designer": {
        "gaji": 5500000,
        "xp": 18,
        "deskripsi": "Membuat desain grafis untuk berbagai keperluan",
        "lokasi": "Creative Agency",
        "jam_kerja": "09:00 - 18:00",
        "requirement_level": 6,
        "buildings": ["creative_agency"],
        "skill": {
            "name": "Design Project",
            "command": "designproject",
            "description": "Mengerjakan project design dengan fee premium",
            "cooldown": 14400,  # 4 jam
            "effect": "design_commission"
        }
    },
    "fotografer": {
        "gaji": 6000000,
        "xp": 20,
        "deskripsi": "Mengambil foto untuk acara, produk, dan dokumentasi",
        "lokasi": "Studio Foto",
        "jam_kerja": "Freelance",
        "requirement_level": 5,
        "buildings": ["studio_foto"],
        "skill": {
            "name": "Photo Session",
            "command": "photoshoot",
            "description": "Melakukan sesi foto dengan hasil berkualitas",
            "cooldown": 10800,  # 3 jam
            "effect": "photo_commission"
        }
    },
    "videographer": {
        "gaji": 7500000,
        "xp": 22,
        "deskripsi": "Membuat video untuk promosi, dokumentasi, dan hiburan",
        "lokasi": "Production House",
        "jam_kerja": "Project based",
        "requirement_level": 8,
        "buildings": ["production_house"],
        "skill": {
            "name": "Video Production",
            "command": "producevideo",
            "description": "Produksi video professional dengan revenue sharing",
            "cooldown": 21600,  # 6 jam
            "effect": "video_production"
        }
    },
    "content creator": {
        "gaji": 5000000,
        "xp": 16,
        "deskripsi": "Membuat konten digital untuk media sosial dan platform online",
        "lokasi": "Home Studio",
        "jam_kerja": "Flexible",
        "requirement_level": 3,
        "buildings": ["home_studio"],
        "skill": {
            "name": "Viral Content",
            "command": "createcontent",
            "description": "Buat konten viral dengan monetisasi ads",
            "cooldown": 7200,  # 2 jam
            "effect": "content_monetization"
        }
    },
    "animator": {
        "gaji": 8000000,
        "xp": 24,
        "deskripsi": "Membuat animasi untuk film, game, dan iklan",
        "lokasi": "Animation Studio",
        "jam_kerja": "09:00 - 18:00",
        "requirement_level": 12,
        "buildings": ["animation_studio"],
        "skill": {
            "name": "Animation Project",
            "command": "animate",
            "description": "Buat animasi custom dengan fee tinggi",
            "cooldown": 28800,  # 8 jam
            "effect": "animation_commission"
        }
    },
    
    # === PROFESI KULINER & HOSPITALITY ===
    "chef": {
        "gaji": 8500000,
        "xp": 24,
        "deskripsi": "Memasak dan mengembangkan menu di restoran",
        "lokasi": "Restoran/Hotel",
        "jam_kerja": "11:00 - 23:00",
        "requirement_level": 10,
        "buildings": ["restoran_mewah", "hotel_bintang5"],
        "skill": {
            "name": "Signature Dish",
            "command": "signature",
            "description": "Buat signature dish dan tingkatkan reputasi",
            "cooldown": 14400,  # 4 jam
            "effect": "culinary_reputation"
        }
    },
    "pastry chef": {
        "gaji": 6500000,
        "xp": 20,
        "deskripsi": "Membuat kue, roti, dan dessert berkualitas tinggi",
        "lokasi": "Bakery/Patisserie",
        "jam_kerja": "05:00 - 15:00",
        "requirement_level": 8,
        "buildings": ["bakery_premium"],
        "skill": {
            "name": "Custom Cake",
            "command": "customcake",
            "description": "Buat kue custom dengan harga premium",
            "cooldown": 18000,  # 5 jam
            "effect": "pastry_commission"
        }
    },
    "sommelier": {
        "gaji": 10000000,
        "xp": 26,
        "deskripsi": "Ahli wine dan minuman, memberikan rekomendasi pairing",
        "lokasi": "Fine Dining Restaurant",
        "jam_kerja": "17:00 - 24:00",
        "requirement_level": 15,
        "buildings": ["fine_dining"],
        "skill": {
            "name": "Wine Pairing",
            "command": "winepairing",
            "description": "Berikan wine pairing dan dapatkan tip besar",
            "cooldown": 21600,  # 6 jam
            "effect": "wine_expertise"
        }
    },
    "hotel manager": {
        "gaji": 15000000,
        "xp": 30,
        "deskripsi": "Mengelola operasional hotel dan memastikan kepuasan tamu",
        "lokasi": "Hotel",
        "jam_kerja": "08:00 - 20:00",
        "requirement_level": 18,
        "buildings": ["hotel_bintang5", "hotel_bintang4"],
        "skill": {
            "name": "Guest Experience",
            "command": "guestexp",
            "description": "Tingkatkan rating hotel dan revenue",
            "cooldown": 21600,  # 6 jam
            "effect": "hospitality_excellence"
        }
    },
    
    # === PROFESI TEKNIK & KONSTRUKSI ===
    "arsitek": {
        "gaji": 12000000,
        "xp": 28,
        "deskripsi": "Merancang bangunan dan struktur arsitektur",
        "lokasi": "Firma Arsitektur",
        "jam_kerja": "08:00 - 17:00",
        "requirement_level": 15,
        "buildings": ["firma_arsitektur"],
        "skill": {
            "name": "Architectural Design",
            "command": "archdesign",
            "description": "Buat design arsitektur dengan fee konsultan",
            "cooldown": 28800,  # 8 jam
            "effect": "architectural_fee"
        }
    },
    "civil engineer": {
        "gaji": 10000000,
        "xp": 26,
        "deskripsi": "Merancang dan mengawasi proyek konstruksi sipil",
        "lokasi": "Konsultan Teknik",
        "jam_kerja": "07:00 - 17:00",
        "requirement_level": 12,
        "buildings": ["konsultan_teknik"],
        "skill": {
            "name": "Project Survey",
            "command": "survey",
            "description": "Lakukan survey teknik dengan biaya konsultasi",
            "cooldown": 21600,  # 6 jam
            "effect": "engineering_survey"
        }
    },
    "electrical engineer": {
        "gaji": 9000000,
        "xp": 24,
        "deskripsi": "Merancang dan memelihara sistem kelistrikan",
        "lokasi": "PLN/Kontraktor Listrik",
        "jam_kerja": "08:00 - 17:00",
        "requirement_level": 10,
        "buildings": ["pln_office"],
        "skill": {
            "name": "Power Installation",
            "command": "powerinstall",
            "description": "Install sistem listrik dengan garansi",
            "cooldown": 18000,  # 5 jam
            "effect": "electrical_installation"
        }
    },
    "mechanical engineer": {
        "gaji": 9500000,
        "xp": 25,
        "deskripsi": "Merancang dan memelihara sistem mekanik dan mesin",
        "lokasi": "Pabrik/Workshop",
        "jam_kerja": "08:00 - 17:00",
        "requirement_level": 12,
        "buildings": ["pabrik_manufaktur"],
        "skill": {
            "name": "Machine Optimization",
            "command": "optimize",
            "description": "Optimasi mesin untuk efisiensi maksimal",
            "cooldown": 21600,  # 6 jam
            "effect": "mechanical_optimization"
        }
    },
    "surveyor": {
        "gaji": 6500000,
        "xp": 20,
        "deskripsi": "Melakukan pengukuran dan pemetaan tanah",
        "lokasi": "BPN/Konsultan Survey",
        "jam_kerja": "07:00 - 15:00",
        "requirement_level": 8,
        "buildings": ["bpn_office"],
        "skill": {
            "name": "Land Survey",
            "command": "landsurvey",
            "description": "Survey tanah untuk sertifikat dan pemetaan",
            "cooldown": 14400,  # 4 jam
            "effect": "land_certification"
        }
    },
    
    # === PROFESI MEDIA & KOMUNIKASI ===
    "jurnalis": {
        "gaji": 6000000,
        "xp": 20,
        "deskripsi": "Mencari, mengolah, dan menyajikan berita untuk media massa",
        "lokasi": "Media/Koran",
        "jam_kerja": "Shift fleksibel",
        "requirement_level": 8,
        "buildings": ["kantor_media"],
        "skill": {
            "name": "Breaking News",
            "command": "breakingnews",
            "description": "Publikasikan berita eksklusif dengan fee tinggi",
            "cooldown": 10800,  # 3 jam
            "effect": "news_scoop"
        }
    },
    "penyiar radio": {
        "gaji": 5000000,
        "xp": 18,
        "deskripsi": "Memandu acara radio dan berinteraksi dengan pendengar",
        "lokasi": "Studio Radio",
        "jam_kerja": "Shift 4 jam",
        "requirement_level": 5,
        "buildings": ["radio_station"],
        "skill": {
            "name": "On Air Show",
            "command": "onair",
            "description": "Buat show radio viral dengan sponsor",
            "cooldown": 14400,  # 4 jam
            "effect": "radio_sponsorship"
        }
    },
    "presenter tv": {
        "gaji": 12000000,
        "xp": 28,
        "deskripsi": "Memandu acara televisi dan tampil di depan kamera",
        "lokasi": "Studio TV",
        "jam_kerja": "Recording schedule",
        "requirement_level": 12,
        "buildings": ["tv_station"],
        "skill": {
            "name": "TV Show Host",
            "command": "tvshow",
            "description": "Host acara TV dengan rating tinggi",
            "cooldown": 21600,  # 6 jam
            "effect": "tv_rating_bonus"
        }
    },
    "public relations": {
        "gaji": 8000000,
        "xp": 22,
        "deskripsi": "Mengelola hubungan masyarakat dan citra perusahaan",
        "lokasi": "PR Agency",
        "jam_kerja": "09:00 - 17:00",
        "requirement_level": 10,
        "buildings": ["pr_agency"],
        "skill": {
            "name": "Crisis Management",
            "command": "crisis",
            "description": "Handle krisis dan tingkatkan reputation",
            "cooldown": 18000,  # 5 jam
            "effect": "reputation_recovery"
        }
    },
    
    # === PROFESI TRANSPORTASI & LOGISTIK ===
    "masinis": {
        "gaji": 8500000,
        "xp": 24,
        "deskripsi": "Mengoperasikan kereta api untuk transportasi penumpang",
        "lokasi": "Stasiun Kereta",
        "jam_kerja": "Shift rotasi",
        "requirement_level": 12,
        "buildings": ["stasiun_gambir", "stasiun_tugu"],
        "skill": {
            "name": "Express Train",
            "command": "expresstrain",
            "description": "Operasikan kereta express dengan bonus waktu",
            "cooldown": 21600,  # 6 jam
            "effect": "train_express"
        }
    },
    "nakhoda": {
        "gaji": 15000000,
        "xp": 32,
        "deskripsi": "Memimpin kapal dan bertanggung jawab atas pelayaran",
        "lokasi": "Pelabuhan",
        "jam_kerja": "Pelayaran jarak jauh",
        "requirement_level": 20,
        "buildings": ["pelabuhan_tanjung_priok"],
        "skill": {
            "name": "Maritime Navigation",
            "command": "navigate",
            "description": "Navigasi maritim dengan cargo premium",
            "cooldown": 28800,  # 8 jam
            "effect": "maritime_cargo"
        }
    },
    "logistics coordinator": {
        "gaji": 7000000,
        "xp": 22,
        "deskripsi": "Mengoordinasikan pengiriman barang dan supply chain",
        "lokasi": "Warehouse",
        "jam_kerja": "08:00 - 17:00",
        "requirement_level": 8,
        "buildings": ["warehouse_logistik"],
        "skill": {
            "name": "Supply Chain",
            "command": "supplychain",
            "description": "Optimasi supply chain untuk efisiensi",
            "cooldown": 18000,  # 5 jam
            "effect": "logistics_optimization"
        }
    },
    
    # === PROFESI PERTANIAN & PERIKANAN ===
    "petani": {
        "gaji": 3500000,
        "xp": 15,
        "deskripsi": "Mengolah lahan pertanian dan menanam tanaman pangan",
        "lokasi": "Lahan Pertanian",
        "jam_kerja": "05:00 - 17:00",
        "requirement_level": 1,
        "buildings": ["lahan_pertanian"],
        "skill": {
            "name": "Harvest Season",
            "command": "harvest",
            "description": "Panen hasil pertanian dengan bonus musiman",
            "cooldown": 21600,  # 6 jam
            "effect": "agricultural_harvest"
        }
    },
    "peternak": {
        "gaji": 4500000,
        "xp": 18,
        "deskripsi": "Memelihara hewan ternak untuk produksi pangan",
        "lokasi": "Peternakan",
        "jam_kerja": "05:00 - 18:00",
        "requirement_level": 3,
        "buildings": ["peternakan_sapi", "peternakan_ayam"],
        "skill": {
            "name": "Livestock Care",
            "command": "livestock",
            "description": "Perawatan ternak optimal untuk produksi tinggi",
            "cooldown": 18000,  # 5 jam
            "effect": "livestock_production"
        }
    },
    "nelayan": {
        "gaji": 4000000,
        "xp": 16,
        "deskripsi": "Menangkap ikan dan hasil laut untuk dijual",
        "lokasi": "Pelabuhan Perikanan",
        "jam_kerja": "04:00 - 14:00",
        "requirement_level": 2,
        "buildings": ["pelabuhan_perikanan"],
        "skill": {
            "name": "Deep Sea Fishing",
            "command": "fishing",
            "description": "Tangkap ikan langka dengan harga premium",
            "cooldown": 14400,  # 4 jam
            "effect": "premium_catch"
        }
    },
    
    # === PROFESI OLAHRAGA & FITNESS ===
    "personal trainer": {
        "gaji": 6000000,
        "xp": 20,
        "deskripsi": "Melatih klien untuk mencapai target fitness pribadi",
        "lokasi": "Gym/Fitness Center",
        "jam_kerja": "06:00 - 22:00",
        "requirement_level": 6,
        "buildings": ["fitness_center"],
        "skill": {
            "name": "Fitness Program",
            "command": "fitnessprogram",
            "description": "Buat program fitness custom dengan results guarantee",
            "cooldown": 14400,  # 4 jam
            "effect": "fitness_transformation"
        }
    },
    "atlet profesional": {
        "gaji": 20000000,
        "xp": 35,
        "deskripsi": "Atlet yang berkompetisi di tingkat nasional dan internasional",
        "lokasi": "Pusat Pelatihan",
        "jam_kerja": "Training intensive",
        "requirement_level": 22,
        "buildings": ["gelora_bung_karno"],
        "skill": {
            "name": "Championship Win",
            "command": "championship",
            "description": "Menang kompetisi dan dapatkan prize money",
            "cooldown": 43200,  # 12 jam
            "effect": "sports_achievement"
        }
    },
    "wasit olahraga": {
        "gaji": 5500000,
        "xp": 18,
        "deskripsi": "Memimpin pertandingan dan memastikan fair play",
        "lokasi": "Stadion/Arena",
        "jam_kerja": "Event based",
        "requirement_level": 8,
        "buildings": ["stadion_gelora"],
        "skill": {
            "name": "Fair Judgment",
            "command": "referee",
            "description": "Memimpin pertandingan dengan fee per match",
            "cooldown": 18000,  # 5 jam
            "effect": "referee_fee"
        }
    }
}

# Ranks berdasarkan level
ranks = {
    1: "Pemula",
    5: "Pekerja Keras",
    10: "Profesional Muda",
    15: "Ahli",
    20: "Senior",
    25: "Expert",
    30: "Master",
    40: "Legend",
    50: "Grandmaster"
}

# Items yang bisa didapat
items = {
    "kopi": {"harga": 15000, "deskripsi": "Menambah energi kerja", "effect": "energy_boost"},
    "buku": {"harga": 50000, "deskripsi": "Menambah XP saat bekerja", "effect": "xp_boost"},
    "laptop": {"harga": 8000000, "deskripsi": "Diperlukan untuk pekerjaan IT", "effect": "tool"},
    "stetoskop": {"harga": 500000, "deskripsi": "Diperlukan untuk pekerjaan medis", "effect": "tool"},
    "seragam": {"harga": 200000, "deskripsi": "Meningkatkan gaji 10%", "effect": "salary_boost"},
    "mobil": {"harga": 150000000, "deskripsi": "Transportasi pribadi", "effect": "transport"},
    
    # Tempat tinggal
    "tenda": {"harga": 100000, "deskripsi": "Tempat tinggal sederhana", "effect": "housing", "housing_level": 1},
    "kontrakan": {"harga": 2000000, "deskripsi": "Rumah kontrakan kecil", "effect": "housing", "housing_level": 2},
    "rumah": {"harga": 15000000, "deskripsi": "Rumah pribadi", "effect": "housing", "housing_level": 3},
    "villa": {"harga": 50000000, "deskripsi": "Villa mewah", "effect": "housing", "housing_level": 4},
    
    # Makanan & Minuman
    "roti": {"harga": 5000, "deskripsi": "Makanan ringan (+20 kenyang)", "effect": "food", "hunger_restore": 20},
    "nasi": {"harga": 15000, "deskripsi": "Makanan pokok (+40 kenyang)", "effect": "food", "hunger_restore": 40},
    "gado_gado": {"harga": 25000, "deskripsi": "Makanan sehat (+60 kenyang)", "effect": "food", "hunger_restore": 60},
    "steak": {"harga": 100000, "deskripsi": "Makanan mewah (+80 kenyang)", "effect": "food", "hunger_restore": 80},
    
    "air_mineral": {"harga": 3000, "deskripsi": "Menghilangkan haus (+30 hidrasi)", "effect": "drink", "thirst_restore": 30},
    "jus": {"harga": 15000, "deskripsi": "Minuman segar (+50 hidrasi)", "effect": "drink", "thirst_restore": 50},
    "energy_drink": {"harga": 25000, "deskripsi": "Minuman berenergi (+40 hidrasi, +10 kesehatan)", "effect": "drink", "thirst_restore": 40, "health_restore": 10},
    
    # Obat-obatan
    "obat_flu": {"harga": 15000, "deskripsi": "Menyembuhkan flu (+30 kesehatan)", "effect": "medicine", "health_restore": 30},
    "vitamin": {"harga": 50000, "deskripsi": "Meningkatkan daya tahan (+50 kesehatan)", "effect": "medicine", "health_restore": 50},
    "obat_kuat": {"harga": 100000, "deskripsi": "Obat ampuh (+80 kesehatan)", "effect": "medicine", "health_restore": 80}
}

# Status kondisi untuk display
def get_status_bar(value, max_value=100):
    percentage = min(value / max_value, 1.0)
    filled = int(percentage * 10)
    bar = "█" * filled + "░" * (10 - filled)
    
    if percentage >= 0.8:
        emoji = "🟢"
    elif percentage >= 0.5:
        emoji = "🟡"
    elif percentage >= 0.2:
        emoji = "🟠"
    else:
        emoji = "🔴"
    
    return f"{emoji} {bar} {value}/{max_value}"

def get_housing_name(user_data):
    housing_items = ["tenda", "kontrakan", "rumah", "villa"]
    for item in reversed(housing_items):  # Cek dari yang terbaik
        if item in user_data.get("inventory", {}):
            return item.replace("_", " ").title()
    return "Gelandangan"

def apply_life_effects(user_data):
    """Terapkan efek kehidupan sehari-hari (berkurang seiring waktu)"""
    current_time = int(time.time())
    last_update = user_data.get("last_life_update", current_time)
    
    # Hitung berapa jam yang berlalu
    hours_passed = max(0, (current_time - last_update) // 3600)
    
    if hours_passed > 0:
        # Pengurangan per jam
        hunger_decrease = hours_passed * 5  # -5 per jam
        thirst_decrease = hours_passed * 8  # -8 per jam (haus lebih cepat)
        
        # Housing bonus mengurangi penurunan
        housing_bonus = 0
        housing_items = {"tenda": 1, "kontrakan": 2, "rumah": 3, "villa": 4}
        for item, level in housing_items.items():
            if item in user_data.get("inventory", {}):
                housing_bonus = max(housing_bonus, level)
        
        # Bonus housing mengurangi penurunan hingga 50%
        hunger_decrease = max(1, hunger_decrease - housing_bonus)
        thirst_decrease = max(1, thirst_decrease - housing_bonus)
        
        user_data["lapar"] = max(0, user_data["lapar"] - hunger_decrease)
        user_data["haus"] = max(0, user_data["haus"] - thirst_decrease)
        
        # Jika lapar atau haus, kesehatan menurun
        if user_data["lapar"] < 20 or user_data["haus"] < 20:
            health_decrease = hours_passed * 3
            user_data["kesehatan"] = max(0, user_data["kesehatan"] - health_decrease)
        
        user_data["last_life_update"] = current_time
    
    return user_data

def check_sickness(user_data):
    """Cek apakah user sakit berdasarkan kondisi"""
    sick_conditions = []
    
    if user_data["lapar"] < 10:
        sick_conditions.append("Kelaparan")
    if user_data["haus"] < 10:
        sick_conditions.append("Dehidrasi")
    if user_data["kesehatan"] < 30:
        sick_conditions.append("Sakit")
    
    return sick_conditions

def get_rank(level):
    current_rank = "Pemula"
    for min_level, rank_name in ranks.items():
        if level >= min_level:
            current_rank = rank_name
    return current_rank

def calculate_level(xp):
    return max(1, xp // 100)

def hitung_rating_rata_rata(user_data):
    rating_data = user_data["rating_kredibilitas"]
    if rating_data["jumlah_rating"] == 0:
        return 0.0
    return round(rating_data["total_rating"] / rating_data["jumlah_rating"], 1)

def get_trust_level(avg_rating, jumlah_transaksi):
    if jumlah_transaksi == 0:
        return "🆕 Belum Ada Riwayat"
    elif jumlah_transaksi < 3:
        return "🔸 Pemula"
    elif avg_rating >= 4.5:
        return "💎 Sangat Terpercaya"
    elif avg_rating >= 4.0:
        return "⭐ Terpercaya"
    elif avg_rating >= 3.5:
        return "✅ Cukup Terpercaya"
    elif avg_rating >= 3.0:
        return "⚠️ Perlu Hati-hati"
    else:
        return "❌ Tidak Terpercaya"

def create_user_profile(user_id):
    if user_id not in data:
        data[user_id] = {
            "uang": 0,
            "xp": 0,
            "pekerjaan": None,
            "gaji": 0,
            "hutang": 0,
            "inventory": {},
            "status_kerja": "Menganggur",
            "aplikasi_kerja": {},
            "last_work": None,
            "streak": 0,
            "utang_ke_pemain": {},
            "rating_kredibilitas": {
                "total_rating": 0,
                "jumlah_rating": 0,
                "rating_detail": [],
                "transaksi_selesai": 0
            },
            "riwayat_pinjaman": [],
            # Life simulation stats
            "lapar": 100,
            "haus": 100,
            "kesehatan": 100,
            "last_life_update": int(time.time()),
            "daily_streak": 0,
            "last_daily": 0,
            "last_notifications": {
                "lapar": 0,
                "haus": 0,
                "kesehatan": 0
            }
        }
        save_data(data)
    else:
        # Update data user lama dengan field baru
        if "inventory" not in data[user_id]:
            data[user_id]["inventory"] = {}
        if "pekerjaan" not in data[user_id]:
            data[user_id]["pekerjaan"] = None
        if "status_kerja" not in data[user_id]:
            data[user_id]["status_kerja"] = "Menganggur" if not data[user_id]["pekerjaan"] else "Bekerja"
        if "aplikasi_kerja" not in data[user_id]:
            data[user_id]["aplikasi_kerja"] = {}
        if "last_work" not in data[user_id]:
            data[user_id]["last_work"] = None
        if "streak" not in data[user_id]:
            data[user_id]["streak"] = 0
        if "utang_ke_pemain" not in data[user_id]:
            data[user_id]["utang_ke_pemain"] = {}
        if "rating_kredibilitas" not in data[user_id]:
            data[user_id]["rating_kredibilitas"] = {
                "total_rating": 0,
                "jumlah_rating": 0,
                "rating_detail": [],
                "transaksi_selesai": 0
            }
        if "riwayat_pinjaman" not in data[user_id]:
            data[user_id]["riwayat_pinjaman"] = []
        # Life simulation stats untuk user lama
        if "lapar" not in data[user_id]:
            data[user_id]["lapar"] = 100
        if "haus" not in data[user_id]:
            data[user_id]["haus"] = 100
        if "kesehatan" not in data[user_id]:
            data[user_id]["kesehatan"] = 100
        if "last_life_update" not in data[user_id]:
            data[user_id]["last_life_update"] = int(time.time())
        if "last_notifications" not in data[user_id]:
            data[user_id]["last_notifications"] = {
                "lapar": 0,
                "haus": 0,
                "kesehatan": 0
            }
        save_data(data)

# Sistem notifikasi DM untuk utang
async def kirim_notif_dm(user_id, pesan):
    try:
        user = bot.get_user(int(user_id))
        if user:
            embed = discord.Embed(title="🔔 Pengingat Utang", description=pesan, color=0xff6b6b)
            await user.send(embed=embed)
            return True
    except:
        pass
    return False

# Sistem notifikasi DM untuk kondisi kesehatan
async def kirim_notif_kondisi(user_id, title, pesan, color):
    try:
        user = bot.get_user(int(user_id))
        if user:
            embed = discord.Embed(title=title, description=pesan, color=color)
            await user.send(embed=embed)
            return True
    except:
        pass
    return False

async def send_welcome_guide(user):
    """Kirim panduan lengkap ke DM user baru"""
    try:
        # Pesan welcome utama
        welcome_embed = discord.Embed(
            title="🎉 Selamat Datang di Discord RPG Bot!", 
            description="Halo! Terima kasih sudah bergabung. Bot ini adalah sistem RPG roleplay lengkap dengan berbagai fitur realistis.",
            color=0x00ff00
        )
        welcome_embed.add_field(
            name="🎮 **Apa itu Bot ini?**",
            value="Bot Discord RPG dengan sistem kehidupan, pekerjaan, ekonomi, hukum, real estate, dan fitur sosial yang sangat realistis. Kamu bisa bekerja, berbisnis, investasi, bahkan jadi influencer Instagram!",
            inline=False
        )
        welcome_embed.add_field(
            name="🔥 **Fitur Utama:**",
            value="• **Sistem Kehidupan** - Lapar, haus, kesehatan yang realistis\n• **25+ Pekerjaan** dengan skill unik masing-masing\n• **Real Estate** - Beli, jual, sewa properti\n• **Banking & Investment** - Tabungan, investasi berisiko\n• **Sistem Hukum** - Pengadilan 7 tahap, banding, mediasi\n• **Instagram Influencer** - Posting, followers, sponsorship\n• **Marketplace P2P** - Jual beli antar player\n• **Kerja Interaktif** - Melayani customer real-time via DM",
            inline=False
        )
        
        # Kirim welcome embed
        await user.send(embed=welcome_embed)
        await asyncio.sleep(2)
        
        # Panduan basic
        basic_embed = discord.Embed(
            title="🚀 Panduan Mulai Bermain",
            description="Ikuti langkah-langkah ini untuk memulai petualangan RPG kamu:",
            color=0x3498db
        )
        basic_embed.add_field(
            name="1️⃣ **Cek Kondisi Kamu**",
            value="`!profil` - Lihat semua stats lengkap\n`!kondisi` - Cek lapar, haus, kesehatan",
            inline=False
        )
        basic_embed.add_field(
            name="2️⃣ **Mulai Bekerja**",
            value="`!kerja` - Kerja freelance dapat Rp50k (cooldown 1 jam)\n`!pekerjaan` - Lihat 25+ pekerjaan tetap tersedia\n`!apply [nama_pekerjaan]` - Melamar pekerjaan tetap",
            inline=False
        )
        basic_embed.add_field(
            name="3️⃣ **Jaga Kondisi Hidup**",
            value="`!toko` - Beli makanan, minuman, rumah\n`!makan [nama]` - Makan untuk kurangi lapar\n`!minum [nama]` - Minum untuk kurangi haus\n`!istirahat` - Pulihkan kesehatan",
            inline=False
        )
        basic_embed.add_field(
            name="⚠️ **PENTING!**",
            value="• Kondisi (lapar/haus/kesehatan) menurun seiring waktu\n• Kondisi buruk = tidak bisa kerja\n• Rumah lebih baik = kondisi terjaga lebih lama\n• Kamu akan dapat notifikasi DM otomatis jika kondisi kritis",
            inline=False
        )
        
        await user.send(embed=basic_embed)
        await asyncio.sleep(2)
        
        # Panduan menu lengkap
        menu_embed = discord.Embed(
            title="📋 Menu Lengkap Bot",
            description="Bot ini punya 10+ kategori fitur. Ketik command ini di server untuk eksplorasi:",
            color=0x9b59b6
        )
        menu_embed.add_field(
            name="🗂️ **Menu Utama**",
            value="`!menu` - Lihat semua kategori fitur\n`!menubasic` - Panduan dasar\n`!menukerja` - Sistem pekerjaan\n`!menukondisi` - Sistem kehidupan",
            inline=False
        )
        menu_embed.add_field(
            name="💼 **Pekerjaan & Karir**",
            value="`!menukerja` - Pekerjaan tetap & freelance\n`!menuskill` - Job skills unik per pekerjaan\n`!menukerjainteraktif` - Kerja via DM dengan customer\n`!menuhukum` - Sistem pengadilan realistis",
            inline=False
        )
        menu_embed.add_field(
            name="💰 **Ekonomi & Bisnis**",
            value="`!menubank` - Banking & investment\n`!menubisnis` - Sistem bisnis\n`!menurealestate` - Property investment\n`!menupasar` - Marketplace P2P",
            inline=False
        )
        menu_embed.add_field(
            name="🎭 **Sosial & Hiburan**",
            value="`!menuinstagram` - Instagram influencer (DM only)\n`!menusosial` - Nikah, transfer, daily\n`!menuhiburan` - Crime, judi, achievement",
            inline=False
        )
        
        await user.send(embed=menu_embed)
        await asyncio.sleep(2)
        
        # Panduan fitur khusus
        special_embed = discord.Embed(
            title="✨ Fitur Khusus & Advanced",
            description="Fitur-fitur canggih yang membuat bot ini unik:",
            color=0xff6b6b
        )
        special_embed.add_field(
            name="💼 **Kerja Interaktif (DM Only)**",
            value="• Melayani customer real-time via DM Bot\n• 6 jenis pekerjaan: kasir, barista, delivery, dll\n• Komisi berdasarkan performa dan rating customer\n• Command: `/kerjadm [job_type]` di DM Bot",
            inline=False
        )
        special_embed.add_field(
            name="📱 **Instagram Influencer (DM Only)**",
            value="• Posting konten, dapat followers & engagement\n• Sponsorship deals dari brand\n• Passive income dari follower count\n• Command: `/posting [caption]` di DM Bot",
            inline=False
        )
        special_embed.add_field(
            name="⚖️ **Sistem Hukum Mendalam**",
            value="• Pengadilan 7 tahapan realistis\n• Peran hakim, jaksa, pengacara\n• Sistem banding & mediasi\n• Transkrip sidang tersimpan permanent",
            inline=False
        )
        special_embed.add_field(
            name="🏠 **Real Estate Investment**",
            value="• 10+ jenis properti dari rumah hingga mall\n• Sistem rental untuk passive income\n• Lelang properti antar player\n• Market trends yang berubah-ubah",
            inline=False
        )
        
        await user.send(embed=special_embed)
        await asyncio.sleep(2)
        
        # Tips & warning
        tips_embed = discord.Embed(
            title="💡 Tips Penting & Yang Perlu Diketahui",
            description="Baca ini agar kamu bisa bermain dengan optimal:",
            color=0xffd700
        )
        tips_embed.add_field(
            name="🔔 **Notifikasi Otomatis**",
            value="• Bot akan kirim DM otomatis jika kondisi kritis\n• Reminder utang sebelum jatuh tempo\n• Notifikasi item terjual di marketplace\n• Update sponsorship Instagram & property income",
            inline=False
        )
        tips_embed.add_field(
            name="⚠️ **Hal Penting**",
            value="• **Kondisi menurun setiap jam** - jaga terus!\n• **Utang ada batas waktu** - bisa dilaporkan ke pengadilan\n• **Level tinggi** = peluang kerja & income lebih baik\n• **Beberapa fitur hanya di DM** untuk privasi",
            inline=False
        )
        tips_embed.add_field(
            name="🎯 **Strategi Awal**",
            value="• Kerja freelance `!kerja` setiap jam untuk uang cepat\n• Beli rumah untuk jaga kondisi hidup\n• Apply pekerjaan tetap saat level cukup\n• Eksplorasi job skills setiap pekerjaan\n• Coba sistem real estate untuk passive income",
            inline=False
        )
        tips_embed.add_field(
            name="🆘 **Butuh Bantuan?**",
            value="• Semua command ada help: ketik command tanpa parameter\n• Menu lengkap: `!menu` di server\n• Tanya di channel jika bingung\n• Bot ini sangat kompleks, eksplorasi pelan-pelan!",
            inline=False
        )
        
        await user.send(embed=tips_embed)
        await asyncio.sleep(1)
        
        # Final message
        final_embed = discord.Embed(
            title="🎊 Selamat Bermain!",
            description="Kamu sekarang siap memulai petualangan RPG yang seru!\n\n🚀 **Mulai dengan:** `!profil` untuk cek status, lalu `!kerja` untuk dapat uang pertama!\n\n💬 **Jangan ragu bertanya** di server jika ada yang bingung. Selamat bermain! 🎮",
            color=0x00ff00
        )
        final_embed.set_footer(text="Sistem RPG Discord Bot - Versi Lengkap dengan 15+ Fitur Utama")
        
        await user.send(embed=final_embed)
        
    except discord.Forbidden:
        # Jika user block DM, tidak bisa kirim
        pass
    except Exception as e:
        # Log error tapi jangan crash bot
        print(f"Error sending welcome guide: {e}")

async def cek_dan_kirim_notifikasi_kondisi():
    """Cek kondisi semua user dan kirim notifikasi jika kondisi kritis"""
    current_time = int(time.time())
    
    # Create a copy of items to avoid RuntimeError when dictionary changes during iteration
    for user_id, user_data in list(data.items()):
        # Pastikan user punya semua field yang diperlukan
        create_user_profile(user_id)
        
        # Apply life effects untuk semua user
        user_data = apply_life_effects(user_data)
        
        # Cek kapan terakhir kali notifikasi dikirim (cooldown 2 jam per jenis notifikasi)
        last_notifications = user_data.setdefault("last_notifications", {
            "lapar": 0,
            "haus": 0,
            "kesehatan": 0
        })
        
        notification_cooldown = 7200  # 2 jam
        
        # Notifikasi lapar (30% atau kurang)
        if user_data.get("lapar", 100) <= 30 and (current_time - last_notifications["lapar"]) >= notification_cooldown:
            if user_data.get("lapar", 100) <= 10:
                title = "🚨 KELAPARAN KRITIS!"
                pesan = f"⚠️ **BAHAYA!** Level kelaparan kamu sangat kritis ({user_data.get('lapar', 100)}/100)!\n\n🍽️ Segera beli makanan sebelum kesehatan menurun drastis!\n\nGunakan: `!toko` untuk melihat makanan atau `!makan [nama_makanan]`"
                color = 0xff0000
            else:
                title = "🍽️ Peringatan Lapar"
                pesan = f"⚠️ Kamu mulai lapar ({user_data.get('lapar', 100)}/100).\n\n🍞 Segera makan sebelum kondisi memburuk!\n\nGunakan: `!makan [nama_makanan]` atau `!toko`"
                color = 0xff9900
                
            await kirim_notif_kondisi(user_id, title, pesan, color)
            last_notifications["lapar"] = current_time
        
        # Notifikasi haus (30% atau kurang)
        if user_data.get("haus", 100) <= 30 and (current_time - last_notifications["haus"]) >= notification_cooldown:
            if user_data.get("haus", 100) <= 10:
                title = "🚨 DEHIDRASI KRITIS!"
                pesan = f"⚠️ **BAHAYA!** Level kehausan kamu sangat kritis ({user_data.get('haus', 100)}/100)!\n\n💧 Segera minum sebelum kesehatan menurun drastis!\n\nGunakan: `!toko` untuk melihat minuman atau `!minum [nama_minuman]`"
                color = 0xff0000
            else:
                title = "💧 Peringatan Haus"
                pesan = f"⚠️ Kamu mulai haus ({user_data.get('haus', 100)}/100).\n\n🥤 Segera minum sebelum kondisi memburuk!\n\nGunakan: `!minum [nama_minuman]` atau `!toko`"
                color = 0xff9900
                
            await kirim_notif_kondisi(user_id, title, pesan, color)
            last_notifications["haus"] = current_time
        
        # Notifikasi kesehatan (50% atau kurang)
        if user_data.get("kesehatan", 100) <= 50 and (current_time - last_notifications["kesehatan"]) >= notification_cooldown:
            if user_data.get("kesehatan", 100) <= 20:
                title = "🚨 KESEHATAN KRITIS!"
                pesan = f"⚠️ **BAHAYA!** Kesehatan kamu sangat rendah ({user_data.get('kesehatan', 100)}/100)!\n\n💊 Segera minum obat dan istirahat!\n❤️ Kamu tidak bisa bekerja dalam kondisi ini!\n\nGunakan: `!obat [nama_obat]` atau `!istirahat`"
                color = 0xff0000
            else:
                title = "❤️ Peringatan Kesehatan"
                pesan = f"⚠️ Kesehatan kamu menurun ({user_data.get('kesehatan', 100)}/100).\n\n💊 Pertimbangkan untuk minum obat atau istirahat.\n🏠 Tempat tinggal yang lebih baik membantu menjaga kesehatan.\n\nGunakan: `!obat [nama_obat]`, `!istirahat`, atau `!toko`"
                color = 0xff9900
                
            await kirim_notif_kondisi(user_id, title, pesan, color)
            last_notifications["kesehatan"] = current_time
        
        # Update data dengan notifikasi terbaru
        user_data["last_notifications"] = last_notifications
        
        await asyncio.sleep(0.5)  # Delay untuk avoid rate limit
    
    save_data(data)

async def cek_dan_kirim_notifikasi():
    """Cek semua utang dan kirim notifikasi sesuai batas waktu"""
    sekarang = int(time.time())
    
    for user_id, user_data in data.items():
        if "utang_ke_pemain" not in user_data or not user_data["utang_ke_pemain"]:
            continue
            
        for pemberi_id, utang_data in user_data["utang_ke_pemain"].items():
            jatuh_tempo = utang_data.get("jatuh_tempo", 0)
            if jatuh_tempo == 0:
                continue
                
            sisa_detik = jatuh_tempo - sekarang
            sisa_hari = sisa_detik // 86400
            jumlah_utang = utang_data["jumlah_pokok"]
            
            # Ambil nama pemberi pinjaman
            try:
                pemberi_user = bot.get_user(int(pemberi_id))
                nama_pemberi = pemberi_user.display_name if pemberi_user else f"UserID {pemberi_id}"
            except:
                nama_pemberi = f"UserID {pemberi_id}"
            
            # Notifikasi berdasarkan sisa waktu
            pesan = None
            
            if sisa_detik < 0:  # Sudah jatuh tempo
                hari_terlambat = abs(sisa_hari)
                pesan = f"⚠️ **UTANG JATUH TEMPO!**\n\nUtang kamu ke **{nama_pemberi}** sebesar **Rp{jumlah_utang:,}** sudah jatuh tempo sejak **{hari_terlambat} hari** yang lalu!\n\nSegera bayar dengan: `!bayarpemain @{nama_pemberi} {jumlah_utang}`"
                
            elif sisa_hari == 0:  # Jatuh tempo hari ini
                pesan = f"🚨 **UTANG JATUH TEMPO HARI INI!**\n\nUtang kamu ke **{nama_pemberi}** sebesar **Rp{jumlah_utang:,}** jatuh tempo **HARI INI**!\n\nSegera bayar dengan: `!bayarpemain @{nama_pemberi} {jumlah_utang}`"
                
            elif sisa_hari == 1:  # Besok jatuh tempo
                pesan = f"⏰ **PERINGATAN UTANG**\n\nUtang kamu ke **{nama_pemberi}** sebesar **Rp{jumlah_utang:,}** akan jatuh tempo **BESOK**!\n\nSiapkan uang untuk membayar: `!bayarpemain @{nama_pemberi} {jumlah_utang}`"
                
            elif sisa_hari == 3:  # 3 hari lagi
                pesan = f"📅 **Pengingat Utang**\n\nUtang kamu ke **{nama_pemberi}** sebesar **Rp{jumlah_utang:,}** akan jatuh tempo dalam **3 hari**.\n\nMulai siapkan uang untuk pembayaran!"
            
            # Kirim notifikasi jika ada pesan
            if pesan:
                await kirim_notif_dm(user_id, pesan)
                await asyncio.sleep(1)  # Delay untuk avoid rate limit

@tasks.loop(hours=6)  # Cek setiap 6 jam
async def notifikasi_utang_loop():
    await cek_dan_kirim_notifikasi()

@tasks.loop(hours=2)  # Cek kondisi kesehatan setiap 2 jam
async def notifikasi_kondisi_loop():
    await cek_dan_kirim_notifikasi_kondisi()

@bot.event
async def on_ready():
    bot.start_time = time.time()  # Track start time
    print(f'Bot siap! Login sebagai {bot.user}')
    print(f'Health check endpoint: http://0.0.0.0:5000/')
    notifikasi_utang_loop.start()  # Mulai loop notifikasi utang
    notifikasi_kondisi_loop.start()  # Mulai loop notifikasi kondisi
    real_estate_management.start()  # Mulai loop real estate management
    update_market_trends.start()  # Mulai loop market trends
    print("Semua sistem background dimulai!")

# !daftar
@bot.command()
async def daftar(ctx):
    user_id = str(ctx.author.id)
    
    # Cek apakah user sudah pernah daftar
    if user_id in data:
        await ctx.send("❌ Kamu sudah terdaftar sebelumnya! Gunakan `!profil` untuk melihat data kamu.")
        return
    
    # User baru - buat profil
    create_user_profile(user_id)
    
    await ctx.send(f"{ctx.author.mention}, akun kamu berhasil dibuat ✅\n\n📱 **Cek DM kamu untuk panduan lengkap sistem bot!**")
    
    # Kirim panduan lengkap ke DM
    await send_welcome_guide(ctx.author)

# !profil - Profil lengkap user
@bot.command()
async def profil(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("User belum terdaftar. Ketik `!daftar` dulu.")
        return
    
    # Pastikan data user sudah ter-update dengan field baru
    create_user_profile(user_id)
    init_building_system()
    user_data = data[user_id]
    
    # Apply life effects sebelum menampilkan profil
    user_data = apply_life_effects(user_data)
    save_data(data)
    
    level = calculate_level(user_data["xp"])
    rank = get_rank(level)
    sick_conditions = check_sickness(user_data)
    
    # Warna embed berdasarkan kondisi kesehatan
    if sick_conditions:
        embed_color = 0xff0000  # Merah jika sakit
    elif user_data["kesehatan"] < 50:
        embed_color = 0xff9900  # Orange jika kesehatan rendah
    else:
        embed_color = 0x00ff00  # Hijau jika sehat
    
    embed = discord.Embed(title=f"👤 Profil {member.display_name}", color=embed_color)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    # Info dasar
    embed.add_field(name="💰 Uang", value=f"Rp{user_data['uang']:,}", inline=True)
    embed.add_field(name="⭐ XP", value=f"{user_data['xp']:,}", inline=True)
    embed.add_field(name="📊 Level", value=f"{level}", inline=True)
    embed.add_field(name="🏆 Rank", value=rank, inline=True)
    embed.add_field(name="💼 Pekerjaan", value=user_data['pekerjaan'] or "Tidak bekerja", inline=True)
    embed.add_field(name="📈 Status", value=user_data['status_kerja'], inline=True)
    
    # Lokasi info
    location_data = user_data.get("location", {"current_city": "jakarta", "current_building": None})
    current_city = location_data["current_city"]
    current_building = location_data.get("current_building")
    
    city_info = cities.get(current_city, {"nama": "Jakarta"})
    location_text = f"🏙️ {city_info['nama']}"
    
    if current_building and current_building in city_info.get("buildings", {}):
        building_info = city_info["buildings"][current_building]
        location_text += f"\n🏢 {building_info['nama']}"
    else:
        location_text += "\n🚶 Area umum"
    
    embed.add_field(name="📍 Lokasi", value=location_text, inline=True)
    
    # Life stats
    embed.add_field(name="🍽️ Lapar", value=get_status_bar(user_data['lapar']), inline=False)
    embed.add_field(name="💧 Haus", value=get_status_bar(user_data['haus']), inline=False)
    embed.add_field(name="❤️ Kesehatan", value=get_status_bar(user_data['kesehatan']), inline=False)
    embed.add_field(name="🏠 Tempat Tinggal", value=get_housing_name(user_data), inline=True)
    
    # Status sakit
    if sick_conditions:
        embed.add_field(name="🤒 Kondisi", value=" | ".join(sick_conditions), inline=True)
    
    if user_data['gaji'] > 0:
        embed.add_field(name="💵 Gaji", value=f"Rp{user_data['gaji']:,}", inline=True)
    
    if user_data['hutang'] > 0:
        embed.add_field(name="💳 Hutang", value=f"Rp{user_data['hutang']:,}", inline=True)
    
    # Rating Kredibilitas
    avg_rating = hitung_rating_rata_rata(user_data)
    jumlah_transaksi = user_data["rating_kredibilitas"]["transaksi_selesai"]
    trust_level = get_trust_level(avg_rating, jumlah_transaksi)
    
    if jumlah_transaksi > 0:
        rating_text = f"{avg_rating:.1f}/5.0 ⭐\n{trust_level}\n({user_data['rating_kredibilitas']['jumlah_rating']} rating, {jumlah_transaksi} transaksi)"
        embed.add_field(name="🏦 Kredibilitas", value=rating_text, inline=True)
    
    # Inventory
    if user_data['inventory']:
        inv_text = ""
        for item, jumlah in user_data['inventory'].items():
            inv_text += f"• {item.title()} x{jumlah}\n"
        embed.add_field(name="🎒 Inventory", value=inv_text[:1024], inline=False)
    
    embed.set_footer(text=f"Streak kerja: {user_data['streak']} hari")
    await ctx.send(embed=embed)

# !saldo
@bot.command()
async def saldo(ctx):
    user_id = str(ctx.author.id)
    if user_id in data:
        uang = data[user_id]["uang"]
        await ctx.send(f"{ctx.author.mention}, saldo kamu: Rp{uang:,}")
    else:
        await ctx.send("Kamu belum daftar. Ketik `!daftar` dulu.")

# !kerja - Sistem kerja sederhana dengan cooldown
@bot.command()
async def kerja(ctx):
    user_id = str(ctx.author.id)
    if user_id not in data:
        await ctx.send("Kamu belum daftar. Ketik `!daftar` dulu.")
        return
    
    # Cek apakah user sedang tidur
    if check_sleep_status(user_id):
        await ctx.send("😴 Kamu sedang tidur! Bangun dulu dengan `!bangun` sebelum bisa kerja.")
        return
    
    # Apply life effects
    data[user_id] = apply_life_effects(data[user_id])
    
    # Cek kondisi kesehatan
    sick_conditions = check_sickness(data[user_id])
    if sick_conditions:
        await ctx.send(f"❌ Kamu tidak bisa bekerja karena kondisi: **{', '.join(sick_conditions)}**\nMakan, minum, dan beristirahat dulu!")
        return
    
    if data[user_id]["kesehatan"] < 30:
        await ctx.send("❌ Kesehatan kamu terlalu rendah untuk bekerja! Minum obat atau istirahat dulu.")
        return
    
    # Cooldown 1 jam
    current_time = int(time.time())
    last_work = data[user_id].get("last_work_simple", 0)
    if current_time - last_work < 3600:  # 1 jam
        remaining = 3600 - (current_time - last_work)
        await ctx.send(f"⏰ Tunggu {remaining//60} menit lagi untuk kerja lagi.")
        return
    
    # Calculate earnings
    level = calculate_level(data[user_id]["xp"])
    base_pay = 50000 + (level * 2000)  # Rp50k + bonus level
    
    # Bonus streak
    streak_bonus = min(data[user_id].get("streak", 0) * 5000, 50000)  # Max 50k
    
    total_earnings = base_pay + streak_bonus
    
    # Process work
    data[user_id]["uang"] += total_earnings
    data[user_id]["xp"] += 25
    data[user_id]["last_work_simple"] = current_time
    
    # Update streak
    if data[user_id].get('last_work'):
        last_work_date = datetime.fromisoformat(data[user_id]['last_work'])
        if datetime.now().date() - last_work_date.date() == timedelta(days=1):
            data[user_id]['streak'] += 1
        elif datetime.now().date() - last_work_date.date() > timedelta(days=1):
            data[user_id]['streak'] = 1
    else:
        data[user_id]['streak'] = 1
    
    data[user_id]['last_work'] = datetime.now().isoformat()
    
    # Efek pada kondisi
    data[user_id]["lapar"] = max(0, data[user_id]["lapar"] - 10)
    data[user_id]["haus"] = max(0, data[user_id]["haus"] - 15)
    data[user_id]["kesehatan"] = max(0, data[user_id]["kesehatan"] - 5)
    
    embed = discord.Embed(title="💼 Kerja Selesai!", color=0x00ff00)
    embed.add_field(name="💰 Gaji Dasar", value=f"Rp{base_pay:,}", inline=True)
    embed.add_field(name="🔥 Bonus Streak", value=f"Rp{streak_bonus:,}", inline=True)
    embed.add_field(name="💎 Total", value=f"Rp{total_earnings:,}", inline=True)
    embed.add_field(name="⭐ XP", value="+25", inline=True)
    embed.add_field(name="🔥 Streak", value=f"{data[user_id]['streak']} hari", inline=True)
    embed.add_field(name="⏰ Cooldown", value="1 jam", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !apply - Melamar pekerjaan tetap
@bot.command()
async def apply(ctx, *, nama_pekerjaan):
    user_id = str(ctx.author.id)
    if user_id not in data:
        await ctx.send("Kamu belum daftar. Ketik `!daftar` dulu.")
        return
    
    job = jobs.get(nama_pekerjaan.lower())
    if not job:
        await ctx.send("❌ Pekerjaan tidak ditemukan.")
        return
    
    level = calculate_level(data[user_id]["xp"])
    if level < job["requirement_level"]:
        await ctx.send(f"❌ Level kamu ({level}) belum cukup untuk pekerjaan ini. Minimal level {job['requirement_level']}.")
        return
    
    if data[user_id]["pekerjaan"]:
        await ctx.send("❌ Kamu sudah bekerja. Ketik `!resign` dulu untuk keluar dari pekerjaan saat ini.")
        return
    
    # Proses aplikasi
    success_rate = min(70 + (level * 2), 95)  # Max 95% success rate
    if random.randint(1, 100) <= success_rate:
        data[user_id]["pekerjaan"] = nama_pekerjaan.lower()
        data[user_id]["gaji"] = job["gaji"]
        data[user_id]["status_kerja"] = "Bekerja"
        save_data(data)
        
        embed = discord.Embed(title="🎉 Lamaran Diterima!", color=0x00ff00)
        embed.add_field(name="💼 Pekerjaan", value=nama_pekerjaan.title(), inline=True)
        embed.add_field(name="💰 Gaji", value=f"Rp{job['gaji']:,}", inline=True)
        embed.add_field(name="📍 Lokasi", value=job['lokasi'], inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Lamaran ditolak. Coba lagi nanti atau tingkatkan level kamu. (Success rate: {success_rate}%)")

# !resign - Keluar dari pekerjaan
@bot.command()
async def resign(ctx):
    user_id = str(ctx.author.id)
    if user_id not in data:
        await ctx.send("Kamu belum daftar.")
        return
    
    if not data[user_id]["pekerjaan"]:
        await ctx.send("❌ Kamu tidak sedang bekerja.")
        return
    
    old_job = data[user_id]["pekerjaan"]
    data[user_id]["pekerjaan"] = None
    data[user_id]["gaji"] = 0
    data[user_id]["status_kerja"] = "Menganggur"
    save_data(data)
    
    await ctx.send(f"✅ Kamu berhasil resign dari pekerjaan **{old_job.title()}**.")

# !gajian - Ambil gaji bulanan
@bot.command()
async def gajian(ctx):
    user_id = str(ctx.author.id)
    if user_id not in data:
        await ctx.send("Kamu belum daftar.")
        return
    
    if not data[user_id]["pekerjaan"] or data[user_id]["gaji"] == 0:
        await ctx.send("❌ Kamu tidak memiliki pekerjaan tetap.")
        return
    
    gaji = data[user_id]["gaji"]
    
    # Bonus dari item
    if "seragam" in data[user_id]["inventory"]:
        gaji = int(gaji * 1.1)  # +10% dari seragam
    
    data[user_id]["uang"] += gaji
    data[user_id]["xp"] += jobs[data[user_id]["pekerjaan"]]["xp"]
    save_data(data)
    
    await ctx.send(f"💰 {ctx.author.mention} menerima gaji sebesar Rp{gaji:,} dari pekerjaan **{data[user_id]['pekerjaan'].title()}**!")

# !toko - Lihat toko item
@bot.command()
async def toko(ctx):
    embed = discord.Embed(title="🛒 Toko Item", color=0x0099ff)
    
    # Kategori makanan
    makanan = "**🍽️ Makanan:**\n"
    for item_name, item_data in items.items():
        if item_data["effect"] == "food":
            makanan += f"• {item_name.title()} - Rp{item_data['harga']:,} (+{item_data['hunger_restore']} kenyang)\n"
    
    # Kategori minuman
    minuman = "**💧 Minuman:**\n"
    for item_name, item_data in items.items():
        if item_data["effect"] == "drink":
            minuman += f"• {item_name.title()} - Rp{item_data['harga']:,} (+{item_data['thirst_restore']} hidrasi)\n"
    
    # Kategori obat
    obat = "**💊 Obat-obatan:**\n"
    for item_name, item_data in items.items():
        if item_data["effect"] == "medicine":
            obat += f"• {item_name.title()} - Rp{item_data['harga']:,} (+{item_data['health_restore']} kesehatan)\n"
    
    # Kategori tempat tinggal
    rumah = "**🏠 Tempat Tinggal:**\n"
    for item_name, item_data in items.items():
        if item_data["effect"] == "housing":
            rumah += f"• {item_name.title()} - Rp{item_data['harga']:,} (Level {item_data['housing_level']})\n"
    
    # Kategori lainnya
    lainnya = "**🔧 Lainnya:**\n"
    for item_name, item_data in items.items():
        if item_data["effect"] not in ["food", "drink", "medicine", "housing"]:
            lainnya += f"• {item_name.title()} - Rp{item_data['harga']:,}\n"
    
    embed.add_field(name="\u200b", value=makanan, inline=True)
    embed.add_field(name="\u200b", value=minuman, inline=True)
    embed.add_field(name="\u200b", value=obat, inline=True)
    embed.add_field(name="\u200b", value=rumah, inline=True)
    embed.add_field(name="\u200b", value=lainnya, inline=True)
    
    embed.set_footer(text="!beli [item] | !makan [makanan] | !minum [minuman] | !obat [obat]")
    await ctx.send(embed=embed)

# !beli - Beli item dari toko atau marketplace
@bot.command()
async def beli(ctx, listing_id_or_item=None, *, nama_item=None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if not listing_id_or_item:
        await ctx.send("❌ Masukkan listing ID untuk marketplace atau nama item untuk toko: `!beli [listing_id/nama_item]`")
        return
    
    # Cek apakah ini adalah listing ID dari marketplace (8 karakter)
    if len(listing_id_or_item) == 8 and listing_id_or_item.isalnum():
        # Beli dari marketplace
        if "marketplace" not in data or not data["marketplace"]:
            await ctx.send("❌ Marketplace kosong.")
            return
        
        # Cari listing berdasarkan ID (partial match)
        target_listing = None
        target_id = None
        
        for listing_id, listing in data["marketplace"].items():
            if listing_id.endswith(listing_id_or_item) or listing_id[-8:] == listing_id_or_item:
                target_listing = listing
                target_id = listing_id
                break
        
        if not target_listing:
            await ctx.send(f"❌ Listing dengan ID `{listing_id_or_item}` tidak ditemukan.")
            return
        
        # Tidak bisa beli item sendiri
        if target_listing["seller_id"] == user_id:
            await ctx.send("❌ Kamu tidak bisa membeli item yang kamu jual sendiri.")
            return
        
        # Cek uang
        price = target_listing["price"]
        if data[user_id]["uang"] < price:
            await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{price:,}")
            return
        
        # Proses transaksi marketplace
        item_name = target_listing["item"]
        seller_id = target_listing["seller_id"]
        seller_name = target_listing["seller_name"]
        
        # Kurangi uang pembeli
        data[user_id]["uang"] -= price
        
        # Tambah uang penjual
        if seller_id in data:
            data[seller_id]["uang"] += price
        
        # Tambah item ke inventory pembeli
        if item_name not in data[user_id]["inventory"]:
            data[user_id]["inventory"][item_name] = 0
        data[user_id]["inventory"][item_name] += 1
        
        # Hapus listing dari marketplace
        del data["marketplace"][target_id]
        
        save_data(data)
        
        embed = discord.Embed(title="🛒 Pembelian Berhasil!", color=0x00ff00)
        embed.add_field(name="📦 Item", value=item_name.title(), inline=True)
        embed.add_field(name="💰 Harga", value=f"Rp{price:,}", inline=True)
        embed.add_field(name="👤 Penjual", value=seller_name, inline=True)
        embed.add_field(name="💳 Saldo Tersisa", value=f"Rp{data[user_id]['uang']:,}", inline=False)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
        
        # Notifikasi ke penjual
        if seller_id in data:
            pesan_notif = f"💰 **Item Terjual!**\n\n**{ctx.author.display_name}** membeli **{item_name.title()}** dari kamu seharga **Rp{price:,}**.\n\n💳 Saldo baru: **Rp{data[seller_id]['uang']:,}**"
            await kirim_notif_dm(seller_id, pesan_notif)
        
        return
    
    # Beli dari toko (sistem lama)
    if nama_item:
        item_name = f"{listing_id_or_item} {nama_item}"
    else:
        item_name = listing_id_or_item
    
    # Apply life effects
    data[user_id] = apply_life_effects(data[user_id])
    
    item = items.get(item_name.lower())
    if not item:
        await ctx.send("❌ Item tidak ditemukan di toko. Gunakan `!toko` untuk melihat item atau `!pasar` untuk marketplace.")
        return
    
    if data[user_id]["uang"] < item["harga"]:
        await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{item['harga']:,}")
        return
    
    data[user_id]["uang"] -= item["harga"]
    
    # Langsung konsumsi jika makanan/minuman/obat
    if item["effect"] in ["food", "drink", "medicine"]:
        result_message = f"✅ {ctx.author.mention} berhasil **mengonsumsi** **{item_name.title()}** seharga Rp{item['harga']:,}!\n\n"
        
        if item["effect"] == "food":
            old_hunger = data[user_id]["lapar"]
            data[user_id]["lapar"] = min(100, data[user_id]["lapar"] + item["hunger_restore"])
            result_message += f"🍽️ Lapar: {old_hunger} → {data[user_id]['lapar']} (+{item['hunger_restore']})"
        
        elif item["effect"] == "drink":
            old_thirst = data[user_id]["haus"]
            data[user_id]["haus"] = min(100, data[user_id]["haus"] + item["thirst_restore"])
            result_message += f"💧 Haus: {old_thirst} → {data[user_id]['haus']} (+{item['thirst_restore']})"
            
            # Energy drink juga restore health
            if "health_restore" in item:
                old_health = data[user_id]["kesehatan"]
                data[user_id]["kesehatan"] = min(100, data[user_id]["kesehatan"] + item["health_restore"])
                result_message += f"\n❤️ Kesehatan: {old_health} → {data[user_id]['kesehatan']} (+{item['health_restore']})"
        
        elif item["effect"] == "medicine":
            old_health = data[user_id]["kesehatan"]
            data[user_id]["kesehatan"] = min(100, data[user_id]["kesehatan"] + item["health_restore"])
            result_message += f"❤️ Kesehatan: {old_health} → {data[user_id]['kesehatan']} (+{item['health_restore']})"
    
    # Housing upgrade system
    elif item["effect"] == "housing":
        current_housing_level = 0
        housing_items = {"tenda": 1, "kontrakan": 2, "rumah": 3, "villa": 4}
        
        # Cek level housing saat ini
        for housing_item, level in housing_items.items():
            if housing_item in data[user_id]["inventory"]:
                current_housing_level = max(current_housing_level, level)
        
        new_level = item["housing_level"]
        if new_level <= current_housing_level:
            data[user_id]["uang"] += item["harga"]  # Refund
            await ctx.send(f"❌ Kamu sudah memiliki tempat tinggal yang sama atau lebih baik!")
            return
        
        # Remove housing lama dan add yang baru
        for housing_item in housing_items.keys():
            if housing_item in data[user_id]["inventory"]:
                del data[user_id]["inventory"][housing_item]
        
        data[user_id]["inventory"][item_name.lower()] = 1
        result_message = f"🏠 {ctx.author.mention} berhasil **upgrade tempat tinggal** ke **{item_name.title()}** seharga Rp{item['harga']:,}!\n\nSekarang kondisi hidup kamu akan lebih terjaga."
    
    # Item lainnya (tools, etc.)
    else:
        if item_name.lower() not in data[user_id]["inventory"]:
            data[user_id]["inventory"][item_name.lower()] = 0
        data[user_id]["inventory"][item_name.lower()] += 1
        result_message = f"✅ {ctx.author.mention} berhasil membeli **{item_name.title()}** seharga Rp{item['harga']:,}!"
    
    save_data(data)
    await ctx.send(result_message)

# !leaderboard - Ranking user
@bot.command()
async def leaderboard(ctx):
    if not data:
        await ctx.send("Belum ada data user.")
        return
    
    # Sort berdasarkan level (XP)
    sorted_users = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 Leaderboard", color=0xffd700)
    
    for i, (user_id, user_data) in enumerate(sorted_users, 1):
        try:
            user = bot.get_user(int(user_id))
            username = user.display_name if user else f"User {user_id[:4]}..."
            level = calculate_level(user_data["xp"])
            rank = get_rank(level)
            
            embed.add_field(
                name=f"{i}. {username}",
                value=f"Level {level} ({rank})\nXP: {user_data['xp']:,}\nUang: Rp{user_data['uang']:,}",
                inline=True
            )
        except:
            continue
    
    await ctx.send(embed=embed)

# !pekerjaan (daftar semua pekerjaan)
@bot.command()
async def pekerjaan(ctx):
    embed = discord.Embed(title="📋 Daftar Pekerjaan Tersedia", color=0x00ff00)
    
    # Kategori Hukum
    hukum = "**⚖️ Bidang Hukum:**\n"
    hukum += "• Hakim (Rp18.000.000) - Lv.15\n• Pengacara (Rp15.000.000) - Lv.12\n• Jaksa (Rp16.000.000) - Lv.14\n"
    
    # Kategori Medis
    medis = "**🩺 Bidang Medis:**\n"
    medis += "• Dokter Umum (Rp25.000.000) - Lv.18\n• Dokter Gigi (Rp30.000.000) - Lv.16\n• Dokter Anak (Rp35.000.000) - Lv.20\n• Dokter Bedah (Rp50.000.000) - Lv.25\n"
    
    # Kategori Pendidikan
    pendidikan = "**📚 Bidang Pendidikan:**\n"
    pendidikan += "• Guru SD (Rp3.500.000) - Lv.5\n• Guru SMP (Rp4.000.000) - Lv.7\n• Guru SMA (Rp4.500.000) - Lv.8\n• Dosen (Rp12.000.000) - Lv.10\n"
    
    # Kategori Teknologi
    teknologi = "**💻 Bidang Teknologi:**\n"
    teknologi += "• Programmer (Rp8.000.000) - Lv.12\n• Data Analyst (Rp9.000.000) - Lv.14\n"
    
    # Kategori Transportasi
    transportasi = "**✈️ Bidang Transportasi:**\n"
    transportasi += "• Pilot (Rp40.000.000) - Lv.30\n• Pramugari (Rp8.000.000) - Lv.15\n• Sopir Truk (Rp4.500.000) - Lv.8\n"
    
    # Kategori Retail & Service
    retail = "**🛍️ Bidang Retail & Service:**\n"
    retail += "• Pegawai Toko (Rp3.000.000) - Lv.3\n• Kasir (Rp3.000.000) - Lv.3\n• Barista (Rp3.500.000) - Lv.4\n• Montir (Rp4.000.000) - Lv.6\n"
    
    embed.add_field(name="\u200b", value=hukum, inline=True)
    embed.add_field(name="\u200b", value=medis, inline=True)
    embed.add_field(name="\u200b", value=pendidikan, inline=True)
    embed.add_field(name="\u200b", value=teknologi, inline=True)
    embed.add_field(name="\u200b", value=transportasi, inline=True)
    embed.add_field(name="\u200b", value=retail, inline=True)
    
    embed.set_footer(text="Gunakan !apply [nama_pekerjaan] untuk melamar | !jobinfo [nama] untuk detail")
    await ctx.send(embed=embed)

# !jobinfo (info detail pekerjaan)
@bot.command()
async def jobinfo(ctx, *, nama_pekerjaan):
    pekerjaan = jobs.get(nama_pekerjaan.lower())
    if pekerjaan:
        deskripsi = pekerjaan['deskripsi']
        gaji = pekerjaan['gaji']
        xp = pekerjaan['xp']
        lokasi = pekerjaan['lokasi']
        jam = pekerjaan['jam_kerja']
        req_level = pekerjaan['requirement_level']
        
        embed = discord.Embed(title=f"💼 {nama_pekerjaan.title()}", color=0x0099ff)
        embed.add_field(name="📍 Lokasi", value=lokasi, inline=True)
        embed.add_field(name="🕒 Jam Kerja", value=jam, inline=True)
        embed.add_field(name="💰 Gaji", value=f"Rp{gaji:,}", inline=True)
        embed.add_field(name="⭐ XP", value=f"{xp} XP", inline=True)
        embed.add_field(name="📊 Level Minimum", value=f"Level {req_level}", inline=True)
        embed.add_field(name="📝 Deskripsi", value=deskripsi, inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Pekerjaan tidak ditemukan. Ketik `!pekerjaan` untuk melihat daftar lengkap.")

# !pinjampemain - Pinjam uang dari pemain lain
@bot.command()
async def pinjampemain(ctx, target: discord.Member, jumlah: int):
    pemberi_id = str(ctx.author.id)
    peminjam_id = str(target.id)

    create_user_profile(pemberi_id)
    create_user_profile(peminjam_id)

    if jumlah <= 0:
        await ctx.send("❌ Jumlah pinjaman harus lebih dari 0.")
        return

    if data[pemberi_id]["uang"] < jumlah:
        await ctx.send(f"❌ {ctx.author.display_name} tidak memiliki cukup uang untuk meminjamkan Rp{jumlah:,}.")
        return

    # Kurangi uang pemberi, tambahkan ke peminjam
    data[pemberi_id]["uang"] -= jumlah
    data[peminjam_id]["uang"] += jumlah

    # Inisialisasi jika belum ada
    if "utang_ke_pemain" not in data[peminjam_id]:
        data[peminjam_id]["utang_ke_pemain"] = {}

    utang_pemain = data[peminjam_id]["utang_ke_pemain"]

    sekarang = int(time.time())
    jatuh_tempo = sekarang + (PINJAMAN_BATAS_HARI * 86400)

    # Tambahkan data utang
    if pemberi_id in utang_pemain:
        utang_pemain[pemberi_id]["jumlah_pokok"] += jumlah
        utang_pemain[pemberi_id]["jatuh_tempo"] = jatuh_tempo
        utang_pemain[pemberi_id]["waktu_pinjam"] = sekarang
    else:
        utang_pemain[pemberi_id] = {
            "jumlah_pokok": jumlah,
            "waktu_pinjam": sekarang,
            "jatuh_tempo": jatuh_tempo
        }

    save_data(data)

    # Kirim notifikasi ke channel
    embed = discord.Embed(
        title="✅ Pinjaman Tercatat",
        description=f"**{ctx.author.display_name}** meminjam **Rp{jumlah:,}** dari **{target.display_name}**.",
        color=0x2ecc71
    )
    embed.set_footer(text="Jatuh tempo dalam 7 hari")
    await ctx.send(embed=embed)

    embed = discord.Embed(title="💰 Pinjaman Berhasil", color=0x00ff00)
    embed.add_field(name="Peminjam", value=ctx.author.display_name, inline=True)
    embed.add_field(name="Pemberi Pinjaman", value=target.display_name, inline=True)
    embed.add_field(name="Jumlah", value=f"Rp{jumlah:,}", inline=True)
    embed.add_field(name="Batas Waktu", value=f"{PINJAMAN_BATAS_HARI} hari", inline=False)
    await ctx.send(embed=embed)
    
    # Kirim notifikasi DM ke peminjam
    pesan_konfirmasi = f"💰 **Konfirmasi Pinjaman**\n\nKamu berhasil meminjam **Rp{jumlah:,}** dari **{target.display_name}**.\n\n⏰ **Batas waktu pembayaran: {PINJAMAN_BATAS_HARI} hari**\n\nKamu akan menerima pengingat otomatis sebelum jatuh tempo. Bayar dengan: `!bayarpemain @{target.display_name} {jumlah}`"
    await kirim_notif_dm(peminjam_id, pesan_konfirmasi)

# ===== SISTEM PELAPORAN UTANG KE PENGADILAN =====

# Initialize court system
def init_court_system():
    if "court_cases" not in data:
        data["court_cases"] = {}
    if "court_settings" not in data:
        data["court_settings"] = {
            "filing_fee": 100000,  # Biaya lapor ke pengadilan
            "judge_fee": 1000000,  # Fee hakim per sidang
            "prosecutor_fee": 600000,  # Fee jaksa per sidang 
            "lawyer_fee": 500000,  # Fee pengacara per sidang
            "fine_percentage": 0.5  # Denda 50% dari nilai utang
        }
    save_data(data)

# !laporutang - Laporkan penghutang ke pengadilan
@bot.command()
async def laporutang(ctx, penghutang: discord.Member, *, alasan=None):
    if not alasan:
        await ctx.send("⚖️ **Cara Lapor Utang ke Pengadilan:**\n`!laporutang @penghutang [alasan]`\n\n💰 **Biaya:** Rp100.000\n📋 **Syarat:** Utang sudah jatuh tempo\n🏛️ **Proses:** Hakim, Jaksa, Pengacara terlibat")
        return
    
    penuduh_id = str(ctx.author.id)
    tergugat_id = str(penghutang.id)
    
    if penuduh_id == tergugat_id:
        await ctx.send("❌ Kamu tidak bisa menuntut diri sendiri.")
        return
    
    create_user_profile(penuduh_id)
    create_user_profile(tergugat_id)
    init_court_system()
    
    # Cek apakah ada utang yang jatuh tempo
    if tergugat_id not in data or "utang_ke_pemain" not in data[tergugat_id]:
        await ctx.send("❌ Target tidak memiliki utang ke kamu.")
        return
    
    utang_data = data[tergugat_id]["utang_ke_pemain"].get(penuduh_id)
    if not utang_data:
        await ctx.send("❌ Target tidak memiliki utang ke kamu.")
        return
    
    # Cek apakah sudah jatuh tempo
    current_time = int(time.time())
    if utang_data["jatuh_tempo"] > current_time:
        sisa_hari = (utang_data["jatuh_tempo"] - current_time) // 86400
        await ctx.send(f"❌ Utang belum jatuh tempo. Sisa {sisa_hari} hari.")
        return
    
    # Biaya pengaduan
    filing_fee = data["court_settings"]["filing_fee"]
    if data[penuduh_id]["uang"] < filing_fee:
        await ctx.send(f"❌ Biaya pengaduan Rp{filing_fee:,} tidak cukup.")
        return
    
    # Buat kasus pengadilan
    case_id = f"case_{penuduh_id}_{tergugat_id}_{int(time.time())}"
    
    data["court_cases"][case_id] = {
        "plaintiff_id": penuduh_id,
        "plaintiff_name": ctx.author.display_name,
        "defendant_id": tergugat_id,
        "defendant_name": penghutang.display_name,
        "debt_amount": utang_data["jumlah_pokok"],
        "reason": alasan,
        "case_type": "debt_collection",
        "status": "waiting_for_legal_team",
        "filed_date": current_time,
        "judge_id": None,
        "prosecutor_id": None,
        "defense_lawyer_id": None,
        "trial_date": None,
        "verdict": None
    }
    
    data[penuduh_id]["uang"] -= filing_fee
    save_data(data)
    
    embed = discord.Embed(title="⚖️ Laporan Utang Diterima", color=0xff9900)
    embed.add_field(name="🏛️ Case ID", value=case_id[-8:], inline=True)
    embed.add_field(name="👨‍💼 Penuduh", value=ctx.author.display_name, inline=True)
    embed.add_field(name="👤 Tergugat", value=penghutang.display_name, inline=True)
    embed.add_field(name="💰 Nilai Utang", value=f"Rp{utang_data['jumlah_pokok']:,}", inline=True)
    embed.add_field(name="💸 Biaya Pengaduan", value=f"Rp{filing_fee:,}", inline=True)
    embed.add_field(name="📋 Status", value="Menunggu tim hukum", inline=True)
    embed.add_field(name="📝 Alasan", value=alasan[:200], inline=False)
    embed.add_field(name="📋 Selanjutnya", value="Hakim, Jaksa, dan Pengacara dapat mengambil kasus ini", inline=False)
    
    await ctx.send(embed=embed)
    
    # Notifikasi ke tergugat
    pesan_notif = f"⚖️ **PANGGILAN PENGADILAN**\n\n**{ctx.author.display_name}** telah melaporkan utang kamu ke pengadilan!\n\n💰 **Nilai utang:** Rp{utang_data['jumlah_pokok']:,}\n🏛️ **Case ID:** {case_id[-8:]}\n📝 **Alasan:** {alasan}\n\n🔍 Kamu bisa mencari pengacara pembela dengan `!cariadvokatpengacara {case_id[-8:]}`"
    await kirim_notif_dm(tergugat_id, pesan_notif)

# !cariadvokatpengacara - Cari pengacara untuk kasus tertentu
@bot.command()
async def cariadvokatpengacara(ctx, case_id=None):
    if not case_id:
        await ctx.send("🔍 **Cara Cari Pengacara:**\n`!cariadvokatpengacara [case_id]`\n\n💼 Hanya tergugat yang bisa mencari pengacara pembela")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_court_system()
    
    # Cari kasus berdasarkan ID
    target_case = None
    full_case_id = None
    
    for full_id, case_data in data["court_cases"].items():
        if full_id.endswith(case_id) or full_id[-8:] == case_id:
            target_case = case_data
            full_case_id = full_id
            break
    
    if not target_case:
        await ctx.send(f"❌ Kasus dengan ID `{case_id}` tidak ditemukan.")
        return
    
    # Hanya tergugat yang bisa cari pengacara
    if target_case["defendant_id"] != user_id:
        await ctx.send("❌ Hanya tergugat yang bisa mencari pengacara untuk kasus ini.")
        return
    
    if target_case["defense_lawyer_id"]:
        await ctx.send("❌ Kasus ini sudah memiliki pengacara pembela.")
        return
    
    embed = discord.Embed(title="🔍 Mencari Pengacara Pembela", color=0x0099ff)
    embed.add_field(name="🏛️ Case ID", value=case_id, inline=True)
    embed.add_field(name="👤 Tergugat", value=ctx.author.display_name, inline=True)
    embed.add_field(name="💰 Nilai Kasus", value=f"Rp{target_case['debt_amount']:,}", inline=True)
    embed.add_field(name="💼 Fee Pengacara", value=f"Rp{data['court_settings']['lawyer_fee']:,}", inline=True)
    embed.add_field(name="📢 Panggilan", value="Pengacara dapat mengambil kasus ini dengan `!ambilkasus`", inline=False)
    embed.add_field(name="📋 Status", value=target_case["status"], inline=True)
    
    await ctx.send(embed=embed)

# !kasusaktif - Lihat kasus sesuai profesi
@bot.command()
async def kasusaktif(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if "court_cases" not in data or not data["court_cases"]:
        await ctx.send("⚖️ Tidak ada kasus aktif di pengadilan.")
        return
    
    user_job = data[user_id].get("pekerjaan", "").lower()
    
    if user_job not in ["hakim", "jaksa", "pengacara"]:
        await ctx.send("❌ Hanya Hakim, Jaksa, atau Pengacara yang bisa melihat kasus aktif.")
        return
    
    available_cases = []
    
    for case_id, case_data in data["court_cases"].items():
        if case_data["status"] == "waiting_for_legal_team":
            if user_job == "hakim" and not case_data["judge_id"]:
                available_cases.append((case_id, case_data))
            elif user_job == "jaksa" and not case_data["prosecutor_id"]:
                available_cases.append((case_id, case_data))
            elif user_job == "pengacara" and not case_data["defense_lawyer_id"]:
                available_cases.append((case_id, case_data))
    
    if not available_cases:
        await ctx.send(f"📋 Tidak ada kasus yang tersedia untuk {user_job.title()}.")
        return
    
    embed = discord.Embed(title=f"⚖️ Kasus Tersedia untuk {user_job.title()}", color=0x9b59b6)
    
    for case_id, case_data in available_cases[:10]:  # Max 10 kasus
        embed.add_field(
            name=f"🏛️ {case_id[-8:]}",
            value=f"👨‍💼 {case_data['plaintiff_name']} vs {case_data['defendant_name']}\n💰 Rp{case_data['debt_amount']:,}\n📅 {int((int(time.time()) - case_data['filed_date']) / 86400)} hari lalu",
            inline=True
        )
    
    fees = {
        "hakim": data["court_settings"]["judge_fee"],
        "jaksa": data["court_settings"]["prosecutor_fee"],
        "pengacara": data["court_settings"]["lawyer_fee"]
    }
    
    embed.add_field(name="💰 Fee per Sidang", value=f"Rp{fees[user_job]:,}", inline=False)
    embed.set_footer(text="!ambilkasus [case_id] untuk mengambil kasus")
    await ctx.send(embed=embed)

# !ambilkasus - Ambil kasus sebagai hakim/jaksa/pengacara
@bot.command()
async def ambilkasus(ctx, case_id=None):
    if not case_id:
        await ctx.send("⚖️ **Cara Ambil Kasus:**\n`!ambilkasus [case_id]`\n\n📋 Gunakan `!kasusaktif` untuk melihat kasus tersedia")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_court_system()
    
    user_job = data[user_id].get("pekerjaan", "").lower()
    if user_job not in ["hakim", "jaksa", "pengacara"]:
        await ctx.send("❌ Hanya Hakim, Jaksa, atau Pengacara yang bisa mengambil kasus.")
        return
    
    # Cari kasus berdasarkan ID
    target_case = None
    full_case_id = None
    
    for full_id, case_data in data["court_cases"].items():
        if full_id.endswith(case_id) or full_id[-8:] == case_id:
            target_case = case_data
            full_case_id = full_id
            break
    
    if not target_case:
        await ctx.send(f"❌ Kasus dengan ID `{case_id}` tidak ditemukan.")
        return
    
    if target_case["status"] != "waiting_for_legal_team":
        await ctx.send("❌ Kasus ini sudah tidak tersedia.")
        return
    
    # Cek apakah posisi sudah terisi
    if user_job == "hakim" and target_case["judge_id"]:
        await ctx.send("❌ Kasus ini sudah memiliki hakim.")
        return
    elif user_job == "jaksa" and target_case["prosecutor_id"]:
        await ctx.send("❌ Kasus ini sudah memiliki jaksa.")
        return
    elif user_job == "pengacara" and target_case["defense_lawyer_id"]:
        await ctx.send("❌ Kasus ini sudah memiliki pengacara pembela.")
        return
    
    # Assign ke kasus
    if user_job == "hakim":
        target_case["judge_id"] = user_id
    elif user_job == "jaksa":
        target_case["prosecutor_id"] = user_id
    elif user_job == "pengacara":
        target_case["defense_lawyer_id"] = user_id
    
    # Cek apakah tim lengkap
    if target_case["judge_id"] and target_case["prosecutor_id"] and target_case["defense_lawyer_id"]:
        target_case["status"] = "ready_for_trial"
        target_case["trial_date"] = int(time.time()) + 3600  # Sidang 1 jam kemudian
    
    embed = discord.Embed(title="⚖️ Kasus Berhasil Diambil", color=0x00ff00)
    embed.add_field(name="🏛️ Case ID", value=case_id, inline=True)
    embed.add_field(name="👔 Peran", value=user_job.title(), inline=True)
    embed.add_field(name="💰 Nilai Kasus", value=f"Rp{target_case['debt_amount']:,}", inline=True)
    
    fees = {
        "hakim": data["court_settings"]["judge_fee"],
        "jaksa": data["court_settings"]["prosecutor_fee"],
        "pengacara": data["court_settings"]["lawyer_fee"]
    }
    
    embed.add_field(name="💰 Fee", value=f"Rp{fees[user_job]:,}", inline=True)
    
    if target_case["status"] == "ready_for_trial":
        embed.add_field(name="🎉 Status", value="Tim lengkap! Siap sidang!", inline=True)
        embed.add_field(name="📅 Jadwal", value="Sidang dapat dimulai sekarang", inline=True)
    else:
        embed.add_field(name="📋 Status", value="Menunggu tim lengkap", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# ===== SISTEM SIDANG HUKUM MENDALAM =====

# Initialize court system yang lebih kompleks
def init_advanced_court_system():
    if "court_cases" not in data:
        data["court_cases"] = {}
    if "court_settings" not in data:
        data["court_settings"] = {
            "filing_fee": 100000,
            "judge_fee": 1000000,
            "prosecutor_fee": 600000,
            "lawyer_fee": 500000,
            "fine_percentage": 0.5,
            "witness_fee": 200000,
            "expert_witness_fee": 500000
        }
    if "court_sessions" not in data:
        data["court_sessions"] = {}
    if "court_evidence" not in data:
        data["court_evidence"] = {}
    save_data(data)

# !sidang - Sistem sidang mendalam dengan tahapan
@bot.command()
async def sidang(ctx, case_id=None, tahap=None):
    if not case_id:
        await ctx.send("⚖️ **Sistem Sidang Mendalam:**\n`!sidang [case_id]` - Mulai sidang baru\n`!sidang [case_id] lanjut` - Lanjut ke tahap berikutnya\n`!sidang [case_id] vonis` - Bacakan vonis final\n\n👨‍⚖️ Hanya hakim yang bisa memimpin sidang")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_advanced_court_system()
    
    user_job = data[user_id].get("pekerjaan", "").lower()
    if user_job != "hakim":
        await ctx.send("❌ Hanya Hakim yang bisa memimpin sidang.")
        return
    
    # Cari kasus berdasarkan ID
    target_case = None
    full_case_id = None
    
    for full_id, case_data in data["court_cases"].items():
        if full_id.endswith(case_id) or full_id[-8:] == case_id:
            if case_data["judge_id"] == user_id:
                target_case = case_data
                full_case_id = full_id
                break
    
    if not target_case:
        await ctx.send(f"❌ Kasus dengan ID `{case_id}` tidak ditemukan atau bukan tanggung jawab kamu.")
        return
    
    if target_case["status"] != "ready_for_trial":
        await ctx.send("❌ Kasus belum siap untuk sidang. Tim hukum belum lengkap.")
        return
    
    # Initialize session jika belum ada
    if full_case_id not in data["court_sessions"]:
        data["court_sessions"][full_case_id] = {
            "tahap": "pembukaan",
            "tahap_selesai": [],
            "bukti_diajukan": [],
            "saksi_dipanggil": [],
            "argumen_jaksa": "",
            "argumen_pembela": "",
            "skor_jaksa": 0,
            "skor_pembela": 0,
            "session_start": int(time.time()),
            "transcript": []
        }
    
    session = data["court_sessions"][full_case_id]
    
    if tahap is None:
        # Tampilkan status sidang
        await show_court_session_status(ctx, case_id, target_case, session)
        return
    elif tahap.lower() == "lanjut":
        await proceed_court_session(ctx, case_id, target_case, session, user_id)
    elif tahap.lower() == "vonis":
        await deliver_final_verdict(ctx, case_id, target_case, session, user_id)
    else:
        await ctx.send("❌ Tahap tidak valid. Gunakan 'lanjut' atau 'vonis'")

async def show_court_session_status(ctx, case_id, target_case, session):
    """Tampilkan status sidang saat ini"""
    tahap_names = {
        "pembukaan": "Pembukaan Sidang",
        "dakwaan": "Pembacaan Dakwaan",
        "pembelaan": "Pembelaan Awal",
        "pembuktian": "Pembuktian",
        "saksi": "Pemeriksaan Saksi",
        "alegasi": "Alegasi & Duplik",
        "putusan": "Siap untuk Putusan"
    }
    
    current_tahap = session["tahap"]
    
    embed = discord.Embed(title="⚖️ Status Sidang", color=0x9b59b6)
    embed.add_field(name="🏛️ Case ID", value=case_id, inline=True)
    embed.add_field(name="📋 Tahap Saat Ini", value=tahap_names.get(current_tahap, current_tahap), inline=True)
    embed.add_field(name="⏰ Durasi", value=f"{int((int(time.time()) - session['session_start']) / 60)} menit", inline=True)
    
    # Progress bar
    all_tahaps = ["pembukaan", "dakwaan", "pembelaan", "pembuktian", "saksi", "alegasi", "putusan"]
    current_index = all_tahaps.index(current_tahap) if current_tahap in all_tahaps else 0
    progress = (current_index / len(all_tahaps)) * 100
    
    embed.add_field(name="📊 Progress", value=f"{progress:.1f}%", inline=True)
    
    # Skor sementara
    embed.add_field(name="⚔️ Skor Jaksa", value=f"{session['skor_jaksa']}", inline=True)
    embed.add_field(name="🛡️ Skor Pembela", value=f"{session['skor_pembela']}", inline=True)
    
    # Bukti dan saksi
    if session["bukti_diajukan"]:
        bukti_text = "\n".join([f"• {bukti}" for bukti in session["bukti_diajukan"][-3:]])
        embed.add_field(name="📄 Bukti Terbaru", value=bukti_text, inline=False)
    
    if session["saksi_dipanggil"]:
        saksi_text = "\n".join([f"• {saksi}" for saksi in session["saksi_dipanggil"][-3:]])
        embed.add_field(name="👥 Saksi Terbaru", value=saksi_text, inline=False)
    
    embed.add_field(name="📋 Selanjutnya", value="`!sidang [case_id] lanjut` untuk lanjut tahap", inline=False)
    
    await ctx.send(embed=embed)

async def proceed_court_session(ctx, case_id, target_case, session, judge_id):
    """Lanjutkan ke tahap berikutnya dalam sidang"""
    current_tahap = session["tahap"]
    
    if current_tahap == "pembukaan":
        await tahap_pembukaan(ctx, case_id, target_case, session)
        session["tahap"] = "dakwaan"
    elif current_tahap == "dakwaan":
        await tahap_dakwaan(ctx, case_id, target_case, session)
        session["tahap"] = "pembelaan"
    elif current_tahap == "pembelaan":
        await tahap_pembelaan(ctx, case_id, target_case, session)
        session["tahap"] = "pembuktian"
    elif current_tahap == "pembuktian":
        await tahap_pembuktian(ctx, case_id, target_case, session)
        session["tahap"] = "saksi"
    elif current_tahap == "saksi":
        await tahap_saksi(ctx, case_id, target_case, session)
        session["tahap"] = "alegasi"
    elif current_tahap == "alegasi":
        await tahap_alegasi(ctx, case_id, target_case, session)
        session["tahap"] = "putusan"
    else:
        await ctx.send("❌ Sidang sudah sampai tahap putusan. Gunakan `!sidang [case_id] vonis` untuk bacakan vonis.")
        return
    
    save_data(data)

async def tahap_pembukaan(ctx, case_id, target_case, session):
    """Tahap pembukaan sidang"""
    embed = discord.Embed(title="⚖️ PEMBUKAAN SIDANG", color=0x0099ff)
    embed.add_field(name="🏛️ Majelis Hakim", value=ctx.author.display_name, inline=True)
    embed.add_field(name="📋 Kasus", value=f"Penagihan Utang ID {case_id}", inline=True)
    embed.add_field(name="💰 Nilai Sengketa", value=f"Rp{target_case['debt_amount']:,}", inline=True)
    
    try:
        penggugat = bot.get_user(int(target_case["plaintiff_id"]))
        tergugat = bot.get_user(int(target_case["defendant_id"]))
        
        embed.add_field(name="👨‍💼 Penggugat", value=penggugat.display_name if penggugat else "Unknown", inline=True)
        embed.add_field(name="👤 Tergugat", value=tergugat.display_name if tergugat else "Unknown", inline=True)
    except:
        pass
    
    embed.add_field(name="📜 Pembukaan", value="Sidang dibuka untuk umum. Semua pihak hadir dan siap memulai persidangan.", inline=False)
    
    session["transcript"].append("PEMBUKAAN: Sidang resmi dibuka oleh Majelis Hakim")
    await ctx.send(embed=embed)

async def tahap_dakwaan(ctx, case_id, target_case, session):
    """Tahap pembacaan dakwaan oleh jaksa"""
    dakwaan_templates = [
        "Tergugat terbukti memiliki utang yang telah jatuh tempo dan menolak untuk melunasi",
        "Tergugat melakukan wanprestasi terhadap perjanjian hutang piutang",
        "Tergugat telah melanggar kesepakatan pembayaran yang telah ditetapkan",
        "Tergugat dengan sengaja menghindar dari kewajiban finansial"
    ]
    
    dakwaan = random.choice(dakwaan_templates)
    session["argumen_jaksa"] = dakwaan
    
    # Skor untuk jaksa berdasarkan kualitas dakwaan
    dakwaan_score = random.randint(15, 25)
    session["skor_jaksa"] += dakwaan_score
    
    embed = discord.Embed(title="⚔️ DAKWAAN JAKSA", color=0xff9900)
    embed.add_field(name="👨‍💼 Jaksa Penuntut", value="JPU Negara", inline=True)
    embed.add_field(name="📋 Dakwaan", value=dakwaan, inline=False)
    embed.add_field(name="💰 Tuntutan", value=f"Pembayaran utang Rp{target_case['debt_amount']:,} plus denda 50%", inline=False)
    embed.add_field(name="📊 Kekuatan Dakwaan", value=f"{dakwaan_score}/25", inline=True)
    
    session["transcript"].append(f"DAKWAAN: {dakwaan}")
    await ctx.send(embed=embed)

async def tahap_pembelaan(ctx, case_id, target_case, session):
    """Tahap pembelaan awal oleh pengacara"""
    pembelaan_templates = [
        "Klien kami memiliki kesulitan finansial yang legitimate dan perlu waktu tambahan",
        "Terdapat dispute mengenai jumlah utang yang sebenarnya harus dibayar",
        "Klien kami telah melakukan upaya pembayaran bertahap sesuai kemampuan",
        "Penggugat tidak memberikan kelonggaran waktu yang wajar untuk pembayaran"
    ]
    
    pembelaan = random.choice(pembelaan_templates)
    session["argumen_pembela"] = pembelaan
    
    # Skor untuk pembela berdasarkan kualitas pembelaan
    pembelaan_score = random.randint(12, 22)
    session["skor_pembela"] += pembelaan_score
    
    embed = discord.Embed(title="🛡️ PEMBELAAN", color=0x00ff00)
    embed.add_field(name="👨‍⚖️ Pengacara Pembela", value="Kuasa Hukum Tergugat", inline=True)
    embed.add_field(name="📋 Pembelaan", value=pembelaan, inline=False)
    embed.add_field(name="📊 Kekuatan Pembelaan", value=f"{pembelaan_score}/22", inline=True)
    
    session["transcript"].append(f"PEMBELAAN: {pembelaan}")
    await ctx.send(embed=embed)

async def tahap_pembuktian(ctx, case_id, target_case, session):
    """Tahap pembuktian dengan bukti-bukti"""
    bukti_jaksa = [
        "Screenshot percakapan WhatsApp tentang utang",
        "Nota kesepakatan pinjaman",
        "Riwayat transfer uang",
        "Bukti jatuh tempo pembayaran",
        "Screenshot notifikasi reminder"
    ]
    
    bukti_pembela = [
        "Bukti kesulitan finansial",
        "Riwayat upaya pembayaran parsial",
        "Dokumen force majeure",
        "Bukti komunikasi untuk negosiasi",
        "Pernyataan saksi ahli keuangan"
    ]
    
    # Random bukti yang diajukan
    jaksa_evidence = random.sample(bukti_jaksa, random.randint(2, 4))
    pembela_evidence = random.sample(bukti_pembela, random.randint(1, 3))
    
    # Skor berdasarkan kualitas bukti
    jaksa_evidence_score = len(jaksa_evidence) * random.randint(8, 12)
    pembela_evidence_score = len(pembela_evidence) * random.randint(6, 10)
    
    session["skor_jaksa"] += jaksa_evidence_score
    session["skor_pembela"] += pembela_evidence_score
    session["bukti_diajukan"] = jaksa_evidence + pembela_evidence
    
    embed = discord.Embed(title="📄 PEMBUKTIAN", color=0x9b59b6)
    
    jaksa_bukti_text = "\n".join([f"• {bukti}" for bukti in jaksa_evidence])
    pembela_bukti_text = "\n".join([f"• {bukti}" for bukti in pembela_evidence])
    
    embed.add_field(name="⚔️ Bukti Jaksa", value=jaksa_bukti_text, inline=True)
    embed.add_field(name="🛡️ Bukti Pembela", value=pembela_bukti_text, inline=True)
    embed.add_field(name="📊 Skor Bukti", value=f"Jaksa: +{jaksa_evidence_score}\nPembela: +{pembela_evidence_score}", inline=True)
    
    session["transcript"].append(f"BUKTI JAKSA: {', '.join(jaksa_evidence)}")
    session["transcript"].append(f"BUKTI PEMBELA: {', '.join(pembela_evidence)}")
    await ctx.send(embed=embed)

async def tahap_saksi(ctx, case_id, target_case, session):
    """Tahap pemeriksaan saksi"""
    saksi_jaksa = [
        "Saksi yang menyaksikan transaksi pinjaman",
        "Teman yang tahu tentang kesepakatan",
        "Saksi ahli perbankan",
        "Orang yang memediasi pinjaman"
    ]
    
    saksi_pembela = [
        "Keluarga yang tahu kondisi finansial",
        "Teman yang memahami situasi",
        "Saksi ahli hukum kontrak",
        "Mediator yang mencoba menyelesaikan"
    ]
    
    # Random saksi
    jaksa_witnesses = random.sample(saksi_jaksa, random.randint(1, 2))
    pembela_witnesses = random.sample(saksi_pembela, random.randint(1, 2))
    
    # Skor berdasarkan kualitas kesaksian
    jaksa_witness_score = len(jaksa_witnesses) * random.randint(10, 15)
    pembela_witness_score = len(pembela_witnesses) * random.randint(8, 13)
    
    session["skor_jaksa"] += jaksa_witness_score
    session["skor_pembela"] += pembela_witness_score
    session["saksi_dipanggil"] = jaksa_witnesses + pembela_witnesses
    
    # Bayar fee saksi dari kas pengadilan
    witness_total_fee = (len(jaksa_witnesses) + len(pembela_witnesses)) * data["court_settings"]["witness_fee"]
    
    embed = discord.Embed(title="👥 PEMERIKSAAN SAKSI", color=0xff6b6b)
    
    jaksa_saksi_text = "\n".join([f"• {saksi}" for saksi in jaksa_witnesses])
    pembela_saksi_text = "\n".join([f"• {saksi}" for saksi in pembela_witnesses])
    
    embed.add_field(name="⚔️ Saksi Jaksa", value=jaksa_saksi_text if jaksa_saksi_text else "Tidak ada", inline=True)
    embed.add_field(name="🛡️ Saksi Pembela", value=pembela_saksi_text if pembela_saksi_text else "Tidak ada", inline=True)
    embed.add_field(name="📊 Skor Kesaksian", value=f"Jaksa: +{jaksa_witness_score}\nPembela: +{pembela_witness_score}", inline=True)
    embed.add_field(name="💰 Fee Saksi", value=f"Rp{witness_total_fee:,}", inline=False)
    
    session["transcript"].append(f"SAKSI JAKSA: {', '.join(jaksa_witnesses)}")
    session["transcript"].append(f"SAKSI PEMBELA: {', '.join(pembela_witnesses)}")
    await ctx.send(embed=embed)

async def tahap_alegasi(ctx, case_id, target_case, session):
    """Tahap alegasi dan duplik final"""
    
    # Alegasi final berdasarkan skor yang terkumpul
    jaksa_total = session["skor_jaksa"]
    pembela_total = session["skor_pembela"]
    
    alegasi_jaksa = [
        "Berdasarkan bukti dan saksi, tergugat jelas bersalah dan harus membayar",
        "Semua evidence menunjukkan bahwa tergugat melakukan wanprestasi",
        "Tergugat tidak memiliki alasan yang sah untuk tidak membayar utang"
    ]
    
    alegasi_pembela = [
        "Klien kami telah berusaha maksimal dalam kondisi yang sulit",
        "Penggugat tidak memberikan kelonggaran yang wajar",
        "Mohon pengadilan mempertimbangkan kondisi finansial klien"
    ]
    
    final_jaksa = random.choice(alegasi_jaksa)
    final_pembela = random.choice(alegasi_pembela)
    
    # Bonus skor untuk alegasi
    final_jaksa_score = random.randint(15, 25)
    final_pembela_score = random.randint(12, 20)
    
    session["skor_jaksa"] += final_jaksa_score
    session["skor_pembela"] += final_pembela_score
    
    embed = discord.Embed(title="🗣️ ALEGASI FINAL", color=0xe74c3c)
    embed.add_field(name="⚔️ Alegasi Jaksa", value=final_jaksa, inline=False)
    embed.add_field(name="🛡️ Alegasi Pembela", value=final_pembela, inline=False)
    embed.add_field(name="📊 Skor Akhir", value=f"Jaksa: {session['skor_jaksa']}\nPembela: {session['skor_pembela']}", inline=True)
    embed.add_field(name="⚖️ Status", value="Siap untuk putusan hakim", inline=True)
    
    session["transcript"].append(f"ALEGASI JAKSA: {final_jaksa}")
    session["transcript"].append(f"ALEGASI PEMBELA: {final_pembela}")
    await ctx.send(embed=embed)

async def deliver_final_verdict(ctx, case_id, target_case, session, judge_id):
    """Bacakan vonis final berdasarkan skor dan evidence"""
    
    if session["tahap"] != "putusan":
        await ctx.send("❌ Sidang belum sampai tahap putusan. Selesaikan tahapan sebelumnya dulu.")
        return
    
    jaksa_score = session["skor_jaksa"]
    pembela_score = session["skor_pembela"]
    
    # Tentukan pemenang berdasarkan skor
    if jaksa_score > pembela_score:
        verdict = "guilty"
        kekuatan_putusan = "Meyakinkan"
        winning_margin = jaksa_score - pembela_score
    else:
        verdict = "not_guilty"
        kekuatan_putusan = "Meragukan"
        winning_margin = pembela_score - jaksa_score
    
    # Hitung punishment/reward berdasarkan skor
    debt_amount = target_case["debt_amount"]
    
    if verdict == "guilty":
        if winning_margin > 50:
            fine_percentage = 0.75  # Denda 75%
            court_decision = "BERSALAH dengan bukti yang sangat kuat"
        elif winning_margin > 25:
            fine_percentage = 0.50  # Denda 50%
            court_decision = "BERSALAH dengan bukti yang cukup"
        else:
            fine_percentage = 0.25  # Denda 25%
            court_decision = "BERSALAH dengan bukti minimal"
    else:
        fine_percentage = 0
        court_decision = "TIDAK TERBUKTI BERSALAH"
    
    fine_amount = int(debt_amount * fine_percentage)
    court_costs = data["court_settings"]["filing_fee"]
    
    # Proses eksekusi putusan
    plaintiff_id = target_case["plaintiff_id"]
    defendant_id = target_case["defendant_id"]
    prosecutor_id = target_case["prosecutor_id"]
    lawyer_id = target_case["defense_lawyer_id"]
    
    # Bayar fee tim hukum
    judge_fee = data["court_settings"]["judge_fee"]
    prosecutor_fee = data["court_settings"]["prosecutor_fee"]
    lawyer_fee = data["court_settings"]["lawyer_fee"]
    
    data[judge_id]["uang"] += judge_fee
    if prosecutor_id in data:
        data[prosecutor_id]["uang"] += prosecutor_fee
    if lawyer_id in data:
        data[lawyer_id]["uang"] += lawyer_fee
    
    if verdict == "guilty":
        total_payment = debt_amount + fine_amount + court_costs
        
        if defendant_id in data:
            defendant_money = data[defendant_id]["uang"]
            
            if defendant_money >= total_payment:
                # Mampu bayar penuh
                data[defendant_id]["uang"] -= total_payment
                data[plaintiff_id]["uang"] += debt_amount
                execution_result = "Tergugat membayar penuh"
            else:
                # Penyitaan aset
                confiscated = defendant_money
                data[defendant_id]["uang"] = 0
                data[plaintiff_id]["uang"] += min(confiscated, debt_amount)
                execution_result = f"Aset tergugat disita Rp{confiscated:,}"
            
            # Hapus utang dari sistem
            if "utang_ke_pemain" in data[defendant_id] and plaintiff_id in data[defendant_id]["utang_ke_pemain"]:
                del data[defendant_id]["utang_ke_pemain"][plaintiff_id]
    else:
        total_payment = 0
        execution_result = "Tergugat dibebaskan dari tuntutan"
        # Plaintiff bayar court costs
        if plaintiff_id in data and data[plaintiff_id]["uang"] >= court_costs:
            data[plaintiff_id]["uang"] -= court_costs
    
    # Finalize case
    target_case["verdict"] = verdict
    target_case["status"] = "closed"
    target_case["verdict_date"] = int(time.time())
    target_case["final_score"] = f"Jaksa: {jaksa_score}, Pembela: {pembela_score}"
    target_case["court_transcript"] = session["transcript"]
    
    # Create detailed verdict embed
    embed = discord.Embed(
        title="⚖️ PUTUSAN PENGADILAN", 
        color=0xff0000 if verdict == "guilty" else 0x00ff00
    )
    embed.add_field(name="🏛️ Hakim Ketua", value=ctx.author.display_name, inline=True)
    embed.add_field(name="📋 Case ID", value=case_id, inline=True)
    embed.add_field(name="⏰ Durasi Sidang", value=f"{int((int(time.time()) - session['session_start']) / 60)} menit", inline=True)
    
    embed.add_field(name="📊 Skor Akhir", value=f"Jaksa: {jaksa_score}\nPembela: {pembela_score}", inline=True)
    embed.add_field(name="📜 Putusan", value=court_decision, inline=True)
    embed.add_field(name="💪 Kekuatan", value=kekuatan_putusan, inline=True)
    
    if verdict == "guilty":
        embed.add_field(name="💰 Utang Pokok", value=f"Rp{debt_amount:,}", inline=True)
        embed.add_field(name="💸 Denda", value=f"Rp{fine_amount:,} ({int(fine_percentage*100)}%)", inline=True)
        embed.add_field(name="🏛️ Biaya Pengadilan", value=f"Rp{court_costs:,}", inline=True)
        embed.add_field(name="💵 Total Pembayaran", value=f"Rp{total_payment:,}", inline=True)
    
    embed.add_field(name="⚖️ Eksekusi", value=execution_result, inline=False)
    embed.add_field(name="💰 Honor Tim Hukum", value=f"Hakim: Rp{judge_fee:,}\nJaksa: Rp{prosecutor_fee:,}\nPengacara: Rp{lawyer_fee:,}", inline=False)
    
    save_data(data)
    await ctx.send(embed=embed)
    
    # Notifikasi lengkap ke semua pihak
    verdict_details = f"⚖️ **PUTUSAN PENGADILAN FINAL**\n\n🏛️ **Hakim:** {ctx.author.display_name}\n📋 **Case ID:** {case_id}\n\n📊 **Skor Sidang:**\n- Jaksa: {jaksa_score}\n- Pembela: {pembela_score}\n\n📜 **Putusan:** {court_decision}\n⚖️ **Eksekusi:** {execution_result}\n\n🎭 **Tahapan yang Dilalui:**\n✅ Pembukaan Sidang\n✅ Dakwaan Jaksa\n✅ Pembelaan\n✅ Pembuktian\n✅ Pemeriksaan Saksi\n✅ Alegasi Final\n✅ Putusan\n\n💰 **Detail Finansial:**"
    
    if verdict == "guilty":
        verdict_details += f"\n- Utang pokok: Rp{debt_amount:,}\n- Denda: Rp{fine_amount:,}\n- Biaya pengadilan: Rp{court_costs:,}\n- Total: Rp{total_payment:,}"
    
    await kirim_notif_dm(plaintiff_id, verdict_details)
    await kirim_notif_dm(defendant_id, verdict_details)
    
    # Clean up session
    if case_id in data["court_sessions"]:
        del data["court_sessions"][case_id]

# !statushukum - Cek status kasus hukum user
@bot.command()
async def statushukum(ctx, target: discord.Member = None):
    if target is None:
        target = ctx.author
    
    target_id = str(target.id)
    
    if "court_cases" not in data or not data["court_cases"]:
        await ctx.send(f"⚖️ {target.display_name} tidak memiliki kasus hukum aktif.")
        return
    
    # Cari kasus yang melibatkan user
    user_cases = []
    
    for case_id, case_data in data["court_cases"].items():
        if (case_data["plaintiff_id"] == target_id or 
            case_data["defendant_id"] == target_id or
            case_data["judge_id"] == target_id or
            case_data["prosecutor_id"] == target_id or
            case_data["defense_lawyer_id"] == target_id):
            user_cases.append((case_id, case_data))
    
    if not user_cases:
        await ctx.send(f"⚖️ {target.display_name} tidak memiliki kasus hukum aktif.")
        return
    
    embed = discord.Embed(title=f"⚖️ Status Hukum {target.display_name}", color=0x9b59b6)
    embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
    
    for case_id, case_data in user_cases[:5]:  # Max 5 kasus
        # Tentukan peran user dalam kasus
        role = "Unknown"
        if case_data["plaintiff_id"] == target_id:
            role = "Penuduh"
        elif case_data["defendant_id"] == target_id:
            role = "Tergugat"
        elif case_data["judge_id"] == target_id:
            role = "Hakim"
        elif case_data["prosecutor_id"] == target_id:
            role = "Jaksa"
        elif case_data["defense_lawyer_id"] == target_id:
            role = "Pengacara"
        
        status_map = {
            "waiting_for_legal_team": "Menunggu tim hukum",
            "ready_for_trial": "Siap sidang",
            "closed": "Selesai"
        }
        
        # Tambahkan info skor jika sidang sedang berlangsung
        score_info = ""
        if case_id in data.get("court_sessions", {}):
            session = data["court_sessions"][case_id]
            score_info = f"\n📊 Skor: J{session['skor_jaksa']}-P{session['skor_pembela']}"
        
        embed.add_field(
            name=f"🏛️ {case_id[-8:]}",
            value=f"👔 {role}\n💰 Rp{case_data['debt_amount']:,}\n📋 {status_map.get(case_data['status'], case_data['status'])}\n📅 {int((int(time.time()) - case_data['filed_date']) / 86400)} hari lalu{score_info}",
            inline=True
        )
    
    embed.set_footer(text="!transkrip [case_id] untuk lihat detail sidang")
    await ctx.send(embed=embed)

# !transkrip - Lihat transkrip sidang
@bot.command()
async def transkrip(ctx, case_id=None):
    if not case_id:
        await ctx.send("📋 **Cara Lihat Transkrip:**\n`!transkrip [case_id]` - Lihat detail sidang\n\n📄 Tersedia untuk kasus yang sudah selesai")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    # Cari kasus berdasarkan ID
    target_case = None
    full_case_id = None
    
    for full_id, case_data in data.get("court_cases", {}).items():
        if full_id.endswith(case_id) or full_id[-8:] == case_id:
            # Cek apakah user terlibat dalam kasus ini
            if (case_data["plaintiff_id"] == user_id or 
                case_data["defendant_id"] == user_id or
                case_data["judge_id"] == user_id or
                case_data["prosecutor_id"] == user_id or
                case_data["defense_lawyer_id"] == user_id):
                target_case = case_data
                full_case_id = full_id
                break
    
    if not target_case:
        await ctx.send(f"❌ Kasus dengan ID `{case_id}` tidak ditemukan atau kamu tidak terlibat dalam kasus ini.")
        return
    
    if target_case["status"] != "closed":
        await ctx.send("❌ Transkrip hanya tersedia untuk kasus yang sudah selesai.")
        return
    
    transcript = target_case.get("court_transcript", [])
    if not transcript:
        await ctx.send("❌ Transkrip tidak tersedia untuk kasus ini.")
        return
    
    embed = discord.Embed(title=f"📄 Transkrip Sidang {case_id}", color=0x9b59b6)
    
    # Info kasus
    embed.add_field(name="💰 Nilai Sengketa", value=f"Rp{target_case['debt_amount']:,}", inline=True)
    embed.add_field(name="📜 Putusan", value=target_case.get("verdict", "Unknown"), inline=True)
    embed.add_field(name="📊 Skor Final", value=target_case.get("final_score", "N/A"), inline=True)
    
    # Transkrip detail
    if len(transcript) <= 10:
        transcript_text = "\n".join(transcript)
    else:
        transcript_text = "\n".join(transcript[:10]) + f"\n... dan {len(transcript)-10} baris lainnya"
    
    embed.add_field(name="📋 Jalannya Sidang", value=transcript_text[:1024], inline=False)
    
    # Tanggal putusan
    if target_case.get("verdict_date"):
        verdict_date = datetime.fromtimestamp(target_case["verdict_date"])
        embed.add_field(name="📅 Tanggal Putusan", value=verdict_date.strftime("%d/%m/%Y %H:%M"), inline=True)
    
    await ctx.send(embed=embed)

# !kasusselesai - Lihat riwayat kasus yang sudah selesai
@bot.command()
async def kasusselesai(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    
    if "court_cases" not in data or not data["court_cases"]:
        await ctx.send("⚖️ Belum ada kasus hukum yang selesai.")
        return
    
    # Cari kasus selesai yang melibatkan user
    closed_cases = []
    
    for case_id, case_data in data["court_cases"].items():
        if case_data["status"] == "closed" and (
            case_data["plaintiff_id"] == user_id or 
            case_data["defendant_id"] == user_id or
            case_data["judge_id"] == user_id or
            case_data["prosecutor_id"] == user_id or
            case_data["defense_lawyer_id"] == user_id):
            closed_cases.append((case_id, case_data))
    
    if not closed_cases:
        await ctx.send(f"⚖️ {member.display_name} belum memiliki riwayat kasus yang selesai.")
        return
    
    # Sort berdasarkan tanggal putusan terbaru
    closed_cases.sort(key=lambda x: x[1].get("verdict_date", 0), reverse=True)
    
    embed = discord.Embed(title=f"📚 Riwayat Kasus Selesai {member.display_name}", color=0x2ecc71)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    total_win = 0
    total_lose = 0
    
    for case_id, case_data in closed_cases[:10]:  # Max 10 kasus
        # Tentukan hasil untuk user
        user_role = "Unknown"
        case_result = "N/A"
        
        if case_data["plaintiff_id"] == user_id:
            user_role = "Penuduh"
            case_result = "Menang" if case_data["verdict"] == "guilty" else "Kalah"
        elif case_data["defendant_id"] == user_id:
            user_role = "Tergugat"
            case_result = "Kalah" if case_data["verdict"] == "guilty" else "Menang"
        elif case_data["judge_id"] == user_id:
            user_role = "Hakim"
            case_result = "Memimpin"
        elif case_data["prosecutor_id"] == user_id:
            user_role = "Jaksa"
            case_result = "Menang" if case_data["verdict"] == "guilty" else "Kalah"
        elif case_data["defense_lawyer_id"] == user_id:
            user_role = "Pengacara"
            case_result = "Kalah" if case_data["verdict"] == "guilty" else "Menang"
        
        # Hitung statistik
        if case_result == "Menang":
            total_win += 1
        elif case_result == "Kalah":
            total_lose += 1
        
        verdict_date = datetime.fromtimestamp(case_data.get("verdict_date", 0))
        
        embed.add_field(
            name=f"⚖️ {case_id[-8:]}",
            value=f"👔 {user_role}\n💰 Rp{case_data['debt_amount']:,}\n📜 {case_result}\n📅 {verdict_date.strftime('%d/%m/%Y')}",
            inline=True
        )
    
    # Statistik keseluruhan
    if total_win + total_lose > 0:
        win_rate = (total_win / (total_win + total_lose)) * 100
        embed.add_field(name="📊 Statistik", value=f"Menang: {total_win}\nKalah: {total_lose}\nWin Rate: {win_rate:.1f}%", inline=False)
    
    embed.set_footer(text="!transkrip [case_id] untuk detail kasus")
    await ctx.send(embed=embed)

# !bayarpemain - Bayar utang ke pemain lain
@bot.command()
async def bayarpemain(ctx, target: discord.Member, jumlah: int):
    if jumlah <= 0:
        await ctx.send("❌ Jumlah pembayaran harus lebih dari 0.")
        return

    peminjam_id = str(ctx.author.id)
    pemberi_id = str(target.id)

    if peminjam_id == pemberi_id:
        await ctx.send("❌ Kamu tidak punya utang ke diri sendiri.")
        return

    create_user_profile(peminjam_id)
    create_user_profile(pemberi_id)

    if "utang_ke_pemain" not in data[peminjam_id] or not data[peminjam_id]["utang_ke_pemain"]:
        await ctx.send("❌ Kamu tidak punya utang ke pemain manapun.")
        return

    utang_pemain = data[peminjam_id]["utang_ke_pemain"]

    if pemberi_id not in utang_pemain or utang_pemain[pemberi_id]["jumlah_pokok"] <= 0:
        await ctx.send(f"❌ Kamu tidak punya utang ke {target.display_name}.")
        return

    uang = data[peminjam_id]["uang"]
    if uang < jumlah:
        await ctx.send("❌ Saldo uangmu tidak cukup untuk membayar utang sebanyak itu.")
        return

    jumlah_utang = utang_pemain[pemberi_id]["jumlah_pokok"]
    if jumlah > jumlah_utang:
        jumlah = jumlah_utang  # bayar maksimal lunas

    sisa = jumlah_utang - jumlah

    lunas = False
    if sisa <= 0:
        lunas = True
        del utang_pemain[pemberi_id]
        
        # Tambah ke riwayat pinjaman peminjam
        data[peminjam_id]["riwayat_pinjaman"].append({
            "pemberi": pemberi_id,
            "jumlah": jumlah_utang,
            "waktu_selesai": int(time.time()),
            "status": "lunas"
        })
        
        # Update statistik transaksi selesai untuk peminjam
        data[peminjam_id]["rating_kredibilitas"]["transaksi_selesai"] += 1
        
    else:
        utang_pemain[pemberi_id]["jumlah_pokok"] = sisa

    data[peminjam_id]["uang"] -= jumlah
    data[pemberi_id]["uang"] += jumlah
    save_data(data)

    embed = discord.Embed(title="💳 Pembayaran Utang", color=0x00ff00)
    embed.add_field(name="Dibayar ke", value=target.display_name, inline=True)
    embed.add_field(name="Jumlah Bayar", value=f"Rp{jumlah:,}", inline=True)
    embed.add_field(name="Sisa Utang", value=f"Rp{sisa:,}", inline=True)
    
    if lunas:
        embed.add_field(name="🎉 Status", value="Utang Lunas!", inline=False)
        embed.add_field(name="⭐ Rating", value=f"Kini {target.display_name} dapat memberikan rating kredibilitas untuk {ctx.author.display_name}\nGunakan: `!rating @{ctx.author.display_name} [1-5] [komentar]`", inline=False)
    
    await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    # Kirim konfirmasi pembayaran ke kedua pihak
    if lunas:
        pesan_peminjam = f"✅ **Utang Lunas!**\n\nKamu berhasil melunasi utang ke **{target.display_name}** sebesar **Rp{jumlah_utang:,}**.\n\nTerima kasih sudah membayar tepat waktu! 🎉"
        pesan_pemberi = f"💰 **Pembayaran Diterima**\n\n**{ctx.author.display_name}** telah melunasi utang sebesar **Rp{jumlah_utang:,}**.\n\nTransaksi selesai! 🎉\n\n⭐ Kamu bisa memberikan rating kredibilitas:\n`!rating @{ctx.author.display_name} [1-5] [komentar]`"
    else:
        pesan_peminjam = f"💳 **Pembayaran Berhasil**\n\nKamu berhasil membayar **Rp{jumlah:,}** ke **{target.display_name}**.\n\nSisa utang: **Rp{sisa:,}**"
        pesan_pemberi = f"💰 **Pembayaran Diterima**\n\n**{ctx.author.display_name}** telah membayar **Rp{jumlah:,}**.\n\nSisa yang harus dibayar: **Rp{sisa:,}**"
    
    await kirim_notif_dm(peminjam_id, pesan_peminjam)
    await kirim_notif_dm(pemberi_id, pesan_pemberi)

# !cekutang - Cek semua utang user
@bot.command()
async def cekutang(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(user_id)
    
    # Cek utang ke pemain lain
    utang_pemain = data[user_id].get("utang_ke_pemain", {})
    
    if not utang_pemain:
        await ctx.send(f"✅ {member.display_name} tidak memiliki utang ke pemain manapun.")
        return
    
    embed = discord.Embed(title=f"💳 Daftar Utang {member.display_name}", color=0xff9900)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    total_utang = 0
    
    for pemberi_id, utang_data in utang_pemain.items():
        try:
            pemberi = bot.get_user(int(pemberi_id))
            nama_pemberi = pemberi.display_name if pemberi else f"User {pemberi_id[:4]}..."
            
            jumlah = utang_data["jumlah_pokok"]
            total_utang += jumlah
            
            # Cek status jatuh tempo
            jatuh_tempo_info = cek_jatuh_tempo(utang_data)
            
            embed.add_field(
                name=f"💰 Utang ke {nama_pemberi}",
                value=f"💵 Jumlah: Rp{jumlah:,}\n⏰ {jatuh_tempo_info}",
                inline=True
            )
        except:
            continue
    
    embed.add_field(name="📊 Total Utang", value=f"Rp{total_utang:,}", inline=False)
    embed.set_footer(text="!bayarpemain [user] [jumlah] untuk membayar")
    await ctx.send(embed=embed)

# !hutangke - Lihat daftar orang yang berhutang ke kamu
@bot.command()
async def hutangke(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    # Cari siapa yang berhutang ke user ini
    penghutang_list = []
    
    for debtor_id, user_data in data.items():
        if debtor_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings"]:
            continue
        
        if "utang_ke_pemain" in user_data and user_id in user_data["utang_ke_pemain"]:
            utang_data = user_data["utang_ke_pemain"][user_id]
            try:
                debtor = bot.get_user(int(debtor_id))
                nama_penghutang = debtor.display_name if debtor else f"User {debtor_id[:4]}..."
                penghutang_list.append({
                    "id": debtor_id,
                    "nama": nama_penghutang,
                    "jumlah": utang_data["jumlah_pokok"],
                    "jatuh_tempo": utang_data.get("jatuh_tempo", 0)
                })
            except:
                continue
    
    if not penghutang_list:
        await ctx.send("✅ Tidak ada yang berhutang ke kamu.")
        return
    
    embed = discord.Embed(title="💰 Daftar Penghutang", color=0x00ff00)
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    
    total_piutang = 0
    
    for penghutang in penghutang_list:
        total_piutang += penghutang["jumlah"]
        
        # Status jatuh tempo
        if penghutang["jatuh_tempo"] > 0:
            current_time = int(time.time())
            if current_time > penghutang["jatuh_tempo"]:
                status = "🚨 Jatuh Tempo"
            else:
                sisa_hari = (penghutang["jatuh_tempo"] - current_time) // 86400
                status = f"⏰ {sisa_hari} hari lagi"
        else:
            status = "📅 Tidak ada batas"
        
        embed.add_field(
            name=f"👤 {penghutang['nama']}",
            value=f"💵 Utang: Rp{penghutang['jumlah']:,}\n{status}",
            inline=True
        )
    
    embed.add_field(name="📊 Total Piutang", value=f"Rp{total_piutang:,}", inline=False)
    embed.set_footer(text="Jika sudah jatuh tempo, bisa dilaporkan ke pengadilan dengan !laporutang")
    await ctx.send(embed=embed)

# !seturhutang - Set/ubah jumlah utang manual (Admin only)
@bot.command()
async def seturhutang(ctx, penghutang: discord.Member, pemberi: discord.Member, jumlah: int):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Command ini hanya untuk admin.")
        return
    
    if jumlah < 0:
        await ctx.send("❌ Jumlah tidak boleh negatif.")
        return
    
    penghutang_id = str(penghutang.id)
    pemberi_id = str(pemberi.id)
    
    create_user_profile(penghutang_id)
    create_user_profile(pemberi_id)
    
    if jumlah == 0:
        # Hapus utang
        if "utang_ke_pemain" in data[penghutang_id] and pemberi_id in data[penghutang_id]["utang_ke_pemain"]:
            del data[penghutang_id]["utang_ke_pemain"][pemberi_id]
            await ctx.send(f"✅ Utang {penghutang.display_name} ke {pemberi.display_name} telah dihapus.")
        else:
            await ctx.send("❌ Tidak ada utang yang ditemukan.")
    else:
        # Set/update utang
        if "utang_ke_pemain" not in data[penghutang_id]:
            data[penghutang_id]["utang_ke_pemain"] = {}
        
        data[penghutang_id]["utang_ke_pemain"][pemberi_id] = {
            "jumlah_pokok": jumlah,
            "waktu_pinjam": int(time.time()),
            "jatuh_tempo": int(time.time()) + (PINJAMAN_BATAS_HARI * 86400)
        }
        
        await ctx.send(f"✅ Utang {penghutang.display_name} ke {pemberi.display_name} telah diset ke Rp{jumlah:,}")
    
    save_data(data)

# !lupautang - Hapus utang (untuk pemberi pinjaman)
@bot.command()
async def lupautang(ctx, penghutang: discord.Member):
    user_id = str(ctx.author.id)
    penghutang_id = str(penghutang.id)
    
    if user_id == penghutang_id:
        await ctx.send("❌ Kamu tidak bisa melupa utang diri sendiri.")
        return
    
    create_user_profile(penghutang_id)
    
    if "utang_ke_pemain" not in data[penghutang_id] or user_id not in data[penghutang_id]["utang_ke_pemain"]:
        await ctx.send(f"❌ {penghutang.display_name} tidak berhutang ke kamu.")
        return
    
    jumlah_utang = data[penghutang_id]["utang_ke_pemain"][user_id]["jumlah_pokok"]
    
    # Hapus utang
    del data[penghutang_id]["utang_ke_pemain"][user_id]
    save_data(data)
    
    embed = discord.Embed(title="💝 Utang Dimaafkan", color=0x00ff00)
    embed.add_field(name="👤 Penghutang", value=penghutang.display_name, inline=True)
    embed.add_field(name="💰 Jumlah", value=f"Rp{jumlah_utang:,}", inline=True)
    embed.add_field(name="❤️ Pesan", value="Utang telah dimaafkan dengan hati yang lapang", inline=False)
    
    await ctx.send(embed=embed)
    
    # Kirim notifikasi ke penghutang
    pesan_notif = f"💝 **Utang Dimaafkan!**\n\n**{ctx.author.display_name}** telah memaafkan utang kamu sebesar **Rp{jumlah_utang:,}**.\n\nTerima kasih atas kebaikan hatinya! ❤️"
    await kirim_notif_dm(penghutang_id, pesan_notif)

# !ceknotif - Trigger manual notification check (Admin only)
@bot.command()
async def ceknotif(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Command ini hanya untuk admin.")
        return
    
    await ctx.send("🔄 Memulai pengecekan notifikasi utang...")
    await cek_dan_kirim_notifikasi()
    await ctx.send("✅ Pengecekan notifikasi utang selesai!")

# !cekkondisi - Trigger manual health condition check (Admin only)
@bot.command()
async def cekkondisi(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Command ini hanya untuk admin.")
        return
    
    await ctx.send("🔄 Memulai pengecekan kondisi kesehatan semua user...")
    await cek_dan_kirim_notifikasi_kondisi()
    await ctx.send("✅ Pengecekan kondisi kesehatan selesai!")

# !utangpemain - Cek daftar utang ke pemain lain
@bot.command()
async def utangpemain(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if "utang_ke_pemain" not in data[user_id] or not data[user_id]["utang_ke_pemain"]:
        await ctx.send("✅ Kamu tidak punya utang ke pemain manapun.")
        return

    utang_pemain = data[user_id]["utang_ke_pemain"]
    
    embed = discord.Embed(title="💳 Daftar Utang ke Pemain", color=0xff9900)
    
    total_utang = 0
    for pemberi_id, utang_data in utang_pemain.items():
        try:
            member = ctx.guild.get_member(int(pemberi_id))
            nama = member.display_name if member else f"UserID {pemberi_id}"
            jatuh_tempo_info = cek_jatuh_tempo(utang_data)
            jumlah = utang_data['jumlah_pokok']
            total_utang += jumlah
            
            embed.add_field(
                name=f"💰 {nama}",
                value=f"Rp{jumlah:,}\n⏰ {jatuh_tempo_info}",
                inline=True
            )
        except:
            continue
    
    embed.add_field(name="📊 Total Utang", value=f"Rp{total_utang:,}", inline=False)
    embed.set_footer(text="Gunakan !bayarpemain [user] [jumlah] untuk membayar")
    await ctx.send(embed=embed)

# !rating - Berikan rating kredibilitas ke peminjam
@bot.command()
async def rating(ctx, target: discord.Member, nilai: int, *, komentar=""):
    if nilai < 1 or nilai > 5:
        await ctx.send("❌ Rating harus antara 1-5.")
        return
    
    pemberi_id = str(ctx.author.id)
    penerima_id = str(target.id)
    
    if pemberi_id == penerima_id:
        await ctx.send("❌ Kamu tidak bisa memberi rating ke diri sendiri.")
        return
    
    create_user_profile(pemberi_id)
    create_user_profile(penerima_id)
    
    # Cek apakah ada riwayat pinjaman yang sudah selesai
    riwayat_valid = False
    for riwayat in data[penerima_id]["riwayat_pinjaman"]:
        if riwayat["pemberi"] == pemberi_id and riwayat["status"] == "lunas":
            riwayat_valid = True
            break
    
    if not riwayat_valid:
        await ctx.send(f"❌ Kamu tidak bisa memberi rating ke {target.display_name}. Hanya pemberi pinjaman yang pernah dilunasi yang bisa memberikan rating.")
        return
    
    # Cek apakah sudah pernah memberi rating
    for rating_item in data[penerima_id]["rating_kredibilitas"]["rating_detail"]:
        if rating_item["pemberi"] == pemberi_id:
            await ctx.send(f"❌ Kamu sudah pernah memberi rating ke {target.display_name}.")
            return
    
    # Tambah rating
    rating_baru = {
        "pemberi": pemberi_id,
        "nilai": nilai,
        "komentar": komentar,
        "waktu": int(time.time())
    }
    
    data[penerima_id]["rating_kredibilitas"]["rating_detail"].append(rating_baru)
    data[penerima_id]["rating_kredibilitas"]["total_rating"] += nilai
    data[penerima_id]["rating_kredibilitas"]["jumlah_rating"] += 1
    save_data(data)
    
    avg_rating = hitung_rating_rata_rata(data[penerima_id])
    trust_level = get_trust_level(avg_rating, data[penerima_id]["rating_kredibilitas"]["transaksi_selesai"])
    
    embed = discord.Embed(title="⭐ Rating Kredibilitas", color=0xffd700)
    embed.add_field(name="Pemberi Rating", value=ctx.author.display_name, inline=True)
    embed.add_field(name="Penerima Rating", value=target.display_name, inline=True)
    embed.add_field(name="Rating", value=f"{nilai}/5 ⭐", inline=True)
    embed.add_field(name="Rating Rata-rata Baru", value=f"{avg_rating:.1f}/5.0", inline=True)
    embed.add_field(name="Level Kepercayaan", value=trust_level, inline=True)
    if komentar:
        embed.add_field(name="Komentar", value=komentar, inline=False)
    
    await ctx.send(embed=embed)
    
    # Kirim notifikasi ke penerima rating
    pesan_notif = f"⭐ **Rating Kredibilitas**\n\n**{ctx.author.display_name}** memberikan rating **{nilai}/5** untuk kredibilitas kamu!\n\nRating rata-rata: **{avg_rating:.1f}/5.0**\nLevel kepercayaan: **{trust_level}**"
    if komentar:
        pesan_notif += f"\n\nKomentar: *\"{komentar}\"*"
    
    await kirim_notif_dm(penerima_id, pesan_notif)

# !lihatrating - Lihat detail rating kredibilitas seseorang
@bot.command()
async def lihatrating(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    create_user_profile(user_id)
    
    rating_data = data[user_id]["rating_kredibilitas"]
    avg_rating = hitung_rating_rata_rata(data[user_id])
    trust_level = get_trust_level(avg_rating, rating_data["transaksi_selesai"])
    
    embed = discord.Embed(title=f"⭐ Rating Kredibilitas {member.display_name}", color=0xffd700)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    if rating_data["jumlah_rating"] == 0:
        embed.add_field(name="Status", value="🆕 Belum ada rating", inline=False)
        embed.add_field(name="Transaksi Selesai", value=f"{rating_data['transaksi_selesai']} transaksi", inline=True)
    else:
        embed.add_field(name="Rating Rata-rata", value=f"{avg_rating:.1f}/5.0 ⭐", inline=True)
        embed.add_field(name="Total Rating", value=f"{rating_data['jumlah_rating']} rating", inline=True)
        embed.add_field(name="Transaksi Selesai", value=f"{rating_data['transaksi_selesai']} transaksi", inline=True)
        embed.add_field(name="Level Kepercayaan", value=trust_level, inline=False)
        
        # Tampilkan 5 rating terbaru
        if rating_data["rating_detail"]:
            rating_text = ""
            recent_ratings = sorted(rating_data["rating_detail"], key=lambda x: x["waktu"], reverse=True)[:5]
            
            for rating_item in recent_ratings:
                try:
                    pemberi = ctx.guild.get_member(int(rating_item["pemberi"]))
                    nama_pemberi = pemberi.display_name if pemberi else f"User {rating_item['pemberi'][:4]}..."
                    rating_text += f"• **{rating_item['nilai']}/5** dari {nama_pemberi}\n"
                    if rating_item.get("komentar"):
                        rating_text += f"  *\"{rating_item['komentar'][:50]}{'...' if len(rating_item['komentar']) > 50 else ''}\"*\n"
                except:
                    continue
            
            if rating_text:
                embed.add_field(name="Rating Terbaru", value=rating_text[:1024], inline=False)
    
    await ctx.send(embed=embed)

# !kredibilitasrank - Ranking pemain berdasarkan kredibilitas
@bot.command()
async def kredibilitasrank(ctx):
    if not data:
        await ctx.send("Belum ada data user.")
        return
    
    # Filter user yang punya rating dan sort berdasarkan rata-rata rating + jumlah transaksi
    rated_users = []
    for user_id, user_data in data.items():
        rating_data = user_data["rating_kredibilitas"]
        if rating_data["jumlah_rating"] > 0:
            avg_rating = hitung_rating_rata_rata(user_data)
            # Score gabungan: rating rata-rata + bonus dari jumlah transaksi
            score = avg_rating + (rating_data["transaksi_selesai"] * 0.1)
            rated_users.append((user_id, user_data, avg_rating, score))
    
    if not rated_users:
        await ctx.send("Belum ada user dengan rating kredibilitas.")
        return
    
    # Sort berdasarkan score
    sorted_users = sorted(rated_users, key=lambda x: x[3], reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 Ranking Kredibilitas", color=0xffd700)
    
    for i, (user_id, user_data, avg_rating, score) in enumerate(sorted_users, 1):
        try:
            user = bot.get_user(int(user_id))
            username = user.display_name if user else f"User {user_id[:4]}..."
            trust_level = get_trust_level(avg_rating, user_data["rating_kredibilitas"]["transaksi_selesai"])
            
            embed.add_field(
                name=f"{i}. {username}",
                value=f"{avg_rating:.1f}/5.0 ⭐\n{trust_level}\n{user_data['rating_kredibilitas']['transaksi_selesai']} transaksi",
                inline=True
            )
        except:
            continue
    
    embed.set_footer(text="Rating berdasarkan pinjaman yang telah dilunasi")
    await ctx.send(embed=embed)

# !kondisi - Cek kondisi kesehatan singkat
@bot.command()
async def kondisi(ctx):
    user_id = str(ctx.author.id)
    if user_id not in data:
        await ctx.send("Kamu belum daftar. Ketik `!daftar` dulu.")
        return
    
    create_user_profile(user_id)
    data[user_id] = apply_life_effects(data[user_id])
    save_data(data)
    
    user_data = data[user_id]
    sick_conditions = check_sickness(user_data)
    
    embed = discord.Embed(title=f"🏥 Kondisi {ctx.author.display_name}", color=0x00ff00 if not sick_conditions else 0xff0000)
    embed.add_field(name="🍽️ Lapar", value=get_status_bar(user_data['lapar']), inline=False)
    embed.add_field(name="💧 Haus", value=get_status_bar(user_data['haus']), inline=False)
    embed.add_field(name="❤️ Kesehatan", value=get_status_bar(user_data['kesehatan']), inline=False)
    embed.add_field(name="🏠 Tempat Tinggal", value=get_housing_name(user_data), inline=True)
    
    if sick_conditions:
        embed.add_field(name="🤒 Status", value=" | ".join(sick_conditions), inline=False)
        embed.add_field(name="💡 Saran", value="Beli makanan (!toko), minum, dan obat-obatan untuk pulih!", inline=False)
    
    await ctx.send(embed=embed)

# !istirahat - Pulihkan kesehatan dengan biaya
@bot.command()
async def istirahat(ctx, durasi: int = None):
    user_id = str(ctx.author.id)
    if user_id not in data:
        await ctx.send("Kamu belum daftar. Ketik `!daftar` dulu.")
        return
    
    create_user_profile(user_id)
    data[user_id] = apply_life_effects(data[user_id])
    
    if durasi is None:
        await ctx.send("💤 **Istirahat**\n\n`!istirahat` - Istirahat cepat (tanpa durasi)\n`!istirahat [durasi_jam]` - Istirahat panjang (1-4 jam)\n\n💡 Istirahat memulihkan kesehatan!")
        return
    
    if durasi and (durasi < 1 or durasi > 4):
        await ctx.send("❌ Durasi istirahat harus 1-4 jam.")
        return
    
    # Biaya istirahat tergantung tempat tinggal
    housing_items = {"tenda": 5000, "kontrakan": 10000, "rumah": 15000, "villa": 20000}
    rest_cost = 0  # Gelandangan gratis tapi efek minimal
    base_healing = 10  # Base healing
    
    for item, cost in housing_items.items():
        if item in data[user_id]["inventory"]:
            rest_cost = cost if durasi else cost // 2
            base_healing = cost // 1000 + 10  # Lebih mahal = lebih efektif
            break
    
    if durasi:
        rest_cost *= durasi
        total_healing = base_healing * durasi
    else:
        total_healing = base_healing
    
    if data[user_id]["uang"] < rest_cost and rest_cost > 0:
        await ctx.send(f"❌ Kamu butuh Rp{rest_cost:,} untuk istirahat dengan nyaman.")
        return
    
    # Cooldown check hanya untuk istirahat cepat
    current_time = int(time.time())
    if not durasi:
        last_rest = data[user_id].get("last_rest", 0)
        if current_time - last_rest < 7200:  # 2 jam
            remaining = 7200 - (current_time - last_rest)
            await ctx.send(f"⏰ Tunggu {remaining//60} menit lagi untuk istirahat cepat. Atau gunakan `!istirahat [durasi]` untuk istirahat panjang.")
            return
    
    # Process rest
    data[user_id]["uang"] -= rest_cost
    old_health = data[user_id]["kesehatan"]
    old_hunger = data[user_id]["lapar"]
    old_thirst = data[user_id]["haus"]
    
    # Healing dan recovery
    data[user_id]["kesehatan"] = min(100, data[user_id]["kesehatan"] + total_healing)
    
    if durasi:
        # Istirahat panjang juga pulihkan lapar dan haus sedikit
        hunger_restore = min(durasi * 10, 30)
        thirst_restore = min(durasi * 15, 40)
        data[user_id]["lapar"] = min(100, data[user_id]["lapar"] + hunger_restore)
        data[user_id]["haus"] = min(100, data[user_id]["haus"] + thirst_restore)
    
    data[user_id]["last_rest"] = current_time
    save_data(data)
    
    embed = discord.Embed(title="💤 Istirahat", color=0x00ff00)
    
    if durasi:
        embed.add_field(name="⏰ Durasi", value=f"{durasi} jam", inline=True)
        embed.add_field(name="💰 Biaya", value=f"Rp{rest_cost:,}", inline=True)
        embed.add_field(name="❤️ Kesehatan", value=f"{old_health} → {data[user_id]['kesehatan']}", inline=True)
        embed.add_field(name="🍽️ Lapar", value=f"{old_hunger} → {data[user_id]['lapar']}", inline=True)
        embed.add_field(name="💧 Haus", value=f"{old_thirst} → {data[user_id]['haus']}", inline=True)
    else:
        embed.add_field(name="💰 Biaya", value=f"Rp{rest_cost:,}", inline=True)
        embed.add_field(name="❤️ Kesehatan", value=f"{old_health} → {data[user_id]['kesehatan']} (+{total_healing})", inline=True)
    
    embed.add_field(name="🏠 Lokasi", value=get_housing_name(data[user_id]), inline=True)
    
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !makan, !minum, !obat - Shortcut commands untuk beli dari toko
@bot.command()
async def makan(ctx, *, nama_makanan=None):
    if nama_makanan is None:
        makanan_tersedia = [item for item, data_item in items.items() if data_item["effect"] == "food"]
        await ctx.send(f"🍽️ **Makanan tersedia:**\n" + "\n".join([f"• {item.title()} - Rp{items[item]['harga']:,}" for item in makanan_tersedia]) + "\n\nGunakan: `!makan [nama_makanan]`")
        return
    
    # Langsung beli dari toko, bukan dari marketplace
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    data[user_id] = apply_life_effects(data[user_id])
    
    item = items.get(nama_makanan.lower())
    if not item or item["effect"] != "food":
        await ctx.send("❌ Makanan tidak ditemukan di toko. Gunakan `!makan` untuk melihat daftar.")
        return
    
    if data[user_id]["uang"] < item["harga"]:
        await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{item['harga']:,}")
        return
    
    # Proses konsumsi langsung
    data[user_id]["uang"] -= item["harga"]
    old_hunger = data[user_id]["lapar"]
    data[user_id]["lapar"] = min(100, data[user_id]["lapar"] + item["hunger_restore"])
    
    result_message = f"✅ {ctx.author.mention} berhasil **makan** **{nama_makanan.title()}** seharga Rp{item['harga']:,}!\n\n"
    result_message += f"🍽️ Lapar: {old_hunger} → {data[user_id]['lapar']} (+{item['hunger_restore']})"
    
    save_data(data)
    await ctx.send(result_message)

@bot.command()
async def minum(ctx, *, nama_minuman=None):
    if nama_minuman is None:
        minuman_tersedia = [item for item, data_item in items.items() if data_item["effect"] == "drink"]
        await ctx.send(f"💧 **Minuman tersedia:**\n" + "\n".join([f"• {item.title()} - Rp{items[item]['harga']:,}" for item in minuman_tersedia]) + "\n\nGunakan: `!minum [nama_minuman]`")
        return
    
    # Langsung beli dari toko, bukan dari marketplace
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    data[user_id] = apply_life_effects(data[user_id])
    
    item = items.get(nama_minuman.lower())
    if not item or item["effect"] != "drink":
        await ctx.send("❌ Minuman tidak ditemukan di toko. Gunakan `!minum` untuk melihat daftar.")
        return
    
    if data[user_id]["uang"] < item["harga"]:
        await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{item['harga']:,}")
        return
    
    # Proses konsumsi langsung
    data[user_id]["uang"] -= item["harga"]
    old_thirst = data[user_id]["haus"]
    data[user_id]["haus"] = min(100, data[user_id]["haus"] + item["thirst_restore"])
    
    result_message = f"✅ {ctx.author.mention} berhasil **minum** **{nama_minuman.title()}** seharga Rp{item['harga']:,}!\n\n"
    result_message += f"💧 Haus: {old_thirst} → {data[user_id]['haus']} (+{item['thirst_restore']})"
    
    # Energy drink juga restore health
    if "health_restore" in item:
        old_health = data[user_id]["kesehatan"]
        data[user_id]["kesehatan"] = min(100, data[user_id]["kesehatan"] + item["health_restore"])
        result_message += f"\n❤️ Kesehatan: {old_health} → {data[user_id]['kesehatan']} (+{item['health_restore']})"
    
    save_data(data)
    await ctx.send(result_message)

@bot.command()
async def obat(ctx, *, nama_obat=None):
    if nama_obat is None:
        obat_tersedia = [item for item, data_item in items.items() if data_item["effect"] == "medicine"]
        await ctx.send(f"💊 **Obat tersedia:**\n" + "\n".join([f"• {item.title()} - Rp{items[item]['harga']:,}" for item in obat_tersedia]) + "\n\nGunakan: `!obat [nama_obat]`")
        return
    
    # Langsung beli dari toko, bukan dari marketplace
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    data[user_id] = apply_life_effects(data[user_id])
    
    item = items.get(nama_obat.lower())
    if not item or item["effect"] != "medicine":
        await ctx.send("❌ Obat tidak ditemukan di toko. Gunakan `!obat` untuk melihat daftar.")
        return
    
    if data[user_id]["uang"] < item["harga"]:
        await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{item['harga']:,}")
        return
    
    # Proses konsumsi langsung
    data[user_id]["uang"] -= item["harga"]
    old_health = data[user_id]["kesehatan"]
    data[user_id]["kesehatan"] = min(100, data[user_id]["kesehatan"] + item["health_restore"])
    
    result_message = f"✅ {ctx.author.mention} berhasil **minum obat** **{nama_obat.title()}** seharga Rp{item['harga']:,}!\n\n"
    result_message += f"❤️ Kesehatan: {old_health} → {data[user_id]['kesehatan']} (+{item['health_restore']})"
    
    save_data(data)
    await ctx.send(result_message)

# !menu - Menu utama dengan semua kategori fitur
@bot.command()
async def menu(ctx):
    embed = discord.Embed(title="📋 Menu Utama Bot Discord", color=0x0099ff)
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    
    embed.add_field(
        name="👤 **Basic**", 
        value="`!menubasic` - Registrasi & Profil\n`!menukondisi` - Sistem Kehidupan", 
        inline=True
    )
    embed.add_field(
        name="💼 **Kerja**", 
        value="`!menukerja` - Pekerjaan & Karir\n`!menuskill` - Job Skills System\n`!menukerjainteraktif` - Kerja Interaktif (DM)\n`!menutoko` - Belanja & Item", 
        inline=True
    )
    embed.add_field(
        name="💰 **Finansial**", 
        value="`!menupinjam` - Pinjam Meminjam\n`!menurating` - Sistem Rating", 
        inline=True
    )
    embed.add_field(
        name="🎮 **Hiburan**", 
        value="`!menuhiburan` - Crime, Judi, Achievement\n`!menusosial` - Nikah, Transfer, Daily\n`!menuinstagram` - Social Media Influencer\n`!menusleep` - Sistem Tidur & AI Chat", 
        inline=True
    )
    embed.add_field(
        name="🏢 **Bisnis & Ekonomi**", 
        value="`!menubisnis` - Sistem Bisnis\n`!menubank` - Banking & Investment\n`!menucompany` - Perusahaan & Komunitas", 
        inline=True
    )
    embed.add_field(
        name="📊 **Ranking & Trading**", 
        value="`!menurank` - Leaderboard\n`!menupasar` - Marketplace P2P", 
        inline=True
    )
    embed.add_field(
        name="🏠 **Real Estate**", 
        value="`!menurealestate` - Property Investment\n`!portfolio` - Real Estate Portfolio", 
        inline=True
    )
    embed.add_field(
        name="🚗 **Transportation**", 
        value="`!menutransportasi` - Kendaraan & Perjalanan\n`!garasiqu` - Garasi Pribadi", 
        inline=True
    )
    embed.add_field(
        name="🎓 **Education**", 
        value="`!menueducation` - Kuliah & Gelar\n`!rapor` - Status Pendidikan", 
        inline=True
    )
    embed.add_field(
        name="🎉 **Event System**",
        value="`!menuevent` - Event Bulanan & Tahunan\n`!event` - Event aktif sekarang",
        inline=True
    )
    embed.add_field(
        name="⚙️ **Admin**", 
        value="`!menuadmin` - Admin Tools", 
        inline=True
    )
    
    embed.set_footer(text="Pilih kategori untuk melihat command yang tersedia")
    await ctx.send(embed=embed)

# !menubasic - Menu basic commands
@bot.command()
async def menubasic(ctx):
    embed = discord.Embed(title="👤 Menu Basic Commands", color=0x00ff00)
    
    embed.add_field(
        name="🔰 **Pendaftaran**",
        value="`!daftar` - Daftar akun baru\n`!halo` - Sapa bot",
        inline=False
    )
    
    embed.add_field(
        name="📊 **Profil & Info**",
        value="`!profil [@user]` - Lihat profil lengkap\n`!saldo` - Cek saldo uang\n`!kondisi` - Cek kondisi kesehatan",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# !menukondisi - Menu sistem kehidupan
@bot.command()
async def menukondisi(ctx):
    embed = discord.Embed(title="🏥 Menu Sistem Kehidupan", color=0xff6b6b)
    
    embed.add_field(
        name="📊 **Status Kondisi**",
        value="`!kondisi` - Cek lapar, haus, kesehatan\n`!profil` - Lihat kondisi dalam profil",
        inline=False
    )
    
    embed.add_field(
        name="🍽️ **Makan & Minum**",
        value="`!makan [nama]` - Makan untuk kurangi lapar\n`!minum [nama]` - Minum untuk kurangi haus\n`!obat [nama]` - Minum obat untuk kesehatan",
        inline=False
    )
    
    embed.add_field(
        name="💤 **Istirahat**",
        value="`!istirahat` - Pulihkan kesehatan (cooldown 2 jam)",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ **Info Penting**",
        value="• Kondisi menurun seiring waktu\n• Rumah lebih baik = kondisi terjaga\n• Kondisi buruk = tidak bisa kerja\n• Notifikasi otomatis ke DM",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# !menukerja - Menu pekerjaan
@bot.command()
async def menukerja(ctx):
    embed = discord.Embed(title="💼 Menu Pekerjaan & Karir", color=0xffd700)
    
    embed.add_field(
        name="🔍 **Info Pekerjaan**",
        value="`!pekerjaan` - Daftar semua pekerjaan\n`!jobinfo [nama]` - Detail pekerjaan spesifik\n`!skill` - Lihat skill pekerjaan kamu",
        inline=False
    )
    
    embed.add_field(
        name="💼 **Freelance**",
        value="`!kerja` - Kerja freelance (1 jam cooldown)\n💰 Dapat Rp50k + bonus level + streak",
        inline=False
    )
    
    embed.add_field(
        name="🏢 **Pekerjaan Tetap**",
        value="`!apply [nama]` - Melamar pekerjaan tetap\n`!gajian` - Ambil gaji bulanan\n`!resign` - Keluar dari pekerjaan",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Job Skills (BARU!)**",
        value="`!skill` - Lihat skill unik pekerjaan kamu\n`![skill_command]` - Gunakan skill (contoh: `!vonis`, `!obati`)\n🔒 Beberapa skill hanya di DM\n⏰ Setiap skill punya cooldown unik",
        inline=False
    )
    
    embed.add_field(
        name="⚖️ **Sistem Hukum Mendalam**",
        value="`!menuhukum` - Menu sistem hukum lengkap\n`!kasusaktif` - Lihat kasus tersedia\n`!sidang [case_id]` - Sistem sidang 7 tahap\n`!banding [case_id]` - Sistem banding\n`!mediasi @user` - Mediasi win-win",
        inline=False
    )
    
    embed.add_field(
        name="📈 **Tips**",
        value="• Level tinggi = peluang apply lebih besar\n• Kondisi sehat = kerja lebih optimal\n• Streak kerja = bonus tambahan\n• **Setiap pekerjaan punya skill unik!**\n• **Sistem hukum realistis seperti dunia nyata!**",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu | UPGRADE: Sistem Hukum Mendalam!")
    await ctx.send(embed=embed)

# !menuhukum - Menu khusus sistem hukum
@bot.command()
async def menuhukum(ctx):
    embed = discord.Embed(title="⚖️ Menu Sistem Hukum Mendalam", color=0x9b59b6)
    
    embed.add_field(
        name="🏛️ **Pengadilan Tingkat Pertama**",
        value="`!laporutang @user [alasan]` - Laporkan ke pengadilan\n`!kasusaktif` - Kasus tersedia untuk profesi hukum\n`!ambilkasus [case_id]` - Ambil sebagai hakim/jaksa/pengacara\n`!cariadvokatpengacara [case_id]` - Cari pengacara pembela",
        inline=False
    )
    
    embed.add_field(
        name="⚖️ **Sistem Sidang 7 Tahap**",
        value="`!sidang [case_id]` - Lihat status sidang\n`!sidang [case_id] lanjut` - Lanjut ke tahap berikutnya\n`!sidang [case_id] vonis` - Bacakan vonis final\n\n**Tahapan:** Pembukaan → Dakwaan → Pembelaan → Pembuktian → Saksi → Alegasi → Putusan",
        inline=False
    )
    
    embed.add_field(
        name="📨 **Sistem Banding**",
        value="`!banding [case_id] [alasan]` - Ajukan banding (maks 7 hari)\n`!reviewbanding [case_id]` - Hakim review banding\n💰 **Biaya:** Rp500k, **Fee Hakim:** Rp1.5jt",
        inline=False
    )
    
    embed.add_field(
        name="🤝 **Mediasi & Penyelesaian Damai**",
        value="`!mediasi @user [proposal]` - Ajukan mediasi\n`!responmediasi [id] terima/tolak/counter` - Respon mediasi\n✅ **Manfaat:** Hindari biaya pengadilan, win-win solution",
        inline=False
    )
    
    embed.add_field(
        name="📋 **Monitoring & Riwayat**",
        value="`!statushukum [@user]` - Status kasus aktif\n`!transkrip [case_id]` - Lihat transkrip sidang\n`!kasusselesai [@user]` - Riwayat kasus yang selesai\n📊 **Statistik:** Win rate, total kasus, peran",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Fitur Realistis**",
        value="• **7 tahapan sidang** lengkap dengan skor\n• **Sistem bukti & saksi** yang mempengaruhi putusan\n• **Alegasi & duplik** dari kedua pihak\n• **Banding** untuk kasus yang tidak puas\n• **Mediasi** untuk solusi damai\n• **Transkrip sidang** tersimpan permanent\n• **Fee berbeda** untuk setiap peran hukum",
        inline=False
    )
    
    embed.add_field(
        name="💼 **Profesi Hukum**",
        value="👨‍⚖️ **Hakim:** Pimpin sidang, putuskan vonis, handle banding\n👨‍💼 **Jaksa:** Tuntut, ajukan bukti, argumentasi\n👨‍⚖️ **Pengacara:** Bela klien, counter argumen, cari celah\n💰 **Fee:** Hakim Rp1jt, Jaksa Rp600k, Pengacara Rp500k",
        inline=False
    )
    
    embed.set_footer(text="Sistem hukum paling realistis di Discord RPG! ⚖️")
    await ctx.send(embed=embed)

# !menuskill - Menu khusus job skills
@bot.command()
async def menuskill(ctx):
    embed = discord.Embed(title="🎯 Menu Job Skills System", color=0xe74c3c)
    
    embed.add_field(
        name="🏥 **Medis & Kesehatan**",
        value="🩺 **Dokter Umum:** `!obati [@user]` - Pengobatan gratis (3j)\n🦷 **Dokter Gigi:** `!rawatgigi` - Perawatan gigi (3.5j)\n👶 **Dokter Anak:** `!terapianak` - Terapi & vitamin (4j)\n🏥 **Dokter Bedah:** `!operasi` - Operasi darurat (6j)",
        inline=False
    )
    
    embed.add_field(
        name="⚖️ **Hukum & Keadilan**",
        value="👨‍⚖️ **Hakim:** `!vonis` - Vonis keadilan (6j)\n👨‍💼 **Pengacara:** `!konsultasi` - Konsultasi hukum (4j)\n🕵️ **Jaksa:** `/investigasi` - Investigasi kriminal (5j, DM only)",
        inline=False
    )
    
    embed.add_field(
        name="📚 **Pendidikan**",
        value="👨‍🏫 **Guru SD:** `!bimbingan` - Bimbingan belajar (4j)\n👩‍🏫 **Guru SMP:** `!mentoring` - Mentoring remaja (4.5j)\n👨‍🎓 **Guru SMA:** `!konseling` - Konseling karir (5j)\n👨‍🔬 **Dosen:** `!riset` - Riset akademik (6j)",
        inline=False
    )
    
    embed.add_field(
        name="💻 **Teknologi**",
        value="👨‍💻 **Programmer:** `!coding` - Coding session (3.5j)\n📊 **Data Analyst:** `!analisis` - Analisis data (4j)",
        inline=False
    )
    
    embed.add_field(
        name="✈️ **Transportasi & Service**",
        value="👨‍✈️ **Pilot:** `!terbang` - Penerbangan cepat (5j)\n👩‍✈️ **Pramugari:** `!layani` - Pelayanan prima (3j)\n🚛 **Sopir Truk:** `!ekspedisi` - Ekspedisi barang (4.5j)",
        inline=False
    )
    
    embed.add_field(
        name="🛒 **Retail & Service**",
        value="☕ **Barista:** `!racikkopi` - Racik kopi special (3j)\n💰 **Kasir:** `!kasir` - Transaksi cepat (4j)\n🏪 **Pegawai Toko:** `!stok` - Manajemen stok (6j)\n🔧 **Montir:** `!servis` - Servis kendaraan (5j)",
        inline=False
    )
    
    embed.add_field(
        name="💡 **Cara Pakai**",
        value="`!skill` - Lihat skill pekerjaan kamu\n`![command]` - Gunakan skill langsung\n🔒 Skill investigasi hanya di DM\n⏰ Setiap skill punya cooldown berbeda",
        inline=False
    )
    
    embed.add_field(
        name="🎁 **Keuntungan Skills**",
        value="💰 Bonus uang eksklusif\n❤️ Healing & buff khusus\n⏰ Cooldown reduction\n🎯 Efek unik per pekerjaan\n⭐ XP bonus tambahan\n🔓 Akses fitur khusus",
        inline=False
    )
    
    embed.set_footer(text="Setiap pekerjaan punya keunggulan unik! 🌟")
    await ctx.send(embed=embed)

# !menutoko - Menu toko dan item
@bot.command()
async def menutoko(ctx):
    embed = discord.Embed(title="🛒 Menu Toko & Item", color=0x9b59b6)
    
    embed.add_field(
        name="🏪 **Toko**",
        value="`!toko` - Lihat semua item di toko\n`!beli [item]` - Beli item langsung",
        inline=False
    )
    
    embed.add_field(
        name="🍽️ **Konsumsi Cepat**",
        value="`!makan [nama]` - Beli & makan langsung\n`!minum [nama]` - Beli & minum langsung\n`!obat [nama]` - Beli & minum obat langsung",
        inline=False
    )
    
    embed.add_field(
        name="🏠 **Tempat Tinggal**",
        value="• Tenda (Rp100k) - Level 1\n• Kontrakan (Rp2jt) - Level 2\n• Rumah (Rp15jt) - Level 3\n• Villa (Rp50jt) - Level 4",
        inline=False
    )
    
    embed.add_field(
        name="💡 **Info Item**",
        value="• Makanan/minuman: Konsumsi langsung\n• Rumah: Auto-upgrade, buang yang lama\n• Tools: Disimpan di inventory",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# !menupinjam - Menu sistem pinjam meminjam
@bot.command()
async def menupinjam(ctx):
    embed = discord.Embed(title="💰 Menu Pinjam Meminjam", color=0xe67e22)
    
    embed.add_field(
        name="💸 **Pinjam Uang**",
        value="`!pinjampemain @user [jumlah]` - Pinjam dari user lain\n⏰ Batas waktu: 7 hari",
        inline=False
    )
    
    embed.add_field(
        name="💳 **Bayar Utang**",
        value="`!bayarpemain @user [jumlah]` - Bayar utang\n`!utangpemain` - Cek daftar utang kamu (deprecated)\n`!cekutang [@user]` - Cek utang seseorang",
        inline=False
    )
    
    embed.add_field(
        name="💰 **Cek Piutang**",
        value="`!hutangke` - Lihat siapa yang berhutang ke kamu\n`!lupautang @user` - Maafkan utang seseorang",
        inline=False
    )
    
    embed.add_field(
        name="⚖️ **Jalur Hukum**",
        value="`!laporutang @penghutang [alasan]` - Lapor ke pengadilan\n`!statushukum [@user]` - Cek status kasus hukum",
        inline=False
    )
    
    embed.add_field(
        name="🔔 **Notifikasi Otomatis**",
        value="• 3 hari sebelum jatuh tempo\n• 1 hari sebelum jatuh tempo\n• Hari jatuh tempo\n• Setelah jatuh tempo\n• Bisa laporkan ke pengadilan setelah jatuh tempo",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ **Peringatan**",
        value="• Notifikasi dikirim ke DM\n• Jatuh tempo = reputasi buruk\n• Pengadilan bisa paksa bayar + denda 50%\n• Bayar tepat waktu = rating baik",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# !menurating - Menu sistem rating
@bot.command()
async def menurating(ctx):
    embed = discord.Embed(title="⭐ Menu Sistem Rating", color=0xf1c40f)
    
    embed.add_field(
        name="🏦 **Kredibilitas**",
        value="`!lihatrating [@user]` - Lihat rating kredibilitas\n`!kredibilitasrank` - Ranking kredibilitas terbaik",
        inline=False
    )
    
    embed.add_field(
        name="⭐ **Memberi Rating**",
        value="`!rating @user [1-5] [komentar]` - Beri rating\n📋 Hanya untuk yang pernah melunasi utang",
        inline=False
    )
    
    embed.add_field(
        name="🏅 **Level Kepercayaan**",
        value="• 🆕 Belum Ada Riwayat\n• 🔸 Pemula (< 3 transaksi)\n• ✅ Cukup Terpercaya (3.5+)\n• ⭐ Terpercaya (4.0+)\n• 💎 Sangat Terpercaya (4.5+)",
        inline=False
    )
    
    embed.add_field(
        name="💡 **Tips**",
        value="• Bayar tepat waktu = rating bagus\n• Rating tinggi = lebih mudah pinjam\n• Transaksi banyak = kredibilitas tinggi",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# !menurank - Menu ranking/leaderboard
@bot.command()
async def menurank(ctx):
    embed = discord.Embed(title="🏆 Menu Ranking & Leaderboard", color=0x3498db)
    
    embed.add_field(
        name="📊 **Leaderboard XP**",
        value="`!leaderboard` - Top 10 player berdasarkan XP/Level",
        inline=False
    )
    
    embed.add_field(
        name="⭐ **Ranking Kredibilitas**",
        value="`!kredibilitasrank` - Top 10 player terpercaya\n📋 Berdasarkan rating pinjaman",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Sistem Ranking**",
        value="• Pemula (Lv 1)\n• Pekerja Keras (Lv 5)\n• Profesional Muda (Lv 10)\n• Ahli (Lv 15)\n• Senior (Lv 20)\n• Expert (Lv 25)\n• Master (Lv 30)\n• Legend (Lv 40)\n• Grandmaster (Lv 50)",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# !menuhiburan - Menu hiburan
@bot.command()
async def menuhiburan(ctx):
    embed = discord.Embed(title="🎮 Menu Hiburan", color=0xe91e63)
    
    embed.add_field(
        name="🎭 **Crime System**",
        value="`!crime` - Lakukan kejahatan (risk vs reward)\n⏰ Cooldown: 2 jam",
        inline=False
    )
    
    embed.add_field(
        name="🎰 **Gambling**",
        value="`!judi [jumlah]` - Pertaruhan uang\n🎲 Peluang menang: 45%, Hadiah: 2x lipat",
        inline=False
    )
    
    embed.add_field(
        name="🏆 **Achievement**",
        value="`!achievement` - Lihat pencapaian kamu\n📊 Progress menuju achievement berikutnya",
        inline=False
    )
    
    embed.add_field(
        name="🎁 **Daily Bonus**",
        value="`!daily` - Bonus harian\n🔥 Daily streak untuk bonus ekstra",
        inline=False
    )
    
    embed.add_field(
        name="🐕 **Pet System**",
        value="`!menupet` - Sistem pet lengkap\n`!adopt [pet_type]` - Adopt pet baru\n`!pet` - Lihat pet kamu",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# ===== PET SYSTEM =====

# Database pet types
pet_types = {
    "anjing": {
        "nama": "Anjing",
        "harga": 100000,
        "maintenance_cost": 5000,  # Per hari
        "income_bonus": 0.05,  # 5% bonus income
        "happiness_decay": 10,  # Per hari
        "hunger_decay": 15,  # Per hari
        "emoji": "🐕",
        "skills": ["guard", "fetch"],
        "max_happiness": 100,
        "max_hunger": 100
    },
    "kucing": {
        "nama": "Kucing",
        "harga": 80000,
        "maintenance_cost": 4000,
        "income_bonus": 0.03,
        "happiness_decay": 8,
        "hunger_decay": 12,
        "emoji": "🐱",
        "skills": ["hunt", "comfort"],
        "max_happiness": 100,
        "max_hunger": 100
    },
    "burung": {
        "nama": "Burung",
        "harga": 50000,
        "maintenance_cost": 2000,
        "income_bonus": 0.02,
        "happiness_decay": 15,
        "hunger_decay": 20,
        "emoji": "🐦",
        "skills": ["sing", "messenger"],
        "max_happiness": 100,
        "max_hunger": 100
    },
    "kelinci": {
        "nama": "Kelinci",
        "harga": 60000,
        "maintenance_cost": 3000,
        "income_bonus": 0.025,
        "happiness_decay": 12,
        "hunger_decay": 18,
        "emoji": "🐰",
        "skills": ["lucky", "breed"],
        "max_happiness": 100,
        "max_hunger": 100
    },
    "hamster": {
        "nama": "Hamster",
        "harga": 30000,
        "maintenance_cost": 1500,
        "income_bonus": 0.01,
        "happiness_decay": 20,
        "hunger_decay": 25,
        "emoji": "🐹",
        "skills": ["collect", "cute"],
        "max_happiness": 100,
        "max_hunger": 100
    }
}

# Database bank system
banks = {
    "bca": {
        "nama": "Bank Central Asia",
        "rating": 95,
        "savings_interest": 0.03,  # 3% per tahun
        "loan_interest": 0.12,     # 12% per tahun
        "account_fee": 15000,      # Fee bulanan
        "transfer_fee_same": 0,    # Gratis transfer sesama BCA
        "transfer_fee_other": 7500, # Fee transfer ke bank lain
        "atm_fee_same": 0,         # Gratis tarik di ATM BCA
        "atm_fee_other": 5000,     # Fee tarik di ATM bank lain
        "locations": ["jakarta", "surabaya", "bandung", "medan"],
        "services": ["tabungan", "kredit", "kartu_kredit", "atm"]
    },
    "mandiri": {
        "nama": "Bank Mandiri",
        "rating": 92,
        "savings_interest": 0.025,
        "loan_interest": 0.10,
        "account_fee": 12000,
        "transfer_fee_same": 0,
        "transfer_fee_other": 6500,
        "atm_fee_same": 0,
        "atm_fee_other": 4000,
        "locations": ["jakarta", "yogyakarta", "bandung", "medan"],
        "services": ["tabungan", "kredit", "kartu_kredit", "atm", "bisnis"]
    },
    "bni": {
        "nama": "Bank Negara Indonesia",
        "rating": 90,
        "savings_interest": 0.02,
        "loan_interest": 0.11,
        "account_fee": 10000,
        "transfer_fee_same": 0,
        "transfer_fee_other": 5000,
        "atm_fee_same": 0,
        "atm_fee_other": 3500,
        "locations": ["jakarta", "surabaya", "yogyakarta", "medan"],
        "services": ["tabungan", "kredit", "remitansi", "atm"]
    },
    "bri": {
        "nama": "Bank Rakyat Indonesia",
        "rating": 88,
        "savings_interest": 0.035,  # Bunga tabungan tertinggi
        "loan_interest": 0.09,      # Bunga kredit terendah
        "account_fee": 8000,        # Fee terendah
        "transfer_fee_same": 0,
        "transfer_fee_other": 4000,
        "atm_fee_same": 0,
        "atm_fee_other": 2500,     # ATM fee terendah
        "locations": ["jakarta", "surabaya", "bandung", "yogyakarta", "medan"],
        "services": ["tabungan", "kredit", "mikro", "atm"]
    }
}

# Initialize bank system
def init_bank_system():
    if "bank_accounts" not in data:
        data["bank_accounts"] = {}
    
    for user_id in data:
        if user_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings", "bank_accounts"]:
            continue
        if "bank_data" not in data[user_id]:
            data[user_id]["bank_data"] = {
                "accounts": {},  # bank_code: {balance, opened_date, cards, etc}
                "cards": {},     # card_id: {type, bank, limit, etc}
                "loans": {},     # loan_id: {bank, amount, interest, etc}
                "credit_score": 750,  # 300-850
                "total_savings": 0,
                "total_debt": 0
            }
    save_data(data)

# Initialize pet system
def init_pet_system():
    for user_id in data:
        if user_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings"]:
            continue
        if "pets" not in data[user_id]:
            data[user_id]["pets"] = {}
        if "pet_stats" not in data[user_id]:
            data[user_id]["pet_stats"] = {
                "total_pets": 0,
                "pets_fed_today": 0,
                "last_feed_date": 0,
                "breeding_count": 0
            }
    save_data(data)

# Update pet stats (hunger, happiness decay)
def update_pet_stats(user_id):
    if "pets" not in data[user_id] or not data[user_id]["pets"]:
        return
    
    current_time = int(time.time())
    
    for pet_id, pet_data in data[user_id]["pets"].items():
        last_update = pet_data.get("last_update", current_time)
        hours_passed = max(0, (current_time - last_update) // 3600)
        
        if hours_passed > 0:
            pet_type_data = pet_types[pet_data["type"]]
            
            # Decay per hour
            happiness_decay = (pet_type_data["happiness_decay"] * hours_passed) // 24
            hunger_decay = (pet_type_data["hunger_decay"] * hours_passed) // 24
            
            pet_data["happiness"] = max(0, pet_data["happiness"] - happiness_decay)
            pet_data["hunger"] = max(0, pet_data["hunger"] - hunger_decay)
            pet_data["last_update"] = current_time
            
            # Pet gets sick if stats too low
            if pet_data["happiness"] < 20 or pet_data["hunger"] < 20:
                pet_data["sick"] = True
            elif pet_data["happiness"] > 50 and pet_data["hunger"] > 50:
                pet_data["sick"] = False

# !menupet - Menu pet system
@bot.command()
async def menupet(ctx):
    embed = discord.Embed(title="🐕 Menu Pet System", color=0xff69b4)
    
    embed.add_field(
        name="🏠 **Pet Management**",
        value="`!adopt [pet_type]` - Adopt pet baru\n`!pet` - Lihat semua pet kamu\n`!feed [pet_name]` - Kasih makan pet\n`!play [pet_name]` - Main dengan pet",
        inline=False
    )
    
    embed.add_field(
        name="🐕 **Pet Types Available**",
        value="• **Anjing** (Rp100k) - Guard house, fetch items\n• **Kucing** (Rp80k) - Hunt mice, comfort owner\n• **Burung** (Rp50k) - Sing songs, send messages\n• **Kelinci** (Rp60k) - Lucky charm, breeding\n• **Hamster** (Rp30k) - Collect coins, cuteness overload",
        inline=False
    )
    
    embed.add_field(
        name="💰 **Pet Benefits**",
        value="• **Income Bonus** - Pet sehat = bonus income kerja\n• **Companionship** - Pet bahagia = mood boost\n• **Skills** - Pet punya kemampuan unik\n• **Breeding** - Pet tertentu bisa breeding (future)",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Pet Care**",
        value="• Pet butuh makan dan perhatian harian\n• Pet yang sakit tidak memberikan bonus\n• Maintenance cost otomatis per hari\n• Happy pet = loyal companion",
        inline=False
    )
    
    embed.add_field(
        name="📊 **Pet Stats**",
        value="• **Happiness** - Butuh main dan perhatian\n• **Hunger** - Butuh makanan teratur\n• **Health** - Kombinasi happiness + hunger\n• **Level** - Meningkat dengan care yang baik",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu | Start dengan !adopt [pet_type]")
    await ctx.send(embed=embed)

# !adopt - Adopt pet baru
@bot.command()
async def adopt(ctx, pet_type=None):
    if pet_type is None:
        embed = discord.Embed(title="🏠 Pet Adoption Center", color=0xff69b4)
        
        for pet_key, pet_info in pet_types.items():
            skills_text = ", ".join(pet_info["skills"])
            embed.add_field(
                name=f"{pet_info['emoji']} {pet_info['nama']}",
                value=f"💰 Rp{pet_info['harga']:,}\n💵 Maintenance: Rp{pet_info['maintenance_cost']:,}/hari\n📈 Income bonus: {pet_info['income_bonus']*100}%\n🎯 Skills: {skills_text}",
                inline=True
            )
        
        embed.set_footer(text="!adopt [pet_type] untuk adopt | Contoh: !adopt anjing")
        await ctx.send(embed=embed)
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_pet_system()
    
    if pet_type.lower() not in pet_types:
        await ctx.send("❌ Pet type tidak tersedia. Gunakan `!adopt` untuk melihat daftar.")
        return
    
    pet_info = pet_types[pet_type.lower()]
    
    # Check if user has too many pets (max 3)
    current_pets = len(data[user_id]["pets"])
    if current_pets >= 3:
        await ctx.send("❌ Kamu sudah punya 3 pet (maksimum). Tidak bisa adopt lagi.")
        return
    
    # Check money
    if data[user_id]["uang"] < pet_info["harga"]:
        await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{pet_info['harga']:,} untuk adopt {pet_info['nama']}.")
        return
    
    # Generate pet name dan ID
    pet_names = {
        "anjing": ["Buddy", "Max", "Charlie", "Rocky", "Duke"],
        "kucing": ["Whiskers", "Luna", "Mimi", "Smokey", "Shadow"],
        "burung": ["Tweety", "Rio", "Kiwi", "Sky", "Chirpy"],
        "kelinci": ["Bunny", "Coco", "Fluffy", "Snowball", "Pepper"],
        "hamster": ["Peanut", "Chewy", "Tiny", "Fuzzy", "Biscuit"]
    }
    
    pet_name = random.choice(pet_names[pet_type.lower()])
    pet_id = f"pet_{user_id}_{int(time.time())}"
    
    # Process adoption
    data[user_id]["uang"] -= pet_info["harga"]
    
    data[user_id]["pets"][pet_id] = {
        "name": pet_name,
        "type": pet_type.lower(),
        "happiness": 100,
        "hunger": 100,
        "level": 1,
        "exp": 0,
        "sick": False,
        "adopted_date": int(time.time()),
        "last_update": int(time.time()),
        "last_fed": 0,
        "last_played": 0,
        "total_care": 0
    }
    
    data[user_id]["pet_stats"]["total_pets"] += 1
    
    embed = discord.Embed(title="🎉 Pet Adoption Successful!", color=0x00ff00)
    embed.add_field(name=f"{pet_info['emoji']} Pet Name", value=pet_name, inline=True)
    embed.add_field(name="🐾 Type", value=pet_info['nama'], inline=True)
    embed.add_field(name="💰 Cost", value=f"Rp{pet_info['harga']:,}", inline=True)
    embed.add_field(name="💵 Daily Maintenance", value=f"Rp{pet_info['maintenance_cost']:,}", inline=True)
    embed.add_field(name="📈 Income Bonus", value=f"{pet_info['income_bonus']*100}%", inline=True)
    embed.add_field(name="🎯 Skills", value=", ".join(pet_info['skills']), inline=True)
    embed.add_field(name="💡 Care Tips", value=f"Jangan lupa feed dan play dengan {pet_name} setiap hari!", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !pet - Lihat semua pet yang dimiliki
@bot.command()
async def pet(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(user_id)
    init_pet_system()
    update_pet_stats(user_id)
    
    if not data[user_id]["pets"]:
        await ctx.send(f"🐕 {member.display_name} belum punya pet. Adopt dengan `!adopt [pet_type]`")
        return
    
    embed = discord.Embed(title=f"🐕 Pet Collection {member.display_name}", color=0xff69b4)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    total_bonus = 0
    total_maintenance = 0
    
    for pet_id, pet_data in data[user_id]["pets"].items():
        pet_info = pet_types[pet_data["type"]]
        
        # Status indicators
        if pet_data["sick"]:
            status = "🤒 Sakit"
            status_color = "🔴"
        elif pet_data["happiness"] > 80 and pet_data["hunger"] > 80:
            status = "😊 Sangat Bahagia"
            status_color = "🟢"
        elif pet_data["happiness"] > 50 and pet_data["hunger"] > 50:
            status = "😐 Baik"
            status_color = "🟡"
        else:
            status = "😟 Butuh Perhatian"
            status_color = "🟠"
        
        # Calculate age
        age_days = (int(time.time()) - pet_data["adopted_date"]) // 86400
        
        embed.add_field(
            name=f"{pet_info['emoji']} {pet_data['name']} (Lv.{pet_data['level']})",
            value=f"{status_color} {status}\n😊 Happiness: {pet_data['happiness']}/100\n🍖 Hunger: {pet_data['hunger']}/100\n📅 Age: {age_days} hari\n🎯 Skills: {', '.join(pet_info['skills'])}",
            inline=True
        )
        
        if not pet_data["sick"]:
            total_bonus += pet_info["income_bonus"]
        total_maintenance += pet_info["maintenance_cost"]
    
    embed.add_field(name="📊 Total Income Bonus", value=f"{total_bonus*100:.1f}%", inline=True)
    embed.add_field(name="💵 Daily Maintenance", value=f"Rp{total_maintenance:,}", inline=True)
    embed.add_field(name="🏆 Total Pets", value=f"{len(data[user_id]['pets'])}/3", inline=True)
    
    embed.set_footer(text="!feed [pet_name] | !play [pet_name] untuk merawat pet")
    save_data(data)
    await ctx.send(embed=embed)

# !feed - Kasih makan pet
@bot.command()
async def feed(ctx, *, pet_name=None):
    if pet_name is None:
        await ctx.send("🍖 **Cara Feed Pet:**\n`!feed [pet_name]` - Kasih makan pet\n\nContoh: `!feed Buddy`")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_pet_system()
    update_pet_stats(user_id)
    
    # Find pet by name
    target_pet = None
    pet_id = None
    
    for p_id, pet_data in data[user_id]["pets"].items():
        if pet_data["name"].lower() == pet_name.lower():
            target_pet = pet_data
            pet_id = p_id
            break
    
    if not target_pet:
        available_pets = [pet_data["name"] for pet_data in data[user_id]["pets"].values()]
        await ctx.send(f"❌ Pet dengan nama '{pet_name}' tidak ditemukan.\nPet kamu: {', '.join(available_pets)}")
        return
    
    # Check cooldown (4 jam)
    current_time = int(time.time())
    last_fed = target_pet.get("last_fed", 0)
    if current_time - last_fed < 14400:  # 4 jam
        remaining = 14400 - (current_time - last_fed)
        await ctx.send(f"⏰ {target_pet['name']} masih kenyang. Tunggu {remaining//3600} jam {(remaining%3600)//60} menit lagi.")
        return
    
    # Feed cost
    pet_info = pet_types[target_pet["type"]]
    feed_cost = pet_info["maintenance_cost"] // 2  # Half of daily maintenance
    
    if data[user_id]["uang"] < feed_cost:
        await ctx.send(f"❌ Kamu butuh Rp{feed_cost:,} untuk memberi makan {target_pet['name']}.")
        return
    
    # Process feeding
    data[user_id]["uang"] -= feed_cost
    old_hunger = target_pet["hunger"]
    target_pet["hunger"] = min(100, target_pet["hunger"] + 40)
    target_pet["happiness"] = min(100, target_pet["happiness"] + 10)
    target_pet["last_fed"] = current_time
    target_pet["total_care"] += 1
    target_pet["exp"] += 5
    
    # Level up check
    if target_pet["exp"] >= target_pet["level"] * 100:
        target_pet["level"] += 1
        target_pet["exp"] = 0
        level_up_text = f"\n🎉 {target_pet['name']} naik ke level {target_pet['level']}!"
    else:
        level_up_text = ""
    
    # Update sick status
    if target_pet["happiness"] > 50 and target_pet["hunger"] > 50:
        target_pet["sick"] = False
    
    embed = discord.Embed(title="🍖 Pet Fed Successfully!", color=0x00ff00)
    embed.add_field(name=f"{pet_info['emoji']} Pet", value=target_pet['name'], inline=True)
    embed.add_field(name="💰 Cost", value=f"Rp{feed_cost:,}", inline=True)
    embed.add_field(name="🍖 Hunger", value=f"{old_hunger} → {target_pet['hunger']}", inline=True)
    embed.add_field(name="😊 Happiness", value=f"{target_pet['happiness']}/100", inline=True)
    embed.add_field(name="⭐ EXP", value=f"+5 ({target_pet['exp']}/{target_pet['level']*100})", inline=True)
    
    if level_up_text:
        embed.add_field(name="🎉 Level Up!", value=level_up_text, inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !play - Main dengan pet
@bot.command()
async def play(ctx, *, pet_name=None):
    if pet_name is None:
        await ctx.send("🎾 **Cara Main dengan Pet:**\n`!play [pet_name]` - Main dengan pet\n\nContoh: `!play Luna`")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_pet_system()
    update_pet_stats(user_id)
    
    # Find pet by name
    target_pet = None
    pet_id = None
    
    for p_id, pet_data in data[user_id]["pets"].items():
        if pet_data["name"].lower() == pet_name.lower():
            target_pet = pet_data
            pet_id = p_id
            break
    
    if not target_pet:
        available_pets = [pet_data["name"] for pet_data in data[user_id]["pets"].values()]
        await ctx.send(f"❌ Pet dengan nama '{pet_name}' tidak ditemukan.\nPet kamu: {', '.join(available_pets)}")
        return
    
    # Check cooldown (2 jam)
    current_time = int(time.time())
    last_played = target_pet.get("last_played", 0)
    if current_time - last_played < 7200:  # 2 jam
        remaining = 7200 - (current_time - last_played)
        await ctx.send(f"⏰ {target_pet['name']} masih capek. Tunggu {remaining//3600} jam {(remaining%3600)//60} menit lagi.")
        return
    
    # Play activities
    pet_info = pet_types[target_pet["type"]]
    activities = {
        "anjing": ["bermain lempar tangkap", "berlari di taman", "latihan obedience"],
        "kucing": ["bermain dengan yarn", "berburu mainan", "tidur di pangkuan"],
        "burung": ["bernyanyi bersama", "belajar kata baru", "terbang di ruangan"],
        "kelinci": ["melompat-lompat", "makan wortel", "berlari keliling"],
        "hamster": ["berlari di roda", "mengumpulkan biji", "main di terowongan"]
    }
    
    activity = random.choice(activities[target_pet["type"]])
    
    # Process playing
    old_happiness = target_pet["happiness"]
    target_pet["happiness"] = min(100, target_pet["happiness"] + 30)
    target_pet["last_played"] = current_time
    target_pet["total_care"] += 1
    target_pet["exp"] += 10
    
    # Random bonus
    bonus_chance = random.randint(1, 100)
    bonus_text = ""
    
    if bonus_chance <= 20:  # 20% chance
        bonus_amount = random.randint(1000, 5000)
        data[user_id]["uang"] += bonus_amount
        bonus_text = f"\n💰 {target_pet['name']} menemukan Rp{bonus_amount:,} saat bermain!"
    
    # Level up check
    if target_pet["exp"] >= target_pet["level"] * 100:
        target_pet["level"] += 1
        target_pet["exp"] = 0
        level_up_text = f"\n🎉 {target_pet['name']} naik ke level {target_pet['level']}!"
    else:
        level_up_text = ""
    
    # Update sick status
    if target_pet["happiness"] > 50 and target_pet["hunger"] > 50:
        target_pet["sick"] = False
    
    embed = discord.Embed(title="🎾 Playtime Fun!", color=0x00ff00)
    embed.add_field(name=f"{pet_info['emoji']} Activity", value=f"{target_pet['name']} {activity}!", inline=False)
    embed.add_field(name="😊 Happiness", value=f"{old_happiness} → {target_pet['happiness']}", inline=True)
    embed.add_field(name="⭐ EXP", value=f"+10 ({target_pet['exp']}/{target_pet['level']*100})", inline=True)
    
    if bonus_text:
        embed.add_field(name="🎁 Bonus!", value=bonus_text, inline=False)
    
    if level_up_text:
        embed.add_field(name="🎉 Level Up!", value=level_up_text, inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# ===== EDUCATION EXPANSION =====

# Database universitas dan program studi
universities = {
    "ui": {
        "nama": "Universitas Indonesia",
        "location": "jakarta",
        "prestige": 95,
        "tuition_base": 50000000,  # Per tahun
        "programs": {
            "teknik": {"nama": "Teknik Informatika", "duration": 4, "career_bonus": {"programmer": 0.3, "data analyst": 0.25}},
            "ekonomi": {"nama": "Ekonomi", "duration": 4, "career_bonus": {"bisnis": 0.4, "bank": 0.3}},
            "hukum": {"nama": "Ilmu Hukum", "duration": 4, "career_bonus": {"hakim": 0.5, "pengacara": 0.4, "jaksa": 0.4}},
            "kedokteran": {"nama": "Kedokteran", "duration": 6, "career_bonus": {"dokter umum": 0.6, "dokter anak": 0.5, "dokter bedah": 0.4}}
        }
    },
    "itb": {
        "nama": "Institut Teknologi Bandung",
        "location": "bandung", 
        "prestige": 90,
        "tuition_base": 45000000,
        "programs": {
            "teknik": {"nama": "Teknik Informatika", "duration": 4, "career_bonus": {"programmer": 0.35, "data analyst": 0.3}},
            "arsitektur": {"nama": "Arsitektur", "duration": 5, "career_bonus": {"real_estate": 0.4}},
            "sipil": {"nama": "Teknik Sipil", "duration": 4, "career_bonus": {"konstruksi": 0.5}}
        }
    },
    "ugm": {
        "nama": "Universitas Gadjah Mada",
        "location": "yogyakarta",
        "prestige": 85,
        "tuition_base": 40000000,
        "programs": {
            "psikologi": {"nama": "Psikologi", "duration": 4, "career_bonus": {"konselor": 0.4, "guru sma": 0.2}},
            "ekonomi": {"nama": "Ekonomi", "duration": 4, "career_bonus": {"bisnis": 0.35, "bank": 0.25}},
            "hukum": {"nama": "Ilmu Hukum", "duration": 4, "career_bonus": {"hakim": 0.45, "pengacara": 0.35}}
        }
    },
    "its": {
        "nama": "Institut Teknologi Sepuluh Nopember",
        "location": "surabaya",
        "prestige": 80,
        "tuition_base": 35000000,
        "programs": {
            "teknik": {"nama": "Teknik Informatika", "duration": 4, "career_bonus": {"programmer": 0.3, "data analyst": 0.25}},
            "industri": {"nama": "Teknik Industri", "duration": 4, "career_bonus": {"manajemen": 0.4}},
            "kelautan": {"nama": "Teknik Kelautan", "duration": 4, "career_bonus": {"maritime": 0.5}}
        }
    }
}

# Initialize education system
def init_education_system():
    for user_id in data:
        if user_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings"]:
            continue
        if "education" not in data[user_id]:
            data[user_id]["education"] = {
                "current_study": None,  # None atau {"university": "", "program": "", "semester": 0, "start_date": 0}
                "degrees": [],  # List of completed degrees
                "gpa": 0.0,
                "total_study_time": 0,
                "thesis_completed": False,
                "research_projects": []
            }
    save_data(data)



# !universities - Daftar universitas
@bot.command()
async def universities(ctx):
    embed = discord.Embed(title="🏫 Daftar Universitas Tersedia", color=0x3498db)
    
    for uni_key, uni_data in universities.items():
        programs_list = []
        for prog_key, prog_data in uni_data["programs"].items():
            programs_list.append(f"• {prog_data['nama']} ({prog_data['duration']} tahun)")
        
        embed.add_field(
            name=f"🎓 {uni_data['nama']}",
            value=f"📍 Lokasi: {uni_data['location'].title()}\n⭐ Prestige: {uni_data['prestige']}/100\n💰 Biaya: Rp{uni_data['tuition_base']:,}/tahun\n\n📚 **Program:**\n" + "\n".join(programs_list),
            inline=False
        )
    
    embed.set_footer(text="!kuliah [university_code] [program] untuk daftar | Contoh: !kuliah ui teknik")
    await ctx.send(embed=embed)

# !kuliah - Daftar kuliah
@bot.command()
async def kuliah(ctx, university_code=None, program_code=None):
    if not university_code or not program_code:
        await ctx.send("🎓 **Cara Daftar Kuliah:**\n`!kuliah [university_code] [program_code]`\n\nContoh: `!kuliah ui teknik`\n\n📋 Gunakan `!universities` untuk melihat daftar lengkap")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_education_system()
    
    # Check level requirement
    level = calculate_level(data[user_id]["xp"])
    if level < 15:
        await ctx.send(f"❌ Level kamu ({level}) belum cukup untuk kuliah. Minimal level 15.")
        return
    
    # Check if already studying
    if data[user_id]["education"]["current_study"]:
        current = data[user_id]["education"]["current_study"]
        await ctx.send(f"❌ Kamu sudah kuliah di {universities[current['university']]['nama']} program {current['program']}. Selesaikan dulu atau dropout.")
        return
    
    # Validate university and program
    if university_code.lower() not in universities:
        await ctx.send(f"❌ Universitas '{university_code}' tidak tersedia. Gunakan `!universities` untuk melihat daftar.")
        return
    
    uni_data = universities[university_code.lower()]
    
    if program_code.lower() not in uni_data["programs"]:
        programs = ", ".join(uni_data["programs"].keys())
        await ctx.send(f"❌ Program '{program_code}' tidak tersedia di {uni_data['nama']}.\nProgram tersedia: {programs}")
        return
    
    program_data = uni_data["programs"][program_code.lower()]
    
    # Check tuition fee
    tuition_fee = uni_data["tuition_base"]
    if data[user_id]["uang"] < tuition_fee:
        await ctx.send(f"❌ Uang tidak cukup untuk biaya kuliah tahun pertama. Butuh Rp{tuition_fee:,}")
        return
    
    # Process enrollment
    data[user_id]["uang"] -= tuition_fee
    data[user_id]["education"]["current_study"] = {
        "university": university_code.lower(),
        "program": program_code.lower(),
        "semester": 1,
        "start_date": int(time.time()),
        "last_study": 0,
        "total_credits": 0,
        "tuition_paid": 1  # Tahun ke berapa yang sudah dibayar
    }
    
    embed = discord.Embed(title="🎉 Enrollment Successful!", color=0x00ff00)
    embed.add_field(name="🏫 Universitas", value=uni_data["nama"], inline=True)
    embed.add_field(name="📚 Program", value=program_data["nama"], inline=True)
    embed.add_field(name="⏰ Durasi", value=f"{program_data['duration']} tahun", inline=True)
    embed.add_field(name="💰 Biaya Tahun 1", value=f"Rp{tuition_fee:,}", inline=True)
    embed.add_field(name="⭐ Prestige", value=f"{uni_data['prestige']}/100", inline=True)
    embed.add_field(name="📊 Current Semester", value="1", inline=True)
    embed.add_field(name="💡 Next Steps", value="Gunakan `!study` untuk belajar dan naikan GPA!", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !study - Belajar untuk semester
@bot.command()
async def study(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_education_system()
    
    current_study = data[user_id]["education"]["current_study"]
    if not current_study:
        await ctx.send("❌ Kamu tidak sedang kuliah. Daftar dulu dengan `!kuliah [university] [program]`")
        return
    
    # Check cooldown (6 jam)
    current_time = int(time.time())
    last_study = current_study.get("last_study", 0)
    if current_time - last_study < 21600:  # 6 jam
        remaining = 21600 - (current_time - last_study)
        await ctx.send(f"⏰ Tunggu {remaining//3600} jam {(remaining%3600)//60} menit lagi untuk study session berikutnya.")
        return
    
    uni_data = universities[current_study["university"]]
    program_data = uni_data["programs"][current_study["program"]]
    
    # Check tuition payment for current year
    years_passed = ((current_study["semester"] - 1) // 2) + 1  # 2 semester per tahun
    if years_passed > current_study["tuition_paid"]:
        tuition_due = uni_data["tuition_base"]
        if data[user_id]["uang"] < tuition_due:
            await ctx.send(f"❌ Kamu harus bayar SPP tahun ke-{years_passed}: Rp{tuition_due:,}")
            return
        
        data[user_id]["uang"] -= tuition_due
        current_study["tuition_paid"] = years_passed
        tuition_paid_text = f"\n💳 SPP tahun ke-{years_passed} dibayar: Rp{tuition_due:,}"
    else:
        tuition_paid_text = ""
    
    # Study session
    study_quality = random.randint(60, 100)  # Quality of study session
    level = calculate_level(data[user_id]["xp"])
    
    # Level bonus for better study quality
    study_quality += min(level, 20)  # Max +20 from level
    study_quality = min(study_quality, 100)
    
    # Calculate GPA increase
    gpa_increase = (study_quality / 100) * 0.2  # Max 0.2 per session
    old_gpa = data[user_id]["education"]["gpa"]
    data[user_id]["education"]["gpa"] = min(4.0, old_gpa + gpa_increase)
    
    # Credits and XP
    credits_earned = random.randint(2, 4)
    xp_earned = 25 + (study_quality // 10)
    
    current_study["total_credits"] += credits_earned
    current_study["last_study"] = current_time
    data[user_id]["xp"] += xp_earned
    data[user_id]["education"]["total_study_time"] += 1
    
    # Check semester completion (20 credits per semester)
    semester_complete = False
    if current_study["total_credits"] >= current_study["semester"] * 20:
        current_study["semester"] += 1
        semester_complete = True
        semester_bonus_xp = 50
        data[user_id]["xp"] += semester_bonus_xp
        completion_text = f"\n🎉 Semester {current_study['semester']-1} selesai! Naik ke semester {current_study['semester']}\n⭐ Semester bonus: +{semester_bonus_xp} XP"
    else:
        completion_text = ""
    
    # Check graduation
    total_semesters = program_data["duration"] * 2
    if current_study["semester"] > total_semesters:
        if not data[user_id]["education"]["thesis_completed"]:
            completion_text += "\n📝 Kamu sudah mengambil semua mata kuliah! Saatnya mengerjakan thesis dengan `!thesis`"
        else:
            # Graduate!
            degree = {
                "university": current_study["university"],
                "program": current_study["program"],
                "gpa": data[user_id]["education"]["gpa"],
                "graduation_date": current_time,
                "prestige": uni_data["prestige"]
            }
            data[user_id]["education"]["degrees"].append(degree)
            data[user_id]["education"]["current_study"] = None
            data[user_id]["education"]["thesis_completed"] = False
            data[user_id]["education"]["gpa"] = 0.0
            
            graduation_xp = 200 + (uni_data["prestige"] * 2)
            data[user_id]["xp"] += graduation_xp
            
            completion_text += f"\n🎓 LULUS! Selamat mendapat gelar dari {uni_data['nama']}!\n⭐ Graduation bonus: +{graduation_xp} XP"
    
    embed = discord.Embed(title="📚 Study Session Complete!", color=0x3498db)
    embed.add_field(name="🏫 University", value=uni_data["nama"], inline=True)
    embed.add_field(name="📊 Study Quality", value=f"{study_quality}/100", inline=True)
    embed.add_field(name="📈 GPA", value=f"{old_gpa:.2f} → {data[user_id]['education']['gpa']:.2f}", inline=True)
    embed.add_field(name="📋 Credits", value=f"+{credits_earned} ({current_study['total_credits']} total)", inline=True)
    embed.add_field(name="⭐ XP", value=f"+{xp_earned}", inline=True)
    embed.add_field(name="🗓️ Semester", value=f"{current_study['semester']}", inline=True)
    
    if tuition_paid_text:
        embed.add_field(name="💳 Payment", value=tuition_paid_text, inline=False)
    
    if completion_text:
        embed.add_field(name="🎉 Milestone", value=completion_text, inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !thesis - Kerjakan thesis
@bot.command()
async def thesis(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_education_system()
    
    current_study = data[user_id]["education"]["current_study"]
    if not current_study:
        await ctx.send("❌ Kamu tidak sedang kuliah.")
        return
    
    uni_data = universities[current_study["university"]]
    program_data = uni_data["programs"][current_study["program"]]
    total_semesters = program_data["duration"] * 2
    
    if current_study["semester"] <= total_semesters:
        await ctx.send(f"❌ Kamu belum bisa mengerjakan thesis. Selesaikan semua semester dulu (saat ini semester {current_study['semester']}/{total_semesters})")
        return
    
    if data[user_id]["education"]["thesis_completed"]:
        await ctx.send("❌ Thesis sudah selesai. Gunakan `!study` untuk menyelesaikan wisuda.")
        return
    
    # Thesis requirements
    thesis_cost = 10000000  # Biaya penelitian
    min_gpa = 3.0
    
    if data[user_id]["education"]["gpa"] < min_gpa:
        await ctx.send(f"❌ GPA kamu ({data[user_id]['education']['gpa']:.2f}) terlalu rendah untuk thesis. Minimal GPA {min_gpa}")
        return
    
    if data[user_id]["uang"] < thesis_cost:
        await ctx.send(f"❌ Biaya penelitian thesis: Rp{thesis_cost:,}")
        return
    
    # Process thesis
    data[user_id]["uang"] -= thesis_cost
    
    # Thesis quality berdasarkan GPA dan level
    gpa = data[user_id]["education"]["gpa"]
    level = calculate_level(data[user_id]["xp"])
    thesis_quality = int((gpa / 4.0) * 70) + random.randint(10, 30) + min(level // 5, 20)
    thesis_quality = min(thesis_quality, 100)
    
    # Rewards
    xp_reward = 100 + (thesis_quality // 2) + (uni_data["prestige"] // 2)
    research_bonus = thesis_quality * 1000
    
    data[user_id]["education"]["thesis_completed"] = True
    data[user_id]["xp"] += xp_reward
    data[user_id]["uang"] += research_bonus
    
    # Add research project
    research_project = {
        "title": f"Penelitian {program_data['nama']}",
        "quality": thesis_quality,
        "completion_date": int(time.time()),
        "university": current_study["university"]
    }
    data[user_id]["education"]["research_projects"].append(research_project)
    
    # Determine thesis result
    if thesis_quality >= 90:
        result = "🏆 Summa Cum Laude"
        result_color = 0xffd700
    elif thesis_quality >= 80:
        result = "🥇 Magna Cum Laude"
        result_color = 0x00ff00
    elif thesis_quality >= 70:
        result = "🥈 Cum Laude"
        result_color = 0x3498db
    else:
        result = "📜 Lulus"
        result_color = 0x95a5a6
    
    embed = discord.Embed(title="📝 Thesis Completed!", color=result_color)
    embed.add_field(name="🏫 University", value=uni_data["nama"], inline=True)
    embed.add_field(name="📚 Program", value=program_data["nama"], inline=True)
    embed.add_field(name="📊 Thesis Quality", value=f"{thesis_quality}/100", inline=True)
    embed.add_field(name="🏆 Result", value=result, inline=True)
    embed.add_field(name="⭐ XP Reward", value=f"+{xp_reward}", inline=True)
    embed.add_field(name="💰 Research Grant", value=f"Rp{research_bonus:,}", inline=True)
    embed.add_field(name="🎓 Next", value="Gunakan `!study` sekali lagi untuk wisuda!", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)



# Update kerja command untuk include education bonuses
# This will be added to the existing !kerja command by modifying the bonus calculation

# !menusosial - Menu sosial
@bot.command()
async def menusosial(ctx):
    embed = discord.Embed(title="👥 Menu Sosial", color=0xff69b4)
    
    embed.add_field(
        name="💍 **Pernikahan**",
        value="`!nikah @user` - Melamar user lain\n`!cerai` - Bercerai (biaya Rp500k)\n💰 Biaya nikah: Rp1jt",
        inline=False
    )
    
    embed.add_field(
        name="💸 **Transfer**",
        value="`!transfer @user [jumlah]` - Transfer uang\n💳 Fee: 1% (minimal Rp1000)",
        inline=False
    )
    
    embed.add_field(
        name="🎁 **Daily System**",
        value="`!daily` - Bonus harian dengan streak\n🔥 Streak bonus hingga Rp100k",
        inline=False
    )
    
    embed.add_field(
        name="🏆 **Achievement**",
        value="`!achievement` - Pencapaian personal\n📈 Progress tracking otomatis",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# !menubisnis - Menu bisnis
@bot.command()
async def menubisnis(ctx):
    embed = discord.Embed(title="🏢 Menu Bisnis", color=0x9b59b6)
    
    embed.add_field(
        name="🏗️ **Memulai Bisnis**",
        value="`!bisnis buat [nama]` - Buat bisnis baru\n💰 Biaya: Rp5.000.000",
        inline=False
    )
    
    embed.add_field(
        name="📊 **Manajemen**",
        value="`!bisnis info` - Info bisnis kamu\n`!bisnis profit` - Ambil keuntungan harian\n`!bisnis upgrade` - Upgrade level bisnis",
        inline=False
    )
    
    embed.add_field(
        name="💵 **Profit System**",
        value="• Level 1: Rp100k/hari\n• Level 2: Rp200k/hari\n• Level 3: Rp300k/hari\n• Dan seterusnya...",
        inline=False
    )
    
    embed.add_field(
        name="⬆️ **Upgrade Cost**",
        value="• Level 2: Rp2jt\n• Level 3: Rp4jt\n• Level 4: Rp6jt\n• Formula: Level × Rp2jt",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# !menurealestate - Menu real estate system
@bot.command()
async def menurealestate(ctx):
    embed = discord.Embed(title="🏠 Menu Real Estate System", color=0x2ecc71)
    
    embed.add_field(
        name="🏘️ **Property Catalog**",
        value="`!property` - Lihat katalog properti\n`!property market` - Pasar properti player\n`!property [kategori]` - Filter kategori\n📋 Kategori: residential, commercial, luxury, land, agricultural",
        inline=False
    )
    
    embed.add_field(
        name="💰 **Buying & Selling**",
        value="`!buyhouse [property_key]` - Beli properti baru\n`!buyhouse [property_id]` - Beli dari player\n`!sellhouse [property_id] [harga]` - Jual ke market",
        inline=False
    )
    
    embed.add_field(
        name="🏠 **Rental System**",
        value="`!rent out [property_id] [harga] [durasi]` - Sewakan properti\n`!rent seek [budget]` - Cari properti sewa\n`!rent [rental_id]` - Sewa properti\n💰 Passive income dari sewa",
        inline=False
    )
    
    embed.add_field(
        name="🔨 **Auction System**",
        value="`!auction` - Lihat lelang aktif\n`!auction create [prop_id] [start_price] [hours]` - Buat lelang\n`!auction bid [auction_id] [amount]` - Bid lelang",
        inline=False
    )
    
    embed.add_field(
        name="🏢 **Real Estate Agent**",
        value="`!agent` - Info agent system\n`!agent license` - Dapatkan lisensi (Lv15+, Rp2jt)\n`!agent market` - Market insights\n💼 3% komisi per transaksi",
        inline=False
    )
    
    embed.add_field(
        name="📊 **Portfolio Management**",
        value="`!portfolio` - Lihat portfolio real estate\n📈 Track ROI, passive income, property value\n💎 Diversifikasi properti untuk profit maksimal",
        inline=False
    )
    
    embed.add_field(
        name="💡 **Tips Investment**",
        value="• Properti komersial = income tinggi\n• Properti residential = stabil\n• Luxury properties = high value\n• Sewa properti = passive income\n• Market trends affect prices\n• Agent license = extra income",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Property Types**",
        value="🏠 **Residential:** Rumah, Apartemen, Villa\n🏢 **Commercial:** Toko, Gedung Kantor, Mall\n💎 **Luxury:** Villa Pantai, Penthouse\n🌾 **Agricultural:** Kebun Sawit\n📍 **Land:** Tanah Kosong",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu | Build your real estate empire! 🏗️")
    await ctx.send(embed=embed)

# !tabung - Tabung uang ke bank
@bot.command()
async def setorbank(ctx, bank_code=None, jumlah: int = None):
    if bank_code is None or jumlah is None:
        await ctx.send("🏦 **Cara Menabung:**\n`!tabung [bank_code] [jumlah]` - Tabung ke bank\n\nContoh: `!setornank bca 100000`\n\nBank tersedia: BCA, Mandiri, BNI, BRI")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_bank_system()
    
    bank_code = bank_code.lower()
    if bank_code not in banks:
        await ctx.send(f"❌ Bank '{bank_code}' tidak tersedia.")
        return
    
    bank_data = data[user_id]["bank_data"]
    if bank_code not in bank_data["accounts"]:
        await ctx.send(f"❌ Kamu belum punya rekening di {banks[bank_code]['nama']}. Buka dulu dengan `!bukarekening {bank_code}`")
        return
    
    if jumlah <= 0:
        await ctx.send("❌ Jumlah tabungan harus lebih dari 0.")
        return
    
    if data[user_id]["uang"] < jumlah:
        await ctx.send(f"❌ Uang tidak cukup. Kamu punya Rp{data[user_id]['uang']:,}")
        return
    
    # Process deposit
    data[user_id]["uang"] -= jumlah
    bank_data["accounts"][bank_code]["balance"] += jumlah
    bank_data["total_savings"] += jumlah
    
    # Add transaction history
    transaction = {
        "type": "deposit",
        "amount": jumlah,
        "timestamp": int(time.time()),
        "description": "Setoran tunai"
    }
    bank_data["accounts"][bank_code]["transaction_history"].append(transaction)
    
    embed = discord.Embed(title="💰 Setoran Berhasil!", color=0x00ff00)
    embed.add_field(name="🏦 Bank", value=banks[bank_code]["nama"], inline=True)
    embed.add_field(name="💵 Jumlah", value=f"Rp{jumlah:,}", inline=True)
    embed.add_field(name="💰 Saldo Baru", value=f"Rp{bank_data['accounts'][bank_code]['balance']:,}", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !tarik - Tarik uang dari bank
@bot.command()
async def tarik(ctx, bank_code=None, jumlah: int = None):
    if bank_code is None or jumlah is None:
        await ctx.send("🏦 **Cara Tarik Uang:**\n`!tarik [bank_code] [jumlah]` - Tarik dari bank\n\nContoh: `!tarik bca 50000`")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_bank_system()
    
    bank_code = bank_code.lower()
    if bank_code not in banks:
        await ctx.send(f"❌ Bank '{bank_code}' tidak tersedia.")
        return
    
    bank_data = data[user_id]["bank_data"]
    if bank_code not in bank_data["accounts"]:
        await ctx.send(f"❌ Kamu belum punya rekening di {banks[bank_code]['nama']}.")
        return
    
    if jumlah <= 0:
        await ctx.send("❌ Jumlah penarikan harus lebih dari 0.")
        return
    
    account = bank_data["accounts"][bank_code]
    if account["balance"] < jumlah:
        await ctx.send(f"❌ Saldo tidak cukup. Saldo kamu: Rp{account['balance']:,}")
        return
    
    # Check daily ATM limit
    daily_limit = 5000000  # 5 juta per hari
    today = int(time.time()) // 86400
    last_withdrawal_date = account.get("last_withdrawal_date", 0)
    daily_withdrawn = account.get("daily_withdrawn", 0) if last_withdrawal_date == today else 0
    
    if daily_withdrawn + jumlah > daily_limit:
        remaining_limit = daily_limit - daily_withdrawn
        await ctx.send(f"❌ Melebihi limit penarikan harian. Sisa limit: Rp{remaining_limit:,}")
        return
    
    # Process withdrawal
    account["balance"] -= jumlah
    data[user_id]["uang"] += jumlah
    bank_data["total_savings"] -= jumlah
    
    # Update daily withdrawal tracking
    account["last_withdrawal_date"] = today
    account["daily_withdrawn"] = daily_withdrawn + jumlah
    
    # Add transaction history
    transaction = {
        "type": "withdrawal",
        "amount": jumlah,
        "timestamp": int(time.time()),
        "description": "Penarikan tunai"
    }
    account["transaction_history"].append(transaction)
    
    embed = discord.Embed(title="💸 Penarikan Berhasil!", color=0x3498db)
    embed.add_field(name="🏦 Bank", value=banks[bank_code]["nama"], inline=True)
    embed.add_field(name="💵 Jumlah", value=f"Rp{jumlah:,}", inline=True)
    embed.add_field(name="💰 Saldo Tersisa", value=f"Rp{account['balance']:,}", inline=True)
    embed.add_field(name="📊 Limit Harian", value=f"Rp{daily_limit - account['daily_withdrawn']:,} tersisa", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !transferbank - Transfer antar bank atau sesama bank  
@bot.command()
async def transferbank(ctx, bank_from=None, target: discord.Member = None, jumlah: int = None):
    if bank_from is None or target is None or jumlah is None:
        await ctx.send("🏦 **Cara Transfer:**\n`!transferbank [bank_from] @user [jumlah]` - Transfer ke user lain\n\nContoh: `!transferbank bca @user 100000`")
        return
    
    user_id = str(ctx.author.id)
    target_id = str(target.id)
    
    if user_id == target_id:
        await ctx.send("❌ Tidak bisa transfer ke diri sendiri.")
        return
    
    create_user_profile(user_id)
    create_user_profile(target_id)
    init_bank_system()
    
    bank_from = bank_from.lower()
    if bank_from not in banks:
        await ctx.send(f"❌ Bank '{bank_from}' tidak tersedia.")
        return
    
    # Check sender account
    sender_bank_data = data[user_id]["bank_data"]
    if bank_from not in sender_bank_data["accounts"]:
        await ctx.send(f"❌ Kamu belum punya rekening di {banks[bank_from]['nama']}.")
        return
    
    if jumlah <= 0:
        await ctx.send("❌ Jumlah transfer harus lebih dari 0.")
        return
    
    sender_account = sender_bank_data["accounts"][bank_from]
    bank_info = banks[bank_from]
    
    # Calculate transfer fee
    target_bank_data = data[target_id]["bank_data"]
    target_has_same_bank = bank_from in target_bank_data["accounts"]
    
    if target_has_same_bank:
        fee = bank_info["transfer_fee_same"]  # Usually 0
        fee_description = f"Transfer sesama {bank_info['nama']}"
    else:
        fee = bank_info["transfer_fee_other"]
        fee_description = "Transfer antar bank"
    
    total_deduct = jumlah + fee
    
    if sender_account["balance"] < total_deduct:
        await ctx.send(f"❌ Saldo tidak cukup. Butuh Rp{total_deduct:,} (transfer + fee Rp{fee:,})")
        return
    
    # Process transfer
    sender_account["balance"] -= total_deduct
    sender_bank_data["total_savings"] -= total_deduct
    
    # If target has same bank, add to their account
    if target_has_same_bank:
        target_bank_data["accounts"][bank_from]["balance"] += jumlah
        target_bank_data["total_savings"] += jumlah
        
        # Add transaction history for target
        target_transaction = {
            "type": "transfer_in",
            "amount": jumlah,
            "timestamp": int(time.time()),
            "description": f"Transfer dari {ctx.author.display_name}",
            "from_user": ctx.author.display_name
        }
        target_bank_data["accounts"][bank_from]["transaction_history"].append(target_transaction)
    else:
        # Target doesn't have same bank account, give as cash
        data[target_id]["uang"] += jumlah
    
    # Add transaction history for sender
    sender_transaction = {
        "type": "transfer_out",
        "amount": jumlah,
        "fee": fee,
        "timestamp": int(time.time()),
        "description": f"Transfer ke {target.display_name}",
        "to_user": target.display_name
    }
    sender_account["transaction_history"].append(sender_transaction)
    
    embed = discord.Embed(title="💸 Transfer Berhasil!", color=0x00ff00)
    embed.add_field(name="🏦 Bank", value=bank_info["nama"], inline=True)
    embed.add_field(name="👤 Ke", value=target.display_name, inline=True)
    embed.add_field(name="💵 Jumlah", value=f"Rp{jumlah:,}", inline=True)
    embed.add_field(name="💳 Fee", value=f"Rp{fee:,}", inline=True)
    embed.add_field(name="📊 Total", value=f"Rp{total_deduct:,}", inline=True)
    embed.add_field(name="💰 Saldo Tersisa", value=f"Rp{sender_account['balance']:,}", inline=True)
    embed.add_field(name="📋 Keterangan", value=fee_description, inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    # Notifikasi ke penerima
    if target_has_same_bank:
        pesan_notif = f"💰 **Transfer Diterima!**\n\nKamu menerima transfer **Rp{jumlah:,}** dari **{ctx.author.display_name}** melalui {bank_info['nama']}.\n\nSaldo baru: **Rp{target_bank_data['accounts'][bank_from]['balance']:,}**"
    else:
        pesan_notif = f"💰 **Transfer Diterima!**\n\nKamu menerima transfer **Rp{jumlah:,}** dari **{ctx.author.display_name}** sebagai cash (tidak punya rekening {bank_info['nama']}).\n\nSaldo cash baru: **Rp{data[target_id]['uang']:,}**"
    
    await kirim_notif_dm(target_id, pesan_notif)

# !mutasi - Lihat mutasi rekening
@bot.command()
async def mutasi(ctx, bank_code=None, limit: int = 10):
    if bank_code is None:
        await ctx.send("🏦 **Cara Lihat Mutasi:**\n`!mutasi [bank_code] [limit]` - Lihat riwayat transaksi\n\nContoh: `!mutasi bca 5`")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_bank_system()
    
    bank_code = bank_code.lower()
    if bank_code not in banks:
        await ctx.send(f"❌ Bank '{bank_code}' tidak tersedia.")
        return
    
    bank_data = data[user_id]["bank_data"]
    if bank_code not in bank_data["accounts"]:
        await ctx.send(f"❌ Kamu belum punya rekening di {banks[bank_code]['nama']}.")
        return
    
    account = bank_data["accounts"][bank_code]
    transactions = account.get("transaction_history", [])
    
    if not transactions:
        await ctx.send("📋 Belum ada transaksi di rekening ini.")
        return
    
    embed = discord.Embed(title=f"📋 Mutasi {banks[bank_code]['nama']}", color=0x3498db)
    embed.add_field(name="💰 Saldo Saat Ini", value=f"Rp{account['balance']:,}", inline=True)
    embed.add_field(name="💳 No. Rekening", value=account["account_number"], inline=True)
    
    # Show recent transactions
    recent_transactions = transactions[-limit:] if len(transactions) > limit else transactions
    recent_transactions.reverse()  # Show newest first
    
    transaction_text = ""
    for i, tx in enumerate(recent_transactions):
        tx_time = datetime.fromtimestamp(tx["timestamp"]).strftime("%d/%m %H:%M")
        
        if tx["type"] == "deposit":
            icon = "💰"
            amount_text = f"+Rp{tx['amount']:,}"
        elif tx["type"] == "withdrawal":
            icon = "💸"
            amount_text = f"-Rp{tx['amount']:,}"
        elif tx["type"] == "transfer_in":
            icon = "📥"
            amount_text = f"+Rp{tx['amount']:,}"
        elif tx["type"] == "transfer_out":
            icon = "📤"
            total = tx['amount'] + tx.get('fee', 0)
            amount_text = f"-Rp{total:,}"
        else:
            icon = "📋"
            amount_text = f"Rp{tx['amount']:,}"
        
        transaction_text += f"{icon} {tx_time} {amount_text}\n{tx['description'][:30]}\n\n"
        
        if len(transaction_text) > 900:  # Discord field limit
            break
    
    embed.add_field(name=f"📝 {limit} Transaksi Terakhir", value=transaction_text or "Tidak ada transaksi", inline=False)
    
    await ctx.send(embed=embed)

# !kartukredit - Apply kartu kredit
@bot.command()
async def kartukredit(ctx, bank_code=None):
    if bank_code is None:
        await ctx.send("💳 **Cara Apply Kartu Kredit:**\n`!kartukredit [bank_code]` - Apply kartu kredit\n\nContoh: `!kartukredit bca`\n\n📋 **Syarat:**\n• Punya rekening di bank tersebut\n• Credit score minimal 650\n• Penghasilan minimal Rp5jt/bulan")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_bank_system()
    
    bank_code = bank_code.lower()
    if bank_code not in banks:
        await ctx.send(f"❌ Bank '{bank_code}' tidak tersedia.")
        return
    
    bank_data = data[user_id]["bank_data"]
    if bank_code not in bank_data["accounts"]:
        await ctx.send(f"❌ Kamu harus punya rekening di {banks[bank_code]['nama']} dulu.")
        return
    
    # Check credit score
    credit_score = bank_data["credit_score"]
    if credit_score < 650:
        await ctx.send(f"❌ Credit score kamu ({credit_score}) terlalu rendah. Minimal 650 untuk kartu kredit.")
        return
    
    # Check if already has credit card from this bank
    existing_cards = [card for card_id, card in bank_data["cards"].items() 
                     if card["type"] == "credit" and card["bank"] == bank_code]
    if existing_cards:
        await ctx.send(f"❌ Kamu sudah punya kartu kredit dari {banks[bank_code]['nama']}.")
        return
    
    # Check monthly income (rough estimate from job salary)
    monthly_income = data[user_id].get("gaji", 0)
    if monthly_income < 5000000:
        await ctx.send("❌ Penghasilan bulanan minimal Rp5.000.000 untuk kartu kredit.")
        return
    
    # Determine credit limit based on income and credit score
    base_limit = monthly_income * 3  # 3x monthly income
    score_multiplier = credit_score / 750  # Normalize to 750 score
    credit_limit = int(base_limit * score_multiplier)
    credit_limit = min(credit_limit, 50000000)  # Max 50 juta
    
    # Create credit card
    card_id = f"credit_{bank_code}_{random.randint(100000, 999999)}"
    annual_fee = 500000  # 500k annual fee
    
    bank_data["cards"][card_id] = {
        "type": "credit",
        "bank": bank_code,
        "number": f"**** **** **** {random.randint(1000, 9999)}",
        "credit_limit": credit_limit,
        "current_balance": 0,  # Amount owed
        "available_credit": credit_limit,
        "annual_fee": annual_fee,
        "interest_rate": banks[bank_code]["loan_interest"],
        "issued_date": int(time.time()),
        "last_statement": int(time.time()),
        "status": "active"
    }
    
    embed = discord.Embed(title="💳 Kartu Kredit Disetujui!", color=0x00ff00)
    embed.add_field(name="🏦 Bank", value=banks[bank_code]["nama"], inline=True)
    embed.add_field(name="💳 No. Kartu", value=f"**** **** **** {card_id[-4:]}", inline=True)
    embed.add_field(name="💰 Credit Limit", value=f"Rp{credit_limit:,}", inline=True)
    embed.add_field(name="📊 Credit Score", value=f"{credit_score}/850", inline=True)
    embed.add_field(name="💸 Annual Fee", value=f"Rp{annual_fee:,}", inline=True)
    embed.add_field(name="📈 Interest Rate", value=f"{banks[bank_code]['loan_interest']*100}%/tahun", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !pinjambank - Pinjam uang dari bank
@bot.command()
async def pinjambank(ctx, bank_code=None, jumlah: int = None):
    if bank_code is None or jumlah is None:
        await ctx.send("🏦 **Cara Pinjam dari Bank:**\n`!pinjambank [bank_code] [jumlah]` - Apply pinjaman\n\nContoh: `!pinjambank bca 10000000`\n\n📋 **Info:**\n• Credit score menentukan approval\n• Interest rate berbeda per bank\n• Tenor 12 bulan")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_bank_system()
    
    bank_code = bank_code.lower()
    if bank_code not in banks:
        await ctx.send(f"❌ Bank '{bank_code}' tidak tersedia.")
        return
    
    bank_data = data[user_id]["bank_data"]
    if bank_code not in bank_data["accounts"]:
        await ctx.send(f"❌ Kamu harus punya rekening di {banks[bank_code]['nama']} dulu.")
        return
    
    if jumlah <= 0:
        await ctx.send("❌ Jumlah pinjaman harus lebih dari 0.")
        return
    
    if jumlah > 100000000:  # Max 100 juta
        await ctx.send("❌ Maksimal pinjaman Rp100.000.000")
        return
    
    # Check credit score for approval
    credit_score = bank_data["credit_score"]
    min_score = 600  # Minimum score for loan
    
    if credit_score < min_score:
        await ctx.send(f"❌ Credit score kamu ({credit_score}) terlalu rendah untuk pinjaman. Minimal {min_score}.")
        return
    
    # Check existing loans
    total_existing_debt = bank_data.get("total_debt", 0)
    max_total_debt = data[user_id].get("gaji", 3000000) * 10  # Max 10x monthly salary
    
    if total_existing_debt + jumlah > max_total_debt:
        await ctx.send(f"❌ Total hutang akan melebihi batas maksimal Rp{max_total_debt:,}")
        return
    
    # Calculate approval probability based on credit score
    approval_chance = min(90, (credit_score - 600) / 250 * 90 + 50)  # 50-90% chance
    
    if random.randint(1, 100) > approval_chance:
        await ctx.send(f"❌ Pengajuan pinjaman ditolak. Coba lagi nanti atau tingkatkan credit score. (Approval chance: {approval_chance:.1f}%)")
        return
    
    # Create loan
    loan_id = f"loan_{bank_code}_{int(time.time())}"
    bank_info = banks[bank_code]
    interest_rate = bank_info["loan_interest"]
    tenor_months = 12
    
    # Calculate monthly payment
    monthly_interest = interest_rate / 12
    monthly_payment = jumlah * (monthly_interest * (1 + monthly_interest)**tenor_months) / ((1 + monthly_interest)**tenor_months - 1)
    monthly_payment = int(monthly_payment)
    
    total_payment = monthly_payment * tenor_months
    total_interest = total_payment - jumlah
    
    bank_data["loans"][loan_id] = {
        "bank": bank_code,
        "principal": jumlah,
        "interest_rate": interest_rate,
        "monthly_payment": monthly_payment,
        "remaining_balance": jumlah,
        "payments_made": 0,
        "total_payments": tenor_months,
        "start_date": int(time.time()),
        "last_payment": 0,
        "status": "active"
    }
    
    # Give money to user
    data[user_id]["uang"] += jumlah
    bank_data["total_debt"] += jumlah
    
    # Slightly decrease credit score due to new debt
    bank_data["credit_score"] = max(300, bank_data["credit_score"] - 5)
    
    embed = discord.Embed(title="💰 Pinjaman Disetujui!", color=0x00ff00)
    embed.add_field(name="🏦 Bank", value=bank_info["nama"], inline=True)
    embed.add_field(name="💵 Jumlah", value=f"Rp{jumlah:,}", inline=True)
    embed.add_field(name="📈 Interest Rate", value=f"{interest_rate*100}%/tahun", inline=True)
    embed.add_field(name="💳 Cicilan/Bulan", value=f"Rp{monthly_payment:,}", inline=True)
    embed.add_field(name="⏰ Tenor", value=f"{tenor_months} bulan", inline=True)
    embed.add_field(name="💸 Total Bunga", value=f"Rp{total_interest:,}", inline=True)
    embed.add_field(name="📊 Total Bayar", value=f"Rp{total_payment:,}", inline=True)
    embed.add_field(name="🆔 Loan ID", value=loan_id[-8:], inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !bukarekening - Buka rekening bank baru
@bot.command()
async def bukarekening(ctx, bank_code=None):
    if bank_code is None:
        await ctx.send("🏦 **Cara Buka Rekening:**\n`!bukarekening [bank_code]` - Buka rekening di bank\n\nBank tersedia: BCA, Mandiri, BNI, BRI\nContoh: `!bukarekening bca`")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_bank_system()
    
    bank_code = bank_code.lower()
    if bank_code not in banks:
        await ctx.send(f"❌ Bank '{bank_code}' tidak tersedia. Bank yang ada: {', '.join(banks.keys()).upper()}")
        return
    
    bank_info = banks[bank_code]
    bank_data = data[user_id]["bank_data"]
    
    # Cek apakah sudah punya rekening di bank ini
    if bank_code in bank_data["accounts"]:
        await ctx.send(f"❌ Kamu sudah punya rekening di {bank_info['nama']}.")
        return
    
    # Syarat buka rekening
    min_deposit = 100000  # Minimal setoran awal
    admin_fee = 50000     # Biaya admin buka rekening
    total_cost = min_deposit + admin_fee
    
    if data[user_id]["uang"] < total_cost:
        await ctx.send(f"❌ Tidak cukup uang untuk buka rekening.\n💰 Dibutuhkan: Rp{total_cost:,} (setoran awal Rp{min_deposit:,} + admin Rp{admin_fee:,})")
        return
    
    # Proses buka rekening
    data[user_id]["uang"] -= total_cost
    
    # Buat rekening baru
    account_number = f"{bank_code.upper()}{random.randint(1000000, 9999999)}"
    bank_data["accounts"][bank_code] = {
        "account_number": account_number,
        "balance": min_deposit,
        "opened_date": int(time.time()),
        "cards": [],
        "transaction_history": [],
        "monthly_fee_paid": int(time.time())
    }
    
    bank_data["total_savings"] += min_deposit
    
    # Kartu debit gratis untuk rekening baru
    card_id = f"debit_{bank_code}_{random.randint(100000, 999999)}"
    bank_data["cards"][card_id] = {
        "type": "debit",
        "bank": bank_code,
        "number": f"**** **** **** {random.randint(1000, 9999)}",
        "limit_daily": 5000000,  # Limit tarik harian
        "issued_date": int(time.time()),
        "status": "active"
    }
    
    bank_data["accounts"][bank_code]["cards"].append(card_id)
    
    embed = discord.Embed(title="🎉 Rekening Berhasil Dibuka!", color=0x00ff00)
    embed.add_field(name="🏦 Bank", value=bank_info["nama"], inline=True)
    embed.add_field(name="💳 No. Rekening", value=account_number, inline=True)
    embed.add_field(name="💰 Saldo Awal", value=f"Rp{min_deposit:,}", inline=True)
    embed.add_field(name="💳 Kartu Debit", value=f"**** **** **** {card_id[-4:]}", inline=True)
    embed.add_field(name="📊 Limit Tarik Harian", value=f"Rp{5000000:,}", inline=True)
    embed.add_field(name="💸 Fee Bulanan", value=f"Rp{bank_info['account_fee']:,}", inline=True)
    
    embed.add_field(
        name="💡 Fitur Bank",
        value=f"• Bunga tabungan: {bank_info['savings_interest']*100}%/tahun\n"
              f"• Transfer gratis sesama {bank_info['nama']}\n"
              f"• Fee transfer antar bank: Rp{bank_info['transfer_fee_other']:,}\n"
              f"• ATM gratis di {bank_info['nama']}",
        inline=False
    )
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# tabung command sudah ada sebagai tabungbank



# !kartu - Lihat semua kartu yang dimiliki
@bot.command()
async def kartu(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(user_id)
    init_bank_system()
    
    bank_data = data[user_id]["bank_data"]
    
    if not bank_data["cards"]:
        await ctx.send(f"💳 {member.display_name} belum memiliki kartu. Apply dengan `!kartukredit [bank]`")
        return
    
    embed = discord.Embed(title=f"💳 Kartu {member.display_name}", color=0x3498db)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    for card_id, card_data in bank_data["cards"].items():
        bank_name = banks[card_data["bank"]]["nama"]
        
        if card_data["type"] == "credit":
            status_color = "🟢" if card_data["status"] == "active" else "🔴"
            embed.add_field(
                name=f"💳 {bank_name} Credit Card",
                value=f"{status_color} {card_data['number']}\n💰 Limit: Rp{card_data['credit_limit']:,}\n💸 Available: Rp{card_data['available_credit']:,}\n📊 Balance: Rp{card_data['current_balance']:,}",
                inline=True
            )
        else:  # debit
            embed.add_field(
                name=f"💳 {bank_name} Debit Card",
                value=f"🟢 {card_data['number']}\n💰 Daily Limit: Rp{card_data['limit_daily']:,}",
                inline=True
            )
    
    total_credit_limit = sum(card['credit_limit'] for card in bank_data['cards'].values() if card['type'] == 'credit')
    total_debt = sum(card['current_balance'] for card in bank_data['cards'].values() if card['type'] == 'credit')
    
    if total_credit_limit > 0:
        embed.add_field(name="💎 Total Credit Limit", value=f"Rp{total_credit_limit:,}", inline=True)
        embed.add_field(name="💸 Total Credit Debt", value=f"Rp{total_debt:,}", inline=True)
        embed.add_field(name="📊 Credit Score", value=f"{bank_data['credit_score']}/850", inline=True)
    
    await ctx.send(embed=embed)

# !atm - Sistem ATM
@bot.command()
async def atm(ctx, bank_code=None, action=None, jumlah: int = None):
    if bank_code is None:
        embed = discord.Embed(title="🏧 ATM Services", color=0x9b59b6)
        embed.add_field(
            name="💰 **ATM Operations**",
            value="`!atm [bank] tarik [jumlah]` - Tarik uang di ATM\n`!atm [bank] info` - Info saldo\n`!atm cari` - Cari ATM terdekat",
            inline=False
        )
        embed.add_field(
            name="💳 **ATM Fees**",
            value="• Gratis di ATM bank sendiri\n• Fee Rp2.500-5.000 di ATM bank lain\n• Limit harian: Rp5.000.000",
            inline=False
        )
        embed.add_field(
            name="🏧 **Available ATMs**",
            value="🏧 BCA - Di semua Mall dan kantor\n🏧 Mandiri - Di area pemerintahan\n🏧 BNI - Di bandara dan pelabuhan\n🏧 BRI - Di desa dan pinggiran",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    if bank_code == "cari":
        embed = discord.Embed(title="🏧 ATM Terdekat", color=0x3498db)
        
        for bank_code, bank_info in banks.items():
            locations_text = ", ".join([loc.title() for loc in bank_info["locations"]])
            embed.add_field(
                name=f"🏧 ATM {bank_info['nama']}",
                value=f"📍 Lokasi: {locations_text}\n💳 Fee sesama: Gratis\n💳 Fee antar bank: Rp{bank_info['atm_fee_other']:,}",
                inline=True
            )
        
        await ctx.send(embed=embed)
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_bank_system()
    
    bank_code = bank_code.lower()
    if bank_code not in banks:
        await ctx.send(f"❌ Bank '{bank_code}' tidak tersedia.")
        return
    
    if action == "tarik":
        if jumlah is None:
            await ctx.send("❌ Format: `!atm [bank] tarik [jumlah]`")
            return
        
        # Sama seperti !tarik tapi dengan fee ATM
        bank_data = data[user_id]["bank_data"]
        if bank_code not in bank_data["accounts"]:
            await ctx.send(f"❌ Kamu belum punya rekening di {banks[bank_code]['nama']}.")
            return
        
        # ATM fee
        atm_fee = banks[bank_code]["atm_fee_same"]  # Gratis kalau ATM bank sendiri
        
        account = bank_data["accounts"][bank_code]
        total_withdraw = jumlah + atm_fee
        
        if account["balance"] < total_withdraw:
            await ctx.send(f"❌ Saldo tidak cukup. Saldo: Rp{account['balance']:,}, Dibutuhkan: Rp{total_withdraw:,} (termasuk fee Rp{atm_fee:,})")
            return
        
        # Check daily limit
        daily_limit = 5000000
        today = int(time.time()) // 86400
        last_withdrawal_date = account.get("last_withdrawal_date", 0)
        daily_withdrawn = account.get("daily_withdrawn", 0) if last_withdrawal_date == today else 0
        
        if daily_withdrawn + jumlah > daily_limit:
            remaining_limit = daily_limit - daily_withdrawn
            await ctx.send(f"❌ Melebihi limit ATM harian. Sisa limit: Rp{remaining_limit:,}")
            return
        
        # Process ATM withdrawal
        account["balance"] -= total_withdraw
        data[user_id]["uang"] += jumlah
        account["last_withdrawal_date"] = today
        account["daily_withdrawn"] = daily_withdrawn + jumlah
        
        transaction = {
            "type": "atm_withdrawal",
            "amount": jumlah,
            "fee": atm_fee,
            "timestamp": int(time.time()),
            "description": f"ATM Withdrawal - {banks[bank_code]['nama']}"
        }
        account["transaction_history"].append(transaction)
        
        embed = discord.Embed(title="🏧 ATM Withdrawal Berhasil!", color=0x00ff00)
        embed.add_field(name="🏧 ATM", value=banks[bank_code]["nama"], inline=True)
        embed.add_field(name="💵 Jumlah", value=f"Rp{jumlah:,}", inline=True)
        embed.add_field(name="💳 Fee", value=f"Rp{atm_fee:,}", inline=True)
        embed.add_field(name="💰 Saldo Tersisa", value=f"Rp{account['balance']:,}", inline=True)
        
        save_data(data)
        await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    elif action == "info":
        # Info saldo di ATM
        bank_data = data[user_id]["bank_data"]
        if bank_code not in bank_data["accounts"]:
            await ctx.send(f"❌ Kamu belum punya rekening di {banks[bank_code]['nama']}.")
            return
        
        account = bank_data["accounts"][bank_code]
        
        embed = discord.Embed(title="🏧 Info Rekening ATM", color=0x3498db)
        embed.add_field(name="🏦 Bank", value=banks[bank_code]["nama"], inline=True)
        embed.add_field(name="💰 Saldo", value=f"Rp{account['balance']:,}", inline=True)
        embed.add_field(name="💳 No. Rekening", value=account["account_number"], inline=True)
        
        # Last transaction
        if account.get("transaction_history"):
            last_tx = account["transaction_history"][-1]
            last_tx_time = datetime.fromtimestamp(last_tx["timestamp"]).strftime("%d/%m %H:%M")
            embed.add_field(name="📝 Transaksi Terakhir", value=f"{last_tx['description']}\n{last_tx_time}", inline=False)
        
        await ctx.send(embed=embed)
    
    else:
        await ctx.send("❌ Action tidak valid. Gunakan: tarik, info")



# !bankinfo - Lihat daftar bank atau info rekening
@bot.command()
async def bankinfo(ctx, target: discord.Member = None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_bank_system()
    
    if target is None:
        # Lihat daftar bank tersedia
        embed = discord.Embed(title="🏦 Daftar Bank Tersedia", color=0x2ecc71)
        
        for bank_code, bank_info in banks.items():
            services_text = ", ".join(bank_info["services"])
            locations_text = ", ".join([loc.title() for loc in bank_info["locations"]])
            
            embed.add_field(
                name=f"🏦 {bank_info['nama']} ({bank_code.upper()})",
                value=f"⭐ Rating: {bank_info['rating']}/100\n"
                      f"💰 Bunga Tabungan: {bank_info['savings_interest']*100}%/tahun\n"
                      f"💳 Fee Bulanan: Rp{bank_info['account_fee']:,}\n"
                      f"💸 Transfer Antar Bank: Rp{bank_info['transfer_fee_other']:,}\n"
                      f"📍 Lokasi: {locations_text}\n"
                      f"🛠️ Layanan: {services_text}",
                inline=False
            )
        
        embed.add_field(
            name="💡 **Commands**",
            value="`!bukarekening [bank_code]` - Buka rekening di bank\n"
                  "`!bankinfo @user` - Lihat rekening user\n"
                  "`!tabung [bank] [jumlah]` - Tabung ke bank tertentu\n"
                  "`!tarik [bank] [jumlah]` - Tarik dari bank tertentu",
            inline=False
        )
        
        embed.set_footer(text="Contoh: !bukarekening bca")
        await ctx.send(embed=embed)
        return
    
    # Lihat rekening user tertentu
    target_id = str(target.id)
    if target_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(target_id)
    init_bank_system()
    
    bank_data = data[target_id]["bank_data"]
    
    if not bank_data["accounts"]:
        await ctx.send(f"💳 {target.display_name} belum memiliki rekening bank.")
        return
    
    embed = discord.Embed(title=f"🏦 Rekening Bank {target.display_name}", color=0x3498db)
    embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
    
    total_savings = 0
    for bank_code, account in bank_data["accounts"].items():
        bank_info = banks[bank_code]
        total_savings += account["balance"]
        
        embed.add_field(
            name=f"🏦 {bank_info['nama']}",
            value=f"💰 Saldo: Rp{account['balance']:,}\n"
                  f"📅 Dibuka: {datetime.fromtimestamp(account['opened_date']).strftime('%d/%m/%Y')}\n"
                  f"💳 Kartu: {len(account.get('cards', []))} kartu",
            inline=True
        )
    
    embed.add_field(name="💎 Total Tabungan", value=f"Rp{total_savings:,}", inline=True)
    embed.add_field(name="📊 Credit Score", value=f"{bank_data['credit_score']}/850", inline=True)
    
    if bank_data.get("total_debt", 0) > 0:
        embed.add_field(name="💸 Total Hutang", value=f"Rp{bank_data['total_debt']:,}", inline=True)
    
    await ctx.send(embed=embed)

# !loaninfo - Info detail semua pinjaman
@bot.command()
async def loaninfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(user_id)
    init_bank_system()
    
    bank_data = data[user_id]["bank_data"]
    
    if not bank_data.get("loans"):
        await ctx.send(f"💳 {member.display_name} tidak memiliki pinjaman bank.")
        return
    
    embed = discord.Embed(title=f"💳 Info Pinjaman {member.display_name}", color=0xff9900)
    
    total_debt = 0
    for loan_id, loan_data in bank_data["loans"].items():
        if loan_data["status"] == "active":
            bank_name = banks[loan_data["bank"]]["nama"]
            remaining_payments = loan_data["total_payments"] - loan_data["payments_made"]
            total_debt += loan_data["remaining_balance"]
            
            embed.add_field(
                name=f"🏦 {bank_name}",
                value=f"💰 Sisa: Rp{loan_data['remaining_balance']:,}\n💳 Cicilan: Rp{loan_data['monthly_payment']:,}\n📅 Sisa: {remaining_payments} bulan\n🆔 {loan_id[-8:]}",
                inline=True
            )
    
    embed.add_field(name="💸 Total Hutang", value=f"Rp{total_debt:,}", inline=False)
    embed.add_field(name="📊 Credit Score", value=f"{bank_data['credit_score']}/850", inline=True)
    
    embed.set_footer(text="!bayarcicilan [loan_id] untuk bayar")
    await ctx.send(embed=embed)

# !lunas - Lunasi pinjaman sekaligus
@bot.command()
async def lunas(ctx, loan_id=None):
    if loan_id is None:
        await ctx.send("💳 **Cara Lunasi Pinjaman:**\n`!lunas [loan_id]` - Bayar lunas sekaligus\n\nGunakan `!loaninfo` untuk lihat loan ID")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_bank_system()
    
    bank_data = data[user_id]["bank_data"]
    
    # Find loan
    target_loan = None
    full_loan_id = None
    
    for l_id, loan_data in bank_data["loans"].items():
        if l_id.endswith(loan_id) or l_id[-8:] == loan_id:
            if loan_data["status"] == "active":
                target_loan = loan_data
                full_loan_id = l_id
                break
    
    if not target_loan:
        await ctx.send(f"❌ Loan dengan ID `{loan_id}` tidak ditemukan atau sudah lunas.")
        return
    
    remaining_balance = target_loan["remaining_balance"]
    
    if data[user_id]["uang"] < remaining_balance:
        await ctx.send(f"❌ Uang tidak cukup untuk melunasi. Butuh Rp{remaining_balance:,}")
        return
    
    # Process full payment
    data[user_id]["uang"] -= remaining_balance
    target_loan["status"] = "paid_off"
    target_loan["remaining_balance"] = 0
    target_loan["payments_made"] = target_loan["total_payments"]
    
    bank_data["total_debt"] -= remaining_balance
    
    # Big credit score increase for early payoff
    bank_data["credit_score"] = min(850, bank_data["credit_score"] + 50)
    
    embed = discord.Embed(title="🎉 Pinjaman LUNAS!", color=0x00ff00)
    embed.add_field(name="🏦 Bank", value=banks[target_loan["bank"]]["nama"], inline=True)
    embed.add_field(name="💰 Jumlah Lunas", value=f"Rp{remaining_balance:,}", inline=True)
    embed.add_field(name="📈 Credit Score", value=f"{bank_data['credit_score']}/850 (+50)", inline=True)
    embed.add_field(name="🎊 Bonus", value="Credit score naik signifikan karena pelunasan dipercepat!", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !bayarcicilan - Bayar cicilan pinjaman bank
@bot.command()
async def bayarcicilan(ctx, loan_id=None):
    if loan_id is None:
        await ctx.send("💳 **Cara Bayar Cicilan:**\n`!bayarcicilan [loan_id]` - Bayar cicilan pinjaman\n\nGunakan `!bankinfo @kamu` untuk lihat loan ID")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_bank_system()
    
    bank_data = data[user_id]["bank_data"]
    
    # Find loan
    target_loan = None
    full_loan_id = None
    
    for l_id, loan_data in bank_data["loans"].items():
        if l_id.endswith(loan_id) or l_id[-8:] == loan_id:
            if loan_data["status"] == "active":
                target_loan = loan_data
                full_loan_id = l_id
                break
    
    if not target_loan:
        await ctx.send(f"❌ Loan dengan ID `{loan_id}` tidak ditemukan atau sudah lunas.")
        return
    
    monthly_payment = target_loan["monthly_payment"]
    
    if data[user_id]["uang"] < monthly_payment:
        await ctx.send(f"❌ Uang tidak cukup untuk bayar cicilan Rp{monthly_payment:,}")
        return
    
    # Process payment
    data[user_id]["uang"] -= monthly_payment
    target_loan["payments_made"] += 1
    target_loan["last_payment"] = int(time.time())
    
    # Calculate remaining balance
    remaining_payments = target_loan["total_payments"] - target_loan["payments_made"]
    new_balance = target_loan["remaining_balance"] - (monthly_payment * 0.7)  # Assume 30% interest, 70% principal
    target_loan["remaining_balance"] = max(0, new_balance)
    
    bank_data["total_debt"] -= (monthly_payment * 0.7)
    
    # Check if loan is paid off
    if target_loan["payments_made"] >= target_loan["total_payments"]:
        target_loan["status"] = "paid_off"
        target_loan["remaining_balance"] = 0
        # Increase credit score for good payment
        bank_data["credit_score"] = min(850, bank_data["credit_score"] + 20)
        status_message = "🎉 Pinjaman LUNAS! Credit score naik +20"
    else:
        # Small credit score increase for on-time payment
        bank_data["credit_score"] = min(850, bank_data["credit_score"] + 1)
        status_message = f"✅ Pembayaran berhasil. Sisa {remaining_payments} cicilan"
    
    embed = discord.Embed(title="💳 Cicilan Dibayar!", color=0x00ff00)
    embed.add_field(name="🏦 Bank", value=banks[target_loan["bank"]]["nama"], inline=True)
    embed.add_field(name="💵 Cicilan", value=f"Rp{monthly_payment:,}", inline=True)
    embed.add_field(name="📊 Sisa Saldo Loan", value=f"Rp{target_loan['remaining_balance']:,}", inline=True)
    embed.add_field(name="📈 Credit Score", value=f"{bank_data['credit_score']}/850", inline=True)
    embed.add_field(name="📋 Status", value=status_message, inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !creditscore - Cek dan tingkatkan credit score
@bot.command()
async def creditscore(ctx, target: discord.Member = None):
    if target is None:
        target = ctx.author
    
    target_id = str(target.id)
    if target_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(target_id)
    init_bank_system()
    
    bank_data = data[target_id]["bank_data"]
    credit_score = bank_data["credit_score"]
    
    # Determine credit rating
    if credit_score >= 800:
        rating = "🏆 Excellent"
        rating_color = 0x00ff00
    elif credit_score >= 740:
        rating = "⭐ Very Good"
        rating_color = 0x3498db
    elif credit_score >= 670:
        rating = "✅ Good"
        rating_color = 0x2ecc71
    elif credit_score >= 580:
        rating = "⚠️ Fair"
        rating_color = 0xff9900
    else:
        rating = "❌ Poor"
        rating_color = 0xff0000
    
    embed = discord.Embed(title=f"📊 Credit Score {target.display_name}", color=rating_color)
    embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
    
    embed.add_field(name="📈 Score", value=f"{credit_score}/850", inline=True)
    embed.add_field(name="🏅 Rating", value=rating, inline=True)
    embed.add_field(name="💰 Total Savings", value=f"Rp{bank_data['total_savings']:,}", inline=True)
    embed.add_field(name="💸 Total Debt", value=f"Rp{bank_data.get('total_debt', 0):,}", inline=True)
    
    # Credit improvement tips
    if credit_score < 750:
        tips = []
        if bank_data.get('total_debt', 0) > bank_data['total_savings']:
            tips.append("• Kurangi hutang")
        if len(bank_data['accounts']) < 2:
            tips.append("• Buka rekening di bank lain")
        if not any(card['type'] == 'credit' for card in bank_data['cards'].values()):
            tips.append("• Apply kartu kredit dan gunakan bijak")
        
        tips.append("• Bayar cicilan tepat waktu")
        tips.append("• Tingkatkan tabungan")
        
        embed.add_field(name="💡 Tips Tingkatkan Score", value="\n".join(tips[:4]), inline=False)
    
    await ctx.send(embed=embed)

# !menubank - Menu banking system
@bot.command()
async def menubank(ctx):
    embed = discord.Embed(title="🏦 Menu Multi-Banking System", color=0x2ecc71)
    
    embed.add_field(
        name="🏦 **Bank Management**",
        value="`!bankinfo` - Lihat daftar bank tersedia\n`!bankinfo @user` - Lihat rekening user\n`!bukarekening [bank_code]` - Buka rekening baru",
        inline=False
    )
    
    embed.add_field(
        name="💰 **Banking Operations**",
        value="`!tabung [bank] [jumlah]` - Tabung ke bank tertentu\n`!tarik [bank] [jumlah]` - Tarik dari bank\n`!transferbank [bank_from] @user [jumlah]` - Transfer antar bank",
        inline=False
    )
    
    embed.add_field(
        name="💳 **Cards & Loans**",
        value="`!kartu` - Lihat kartu yang dimiliki\n`!apply kartu [bank] [type]` - Apply kartu kredit/debit\n`!pinjam bank [bank] [jumlah]` - Pinjam dari bank",
        inline=False
    )
    
    embed.add_field(
        name="🏧 **ATM Services**",
        value="`!atm` - Cari ATM terdekat\n`!atm [bank] tarik [jumlah]` - Tarik di ATM\n`!atm transfer [bank] [jumlah]` - Transfer via ATM",
        inline=False
    )
    
    embed.add_field(
        name="🌟 **Bank Features**",
        value="• **4 Bank Berbeda** dengan karakteristik unik\n• **Bunga & Fee** yang realistis per bank\n• **Kartu Kredit/Debit** dengan limit berbeda\n• **Loan System** dengan credit scoring\n• **ATM Network** dengan fee berbeda\n• **Transfer Antar Bank** dengan biaya",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu | Start dengan !bank")
    await ctx.send(embed=embed)

# !menucompany - Menu company system
@bot.command()
async def menucompany(ctx):
    embed = discord.Embed(title="🏢 Menu Perusahaan & Komunitas", color=0x3498db)
    
    embed.add_field(
        name="👔 **Management**",
        value="`!perusahaan buat [nama]` - Buat perusahaan (Lv25+)\n`!perusahaan info` - Info perusahaan kamu\n`!perusahaan list` - Daftar semua perusahaan\n💰 **Modal awal:** Rp10.000.000",
        inline=False
    )
    
    embed.add_field(
        name="👥 **Human Resources**",
        value="`!perusahaan rekrut @user [gaji]` - Rekrut karyawan\n`!perusahaan fire @user` - Pecat karyawan\n`!perusahaan gajian` - Bayar gaji semua karyawan\n👥 **Max:** 10 karyawan per perusahaan",
        inline=False
    )
    
    embed.add_field(
        name="💰 **Finance**",
        value="`!perusahaan deposit [jumlah]` - Setor modal\n`!perusahaan withdraw [jumlah]` - Tarik keuntungan\n💵 **Gaji minimum:** Rp100.000",
        inline=False
    )
    
    embed.add_field(
        name="📋 **Requirements & Benefits**",
        value="• Level 25+ untuk membuat perusahaan\n• Karyawan dapat gaji bulanan otomatis\n• CEO dapat kelola keuangan perusahaan\n• Pesangon 1 bulan gaji saat dipecat\n• Status kerja otomatis update",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# !workorders - Lihat work orders yang tersedia (Admin/monitoring)
@bot.command()
async def workorders(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Command ini hanya untuk admin.")
        return
    
    init_work_orders()
    
    if "work_orders" not in data or not data["work_orders"]:
        await ctx.send("📋 Tidak ada work orders aktif.")
        return
    
    embed = discord.Embed(title="📋 Active Work Orders", color=0x3498db)
    
    pending_orders = 0
    in_progress_orders = 0
    completed_orders = 0
    
    for order_id, order_data in list(data["work_orders"].items())[:10]:
        status_emoji = {
            "pending": "⏳",
            "assigned": "📋",
            "in_progress": "🔄",
            "completed": "✅",
            "cancelled": "❌"
        }
        
        if order_data["status"] == "pending":
            pending_orders += 1
        elif order_data["status"] == "in_progress":
            in_progress_orders += 1
        elif order_data["status"] == "completed":
            completed_orders += 1
        
        embed.add_field(
            name=f"{status_emoji.get(order_data['status'], '❓')} {order_id[-8:]}",
            value=f"Job: {order_data['job_type']}\nCustomer: {order_data['customer_name']}\nWorker: {order_data.get('worker_name', 'None')}\nStatus: {order_data['status']}",
            inline=True
        )
    
    embed.add_field(name="📊 Summary", value=f"Pending: {pending_orders}\nIn Progress: {in_progress_orders}\nCompleted: {completed_orders}", inline=False)
    
    await ctx.send(embed=embed)

# !activeworkers - Lihat workers yang sedang aktif
@bot.command()
async def activeworkers(ctx):
    init_work_orders()
    
    if "active_workers" not in data or not data["active_workers"]:
        await ctx.send("👔 Tidak ada workers yang sedang aktif.")
        return
    
    embed = discord.Embed(title="👔 Active Workers", color=0x00ff00)
    
    for worker_id, worker_data in data["active_workers"].items():
        try:
            worker = bot.get_user(int(worker_id))
            worker_name = worker.display_name if worker else f"User {worker_id[:4]}..."
            
            shift_duration = int(time.time()) - worker_data["shift_start"]
            hours = shift_duration // 3600
            minutes = (shift_duration % 3600) // 60
            
            embed.add_field(
                name=f"👤 {worker_name}",
                value=f"Job: {worker_data['job_type']}\nShift: {hours}h {minutes}m\nOrders: {worker_data['orders_completed']}\nCommission: Rp{worker_data['total_commission']:,}",
                inline=True
            )
        except:
            continue
    
    await ctx.send(embed=embed)

# Update menu untuk include interactive work system
@bot.command()
async def menukerjainteraktif(ctx):
    embed = discord.Embed(title="💼 Menu Kerja Interaktif (DM)", color=0xe67e22)
    
    embed.add_field(
        name="🏪 **Retail Jobs**",
        value="💌 `/kerjadm pegawai_toko` - Melayani pembeli real-time\n💌 `/kerjadm kasir` - Proses transaksi pembayaran\n💰 **Komisi:** 3-5% per transaksi",
        inline=False
    )
    
    embed.add_field(
        name="☕ **Service Jobs**",
        value="💌 `/kerjadm barista` - Buat kopi untuk customer\n💌 `/kerjadm customer_service` - Handle complaints\n💰 **Komisi:** 4-8% + tips",
        inline=False
    )
    
    embed.add_field(
        name="🚗 **Delivery & Technical**",
        value="💌 `/kerjadm delivery` - Antar pesanan customer\n💌 `/kerjadm teknisi` - Repair elektronik\n💰 **Komisi:** 10-15% per job",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Cara Kerja**",
        value="1. **Start shift** dengan `/kerjadm [job_type]` di DM Bot\n2. **Terima work order** otomatis via DM\n3. **Mulai kerja** dengan `/mulai [order_id]`\n4. **Layani customer** sesuai job description\n5. **Selesaikan** dengan `/selesai [order_id] [feedback]`\n6. **End shift** dengan `/selesaishift`",
        inline=False
    )
    
    embed.add_field(
        name="💰 **Income System**",
        value="• **Komisi** berdasarkan nilai transaksi\n• **Rating customer** mempengaruhi bonus\n• **Tips** untuk service excellent\n• **Performance bonus** untuk rating tinggi\n• **XP gain** dari setiap completed order",
        inline=False
    )
    
    embed.add_field(
        name="🎮 **Fitur Realistis**",
        value="• **Real customer interaction** via DM\n• **Time pressure** untuk selesaikan order\n• **Customer feedback** yang mempengaruhi income\n• **NPC customers** dengan personality berbeda\n• **Work orders** generate otomatis\n• **Shift system** seperti kerja sungguhan",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ **Requirements**",
        value="🔒 **Semua interaksi melalui DM Bot**\n📱 **Responsif** dalam melayani customer\n⭐ **Level minimum** berbeda per job\n💬 **Komunikasi** yang baik dengan customer",
        inline=False
    )
    
    embed.set_footer(text="Pengalaman kerja paling realistis di Discord! 💼")
    await ctx.send(embed=embed)

# ===== SLEEP SYSTEM =====

def init_sleep_system():
    """Initialize sleep system untuk semua user"""
    for user_id in data:
        if user_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings"]:
            continue
        if "sleep_status" not in data[user_id]:
            data[user_id]["sleep_status"] = {
                "is_sleeping": False,
                "sleep_start": 0,
                "sleep_duration": 0,
                "total_sleep_time": 0
            }
    save_data(data)

def check_sleep_status(user_id):
    """Cek apakah user sedang tidur"""
    init_sleep_system()
    return data[user_id]["sleep_status"]["is_sleeping"]

# !tidur - Tidur (bisa kapan saja)
@bot.command()
async def tidur(ctx, durasi: int = None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_sleep_system()
    
    if check_sleep_status(user_id):
        await ctx.send("😴 Kamu sudah tidur! Gunakan `!bangun` untuk bangun.")
        return
    
    if durasi is None:
        await ctx.send("😴 **Cara Tidur:**\n`!tidur [durasi_jam]` - Tidur selama beberapa jam\n\nContoh: `!tidur 8` (tidur 8 jam)\n\n💡 **Info:**\n• Bisa tidur kapan saja\n• Saat tidur tidak bisa menggunakan fitur lain\n• Tidur memulihkan kesehatan dan mood\n• Gunakan `!bangun` untuk bangun paksa")
        return
    
    if durasi <= 0 or durasi > 24:
        await ctx.send("❌ Durasi tidur harus 1-24 jam.")
        return
    
    # Mulai tidur
    current_time = int(time.time())
    data[user_id]["sleep_status"]["is_sleeping"] = True
    data[user_id]["sleep_status"]["sleep_start"] = current_time
    data[user_id]["sleep_status"]["sleep_duration"] = durasi
    
    embed = discord.Embed(title="😴 Selamat Tidur!", color=0x3498db)
    embed.add_field(name="⏰ Durasi", value=f"{durasi} jam", inline=True)
    
    wake_time = current_time + (durasi * 3600)
    wake_time_str = datetime.fromtimestamp(wake_time).strftime("%H:%M")
    embed.add_field(name="⏰ Bangun Otomatis", value=wake_time_str, inline=True)
    embed.add_field(name="💤 Status", value="Tidur nyenyak...", inline=True)
    embed.add_field(name="💡 Info", value="Kamu tidak bisa menggunakan command lain saat tidur\nGunakan `!bangun` jika ingin bangun lebih cepat", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !bangun - Bangun dari tidur
@bot.command()
async def bangun(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_sleep_system()
    
    if not check_sleep_status(user_id):
        await ctx.send("🌅 Kamu sudah bangun!")
        return
    
    current_time = int(time.time())
    sleep_data = data[user_id]["sleep_status"]
    sleep_start = sleep_data["sleep_start"]
    planned_duration = sleep_data["sleep_duration"]
    actual_sleep_time = current_time - sleep_start
    actual_hours = actual_sleep_time / 3600
    
    # Hitung benefit dari tidur
    health_restore = min(int(actual_hours * 10), 100)  # Max 100 health
    mood_bonus = min(int(actual_hours * 5), 50)  # Mood bonus untuk XP
    
    # Update kesehatan
    old_health = data[user_id]["kesehatan"]
    data[user_id]["kesehatan"] = min(100, old_health + health_restore)
    
    # XP bonus jika tidur cukup (minimal 6 jam)
    xp_bonus = 0
    if actual_hours >= 6:
        xp_bonus = 30 + mood_bonus
        data[user_id]["xp"] += xp_bonus
    
    # Update sleep stats
    sleep_data["is_sleeping"] = False
    sleep_data["total_sleep_time"] += actual_sleep_time
    
    embed = discord.Embed(title="🌅 Bangun Tidur!", color=0xffd700)
    embed.add_field(name="⏰ Tidur Selama", value=f"{actual_hours:.1f} jam", inline=True)
    embed.add_field(name="❤️ Kesehatan", value=f"{old_health} → {data[user_id]['kesehatan']} (+{health_restore})", inline=True)
    
    if xp_bonus > 0:
        embed.add_field(name="⭐ XP Bonus", value=f"+{xp_bonus} (tidur cukup)", inline=True)
        embed.add_field(name="😊 Mood", value="Segar dan siap beraktivitas!", inline=False)
    else:
        embed.add_field(name="😴 Mood", value="Masih mengantuk (tidur kurang dari 6 jam)", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# ===== AI CHAT SYSTEM =====

import random

# Database respons AI sederhana
ai_responses = {
    "greeting": [
        "Halo! Ada yang bisa saya bantu?",
        "Hi! Apa kabar hari ini?",
        "Selamat datang! Ada pertanyaan?",
        "Halo! Senang bertemu dengan kamu!"
    ],
    "how_are_you": [
        "Saya baik-baik saja! Terima kasih sudah bertanya. Bagaimana dengan kamu?",
        "Saya selalu siap membantu! Kamu sendiri bagaimana?",
        "Saya merasa hebat hari ini! Ada yang ingin kamu tanyakan?"
    ],
    "help": [
        "Saya bisa membantu menjawab pertanyaan umum, memberikan tips tentang game, atau sekadar mengobrol!",
        "Kamu bisa bertanya apa saja! Saya akan berusaha membantu sebaik mungkin.",
        "Apa yang ingin kamu ketahui? Saya siap membantu!"
    ],
    "game_tips": [
        "Tip: Kerja secara konsisten dan jaga kondisi kesehatan untuk income optimal!",
        "Tip: Investasi di real estate bisa memberikan passive income yang bagus!",
        "Tip: Bangun kredibilitas yang baik dengan membayar utang tepat waktu!",
        "Tip: Level up untuk membuka pekerjaan dengan gaji lebih tinggi!"
    ],
    "money": [
        "Uang adalah alat, bukan tujuan. Gunakan dengan bijak!",
        "Diversifikasi sumber income kamu - kerja, bisnis, investasi!",
        "Ingat untuk selalu sisihkan uang untuk tabungan dan investasi!",
        "Jangan lupa bayar utang tepat waktu untuk menjaga kredibilitas!"
    ],
    "motivasi": [
        "Terus semangat! Setiap langkah kecil adalah progress!",
        "Kegagalan adalah pelajaran berharga menuju kesuksesan!",
        "Konsistensi adalah kunci kesuksesan jangka panjang!",
        "Percaya pada diri sendiri dan terus berusaha!"
    ],
    "unknown": [
        "Hmm, itu pertanyaan menarik! Bisa dijelaskan lebih detail?",
        "Maaf, saya tidak terlalu paham. Bisa diulang dengan kata-kata lain?",
        "Itu di luar pengetahuan saya. Ada pertanyaan lain?",
        "Saya belum bisa jawab itu. Coba tanya yang lain?"
    ]
}

def get_ai_response(message):
    """Generate AI response berdasarkan input message"""
    message_lower = message.lower()
    
    # Greeting detection
    if any(word in message_lower for word in ["halo", "hai", "hi", "hello", "selamat", "pagi", "siang", "malam"]):
        return random.choice(ai_responses["greeting"])
    
    # How are you detection
    if any(phrase in message_lower for phrase in ["apa kabar", "bagaimana kabar", "gimana kabar", "how are you"]):
        return random.choice(ai_responses["how_are_you"])
    
    # Help detection
    if any(word in message_lower for word in ["help", "bantuan", "bantu", "tolong"]):
        return random.choice(ai_responses["help"])
    
    # Game tips detection
    if any(word in message_lower for word in ["tips", "tip", "saran", "cara", "bagaimana", "gimana"]):
        return random.choice(ai_responses["game_tips"])
    
    # Money related
    if any(word in message_lower for word in ["uang", "money", "duit", "finansial", "investasi", "tabungan"]):
        return random.choice(ai_responses["money"])
    
    # Motivasi detection
    if any(word in message_lower for word in ["motivasi", "semangat", "down", "sedih", "capek", "lelah", "stress"]):
        return random.choice(ai_responses["motivasi"])
    
    # Default response
    return random.choice(ai_responses["unknown"])

# !tanya - Bertanya ke AI
@bot.command()
async def tanya(ctx, *, pertanyaan=None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    # Cek apakah user sedang tidur
    if check_sleep_status(user_id):
        await ctx.send("😴 Kamu sedang tidur! Bangun dulu dengan `!bangun` sebelum bisa bertanya.")
        return
    
    if pertanyaan is None:
        await ctx.send("🤖 **Cara Bertanya ke AI:**\n`!tanya [pertanyaan]` - Tanya apa saja ke AI\n\nContoh: `!tanya bagaimana cara cepat kaya?`\n\n💡 **Yang bisa ditanyakan:**\n• Tips dan trik game\n• Motivasi dan semangat\n• Pertanyaan umum\n• Atau sekadar mengobrol!")
        return
    
    # Generate AI response
    ai_response = get_ai_response(pertanyaan)
    
    # Cooldown 30 detik untuk avoid spam
    current_time = int(time.time())
    last_ai_chat = data[user_id].get("last_ai_chat", 0)
    if current_time - last_ai_chat < 30:
        remaining = 30 - (current_time - last_ai_chat)
        await ctx.send(f"⏰ Tunggu {remaining} detik lagi untuk bertanya ke AI.")
        return
    
    data[user_id]["last_ai_chat"] = current_time
    
    embed = discord.Embed(title="🤖 AI Assistant", color=0x00ff00)
    embed.add_field(name="❓ Pertanyaan", value=f"*\"{pertanyaan}\"*", inline=False)
    embed.add_field(name="💬 Jawaban AI", value=ai_response, inline=False)
    embed.set_footer(text="AI masih dalam pengembangan, jawaban mungkin tidak selalu akurat")
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# Check functions untuk sleep
def check_sleep_and_work_before_command(func):
    """Decorator untuk cek sleep status sebelum menjalankan command"""
    async def wrapper(ctx, *args, **kwargs):
        if hasattr(ctx, 'author'):
            user_id = str(ctx.author.id)
            if user_id in data:
                if check_sleep_status(user_id):
                    await ctx.send("😴 Kamu sedang tidur! Gunakan `!bangun` untuk bangun dulu.")
                    return
        return await func(ctx, *args, **kwargs)
    return wrapper

# !menusleep - Menu sistem tidur dan AI
@bot.command()
async def menusleep(ctx):
    embed = discord.Embed(title="😴 Menu Tidur & AI Chat", color=0x3498db)
    
    embed.add_field(
        name="😴 **Sistem Tidur**",
        value="`!tidur [jam]` - Tidur selama beberapa jam\n`!bangun` - Bangun dari tidur\n`!statustidur` - Cek status tidur",
        inline=False
    )
    
    embed.add_field(
        name="🤖 **AI Chat**",
        value="`!tanya [pertanyaan]` - Tanya apa saja ke AI\n💡 AI bisa jawab tips game, motivasi, atau ngobrol biasa",
        inline=False
    )
    
    embed.add_field(
        name="💤 **Fitur Tidur**",
        value="• Bisa tidur kapan saja (1-24 jam)\n• Saat tidur tidak bisa pakai command lain\n• Tidur memulihkan kesehatan dan mood\n• Tidur 6+ jam dapat XP bonus\n• Bangun otomatis atau manual",
        inline=False
    )
    
    embed.add_field(
        name="🤖 **Fitur AI**",
        value="• Respons otomatis berdasarkan pertanyaan\n• Tips dan trik bermain game\n• Motivasi dan semangat\n• Cooldown 30 detik per pertanyaan\n• Tidak bisa digunakan saat tidur",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)



# !statustidur - Cek status tidur
@bot.command()
async def statustidur(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(user_id)
    init_sleep_system()
    
    sleep_data = data[user_id]["sleep_status"]
    
    if not sleep_data["is_sleeping"]:
        total_hours = sleep_data["total_sleep_time"] / 3600
        embed = discord.Embed(title=f"🌅 Status Tidur {member.display_name}", color=0xffd700)
        embed.add_field(name="💤 Status", value="Bangun/Tidak tidur", inline=True)
        embed.add_field(name="📊 Total Tidur", value=f"{total_hours:.1f} jam", inline=True)
        embed.add_field(name="😊 Kondisi", value="Siap beraktivitas!", inline=True)
    else:
        current_time = int(time.time())
        sleep_start = sleep_data["sleep_start"]
        planned_duration = sleep_data["sleep_duration"]
        elapsed_time = current_time - sleep_start
        remaining_time = (planned_duration * 3600) - elapsed_time
        
        elapsed_hours = elapsed_time / 3600
        remaining_hours = max(0, remaining_time / 3600)
        
        embed = discord.Embed(title=f"😴 Status Tidur {member.display_name}", color=0x3498db)
        embed.add_field(name="💤 Status", value="Sedang tidur", inline=True)
        embed.add_field(name="⏰ Sudah tidur", value=f"{elapsed_hours:.1f} jam", inline=True)
        embed.add_field(name="⏰ Sisa waktu", value=f"{remaining_hours:.1f} jam", inline=True)
        
        if remaining_time <= 0:
            embed.add_field(name="🌅 Info", value="Sudah waktunya bangun! Gunakan `!bangun`", inline=False)
        else:
            wake_time = current_time + remaining_time
            wake_time_str = datetime.fromtimestamp(wake_time).strftime("%H:%M")
            embed.add_field(name="⏰ Bangun otomatis", value=wake_time_str, inline=False)
    
    await ctx.send(embed=embed)

# !menuadmin - Menu admin commands
@bot.command()
async def menuadmin(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Menu ini hanya untuk admin.")
        return
    
    embed = discord.Embed(title="🔧 Menu Admin Commands", color=0xe74c3c)
    
    embed.add_field(
        name="🔔 **Sistem Notifikasi**",
        value="`!ceknotif` - Trigger manual cek notifikasi utang\n`!cekkondisi` - Trigger manual cek kondisi kesehatan",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ **Sistem Otomatis**",
        value="• Notifikasi utang: Setiap 6 jam\n• Notifikasi kondisi: Setiap 2 jam\n• Life effects: Real-time per command",
        inline=False
    )
    
    embed.add_field(
        name="📊 **Status Bot**",
        value="• Cooldown istirahat: 2 jam\n• Cooldown kerja freelance: 1 jam\n• Cooldown notifikasi: 2 jam per jenis",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# !pergi - Berpindah ke building/lokasi lain
@bot.command()
async def pergi(ctx, building_id=None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_building_system()
    
    if building_id is None:
        embed = discord.Embed(title="🚶 Sistem Perpindahan Lokasi", color=0x3498db)
        embed.add_field(name="🏙️ Cara Pergi", value="`!pergi [building_id]` - Pergi ke building tertentu\n`!pergi [city_name]` - Pergi ke kota lain", inline=False)
        
        current_location = data[user_id]["location"]
        current_city = current_location["current_city"]
        current_building = current_location.get("current_building")
        
        embed.add_field(name="📍 Lokasi Sekarang", value=f"Kota: {cities[current_city]['nama']}", inline=True)
        
        if current_building and current_building in cities[current_city]["buildings"]:
            building_name = cities[current_city]["buildings"][current_building]["nama"]
            embed.add_field(name="🏢 Building", value=building_name, inline=True)
        else:
            embed.add_field(name="🏢 Building", value="Area umum", inline=True)
        
        # Show buildings in current city
        buildings_text = ""
        for bid, building in cities[current_city]["buildings"].items():
            buildings_text += f"• {building['nama']} (ID: {bid})\n"
        
        embed.add_field(name=f"🏢 Buildings di {cities[current_city]['nama']}", value=buildings_text[:1024], inline=False)
        
        await ctx.send(embed=embed)
        return
    
    # Cek apakah itu nama kota
    target_city = None
    for city_key, city_data in cities.items():
        if city_key.lower() == building_id.lower() or city_data["nama"].lower() == building_id.lower():
            target_city = city_key
            break
    
    if target_city:
        # Pergi ke kota lain
        old_city = data[user_id]["location"]["current_city"]
        data[user_id]["location"]["current_city"] = target_city
        data[user_id]["location"]["current_building"] = None  # Reset building
        
        travel_cost = 50000  # Biaya perjalanan antar kota
        if data[user_id]["uang"] < travel_cost:
            await ctx.send(f"❌ Biaya perjalanan ke {cities[target_city]['nama']}: Rp{travel_cost:,}")
            return
        
        data[user_id]["uang"] -= travel_cost
        
        embed = discord.Embed(title="✈️ Perjalanan Berhasil!", color=0x00ff00)
        embed.add_field(name="📍 Dari", value=cities[old_city]["nama"], inline=True)
        embed.add_field(name="📍 Ke", value=cities[target_city]["nama"], inline=True)
        embed.add_field(name="💰 Biaya", value=f"Rp{travel_cost:,}", inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
        
    else:
        # Cek apakah itu building ID
        current_city = data[user_id]["location"]["current_city"]
        target_building = None
        
        # Cari building di kota saat ini
        for bid, building in cities[current_city]["buildings"].items():
            if bid.lower() == building_id.lower():
                target_building = bid
                break
        
        if not target_building:
            await ctx.send(f"❌ Building '{building_id}' tidak ditemukan di {cities[current_city]['nama']}.\nGunakan `!pergi` untuk melihat daftar building.")
            return
        
        # Pergi ke building
        building_data = cities[current_city]["buildings"][target_building]
        travel_cost = building_data.get("biaya_transport", 5000)
        
        if data[user_id]["uang"] < travel_cost:
            await ctx.send(f"❌ Biaya transportasi ke {building_data['nama']}: Rp{travel_cost:,}")
            return
        
        data[user_id]["uang"] -= travel_cost
        data[user_id]["location"]["current_building"] = target_building
        
        embed = discord.Embed(title="🚗 Sampai di Tujuan!", color=0x00ff00)
        embed.add_field(name="🏢 Building", value=building_data["nama"], inline=True)
        embed.add_field(name="📍 Alamat", value=building_data["alamat"], inline=True)
        embed.add_field(name="💰 Biaya Transport", value=f"Rp{travel_cost:,}", inline=True)
        embed.add_field(name="🕒 Jam Operasional", value=building_data["jam_operasional"], inline=True)
        
        if "facilities" in building_data:
            facilities_text = ", ".join(building_data["facilities"][:5])
            embed.add_field(name="🏪 Fasilitas", value=facilities_text, inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    save_data(data)

# !halo (keep original command)
@bot.command()
async def halo(ctx):
    await ctx.send("Halo juga! Aku bot kerja roleplay 🚀\n\n🆕 **Fitur baru:** Sistem kehidupan realistis!\nCek kondisi kamu dengan `!kondisi` dan jaga kesehatan, kelaparan, dan kehausan!\n\n📋 **Lihat semua fitur:** `!menu`")

# ===== REAL ESTATE SYSTEM =====

# Database properti
properties = {
    "rumah_sederhana": {
        "nama": "Rumah Sederhana",
        "harga_base": 15000000,
        "rental_income": 500000,  # Per bulan
        "maintenance_cost": 50000,  # Per bulan
        "kategori": "residential",
        "deskripsi": "Rumah sederhana dengan 2 kamar tidur dan 1 kamar mandi"
    },
    "rumah_mewah": {
        "nama": "Rumah Mewah",
        "harga_base": 50000000,
        "rental_income": 2000000,
        "maintenance_cost": 200000,
        "kategori": "residential",
        "deskripsi": "Rumah mewah dengan 5 kamar tidur, kolam renang, dan garasi"
    },
    "apartemen_studio": {
        "nama": "Apartemen Studio",
        "harga_base": 8000000,
        "rental_income": 300000,
        "maintenance_cost": 30000,
        "kategori": "residential",
        "deskripsi": "Apartemen studio modern di pusat kota"
    },
    "villa_pantai": {
        "nama": "Villa Pantai",
        "harga_base": 100000000,
        "rental_income": 5000000,
        "maintenance_cost": 500000,
        "kategori": "luxury",
        "deskripsi": "Villa mewah di tepi pantai dengan pemandangan laut"
    },
    "penthouse": {
        "nama": "Penthouse",
        "harga_base": 200000000,
        "rental_income": 8000000,
        "maintenance_cost": 800000,
        "kategori": "luxury",
        "deskripsi": "Penthouse eksklusif di gedung tertinggi kota"
    },
    "toko_kecil": {
        "nama": "Toko Kecil",
        "harga_base": 25000000,
        "rental_income": 1000000,
        "maintenance_cost": 100000,
        "kategori": "commercial",
        "deskripsi": "Toko kecil di area komersial strategis"
    },
    "gedung_kantor": {
        "nama": "Gedung Kantor",
        "harga_base": 300000000,
        "rental_income": 15000000,
        "maintenance_cost": 1500000,
        "kategori": "commercial",
        "deskripsi": "Gedung kantor 10 lantai di pusat bisnis"
    },
    "mall_kecil": {
        "nama": "Mall Kecil",
        "harga_base": 500000000,
        "rental_income": 25000000,
        "maintenance_cost": 2500000,
        "kategori": "commercial",
        "deskripsi": "Mall dengan 50 toko dan food court"
    },
    "tanah_kosong": {
        "nama": "Tanah Kosong",
        "harga_base": 5000000,
        "rental_income": 100000,
        "maintenance_cost": 10000,
        "kategori": "land",
        "deskripsi": "Tanah kosong siap bangun dengan sertifikat lengkap"
    },
    "kebun_sawit": {
        "nama": "Kebun Sawit",
        "harga_base": 20000000,
        "rental_income": 800000,
        "maintenance_cost": 150000,
        "kategori": "agricultural",
        "deskripsi": "Kebun sawit produktif seluas 2 hektar"
    }
}

# ===== INTERACTIVE WORK SYSTEM VIA DM =====

# Initialize work orders system
def init_work_orders():
    if "work_orders" not in data:
        data["work_orders"] = {}
    if "active_workers" not in data:
        data["active_workers"] = {}
    save_data(data)

# Database pekerjaan interaktif
interactive_jobs = {
    "pegawai_toko": {
        "nama": "Pegawai Toko",
        "description": "Melayani pembeli secara langsung via DM",
        "base_commission": 0.05,  # 5% komisi dari penjualan
        "work_type": "sales",
        "dm_required": True,
        "level_required": 3
    },
    "kasir": {
        "nama": "Kasir",
        "description": "Memproses transaksi pembayaran via DM",
        "base_commission": 0.03,  # 3% komisi
        "work_type": "cashier",
        "dm_required": True,
        "level_required": 3
    },
    "barista": {
        "nama": "Barista",
        "description": "Membuat dan menyajikan kopi via DM",
        "base_commission": 0.08,  # 8% komisi + tips
        "work_type": "service",
        "dm_required": True,
        "level_required": 4
    },
    "customer_service": {
        "nama": "Customer Service",
        "description": "Menangani keluhan dan bantuan pelanggan",
        "base_commission": 0.04,
        "work_type": "support",
        "dm_required": True,
        "level_required": 6
    },
    "delivery": {
        "nama": "Kurir Delivery",
        "description": "Mengantar pesanan ke customer",
        "base_commission": 0.1,
        "work_type": "delivery",
        "dm_required": True,
        "level_required": 5
    },
    "teknisi": {
        "nama": "Teknisi Repair",
        "description": "Memperbaiki barang elektronik via konsultasi DM",
        "base_commission": 0.15,
        "work_type": "repair",
        "dm_required": True,
        "level_required": 10
    }
}

# Generate work orders (customer requests)
async def generate_work_order(job_type, customer_id=None, order_details=None):
    """Generate work order untuk pekerjaan interaktif"""
    if customer_id is None:
        # Generate NPC customer
        npc_names = ["Budi", "Sari", "Agus", "Rina", "Doni", "Maya", "Rudi", "Tina", "Adi", "Lisa"]
        customer_name = random.choice(npc_names)
        customer_id = f"npc_{random.randint(1000, 9999)}"
        is_npc = True
    else:
        customer_name = "Real Player"
        is_npc = False
    
    order_id = f"order_{job_type}_{int(time.time())}_{random.randint(100, 999)}"
    
    # Generate order details berdasarkan job type
    if job_type == "pegawai_toko":
        items_to_buy = random.choice([
            {"item": "roti", "qty": 2, "unit_price": 5000},
            {"item": "nasi", "qty": 1, "unit_price": 15000},
            {"item": "air_mineral", "qty": 3, "unit_price": 3000},
            {"item": "kopi", "qty": 1, "unit_price": 15000},
            {"item": "energy_drink", "qty": 2, "unit_price": 25000}
        ])
        total_price = items_to_buy["qty"] * items_to_buy["unit_price"]
        
        order_details = {
            "customer_name": customer_name,
            "items": [items_to_buy],
            "total_amount": total_price,
            "location": random.choice(["Mall Jakarta", "Supermarket Bandung", "Mini Market Surabaya"]),
            "urgency": random.choice(["normal", "urgent"]),
            "special_request": random.choice([None, "Tolong pilihkan yang fresh", "Cari yang expired paling lama", "Bungkus rapi ya"])
        }
    
    elif job_type == "kasir":
        total_items = random.randint(3, 8)
        total_amount = random.randint(50000, 200000)
        payment_method = random.choice(["cash", "card", "ewallet"])
        
        order_details = {
            "customer_name": customer_name,
            "total_items": total_items,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "has_discount": random.choice([True, False]),
            "discount_amount": random.randint(5000, 20000) if random.choice([True, False]) else 0
        }
    
    elif job_type == "barista":
        coffee_orders = [
            {"drink": "Espresso", "price": 25000, "difficulty": "medium"},
            {"drink": "Cappuccino", "price": 30000, "difficulty": "medium"},
            {"drink": "Latte", "price": 35000, "difficulty": "easy"},
            {"drink": "Americano", "price": 20000, "difficulty": "easy"},
            {"drink": "Frappuccino", "price": 45000, "difficulty": "hard"},
            {"drink": "Matcha Latte", "price": 40000, "difficulty": "hard"}
        ]
        coffee = random.choice(coffee_orders)
        
        order_details = {
            "customer_name": customer_name,
            "drink": coffee["drink"],
            "price": coffee["price"],
            "difficulty": coffee["difficulty"],
            "size": random.choice(["Regular", "Large"]),
            "customization": random.choice([None, "Extra shot", "Less sugar", "Extra hot", "With oat milk"]),
            "tip_potential": random.randint(2000, 10000)
        }
    
    elif job_type == "delivery":
        delivery_distance = random.randint(2, 15)  # km
        base_fee = 5000
        distance_fee = delivery_distance * 1000
        total_fee = base_fee + distance_fee
        
        order_details = {
            "customer_name": customer_name,
            "pickup_location": random.choice(["Restoran A", "Toko B", "Pharmacy C"]),
            "delivery_address": f"Jl. {random.choice(['Sudirman', 'Thamrin', 'Gatot Subroto'])} No.{random.randint(1, 100)}",
            "distance": delivery_distance,
            "delivery_fee": total_fee,
            "item_type": random.choice(["Makanan", "Obat-obatan", "Barang elektronik"]),
            "urgency": random.choice(["normal", "express"]),
            "special_instruction": random.choice([None, "Jangan sampai tumpah", "Hubungi dulu sebelum antar", "Tinggal di security"])
        }
    
    elif job_type == "teknisi":
        devices = [
            {"device": "Smartphone", "problem": "Layar pecah", "repair_cost": 150000},
            {"device": "Laptop", "problem": "Tidak bisa boot", "repair_cost": 200000},
            {"device": "AC", "problem": "Tidak dingin", "repair_cost": 300000},
            {"device": "TV", "problem": "Gambar buram", "repair_cost": 250000},
            {"device": "Kulkas", "problem": "Tidak dingin", "repair_cost": 400000}
        ]
        repair_job = random.choice(devices)
        
        order_details = {
            "customer_name": customer_name,
            "device": repair_job["device"],
            "problem": repair_job["problem"],
            "repair_cost": repair_job["repair_cost"],
            "warranty": random.choice([True, False]),
            "urgency": random.choice(["normal", "urgent"]),
            "customer_budget": random.randint(100000, 500000)
        }
    
    # Save work order
    if "work_orders" not in data:
        data["work_orders"] = {}
    
    data["work_orders"][order_id] = {
        "job_type": job_type,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "is_npc": is_npc,
        "order_details": order_details,
        "status": "pending",  # pending, assigned, in_progress, completed, cancelled
        "worker_id": None,
        "worker_name": None,
        "created_time": int(time.time()),
        "assigned_time": None,
        "completed_time": None,
        "worker_rating": 0,
        "commission_earned": 0
    }
    
    save_data(data)
    return order_id, order_details

# !kerjadm - Command untuk shift kerja interaktif via DM
@bot.command()
async def kerjadm(ctx, job_type=None):
    """Mulai shift kerja interaktif via DM"""
    if ctx.guild is not None:
        await ctx.send("💼 **Kerja Interaktif hanya bisa di DM Bot!**\n\n💌 Kirim pesan langsung ke bot untuk mulai kerja:\n`/kerjadm [job_type]`\n\nContoh: `/kerjadm pegawai_toko`\n\n📋 Available jobs: pegawai_toko, kasir, barista, customer_service, delivery, teknisi")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_work_orders()
    
    if job_type is None:
        embed = discord.Embed(title="💼 Sistem Kerja Interaktif", color=0x3498db)
        embed.add_field(name="🏪 **Retail Jobs**", value="`/kerjadm pegawai_toko` - Melayani pembeli\n`/kerjadm kasir` - Proses pembayaran", inline=False)
        embed.add_field(name="☕ **Service Jobs**", value="`/kerjadm barista` - Buat kopi untuk customer\n`/kerjadm customer_service` - Handle keluhan", inline=False)
        embed.add_field(name="🚗 **Delivery Jobs**", value="`/kerjadm delivery` - Antar pesanan customer", inline=False)
        embed.add_field(name="🔧 **Technical Jobs**", value="`/kerjadm teknisi` - Repair barang elektronik", inline=False)
        embed.add_field(name="💡 **Cara Kerja**", value="• Mulai shift dengan command di atas\n• Terima work order via DM\n• Kerjakan secara real-time\n• Dapatkan komisi dari setiap transaksi\n• Rating dari customer mempengaruhi income", inline=False)
        await ctx.send(embed=embed)
        return
    
    if job_type not in interactive_jobs:
        await ctx.send("❌ Job type tidak tersedia. Gunakan `/kerjadm` untuk melihat daftar.")
        return
    
    job_info = interactive_jobs[job_type]
    level = calculate_level(data[user_id]["xp"])
    
    if level < job_info["level_required"]:
        await ctx.send(f"❌ Level kamu ({level}) belum cukup. Butuh minimal level {job_info['level_required']}.")
        return
    
    # Cek apakah user sudah dalam shift
    if "active_workers" not in data:
        data["active_workers"] = {}
    
    if user_id in data["active_workers"]:
        await ctx.send("❌ Kamu sedang dalam shift kerja. Selesaikan dulu dengan `/selesaishift`")
        return
    
    # Mulai shift
    data["active_workers"][user_id] = {
        "job_type": job_type,
        "shift_start": int(time.time()),
        "orders_completed": 0,
        "total_commission": 0,
        "current_order": None
    }
    
    save_data(data)
    
    embed = discord.Embed(title="💼 Shift Kerja Dimulai!", color=0x00ff00)
    embed.add_field(name="👔 Pekerjaan", value=job_info["nama"], inline=True)
    embed.add_field(name="💰 Komisi", value=f"{job_info['base_commission']*100}%", inline=True)
    embed.add_field(name="📋 Deskripsi", value=job_info["description"], inline=False)
    embed.add_field(name="⏰ Status", value="Menunggu work order...", inline=True)
    
    await ctx.send(embed=embed)
    
    # Generate work order langsung
    await asyncio.sleep(2)
    await generate_and_send_work_order(user_id, job_type)

async def generate_and_send_work_order(worker_id, job_type):
    """Generate dan kirim work order ke worker"""
    order_id, order_details = await generate_work_order(job_type)
    
    # Assign ke worker
    data["work_orders"][order_id]["worker_id"] = worker_id
    data["work_orders"][order_id]["status"] = "assigned"
    data["work_orders"][order_id]["assigned_time"] = int(time.time())
    
    # Update worker current order
    data["active_workers"][worker_id]["current_order"] = order_id
    
    save_data(data)
    
    # Send work order ke worker
    try:
        worker = bot.get_user(int(worker_id))
        if worker:
            embed = await create_work_order_embed(order_id, order_details, job_type)
            await worker.send(embed=embed)
    except:
        pass

async def create_work_order_embed(order_id, order_details, job_type):
    """Create embed untuk work order berdasarkan job type"""
    embed = discord.Embed(title="📋 NEW WORK ORDER", color=0xff9900)
    embed.add_field(name="🆔 Order ID", value=order_id[-8:], inline=True)
    embed.add_field(name="👤 Customer", value=order_details["customer_name"], inline=True)
    
    if job_type == "pegawai_toko":
        items_text = ""
        for item in order_details["items"]:
            items_text += f"• {item['item'].title()} x{item['qty']} - Rp{item['unit_price']:,}\n"
        
        embed.add_field(name="🛒 Items to Sell", value=items_text, inline=False)
        embed.add_field(name="💰 Total", value=f"Rp{order_details['total_amount']:,}", inline=True)
        embed.add_field(name="📍 Location", value=order_details["location"], inline=True)
        
        if order_details["special_request"]:
            embed.add_field(name="📝 Special Request", value=order_details["special_request"], inline=False)
        
        embed.add_field(name="💼 Your Task", value="1. Greet customer\n2. Show item details & prices\n3. Process the sale\n4. Calculate total with any discounts\n5. Complete transaction", inline=False)
        embed.add_field(name="💬 Commands", value="`/mulai [order_id]` - Start serving customer\n`/selesai [order_id]` - Complete order", inline=False)
    
    elif job_type == "barista":
        embed.add_field(name="☕ Order", value=f"{order_details['drink']} ({order_details['size']})", inline=True)
        embed.add_field(name="💰 Price", value=f"Rp{order_details['price']:,}", inline=True)
        embed.add_field(name="⭐ Difficulty", value=order_details["difficulty"].title(), inline=True)
        
        if order_details["customization"]:
            embed.add_field(name="🎯 Customization", value=order_details["customization"], inline=True)
        
        embed.add_field(name="💡 Tip Potential", value=f"Rp{order_details['tip_potential']:,}", inline=True)
        embed.add_field(name="💼 Your Task", value="1. Confirm order details\n2. Prepare the drink\n3. Explain the process\n4. Serve with care\n5. Ask for feedback", inline=False)
    
    elif job_type == "delivery":
        embed.add_field(name="📦 Pickup", value=order_details["pickup_location"], inline=True)
        embed.add_field(name="📍 Delivery", value=order_details["delivery_address"], inline=True)
        embed.add_field(name="📏 Distance", value=f"{order_details['distance']} km", inline=True)
        embed.add_field(name="💰 Fee", value=f"Rp{order_details['delivery_fee']:,}", inline=True)
        embed.add_field(name="📦 Item", value=order_details["item_type"], inline=True)
        
        if order_details["special_instruction"]:
            embed.add_field(name="📝 Instructions", value=order_details["special_instruction"], inline=False)
        
        embed.add_field(name="💼 Your Task", value="1. Confirm pickup location\n2. Navigate to destination\n3. Contact customer if needed\n4. Deliver safely\n5. Get confirmation", inline=False)
    
    # Add urgency indicator
    if order_details.get("urgency") == "urgent":
        embed.add_field(name="🚨 URGENT", value="This order needs immediate attention!", inline=False)
    
    return embed

# Command untuk memulai work order
@bot.command()
async def mulai(ctx, order_id=None):
    """Mulai mengerjakan work order (DM only)"""
    if ctx.guild is not None:
        await ctx.send("💼 Command ini hanya bisa digunakan di DM saat sedang kerja!")
        return
    
    if not order_id:
        await ctx.send("❌ Masukkan Order ID: `/mulai [order_id]`")
        return
    
    user_id = str(ctx.author.id)
    
    if user_id not in data.get("active_workers", {}):
        await ctx.send("❌ Kamu tidak sedang dalam shift kerja.")
        return
    
    # Find order
    target_order = None
    full_order_id = None
    
    for o_id, order_data in data.get("work_orders", {}).items():
        if o_id.endswith(order_id) or o_id[-8:] == order_id:
            if order_data["worker_id"] == user_id:
                target_order = order_data
                full_order_id = o_id
                break
    
    if not target_order:
        await ctx.send(f"❌ Order `{order_id}` tidak ditemukan atau bukan assignment kamu.")
        return
    
    if target_order["status"] != "assigned":
        await ctx.send("❌ Order ini sudah dikerjakan atau selesai.")
        return
    
    # Start working on order
    data["work_orders"][full_order_id]["status"] = "in_progress"
    save_data(data)
    
    job_type = target_order["job_type"]
    order_details = target_order["order_details"]
    
    # Create interactive work session
    embed = discord.Embed(title="💼 WORK SESSION STARTED", color=0x00ff00)
    embed.add_field(name="🆔 Order ID", value=order_id, inline=True)
    embed.add_field(name="👤 Customer", value=order_details["customer_name"], inline=True)
    
    # Job-specific work simulation
    if job_type == "pegawai_toko":
        embed.add_field(name="🛒 Serving Customer", value="Customer approaches your counter...", inline=False)
        embed.add_field(name="💬 Customer says:", value=f"\"Hi, I'd like to buy {order_details['items'][0]['item']} please. How much is it?\"", inline=False)
        embed.add_field(name="💼 What do you do?", value="Reply dengan:\n`Harga [item] adalah Rp[harga], apakah mau ambil berapa?`", inline=False)
    
    elif job_type == "barista":
        embed.add_field(name="☕ Making Coffee", value="Customer orders a coffee...", inline=False)
        embed.add_field(name="💬 Customer says:", value=f"\"Can I get a {order_details['drink']} please? {order_details.get('customization', '')}\"", inline=False)
        embed.add_field(name="💼 What do you do?", value="Reply dengan:\n`Baik, saya akan buatkan [drink_name]. Mohon tunggu sebentar ya.`", inline=False)
    
    embed.add_field(name="⏰ Time Limit", value="15 menit untuk menyelesaikan", inline=True)
    embed.add_field(name="💰 Commission", value=f"Rp{int(order_details.get('total_amount', order_details.get('price', order_details.get('delivery_fee', 50000))) * interactive_jobs[job_type]['base_commission']):,}", inline=True)
    
    await ctx.send(embed=embed)

# Command untuk menyelesaikan work order
@bot.command()
async def selesai(ctx, order_id=None, *, feedback=None):
    """Selesaikan work order (DM only)"""
    if ctx.guild is not None:
        await ctx.send("💼 Command ini hanya bisa digunakan di DM saat sedang kerja!")
        return
    
    if not order_id:
        await ctx.send("❌ Format: `/selesai [order_id] [feedback_to_customer]`")
        return
    
    user_id = str(ctx.author.id)
    
    # Find and complete order
    target_order = None
    full_order_id = None
    
    for o_id, order_data in data.get("work_orders", {}).items():
        if o_id.endswith(order_id) or o_id[-8:] == order_id:
            if order_data["worker_id"] == user_id and order_data["status"] == "in_progress":
                target_order = order_data
                full_order_id = o_id
                break
    
    if not target_order:
        await ctx.send(f"❌ Order `{order_id}` tidak ditemukan atau belum dimulai.")
        return
    
    # Complete order
    job_type = target_order["job_type"]
    order_details = target_order["order_details"]
    
    # Calculate commission
    base_amount = order_details.get("total_amount", order_details.get("price", order_details.get("delivery_fee", 50000)))
    commission_rate = interactive_jobs[job_type]["base_commission"]
    commission = int(base_amount * commission_rate)
    
    # Customer satisfaction (random + performance)
    satisfaction = random.randint(60, 100)
    if feedback and len(feedback) > 20:  # Good feedback = better rating
        satisfaction += 10
    
    # Bonus for high satisfaction
    if satisfaction >= 90:
        commission = int(commission * 1.5)  # 50% bonus
        tip = random.randint(5000, 15000)
        commission += tip
    elif satisfaction >= 80:
        commission = int(commission * 1.2)  # 20% bonus
    
    # Pay worker
    data[user_id]["uang"] += commission
    data[user_id]["xp"] += 20
    
    # Update order
    data["work_orders"][full_order_id]["status"] = "completed"
    data["work_orders"][full_order_id]["completed_time"] = int(time.time())
    data["work_orders"][full_order_id]["worker_rating"] = satisfaction
    data["work_orders"][full_order_id]["commission_earned"] = commission
    
    # Update worker stats
    data["active_workers"][user_id]["orders_completed"] += 1
    data["active_workers"][user_id]["total_commission"] += commission
    data["active_workers"][user_id]["current_order"] = None
    
    save_data(data)
    
    embed = discord.Embed(title="✅ ORDER COMPLETED!", color=0x00ff00)
    embed.add_field(name="🆔 Order ID", value=order_id, inline=True)
    embed.add_field(name="⭐ Customer Rating", value=f"{satisfaction}/100", inline=True)
    embed.add_field(name="💰 Commission Earned", value=f"Rp{commission:,}", inline=True)
    embed.add_field(name="⭐ XP Gained", value="+20", inline=True)
    
    if feedback:
        embed.add_field(name="💬 Your Service", value=feedback[:200], inline=False)
    
    # Customer feedback simulation
    customer_responses = {
        90: ["Excellent service! Very professional!", "Amazing quality, will come back!", "Perfect execution, thank you!"],
        80: ["Good service, satisfied with the result", "Nice work, keep it up!", "Decent quality, thanks!"],
        70: ["Okay service, could be better", "Average performance", "It's fine, nothing special"],
        60: ["Below expectations", "Need improvement", "Not very satisfied"]
    }
    
    response_key = min([k for k in customer_responses.keys() if satisfaction >= k], default=60)
    customer_feedback = random.choice(customer_responses[response_key])
    
    embed.add_field(name="💬 Customer Feedback", value=f"\"{customer_feedback}\"", inline=False)
    
    await ctx.send(embed=embed)
    
    # Generate next work order after 30 seconds
    await asyncio.sleep(30)
    if user_id in data.get("active_workers", {}):
        await generate_and_send_work_order(user_id, job_type)

# Command untuk selesai shift
@bot.command()
async def selesaishift(ctx):
    """Selesai shift kerja (DM only)"""
    if ctx.guild is not None:
        await ctx.send("💼 Command ini hanya bisa digunakan di DM saat sedang kerja!")
        return
    
    user_id = str(ctx.author.id)
    
    if user_id not in data.get("active_workers", {}):
        await ctx.send("❌ Kamu tidak sedang dalam shift kerja.")
        return
    
    worker_data = data["active_workers"][user_id]
    shift_duration = int(time.time()) - worker_data["shift_start"]
    
    # End shift
    del data["active_workers"][user_id]
    save_data(data)
    
    embed = discord.Embed(title="🏁 SHIFT ENDED", color=0xff9900)
    embed.add_field(name="⏰ Duration", value=f"{shift_duration//3600}h {(shift_duration%3600)//60}m", inline=True)
    embed.add_field(name="📦 Orders Completed", value=worker_data["orders_completed"], inline=True)
    embed.add_field(name="💰 Total Commission", value=f"Rp{worker_data['total_commission']:,}", inline=True)
    
    if worker_data["orders_completed"] > 0:
        avg_commission = worker_data["total_commission"] // worker_data["orders_completed"]
        embed.add_field(name="📊 Avg per Order", value=f"Rp{avg_commission:,}", inline=True)
    
    embed.add_field(name="🎉 Performance", value="Great work! Keep it up!", inline=False)
    
    await ctx.send(embed=embed)

# Initialize building system untuk location tracking
def init_building_system():
    """Initialize building system untuk semua user"""
    for user_id in data:
        if user_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings"]:
            continue
        if "location" not in data[user_id]:
            data[user_id]["location"] = {
                "current_city": "jakarta",  # Default city
                "current_building": None,   # None = area umum
                "travel_history": []
            }
    save_data(data)

# Initialize real estate system
def init_real_estate():
    if "real_estate" not in data:
        data["real_estate"] = {
            "market": {},  # Property listings
            "auctions": {},  # Active auctions
            "rentals": {},  # Active rental agreements
            "agents": {},  # Real estate agents
            "market_trends": {
                "last_update": int(time.time()),
                "price_multiplier": 1.0
            }
        }
    
    # Initialize user real estate data
    for user_id in data:
        if user_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings"]:
            continue
        if "real_estate_portfolio" not in data[user_id]:
            data[user_id]["real_estate_portfolio"] = {
                "owned_properties": {},  # property_id: property_data
                "rented_properties": {},  # property_id: rental_data
                "total_value": 0,
                "monthly_income": 0,
                "monthly_expenses": 0,
                "agent_stats": {
                    "is_agent": False,
                    "license_date": 0,
                    "sales_count": 0,
                    "total_commission": 0,
                    "rating": 5.0
                }
            }
    
    save_data(data)

# !property - Lihat pasar properti
@bot.command()
async def property(ctx, kategori=None):
    init_real_estate()
    
    if kategori == "market":
        # Lihat property yang dijual player
        if not data["real_estate"]["market"]:
            await ctx.send("🏠 Tidak ada properti yang dijual di pasar saat ini.")
            return
        
        embed = discord.Embed(title="🏠 Pasar Properti", color=0x2ecc71)
        
        for prop_id, listing in list(data["real_estate"]["market"].items())[:10]:
            seller_name = "Unknown"
            try:
                seller = bot.get_user(int(listing["seller_id"]))
                seller_name = seller.display_name if seller else f"User {listing['seller_id'][:4]}..."
            except:
                pass
            
            embed.add_field(
                name=f"🏘️ {listing['property_name']}",
                value=f"💰 Rp{listing['price']:,}\n👤 {seller_name}\n🆔 {prop_id[-8:]}\n📅 {int((int(time.time()) - listing['listed_date']) / 86400)} hari lalu",
                inline=True
            )
        
        embed.set_footer(text="!buyhouse [property_id] untuk membeli")
        await ctx.send(embed=embed)
        return
    
    # Lihat katalog properti baru
    embed = discord.Embed(title="🏠 Katalog Properti", color=0x3498db)
    
    # Filter berdasarkan kategori
    if kategori:
        filtered_props = {k: v for k, v in properties.items() if v["kategori"] == kategori.lower()}
        if not filtered_props:
            await ctx.send(f"❌ Kategori '{kategori}' tidak ditemukan. Kategori: residential, commercial, luxury, land, agricultural")
            return
    else:
        filtered_props = properties
    
    # Hitung market price dengan trend
    market_data = data["real_estate"]["market_trends"]
    price_multiplier = market_data["price_multiplier"]
    
    for prop_key, prop_data in list(filtered_props.items())[:15]:
        market_price = int(prop_data["harga_base"] * price_multiplier)
        monthly_profit = prop_data["rental_income"] - prop_data["maintenance_cost"]
        
        embed.add_field(
            name=f"🏘️ {prop_data['nama']}",
            value=f"💰 Rp{market_price:,}\n💵 Profit: Rp{monthly_profit:,}/bulan\n🏷️ {prop_data['kategori'].title()}\n🆔 {prop_key}",
            inline=True
        )
    
    embed.add_field(
        name="📊 Market Trend", 
        value=f"Multiplier: {price_multiplier:.2f}x\n{'📈 Bullish' if price_multiplier > 1.0 else '📉 Bearish' if price_multiplier < 1.0 else '➡️ Stable'}", 
        inline=False
    )
    embed.set_footer(text="!buyhouse [property_key] | !property market | Kategori: residential, commercial, luxury, land, agricultural")
    await ctx.send(embed=embed)

# !buyhouse - Beli properti
@bot.command()
async def buyhouse(ctx, property_key=None):
    if not property_key:
        await ctx.send("🏠 **Cara Beli Properti:**\n`!buyhouse [property_key]` - Beli dari katalog\n`!buyhouse [property_id]` - Beli dari player\n\n📋 `!property` untuk lihat katalog\n`!property market` untuk pasar player")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_real_estate()
    
    # Cek apakah ini property dari katalog atau dari player
    if property_key in properties:
        # Beli dari katalog (properti baru)
        prop_data = properties[property_key]
        market_price = int(prop_data["harga_base"] * data["real_estate"]["market_trends"]["price_multiplier"])
        
        if data[user_id]["uang"] < market_price:
            await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{market_price:,}")
            return
        
        # Generate property ID
        property_id = f"prop_{user_id}_{int(time.time())}"
        
        # Process purchase
        data[user_id]["uang"] -= market_price
        data[user_id]["real_estate_portfolio"]["owned_properties"][property_id] = {
            "property_type": property_key,
            "property_name": prop_data["nama"],
            "purchase_price": market_price,
            "purchase_date": int(time.time()),
            "current_value": market_price,
            "rental_status": "vacant",  # vacant, rented, for_sale
            "rental_income": prop_data["rental_income"],
            "maintenance_cost": prop_data["maintenance_cost"],
            "total_income": 0,
            "condition": 100  # 0-100
        }
        
        # Update portfolio stats
        portfolio = data[user_id]["real_estate_portfolio"]
        portfolio["total_value"] += market_price
        portfolio["monthly_expenses"] += prop_data["maintenance_cost"]
        
        embed = discord.Embed(title="🎉 Properti Berhasil Dibeli!", color=0x00ff00)
        embed.add_field(name="🏘️ Properti", value=prop_data["nama"], inline=True)
        embed.add_field(name="💰 Harga", value=f"Rp{market_price:,}", inline=True)
        embed.add_field(name="🆔 Property ID", value=property_id[-8:], inline=True)
        embed.add_field(name="💵 Potensi Rental", value=f"Rp{prop_data['rental_income']:,}/bulan", inline=True)
        embed.add_field(name="💸 Maintenance", value=f"Rp{prop_data['maintenance_cost']:,}/bulan", inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
        
    else:
        # Beli dari player (property market)
        target_listing = None
        full_prop_id = None
        
        for prop_id, listing in data["real_estate"]["market"].items():
            if prop_id.endswith(property_key) or prop_id[-8:] == property_key:
                target_listing = listing
                full_prop_id = prop_id
                break
        
        if not target_listing:
            await ctx.send(f"❌ Properti dengan ID `{property_key}` tidak ditemukan.")
            return
        
        if target_listing["seller_id"] == user_id:
            await ctx.send("❌ Kamu tidak bisa membeli properti sendiri.")
            return
        
        if data[user_id]["uang"] < target_listing["price"]:
            await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{target_listing['price']:,}")
            return
        
        # Process purchase from player
        seller_id = target_listing["seller_id"]
        commission = int(target_listing["price"] * 0.03)  # 3% commission
        seller_gets = target_listing["price"] - commission
        
        # Transfer property
        property_data = target_listing["property_data"].copy()
        property_data["previous_owner"] = seller_id
        
        data[user_id]["uang"] -= target_listing["price"]
        data[user_id]["real_estate_portfolio"]["owned_properties"][full_prop_id] = property_data
        
        # Pay seller
        if seller_id in data:
            data[seller_id]["uang"] += seller_gets
        
        # Remove from market
        del data["real_estate"]["market"][full_prop_id]
        
        embed = discord.Embed(title="🏠 Properti Berhasil Dibeli dari Player!", color=0x00ff00)
        embed.add_field(name="🏘️ Properti", value=target_listing["property_name"], inline=True)
        embed.add_field(name="💰 Harga", value=f"Rp{target_listing['price']:,}", inline=True)
        embed.add_field(name="👤 Dari", value=target_listing["seller_name"], inline=True)
        embed.add_field(name="💳 Commission", value=f"Rp{commission:,}", inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
        
        # Notifikasi ke seller
        if seller_id in data:
            pesan_notif = f"🏠 **Properti Terjual!**\n\n**{ctx.author.display_name}** membeli properti **{target_listing['property_name']}** dari kamu.\n\n💰 **Harga:** Rp{target_listing['price']:,}\n💳 **Diterima:** Rp{seller_gets:,} (setelah komisi 3%)\n\nSelamat! 🎉"
            await kirim_notif_dm(seller_id, pesan_notif)
    
    save_data(data)

# !sellhouse - Jual properti ke market
@bot.command()
async def sellhouse(ctx, property_id=None, harga: int = None):
    if not property_id or not harga:
        await ctx.send("🏠 **Cara Jual Properti:**\n`!sellhouse [property_id] [harga]` - Jual ke market\n\n📋 `!portfolio` untuk lihat property ID")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_real_estate()
    
    # Find property
    user_properties = data[user_id]["real_estate_portfolio"]["owned_properties"]
    target_property = None
    full_prop_id = None
    
    for prop_id, prop_data in user_properties.items():
        if prop_id.endswith(property_id) or prop_id[-8:] == property_id:
            target_property = prop_data
            full_prop_id = prop_id
            break
    
    if not target_property:
        await ctx.send(f"❌ Properti dengan ID `{property_id}` tidak ditemukan di portfolio kamu.")
        return
    
    if harga <= 0:
        await ctx.send("❌ Harga jual harus lebih dari 0.")
        return
    
    # Cek apakah properti sedang disewa
    if target_property["rental_status"] == "rented":
        await ctx.send("❌ Properti sedang disewa. Tunggu kontrak selesai atau putuskan kontrak dulu.")
        return
    
    # List ke market
    data["real_estate"]["market"][full_prop_id] = {
        "seller_id": user_id,
        "seller_name": ctx.author.display_name,
        "property_name": target_property["property_name"],
        "price": harga,
        "listed_date": int(time.time()),
        "property_data": target_property
    }
    
    # Remove from user's portfolio temporarily (until sold or delisted)
    del data[user_id]["real_estate_portfolio"]["owned_properties"][full_prop_id]
    
    embed = discord.Embed(title="🏠 Properti Listed untuk Dijual", color=0xff9900)
    embed.add_field(name="🏘️ Properti", value=target_property["property_name"], inline=True)
    embed.add_field(name="💰 Harga Jual", value=f"Rp{harga:,}", inline=True)
    embed.add_field(name="🆔 Property ID", value=property_id, inline=True)
    embed.add_field(name="📊 Market Value", value=f"Rp{target_property['current_value']:,}", inline=True)
    
    gain_loss = harga - target_property["purchase_price"]
    if gain_loss > 0:
        embed.add_field(name="📈 Potential Gain", value=f"+Rp{gain_loss:,}", inline=True)
    else:
        embed.add_field(name="📉 Potential Loss", value=f"Rp{abs(gain_loss):,}", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !rent - Sistem sewa properti
@bot.command()
async def rent(ctx, action=None, property_id=None, *, terms=None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_real_estate()
    
    if action is None:
        embed = discord.Embed(title="🏠 Sistem Rental Properti", color=0x9b59b6)
        embed.add_field(name="📋 **Commands**", value="`!rent out [property_id] [harga] [durasi]` - Sewakan properti\n`!rent seek [budget]` - Cari properti sewa\n`!rent [property_id]` - Sewa properti\n`!rent end [property_id]` - Akhiri kontrak", inline=False)
        embed.add_field(name="💡 **Info**", value="• Durasi sewa dalam bulan (1-12)\n• Deposit = 1 bulan sewa\n• Pemilik dapat passive income\n• Penyewa dapat tinggal di properti", inline=False)
        await ctx.send(embed=embed)
        return
    
    if action == "out":
        # Sewakan properti
        if not property_id or not terms:
            await ctx.send("❌ Format: `!rent out [property_id] [harga_sewa] [durasi_bulan]`")
            return
        
        terms_parts = terms.split()
        if len(terms_parts) < 2:
            await ctx.send("❌ Format: `!rent out [property_id] [harga_sewa] [durasi_bulan]`")
            return
        
        try:
            rental_price = int(terms_parts[0])
            duration = int(terms_parts[1])
        except ValueError:
            await ctx.send("❌ Harga dan durasi harus berupa angka.")
            return
        
        if duration < 1 or duration > 12:
            await ctx.send("❌ Durasi sewa harus 1-12 bulan.")
            return
        
        # Find property
        user_properties = data[user_id]["real_estate_portfolio"]["owned_properties"]
        target_property = None
        full_prop_id = None
        
        for prop_id, prop_data in user_properties.items():
            if prop_id.endswith(property_id) or prop_id[-8:] == property_id:
                target_property = prop_data
                full_prop_id = prop_id
                break
        
        if not target_property:
            await ctx.send(f"❌ Properti dengan ID `{property_id}` tidak ditemukan.")
            return
        
        if target_property["rental_status"] != "vacant":
            await ctx.send("❌ Properti sudah disewa atau sedang dijual.")
            return
        
        # List for rent
        rental_id = f"rent_{full_prop_id}_{int(time.time())}"
        data["real_estate"]["rentals"][rental_id] = {
            "landlord_id": user_id,
            "landlord_name": ctx.author.display_name,
            "property_id": full_prop_id,
            "property_name": target_property["property_name"],
            "rental_price": rental_price,
            "duration": duration,
            "deposit": rental_price,  # 1 bulan deposit
            "listed_date": int(time.time()),
            "status": "available",  # available, rented
            "tenant_id": None
        }
        
        target_property["rental_status"] = "for_rent"
        
        embed = discord.Embed(title="🏠 Properti Listed untuk Disewa", color=0x3498db)
        embed.add_field(name="🏘️ Properti", value=target_property["property_name"], inline=True)
        embed.add_field(name="💰 Sewa/Bulan", value=f"Rp{rental_price:,}", inline=True)
        embed.add_field(name="⏰ Durasi", value=f"{duration} bulan", inline=True)
        embed.add_field(name="💳 Deposit", value=f"Rp{rental_price:,}", inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    elif action == "seek":
        # Cari properti sewa
        try:
            budget = int(property_id) if property_id else 999999999
        except ValueError:
            budget = 999999999
        
        available_rentals = []
        for rental_id, rental_data in data["real_estate"]["rentals"].items():
            if rental_data["status"] == "available" and rental_data["rental_price"] <= budget:
                available_rentals.append((rental_id, rental_data))
        
        if not available_rentals:
            await ctx.send(f"🏠 Tidak ada properti sewa dalam budget Rp{budget:,}.")
            return
        
        embed = discord.Embed(title="🔍 Properti Sewa Tersedia", color=0x2ecc71)
        
        for rental_id, rental_data in available_rentals[:10]:
            embed.add_field(
                name=f"🏘️ {rental_data['property_name']}",
                value=f"💰 Rp{rental_data['rental_price']:,}/bulan\n👤 {rental_data['landlord_name']}\n⏰ {rental_data['duration']} bulan\n🆔 {rental_id[-8:]}",
                inline=True
            )
        
        embed.set_footer(text="!rent [rental_id] untuk menyewa")
        await ctx.send(embed=embed)
    
    elif action == "end":
        # Akhiri kontrak sewa
        # TODO: Implement rental termination
        await ctx.send("🚧 Fitur akhiri kontrak sedang dalam pengembangan.")
    
    else:
        # Sewa properti (action adalah rental_id)
        rental_id = action
        target_rental = None
        full_rental_id = None
        
        for r_id, rental_data in data["real_estate"]["rentals"].items():
            if r_id.endswith(rental_id) or r_id[-8:] == rental_id:
                target_rental = rental_data
                full_rental_id = r_id
                break
        
        if not target_rental:
            await ctx.send(f"❌ Rental dengan ID `{rental_id}` tidak ditemukan.")
            return
        
        if target_rental["status"] != "available":
            await ctx.send("❌ Properti sudah disewa.")
            return
        
        if target_rental["landlord_id"] == user_id:
            await ctx.send("❌ Kamu tidak bisa menyewa properti sendiri.")
            return
        
        total_cost = target_rental["rental_price"] + target_rental["deposit"]
        if data[user_id]["uang"] < total_cost:
            await ctx.send(f"❌ Uang tidak cukup. Butuh Rp{total_cost:,} (sewa + deposit).")
            return
        
        # Process rental
        data[user_id]["uang"] -= total_cost
        landlord_id = target_rental["landlord_id"]
        
        # Pay landlord
        if landlord_id in data:
            data[landlord_id]["uang"] += target_rental["rental_price"]
        
        # Update rental status
        target_rental["status"] = "rented"
        target_rental["tenant_id"] = user_id
        target_rental["tenant_name"] = ctx.author.display_name
        target_rental["contract_start"] = int(time.time())
        target_rental["contract_end"] = int(time.time()) + (target_rental["duration"] * 30 * 86400)
        
        # Update property status
        property_id = target_rental["property_id"]
        if landlord_id in data and property_id in data[landlord_id]["real_estate_portfolio"]["owned_properties"]:
            data[landlord_id]["real_estate_portfolio"]["owned_properties"][property_id]["rental_status"] = "rented"
        
        embed = discord.Embed(title="🎉 Properti Berhasil Disewa!", color=0x00ff00)
        embed.add_field(name="🏘️ Properti", value=target_rental["property_name"], inline=True)
        embed.add_field(name="💰 Sewa/Bulan", value=f"Rp{target_rental['rental_price']:,}", inline=True)
        embed.add_field(name="⏰ Durasi", value=f"{target_rental['duration']} bulan", inline=True)
        embed.add_field(name="👤 Pemilik", value=target_rental["landlord_name"], inline=True)
        embed.add_field(name="💳 Total Dibayar", value=f"Rp{total_cost:,}", inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
        
        # Notifikasi ke landlord
        if landlord_id in data:
            pesan_notif = f"🏠 **Properti Disewa!**\n\n**{ctx.author.display_name}** menyewa properti **{target_rental['property_name']}** dari kamu!\n\n💰 **Sewa:** Rp{target_rental['rental_price']:,}/bulan\n⏰ **Durasi:** {target_rental['duration']} bulan\n💵 **Diterima:** Rp{target_rental['rental_price']:,} (bulan pertama)\n\nSelamat! 🎉"
            await kirim_notif_dm(landlord_id, pesan_notif)
    
    save_data(data)

# !portfolio - Lihat portfolio real estate
@bot.command()
async def portfolio(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(user_id)
    init_real_estate()
    
    portfolio = data[user_id]["real_estate_portfolio"]
    
    if not portfolio["owned_properties"]:
        await ctx.send(f"🏠 {member.display_name} belum memiliki properti. Beli dengan `!buyhouse [property_key]`")
        return
    
    embed = discord.Embed(title=f"🏠 Portfolio Real Estate {member.display_name}", color=0x2ecc71)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    total_value = 0
    monthly_income = 0
    monthly_expenses = 0
    
    for prop_id, prop_data in list(portfolio["owned_properties"].items())[:10]:
        total_value += prop_data["current_value"]
        monthly_expenses += prop_data["maintenance_cost"]
        
        if prop_data["rental_status"] == "rented":
            monthly_income += prop_data["rental_income"]
            status_emoji = "🟢"
            status_text = "Disewa"
        elif prop_data["rental_status"] == "for_rent":
            status_emoji = "🟡"
            status_text = "Dicari Penyewa"
        elif prop_data["rental_status"] == "for_sale":
            status_emoji = "🔴"
            status_text = "Dijual"
        else:
            status_emoji = "⚪"
            status_text = "Kosong"
        
        embed.add_field(
            name=f"{status_emoji} {prop_data['property_name']}",
            value=f"💰 Rp{prop_data['current_value']:,}\n💵 Rp{prop_data['rental_income']:,}/bulan\n📋 {status_text}\n🆔 {prop_id[-8:]}",
            inline=True
        )
    
    net_income = monthly_income - monthly_expenses
    
    embed.add_field(name="💎 Total Value", value=f"Rp{total_value:,}", inline=True)
    embed.add_field(name="💚 Monthly Income", value=f"Rp{monthly_income:,}", inline=True)
    embed.add_field(name="💸 Monthly Expenses", value=f"Rp{monthly_expenses:,}", inline=True)
    embed.add_field(name="📊 Net Income", value=f"Rp{net_income:,}", inline=True)
    
    # ROI calculation
    total_invested = sum(prop["purchase_price"] for prop in portfolio["owned_properties"].values())
    if total_invested > 0:
        monthly_roi = (net_income / total_invested) * 100
        embed.add_field(name="📈 Monthly ROI", value=f"{monthly_roi:.2f}%", inline=True)
    
    await ctx.send(embed=embed)

# !auction - Sistem lelang properti
@bot.command()
async def auction(ctx, action=None, property_id=None, *, params=None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_real_estate()
    
    if action is None:
        # Lihat lelang aktif
        active_auctions = data["real_estate"]["auctions"]
        
        if not active_auctions:
            await ctx.send("🔨 Tidak ada lelang properti yang aktif saat ini.")
            return
        
        embed = discord.Embed(title="🔨 Lelang Properti Aktif", color=0xe74c3c)
        
        current_time = int(time.time())
        for auction_id, auction_data in list(active_auctions.items())[:10]:
            time_left = auction_data["end_time"] - current_time
            if time_left <= 0:
                continue
            
            hours_left = time_left // 3600
            current_bid = auction_data["current_bid"]
            
            embed.add_field(
                name=f"🏘️ {auction_data['property_name']}",
                value=f"💰 Bid: Rp{current_bid:,}\n👤 {auction_data['current_bidder_name'] if auction_data['current_bidder'] else 'Belum ada'}\n⏰ {hours_left} jam lagi\n🆔 {auction_id[-8:]}",
                inline=True
            )
        
        embed.set_footer(text="!auction bid [auction_id] [amount] untuk bid")
        await ctx.send(embed=embed)
        return
    
    if action == "create":
        # Buat lelang baru
        if not property_id or not params:
            await ctx.send("❌ Format: `!auction create [property_id] [starting_price] [duration_hours]`")
            return
        
        params_parts = params.split()
        if len(params_parts) < 2:
            await ctx.send("❌ Format: `!auction create [property_id] [starting_price] [duration_hours]`")
            return
        
        try:
            starting_price = int(params_parts[0])
            duration_hours = int(params_parts[1])
        except ValueError:
            await ctx.send("❌ Harga dan durasi harus berupa angka.")
            return
        
        if duration_hours < 1 or duration_hours > 168:  # Max 1 week
            await ctx.send("❌ Durasi lelang harus 1-168 jam (1 minggu).")
            return
        
        # Find property
        user_properties = data[user_id]["real_estate_portfolio"]["owned_properties"]
        target_property = None
        full_prop_id = None
        
        for prop_id, prop_data in user_properties.items():
            if prop_id.endswith(property_id) or prop_id[-8:] == property_id:
                target_property = prop_data
                full_prop_id = prop_id
                break
        
        if not target_property:
            await ctx.send(f"❌ Properti dengan ID `{property_id}` tidak ditemukan.")
            return
        
        if target_property["rental_status"] == "rented":
            await ctx.send("❌ Properti sedang disewa. Tunggu kontrak selesai.")
            return
        
        # Create auction
        auction_id = f"auction_{full_prop_id}_{int(time.time())}"
        data["real_estate"]["auctions"][auction_id] = {
            "seller_id": user_id,
            "seller_name": ctx.author.display_name,
            "property_id": full_prop_id,
            "property_name": target_property["property_name"],
            "property_data": target_property,
            "starting_price": starting_price,
            "current_bid": starting_price,
            "current_bidder": None,
            "current_bidder_name": None,
            "end_time": int(time.time()) + (duration_hours * 3600),
            "bid_history": [],
            "min_increment": max(100000, int(starting_price * 0.05))  # Min 5% or 100k
        }
        
        # Remove from user's portfolio temporarily
        del data[user_id]["real_estate_portfolio"]["owned_properties"][full_prop_id]
        
        embed = discord.Embed(title="🔨 Lelang Properti Dibuat!", color=0xe74c3c)
        embed.add_field(name="🏘️ Properti", value=target_property["property_name"], inline=True)
        embed.add_field(name="💰 Starting Price", value=f"Rp{starting_price:,}", inline=True)
        embed.add_field(name="⏰ Durasi", value=f"{duration_hours} jam", inline=True)
        embed.add_field(name="🆔 Auction ID", value=auction_id[-8:], inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    elif action == "bid":
        # Bid pada lelang
        if not property_id or not params:
            await ctx.send("❌ Format: `!auction bid [auction_id] [amount]`")
            return
        
        try:
            bid_amount = int(params)
        except ValueError:
            await ctx.send("❌ Jumlah bid harus berupa angka.")
            return
        
        # Find auction
        target_auction = None
        full_auction_id = None
        
        for auction_id, auction_data in data["real_estate"]["auctions"].items():
            if auction_id.endswith(property_id) or auction_id[-8:] == property_id:
                target_auction = auction_data
                full_auction_id = auction_id
                break
        
        if not target_auction:
            await ctx.send(f"❌ Lelang dengan ID `{property_id}` tidak ditemukan.")
            return
        
        # Check if auction still active
        current_time = int(time.time())
        if current_time >= target_auction["end_time"]:
            await ctx.send("❌ Lelang sudah berakhir.")
            return
        
        if target_auction["seller_id"] == user_id:
            await ctx.send("❌ Kamu tidak bisa bid pada lelang sendiri.")
            return
        
        # Check bid validity
        min_bid = target_auction["current_bid"] + target_auction["min_increment"]
        if bid_amount < min_bid:
            await ctx.send(f"❌ Bid minimum: Rp{min_bid:,}")
            return
        
        if data[user_id]["uang"] < bid_amount:
            await ctx.send(f"❌ Uang tidak cukup untuk bid Rp{bid_amount:,}")
            return
        
        # Update auction
        old_bidder = target_auction["current_bidder"]
        old_bid = target_auction["current_bid"]
        
        target_auction["current_bid"] = bid_amount
        target_auction["current_bidder"] = user_id
        target_auction["current_bidder_name"] = ctx.author.display_name
        target_auction["bid_history"].append({
            "bidder_id": user_id,
            "bidder_name": ctx.author.display_name,
            "amount": bid_amount,
            "timestamp": current_time
        })
        
        # Refund previous bidder
        if old_bidder and old_bidder in data:
            data[old_bidder]["uang"] += old_bid
        
        # Deduct from new bidder
        data[user_id]["uang"] -= bid_amount
        
        time_left = target_auction["end_time"] - current_time
        hours_left = time_left // 3600
        
        embed = discord.Embed(title="🔨 Bid Berhasil!", color=0x00ff00)
        embed.add_field(name="🏘️ Properti", value=target_auction["property_name"], inline=True)
        embed.add_field(name="💰 Bid Kamu", value=f"Rp{bid_amount:,}", inline=True)
        embed.add_field(name="⏰ Sisa Waktu", value=f"{hours_left} jam", inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
        
        # Notifikasi ke seller dan bidder sebelumnya
        seller_notif = f"🔨 **Bid Baru di Lelang!**\n\n**{ctx.author.display_name}** bid Rp{bid_amount:,} untuk properti **{target_auction['property_name']}**.\n\nLelang berakhir dalam {hours_left} jam!"
        await kirim_notif_dm(target_auction["seller_id"], seller_notif)
        
        if old_bidder and old_bidder in data:
            old_bidder_notif = f"🔨 **Bid Kamu Terlampaui!**\n\nBid kamu untuk **{target_auction['property_name']}** telah dilampaui oleh **{ctx.author.display_name}** dengan Rp{bid_amount:,}.\n\nUang bid sebelumnya (Rp{old_bid:,}) sudah dikembalikan."
            await kirim_notif_dm(old_bidder, old_bidder_notif)
    
    save_data(data)

# ===== FITUR TAMBAHAN LENGKAP =====

# !crime - Sistem kejahatan dengan risk/reward
@bot.command()
async def crime(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    # Cek apakah user sedang tidur
    if check_sleep_status(user_id):
        await ctx.send("😴 Kamu sedang tidur! Bangun dulu dengan `!bangun` sebelum bisa melakukan kejahatan.")
        return
    
    # Cooldown 2 jam
    current_time = int(time.time())
    last_crime = data[user_id].get("last_crime", 0)
    if current_time - last_crime < 7200:
        remaining = 7200 - (current_time - last_crime)
        await ctx.send(f"⏰ Tunggu {remaining//60} menit lagi untuk melakukan kejahatan.")
        return
    
    data[user_id] = apply_life_effects(data[user_id])
    
    crimes = [
        {"name": "Copet", "success": 70, "reward": 25000, "fine": 15000},
        {"name": "Bobol ATM", "success": 40, "reward": 100000, "fine": 75000},
        {"name": "Pencurian Motor", "success": 30, "reward": 500000, "fine": 300000},
        {"name": "Merampok Bank", "success": 15, "reward": 2000000, "fine": 1000000},
        {"name": "Cyber Crime", "success": 60, "reward": 150000, "fine": 100000}
    ]
    
    crime = random.choice(crimes)
    level = calculate_level(data[user_id]["xp"])
    success_rate = min(crime["success"] + (level * 2), 85)
    
    if random.randint(1, 100) <= success_rate:
        # Berhasil
        data[user_id]["uang"] += crime["reward"]
        data[user_id]["xp"] += 10
        data[user_id]["last_crime"] = current_time
        
        embed = discord.Embed(title="🎭 Kejahatan Berhasil!", color=0x00ff00)
        embed.add_field(name="Kejahatan", value=crime["name"], inline=True)
        embed.add_field(name="💰 Dapat", value=f"Rp{crime['reward']:,}", inline=True)
        embed.add_field(name="⭐ XP", value="+10", inline=True)
    else:
        # Tertangkap
        data[user_id]["uang"] = max(0, data[user_id]["uang"] - crime["fine"])
        data[user_id]["last_crime"] = current_time
        
        embed = discord.Embed(title="🚔 Tertangkap Polisi!", color=0xff0000)
        embed.add_field(name="Kejahatan", value=crime["name"], inline=True)
        embed.add_field(name="💸 Denda", value=f"Rp{crime['fine']:,}", inline=True)
        embed.add_field(name="😱 Status", value="Ditangkap!", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !judi - Sistem perjudian
@bot.command()
async def judi(ctx, taruhan: int = None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    # Cek apakah user sedang tidur
    if check_sleep_status(user_id):
        await ctx.send("😴 Kamu sedang tidur! Bangun dulu dengan `!bangun` sebelum bisa berjudi.")
        return
    if taruhan is None:
        await ctx.send("🎰 **Cara Bermain Judi:**\n`!judi [jumlah]` - Taruhan uang\n\n🎲 **Aturan:**\n• Menang: 2x lipat\n• Kalah: Hilang semua\n• Peluang menang: 45%")
        return
    
    if taruhan <= 0:
        await ctx.send("❌ Taruhan harus lebih dari 0.")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if data[user_id]["uang"] < taruhan:
        await ctx.send("❌ Uang tidak cukup untuk taruhan.")
        return
    
    # 45% peluang menang
    if random.randint(1, 100) <= 45:
        # Menang
        kemenangan = taruhan * 2
        data[user_id]["uang"] += kemenangan
        
        embed = discord.Embed(title="🎉 JACKPOT!", color=0xffd700)
        embed.add_field(name="Taruhan", value=f"Rp{taruhan:,}", inline=True)
        embed.add_field(name="💰 Menang", value=f"Rp{kemenangan:,}", inline=True)
        embed.add_field(name="💎 Total", value=f"Rp{data[user_id]['uang']:,}", inline=True)
    else:
        # Kalah
        data[user_id]["uang"] -= taruhan
        
        embed = discord.Embed(title="💸 KALAH!", color=0xff0000)
        embed.add_field(name="Taruhan", value=f"Rp{taruhan:,}", inline=True)
        embed.add_field(name="😭 Hilang", value=f"Rp{taruhan:,}", inline=True)
        embed.add_field(name="💰 Sisa", value=f"Rp{data[user_id]['uang']:,}", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !nikah - Sistem pernikahan
@bot.command()
async def nikah(ctx, partner: discord.Member):
    user_id = str(ctx.author.id)
    partner_id = str(partner.id)
    
    if user_id == partner_id:
        await ctx.send("❌ Kamu tidak bisa menikah dengan diri sendiri.")
        return
    
    create_user_profile(user_id)
    create_user_profile(partner_id)
    
    if data[user_id].get("married_to"):
        await ctx.send("❌ Kamu sudah menikah.")
        return
    
    if data[partner_id].get("married_to"):
        await ctx.send(f"❌ {partner.display_name} sudah menikah.")
        return
    
    # Biaya pernikahan
    wedding_cost = 1000000
    if data[user_id]["uang"] < wedding_cost:
        await ctx.send(f"❌ Kamu butuh Rp{wedding_cost:,} untuk biaya pernikahan.")
        return
    
    # Tunggu konfirmasi dari partner
    await ctx.send(f"💍 {partner.mention}, {ctx.author.display_name} melamar kamu!\nKetik `!terima` dalam 60 detik untuk menerima atau `!tolak` untuk menolak.")
    
    def check(message):
        return message.author == partner and message.content.lower() in ['!terima', '!tolak']
    
    try:
        response = await bot.wait_for('message', check=check, timeout=60.0)
        
        if response.content.lower() == '!terima':
            data[user_id]["uang"] -= wedding_cost
            data[user_id]["married_to"] = partner_id
            data[partner_id]["married_to"] = user_id
            data[user_id]["marriage_date"] = int(time.time())
            data[partner_id]["marriage_date"] = int(time.time())
            
            embed = discord.Embed(title="💒 PERNIKAHAN!", color=0xff69b4)
            embed.add_field(name="👰 Pasangan", value=f"{ctx.author.display_name} ❤️ {partner.display_name}", inline=False)
            embed.add_field(name="💸 Biaya", value=f"Rp{wedding_cost:,}", inline=True)
            embed.add_field(name="🎉 Status", value="Resmi Menikah!", inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"💔 {partner.display_name} menolak lamaran.")
    
    except asyncio.TimeoutError:
        await ctx.send("⏰ Waktu habis. Lamaran dibatalkan.")
    
    save_data(data)

# !cerai - Sistem perceraian
@bot.command()
async def cerai(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if not data[user_id].get("married_to"):
        await ctx.send("❌ Kamu tidak sedang menikah.")
        return
    
    partner_id = data[user_id]["married_to"]
    
    # Biaya perceraian
    divorce_cost = 500000
    if data[user_id]["uang"] < divorce_cost:
        await ctx.send(f"❌ Kamu butuh Rp{divorce_cost:,} untuk biaya perceraian.")
        return
    
    data[user_id]["uang"] -= divorce_cost
    del data[user_id]["married_to"]
    del data[user_id]["marriage_date"]
    
    if partner_id in data:
        if "married_to" in data[partner_id]:
            del data[partner_id]["married_to"]
        if "marriage_date" in data[partner_id]:
            del data[partner_id]["marriage_date"]
    
    embed = discord.Embed(title="💔 Perceraian", color=0x808080)
    embed.add_field(name="Status", value="Resmi Bercerai", inline=True)
    embed.add_field(name="💸 Biaya", value=f"Rp{divorce_cost:,}", inline=True)
    
    await ctx.send(f"{ctx.author.mention}", embed=embed)
    save_data(data)

# !bisnis - Sistem bisnis sederhana
@bot.command()
async def bisnis(ctx, action=None, *, business_name=None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if action is None:
        embed = discord.Embed(title="🏢 Sistem Bisnis", color=0x9b59b6)
        embed.add_field(name="Commands", value="`!bisnis buat [nama]` - Buat bisnis baru\n`!bisnis info` - Info bisnis kamu\n`!bisnis profit` - Ambil keuntungan\n`!bisnis upgrade` - Upgrade bisnis", inline=False)
        embed.add_field(name="💰 Biaya Buat", value="Rp5.000.000", inline=True)
        embed.add_field(name="💵 Profit/Hari", value="Rp100.000 (base)", inline=True)
        await ctx.send(embed=embed)
        return
    
    if action == "buat":
        if not business_name:
            await ctx.send("❌ Masukkan nama bisnis: `!bisnis buat [nama]`")
            return
        
        if data[user_id].get("business"):
            await ctx.send("❌ Kamu sudah punya bisnis.")
            return
        
        cost = 5000000
        if data[user_id]["uang"] < cost:
            await ctx.send(f"❌ Kamu butuh Rp{cost:,} untuk membuat bisnis.")
            return
        
        data[user_id]["uang"] -= cost
        data[user_id]["business"] = {
            "name": business_name,
            "level": 1,
            "last_profit": int(time.time()),
            "total_profit": 0
        }
        
        await ctx.send(f"🏢 Bisnis **{business_name}** berhasil dibuat! Profit harian: Rp100.000")
    
    elif action == "info":
        if not data[user_id].get("business"):
            await ctx.send("❌ Kamu tidak punya bisnis.")
            return
        
        business = data[user_id]["business"]
        daily_profit = 100000 * business["level"]
        
        embed = discord.Embed(title=f"🏢 {business['name']}", color=0x9b59b6)
        embed.add_field(name="Level", value=business["level"], inline=True)
        embed.add_field(name="💰 Profit Harian", value=f"Rp{daily_profit:,}", inline=True)
        embed.add_field(name="📊 Total Profit", value=f"Rp{business['total_profit']:,}", inline=True)
        
        await ctx.send(embed=embed)
    
    elif action == "profit":
        if not data[user_id].get("business"):
            await ctx.send("❌ Kamu tidak punya bisnis.")
            return
        
        business = data[user_id]["business"]
        current_time = int(time.time())
        last_profit = business["last_profit"]
        
        if current_time - last_profit < 86400:  # 24 jam
            remaining = 86400 - (current_time - last_profit)
            await ctx.send(f"⏰ Tunggu {remaining//3600} jam lagi untuk mengambil profit.")
            return
        
        daily_profit = 100000 * business["level"]
        data[user_id]["uang"] += daily_profit
        business["last_profit"] = current_time
        business["total_profit"] += daily_profit
        
        await ctx.send(f"💰 Kamu mendapat profit sebesar Rp{daily_profit:,} dari bisnis **{business['name']}**!")
    
    elif action == "upgrade":
        if not data[user_id].get("business"):
            await ctx.send("❌ Kamu tidak punya bisnis.")
            return
        
        business = data[user_id]["business"]
        upgrade_cost = business["level"] * 2000000
        
        if data[user_id]["uang"] < upgrade_cost:
            await ctx.send(f"❌ Kamu butuh Rp{upgrade_cost:,} untuk upgrade bisnis ke level {business['level'] + 1}.")
            return
        
        data[user_id]["uang"] -= upgrade_cost
        business["level"] += 1
        new_profit = 100000 * business["level"]
        
        await ctx.send(f"⬆️ Bisnis **{business['name']}** berhasil di-upgrade ke level {business['level']}!\nProfit harian baru: Rp{new_profit:,}")
    
    save_data(data)

# !achievement - Sistem pencapaian
@bot.command()
async def achievement(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    achievements = []
    
    # Cek achievements
    level = calculate_level(data[user_id]["xp"])
    uang = data[user_id]["uang"]
    
    if level >= 10:
        achievements.append("🎯 Pekerja Handal (Level 10+)")
    if level >= 25:
        achievements.append("🏆 Master Worker (Level 25+)")
    if level >= 50:
        achievements.append("👑 Grandmaster (Level 50+)")
    
    if uang >= 1000000:
        achievements.append("💰 Jutawan (Rp1jt+)")
    if uang >= 10000000:
        achievements.append("💎 Miliarder (Rp10jt+)")
    if uang >= 100000000:
        achievements.append("🏦 Konglomerat (Rp100jt+)")
    
    if data[user_id].get("married_to"):
        achievements.append("💍 Sudah Menikah")
    
    if data[user_id].get("business"):
        achievements.append("🏢 Pebisnis")
        if data[user_id]["business"]["level"] >= 5:
            achievements.append("📈 Business Tycoon (Bisnis Lv5+)")
    
    # Rating achievements
    rating_data = data[user_id]["rating_kredibilitas"]
    if rating_data["transaksi_selesai"] >= 10:
        achievements.append("⭐ Terpercaya (10+ transaksi)")
    
    avg_rating = hitung_rating_rata_rata(data[user_id])
    if avg_rating >= 4.5 and rating_data["jumlah_rating"] >= 5:
        achievements.append("💎 Rating Emas (4.5+ stars)")
    
    embed = discord.Embed(title=f"🏆 Achievement {ctx.author.display_name}", color=0xffd700)
    
    if achievements:
        embed.add_field(name="🎉 Pencapaian Terbuka", value="\n".join(achievements), inline=False)
    else:
        embed.add_field(name="📋 Status", value="Belum ada achievement", inline=False)
    
    # Progress menuju achievement berikutnya
    progress = []
    if level < 10:
        progress.append(f"🎯 Pekerja Handal: {level}/10 level")
    elif level < 25:
        progress.append(f"🏆 Master Worker: {level}/25 level")
    elif level < 50:
        progress.append(f"👑 Grandmaster: {level}/50 level")
    
    if uang < 1000000:
        progress.append(f"💰 Jutawan: Rp{uang:,}/1.000.000")
    elif uang < 10000000:
        progress.append(f"💎 Miliarder: Rp{uang:,}/10.000.000")
    elif uang < 100000000:
        progress.append(f"🏦 Konglomerat: Rp{uang:,}/100.000.000")
    
    if progress:
        embed.add_field(name="📊 Progress", value="\n".join(progress[:5]), inline=False)
    
    await ctx.send(embed=embed)

# !daily - Bonus harian
@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    current_time = int(time.time())
    last_daily = data[user_id].get("last_daily", 0)
    
    if current_time - last_daily < 86400:  # 24 jam
        remaining = 86400 - (current_time - last_daily)
        await ctx.send(f"⏰ Tunggu {remaining//3600} jam lagi untuk daily bonus.")
        return
    
    # Bonus harian
    base_daily = 50000
    level = calculate_level(data[user_id]["xp"])
    level_bonus = level * 5000
    
    # Streak bonus
    if current_time - last_daily <= 172800:  # Dalam 2 hari
        data[user_id]["daily_streak"] = data[user_id].get("daily_streak", 0) + 1
    else:
        data[user_id]["daily_streak"] = 1
    
    streak_bonus = min(data[user_id]["daily_streak"] * 10000, 100000)
    total_bonus = base_daily + level_bonus + streak_bonus
    
    data[user_id]["uang"] += total_bonus
    data[user_id]["last_daily"] = current_time
    data[user_id]["xp"] += 20
    
    embed = discord.Embed(title="🎁 Daily Bonus!", color=0x00ff00)
    embed.add_field(name="💰 Base", value=f"Rp{base_daily:,}", inline=True)
    embed.add_field(name="📊 Level Bonus", value=f"Rp{level_bonus:,}", inline=True)
    embed.add_field(name="🔥 Streak Bonus", value=f"Rp{streak_bonus:,}", inline=True)
    embed.add_field(name="💎 Total", value=f"Rp{total_bonus:,}", inline=False)
    embed.add_field(name="🔥 Daily Streak", value=f"{data[user_id]['daily_streak']} hari", inline=True)
    embed.add_field(name="⭐ XP", value="+20", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# ===== INSTAGRAM INFLUENCER SYSTEM =====

# !posting - Post content ke Instagram (DM Only)
@bot.command()
async def posting(ctx, *, caption=None):
    # Cek apakah command digunakan di DM
    if ctx.guild is not None:
        await ctx.send("📱 **Instagram Posting hanya bisa di DM Bot!**\n\n💌 Kirim pesan langsung ke bot untuk posting:\n`/posting [caption]`\n\nContoh: `/posting Liburan di Bali! #blessed #vacation`")
        return
    
    if caption is None:
        await ctx.send("📱 **Cara Posting Instagram:**\n`/posting [caption]` - Post konten baru\n\nContoh: `/posting Liburan di Bali! #blessed #vacation`")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    # Initialize Instagram data if doesn't exist
    if "instagram" not in data[user_id]:
        data[user_id]["instagram"] = {
            "followers": 0,
            "posts": 0,
            "last_post": 0,
            "viral_posts": 0,
            "sponsorship_offers": [],
            "total_income": 0,
            "engagement_rate": 50.0  # Base engagement rate
        }
    
    current_time = int(time.time())
    last_post = data[user_id]["instagram"]["last_post"]
    
    # Cooldown 1 jam
    if current_time - last_post < 3600:
        remaining = 3600 - (current_time - last_post)
        await ctx.send(f"⏰ Tunggu {remaining//60} menit lagi untuk posting.")
        return
    
    # Content quality berdasarkan level dan random
    level = calculate_level(data[user_id]["xp"])
    content_quality = random.randint(1, 10) + (level // 5)  # Level bonus
    content_quality = min(content_quality, 10)
    
    # Viral chance berdasarkan quality dan engagement rate
    engagement = data[user_id]["instagram"]["engagement_rate"]
    viral_chance = min((content_quality * 3) + (engagement / 10), 85)
    
    is_viral = random.randint(1, 100) <= viral_chance
    
    # Calculate new followers
    base_followers = random.randint(5, 25)
    quality_bonus = content_quality * 3
    
    if is_viral:
        viral_multiplier = random.randint(10, 50)
        new_followers = (base_followers + quality_bonus) * viral_multiplier
        data[user_id]["instagram"]["viral_posts"] += 1
    else:
        new_followers = base_followers + quality_bonus
    
    # Level bonus followers
    level_bonus = level * 2
    new_followers += level_bonus
    
    old_followers = data[user_id]["instagram"]["followers"]
    data[user_id]["instagram"]["followers"] += new_followers
    data[user_id]["instagram"]["posts"] += 1
    data[user_id]["instagram"]["last_post"] = current_time
    
    # Update engagement rate (trending content = better engagement)
    if content_quality >= 8:
        data[user_id]["instagram"]["engagement_rate"] = min(100, engagement + 2)
    elif content_quality <= 3:
        data[user_id]["instagram"]["engagement_rate"] = max(10, engagement - 1)
    
    # Daily income from followers (passive income)
    daily_income = (data[user_id]["instagram"]["followers"] // 100) * 1000  # 1k per 100 followers
    data[user_id]["uang"] += daily_income
    data[user_id]["instagram"]["total_income"] += daily_income
    
    # XP dari posting
    xp_gained = 15 + (content_quality * 2)
    data[user_id]["xp"] += xp_gained
    
    save_data(data)
    
    # Create embed response untuk DM
    if is_viral:
        embed = discord.Embed(title="🔥 POST VIRAL!", color=0xff6b6b)
        embed.add_field(name="🎉 Status", value="VIRAL CONTENT!", inline=False)
    else:
        embed = discord.Embed(title="📱 Instagram Post", color=0x405DE6)
    
    embed.add_field(name="📝 Caption", value=f"*\"{caption[:100]}{'...' if len(caption) > 100 else ''}\"*", inline=False)
    embed.add_field(name="⭐ Quality Score", value=f"{content_quality}/10", inline=True)
    embed.add_field(name="👥 New Followers", value=f"+{new_followers:,}", inline=True)
    embed.add_field(name="📊 Total Followers", value=f"{data[user_id]['instagram']['followers']:,}", inline=True)
    embed.add_field(name="💰 Income", value=f"Rp{daily_income:,}", inline=True)
    embed.add_field(name="⭐ XP", value=f"+{xp_gained}", inline=True)
    embed.add_field(name="📈 Engagement", value=f"{data[user_id]['instagram']['engagement_rate']:.1f}%", inline=True)
    
    embed.set_footer(text="✨ Posted successfully via Instagram DM!")
    await ctx.send(embed=embed)

# !followers - Cek status Instagram
@bot.command()
async def followers(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(user_id)
    
    if "instagram" not in data[user_id]:
        await ctx.send(f"📱 {member.display_name} belum pernah posting di Instagram. Ketik `/posting [caption]` untuk mulai!")
        return
    
    ig_data = data[user_id]["instagram"]
    level = calculate_level(data[user_id]["xp"])
    
    # Calculate influence level
    followers = ig_data["followers"]
    if followers < 1000:
        influence_level = "🔸 Micro Influencer"
    elif followers < 10000:
        influence_level = "⭐ Rising Influencer"
    elif followers < 100000:
        influence_level = "🎯 Macro Influencer"
    elif followers < 1000000:
        influence_level = "💎 Mega Influencer"
    else:
        influence_level = "👑 Celebrity Influencer"
    
    # Daily income potential
    daily_income = (followers // 100) * 1000
    
    embed = discord.Embed(title=f"📱 Instagram {member.display_name}", color=0x405DE6)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    embed.add_field(name="👥 Followers", value=f"{followers:,}", inline=True)
    embed.add_field(name="📝 Total Posts", value=f"{ig_data['posts']:,}", inline=True)
    embed.add_field(name="🔥 Viral Posts", value=f"{ig_data['viral_posts']:,}", inline=True)
    embed.add_field(name="📊 Influence Level", value=influence_level, inline=False)
    embed.add_field(name="📈 Engagement Rate", value=f"{ig_data['engagement_rate']:.1f}%", inline=True)
    embed.add_field(name="💰 Daily Income", value=f"Rp{daily_income:,}", inline=True)
    embed.add_field(name="💎 Total Earned", value=f"Rp{ig_data['total_income']:,}", inline=True)
    
    # Show available sponsorships
    if ig_data["sponsorship_offers"]:
        offers_text = "\n".join([f"• {offer['brand']} - Rp{offer['payment']:,}" for offer in ig_data["sponsorship_offers"][:3]])
        embed.add_field(name="🤝 Sponsorship Offers", value=offers_text, inline=False)
    
    await ctx.send(embed=embed)

# !sponsorship - Cek dan terima tawaran sponsorship (DM Only)
@bot.command()
async def sponsorship(ctx, action=None):
    # Cek apakah command digunakan di DM
    if ctx.guild is not None:
        await ctx.send("🤝 **Sponsorship hanya bisa diakses di DM Bot!**\n\n💌 Kirim pesan langsung ke bot untuk mengecek sponsorship:\n`/sponsorship`")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if "instagram" not in data[user_id]:
        await ctx.send("📱 Kamu belum punya akun Instagram. Ketik `/posting [caption]` untuk mulai!")
        return
    
    ig_data = data[user_id]["instagram"]
    followers = ig_data["followers"]
    
    if action is None:
        # Show available offers
        if not ig_data["sponsorship_offers"]:
            # Generate new offers if eligible
            if followers >= 1000:  # Minimum followers for sponsorship
                brands = [
                    {"name": "FashionCo", "base_pay": 50000},
                    {"name": "TechGadgets", "base_pay": 75000},
                    {"name": "FoodieApp", "base_pay": 40000},
                    {"name": "TravelPlus", "base_pay": 100000},
                    {"name": "BeautyCare", "base_pay": 60000},
                    {"name": "FitnessGear", "base_pay": 80000}
                ]
                
                # Generate 1-3 random offers
                num_offers = random.randint(1, 3)
                for _ in range(num_offers):
                    brand = random.choice(brands)
                    # Payment based on followers and engagement
                    payment = int(brand["base_pay"] * (followers / 1000) * (ig_data["engagement_rate"] / 50))
                    payment = max(payment, brand["base_pay"])  # Minimum payment
                    
                    offer = {
                        "brand": brand["name"],
                        "payment": payment,
                        "expires": int(time.time()) + 604800  # 1 week expiry
                    }
                    ig_data["sponsorship_offers"].append(offer)
                
                save_data(data)
        
        if not ig_data["sponsorship_offers"]:
            await ctx.send("📱 Belum ada tawaran sponsorship. Butuh minimal 1000 followers dan posting yang konsisten!")
            return
        
        embed = discord.Embed(title="🤝 Sponsorship Offers", color=0xffd700)
        for i, offer in enumerate(ig_data["sponsorship_offers"], 1):
            embed.add_field(
                name=f"{i}. {offer['brand']}",
                value=f"💰 Rp{offer['payment']:,}\n⏰ Berlaku {(offer['expires'] - int(time.time())) // 86400} hari",
                inline=True
            )
        
        embed.set_footer(text="Gunakan: /sponsorship terima [nomor] atau /sponsorship tolak [nomor]")
        await ctx.send(embed=embed)
        return
    
    if action == "terima":
        # Accept sponsorship offer (simplified - take first offer)
        if not ig_data["sponsorship_offers"]:
            await ctx.send("❌ Tidak ada tawaran sponsorship.")
            return
        
        offer = ig_data["sponsorship_offers"].pop(0)  # Take first offer
        payment = offer["payment"]
        
        data[user_id]["uang"] += payment
        ig_data["total_income"] += payment
        
        embed = discord.Embed(title="🎉 Sponsorship Accepted!", color=0x00ff00)
        embed.add_field(name="Brand", value=offer["brand"], inline=True)
        embed.add_field(name="💰 Payment", value=f"Rp{payment:,}", inline=True)
        embed.add_field(name="📈 Status", value="Content posted & paid!", inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
        save_data(data)

# !influencerrank - Ranking influencer terbaik
@bot.command()
async def influencerrank(ctx):
    if not data:
        await ctx.send("Belum ada data user.")
        return
    
    # Filter user yang punya Instagram dan sort berdasarkan followers
    influencers = []
    for user_id, user_data in data.items():
        if "instagram" in user_data and user_data["instagram"]["followers"] > 0:
            influencers.append((user_id, user_data))
    
    if not influencers:
        await ctx.send("📱 Belum ada influencer di server ini.")
        return
    
    # Sort berdasarkan followers
    sorted_influencers = sorted(influencers, key=lambda x: x[1]["instagram"]["followers"], reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 Top Influencers", color=0x405DE6)
    
    for i, (user_id, user_data) in enumerate(sorted_influencers, 1):
        try:
            user = bot.get_user(int(user_id))
            username = user.display_name if user else f"User {user_id[:4]}..."
            
            ig_data = user_data["instagram"]
            followers = ig_data["followers"]
            engagement = ig_data["engagement_rate"]
            
            if followers >= 1000000:
                rank_emoji = "👑"
            elif followers >= 100000:
                rank_emoji = "💎"
            elif followers >= 10000:
                rank_emoji = "⭐"
            else:
                rank_emoji = "🔸"
            
            embed.add_field(
                name=f"{i}. {rank_emoji} {username}",
                value=f"👥 {followers:,} followers\n📈 {engagement:.1f}% engagement\n🔥 {ig_data['viral_posts']} viral posts",
                inline=True
            )
        except:
            continue
    
    await ctx.send(embed=embed)

# !banding - Sistem banding untuk kasus yang sudah diputus
@bot.command()
async def banding(ctx, case_id=None, *, alasan=None):
    if not case_id or not alasan:
        await ctx.send("⚖️ **Cara Mengajukan Banding:**\n`!banding [case_id] [alasan]`\n\n📋 **Syarat:**\n- Kasus sudah diputus\n- Maksimal 7 hari setelah putusan\n- Biaya banding Rp500.000\n- Hanya untuk pihak yang kalah")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_advanced_court_system()
    
    # Cari kasus berdasarkan ID
    target_case = None
    full_case_id = None
    
    for full_id, case_data in data.get("court_cases", {}).items():
        if full_id.endswith(case_id) or full_id[-8:] == case_id:
            target_case = case_data
            full_case_id = full_id
            break
    
    if not target_case:
        await ctx.send(f"❌ Kasus dengan ID `{case_id}` tidak ditemukan.")
        return
    
    if target_case["status"] != "closed":
        await ctx.send("❌ Banding hanya bisa diajukan untuk kasus yang sudah diputus.")
        return
    
    # Cek apakah masih dalam batas waktu (7 hari)
    current_time = int(time.time())
    verdict_date = target_case.get("verdict_date", 0)
    if current_time - verdict_date > 604800:  # 7 hari
        await ctx.send("❌ Batas waktu banding sudah habis (maksimal 7 hari setelah putusan).")
        return
    
    # Cek apakah user adalah pihak yang kalah
    can_appeal = False
    user_role = ""
    
    if target_case["plaintiff_id"] == user_id and target_case["verdict"] != "guilty":
        can_appeal = True
        user_role = "Penuduh"
    elif target_case["defendant_id"] == user_id and target_case["verdict"] == "guilty":
        can_appeal = True
        user_role = "Tergugat"
    
    if not can_appeal:
        await ctx.send("❌ Hanya pihak yang kalah yang bisa mengajukan banding.")
        return
    
    # Biaya banding
    appeal_fee = 500000
    if data[user_id]["uang"] < appeal_fee:
        await ctx.send(f"❌ Biaya banding Rp{appeal_fee:,} tidak cukup.")
        return
    
    # Cek apakah sudah ada banding untuk kasus ini
    if "appeals" not in data:
        data["appeals"] = {}
    
    if full_case_id in data["appeals"]:
        await ctx.send("❌ Kasus ini sudah pernah dibanding.")
        return
    
    # Buat banding
    data[user_id]["uang"] -= appeal_fee
    
    data["appeals"][full_case_id] = {
        "appellant_id": user_id,
        "appellant_name": ctx.author.display_name,
        "appellant_role": user_role,
        "original_case": target_case,
        "appeal_reason": alasan,
        "appeal_date": current_time,
        "status": "pending_review",
        "appeal_judge_id": None,
        "appeal_verdict": None,
        "appeal_date_final": None
    }
    
    embed = discord.Embed(title="📨 Banding Diajukan", color=0xff9900)
    embed.add_field(name="🏛️ Case ID", value=case_id, inline=True)
    embed.add_field(name="👤 Pemohon", value=f"{ctx.author.display_name} ({user_role})", inline=True)
    embed.add_field(name="💰 Biaya", value=f"Rp{appeal_fee:,}", inline=True)
    embed.add_field(name="📝 Alasan", value=alasan[:200], inline=False)
    embed.add_field(name="📋 Status", value="Menunggu review hakim banding", inline=True)
    embed.add_field(name="⏰ Info", value="Hakim dapat mengambil kasus banding ini", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !kasusband - Lihat kasus banding tersedia
@bot.command()
async def kasusband(ctx):
    """Lihat kasus banding yang tersedia untuk hakim"""
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    user_job = data[user_id].get("pekerjaan", "").lower()
    if user_job != "hakim":
        await ctx.send("❌ Hanya Hakim yang bisa menangani kasus banding.")
        return
    
    if "appeals" not in data or not data["appeals"]:
        await ctx.send("📋 Tidak ada kasus banding yang tersedia.")
        return
    
    pending_appeals = []
    for case_id, appeal_data in data["appeals"].items():
        if appeal_data["status"] == "pending_review":
            pending_appeals.append((case_id, appeal_data))
    
    if not pending_appeals:
        await ctx.send("📋 Tidak ada kasus banding yang butuh review.")
        return
    
    embed = discord.Embed(title="⚖️ Kasus Banding Tersedia", color=0x9b59b6)
    
    for case_id, appeal_data in pending_appeals[:10]:
        original_verdict = appeal_data["original_case"]["verdict"]
        
        embed.add_field(
            name=f"📨 {case_id[-8:]}",
            value=f"👤 {appeal_data['appellant_name']} ({appeal_data['appellant_role']})\n💰 Rp{appeal_data['original_case']['debt_amount']:,}\n📜 Putusan Asal: {original_verdict}\n📝 {appeal_data['appeal_reason'][:50]}...\n📅 {int((int(time.time()) - appeal_data['appeal_date']) / 86400)} hari lalu",
            inline=True
        )
    
    embed.set_footer(text="!reviewbanding [case_id] untuk review kasus")
    await ctx.send(embed=embed)

# !reviewbanding - Review dan putuskan banding
@bot.command()
async def reviewbanding(ctx, case_id=None, keputusan=None):
    if not case_id:
        await ctx.send("⚖️ **Cara Review Banding:**\n`!reviewbanding [case_id]` - Lihat detail\n`!reviewbanding [case_id] tolak` - Tolak banding\n`!reviewbanding [case_id] terima` - Terima banding")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    user_job = data[user_id].get("pekerjaan", "").lower()
    if user_job != "hakim":
        await ctx.send("❌ Hanya Hakim yang bisa menangani kasus banding.")
        return
    
    # Cari kasus banding
    target_appeal = None
    full_case_id = None
    
    for appeal_case_id, appeal_data in data.get("appeals", {}).items():
        if appeal_case_id.endswith(case_id) or appeal_case_id[-8:] == case_id:
            target_appeal = appeal_data
            full_case_id = appeal_case_id
            break
    
    if not target_appeal:
        await ctx.send(f"❌ Kasus banding dengan ID `{case_id}` tidak ditemukan.")
        return
    
    if target_appeal["status"] != "pending_review":
        await ctx.send("❌ Kasus banding ini sudah diproses.")
        return
    
    if keputusan is None:
        # Tampilkan detail untuk review
        original_case = target_appeal["original_case"]
        
        embed = discord.Embed(title="📋 Detail Kasus Banding", color=0x9b59b6)
        embed.add_field(name="👤 Pemohon", value=f"{target_appeal['appellant_name']} ({target_appeal['appellant_role']})", inline=True)
        embed.add_field(name="💰 Nilai Sengketa", value=f"Rp{original_case['debt_amount']:,}", inline=True)
        embed.add_field(name="📜 Putusan Asal", value=original_case["verdict"], inline=True)
        embed.add_field(name="📝 Alasan Banding", value=target_appeal["appeal_reason"], inline=False)
        
        # Info kasus asli
        if original_case.get("final_score"):
            embed.add_field(name="📊 Skor Asli", value=original_case["final_score"], inline=True)
        
        # Review checklist
        review_criteria = "📋 **Kriteria Review:**\n• Apakah ada kesalahan prosedural?\n• Apakah bukti dinilai dengan benar?\n• Apakah putusan sesuai dengan fakta?\n• Apakah ada alasan kuat untuk mengubah putusan?"
        embed.add_field(name="⚖️ Panduan Review", value=review_criteria, inline=False)
        
        embed.add_field(name="📋 Keputusan", value="`!reviewbanding [case_id] terima` atau `!reviewbanding [case_id] tolak`", inline=False)
        
        await ctx.send(embed=embed)
        return
    
    # Proses keputusan banding
    appeal_fee_judge = 1500000  # Fee hakim banding lebih tinggi
    
    if keputusan.lower() == "terima":
        # Banding diterima - balik putusan
        original_case = target_appeal["original_case"]
        
        # Balik putusan
        if original_case["verdict"] == "guilty":
            new_verdict = "not_guilty"
            appeal_result = "Putusan dibatalkan, tergugat dibebaskan"
            
            # Kembalikan uang yang sudah dibayar
            plaintiff_id = original_case["plaintiff_id"]
            defendant_id = original_case["defendant_id"]
            
            if plaintiff_id in data:
                # Plaintiff harus kembalikan uang yang diterima
                debt_amount = original_case["debt_amount"]
                if data[plaintiff_id]["uang"] >= debt_amount:
                    data[plaintiff_id]["uang"] -= debt_amount
                    if defendant_id in data:
                        data[defendant_id]["uang"] += debt_amount
        else:
            new_verdict = "guilty"
            appeal_result = "Tergugat dinyatakan bersalah pada tingkat banding"
            
            # Proses pembayaran ulang
            # (implementasi serupa dengan sidang biasa)
        
        target_appeal["appeal_verdict"] = "accepted"
        embed_color = 0x00ff00
        
    elif keputusan.lower() == "tolak":
        # Banding ditolak
        new_verdict = target_appeal["original_case"]["verdict"]
        appeal_result = "Banding ditolak, putusan tingkat pertama tetap berlaku"
        target_appeal["appeal_verdict"] = "rejected"
        embed_color = 0xff0000
    else:
        await ctx.send("❌ Keputusan tidak valid. Gunakan 'terima' atau 'tolak'")
        return
    
    # Finalize appeal
    target_appeal["status"] = "closed"
    target_appeal["appeal_judge_id"] = user_id
    target_appeal["appeal_date_final"] = int(time.time())
    
    # Bayar fee hakim
    data[user_id]["uang"] += appeal_fee_judge
    
    embed = discord.Embed(title="⚖️ PUTUSAN BANDING", color=embed_color)
    embed.add_field(name="👨‍⚖️ Hakim Banding", value=ctx.author.display_name, inline=True)
    embed.add_field(name="📨 Case ID", value=case_id, inline=True)
    embed.add_field(name="👤 Pemohon", value=target_appeal["appellant_name"], inline=True)
    embed.add_field(name="📜 Keputusan", value=target_appeal["appeal_verdict"].title(), inline=True)
    embed.add_field(name="💰 Fee Hakim", value=f"Rp{appeal_fee_judge:,}", inline=True)
    embed.add_field(name="⚖️ Hasil", value=appeal_result, inline=False)
    
    save_data(data)
    await ctx.send(embed=embed)
    
    # Notifikasi ke pemohon
    appeal_notif = f"⚖️ **PUTUSAN BANDING**\n\n👨‍⚖️ **Hakim Banding:** {ctx.author.display_name}\n📨 **Case ID:** {case_id}\n📜 **Keputusan:** {target_appeal['appeal_verdict'].title()}\n⚖️ **Hasil:** {appeal_result}\n\n🎭 **Proses banding selesai.**"
    await kirim_notif_dm(target_appeal["appellant_id"], appeal_notif)

# !mediasi - Sistem mediasi untuk kasus sebelum masuk pengadilan
@bot.command()
async def mediasi(ctx, target: discord.Member, *, proposal=None):
    if not proposal:
        await ctx.send("🤝 **Cara Ajukan Mediasi:**\n`!mediasi @user [proposal_penyelesaian]`\n\n💡 **Contoh:**\n`!mediasi @user Saya bersedia bayar 50% dari utang + cicilan 6 bulan`\n\n✅ **Manfaat:** Hindari biaya pengadilan, win-win solution")
        return
    
    user_id = str(ctx.author.id)
    target_id = str(target.id)
    
    if user_id == target_id:
        await ctx.send("❌ Tidak bisa mediasi dengan diri sendiri.")
        return
    
    create_user_profile(user_id)
    create_user_profile(target_id)
    
    # Cek apakah ada utang antara kedua pihak
    has_debt = False
    debt_amount = 0
    
    if ("utang_ke_pemain" in data[target_id] and 
        user_id in data[target_id]["utang_ke_pemain"]):
        has_debt = True
        debt_amount = data[target_id]["utang_ke_pemain"][user_id]["jumlah_pokok"]
    elif ("utang_ke_pemain" in data[user_id] and 
          target_id in data[user_id]["utang_ke_pemain"]):
        has_debt = True
        debt_amount = data[user_id]["utang_ke_pemain"][target_id]["jumlah_pokok"]
    
    if not has_debt:
        await ctx.send("❌ Tidak ada utang piutang antara kalian yang memerlukan mediasi.")
        return
    
    # Initialize mediasi system
    if "mediations" not in data:
        data["mediations"] = {}
    
    # Buat mediasi ID
    mediation_id = f"mediation_{user_id}_{target_id}_{int(time.time())}"
    
    data["mediations"][mediation_id] = {
        "proposer_id": user_id,
        "proposer_name": ctx.author.display_name,
        "respondent_id": target_id,
        "respondent_name": target.display_name,
        "debt_amount": debt_amount,
        "proposal": proposal,
        "status": "pending",
        "proposed_date": int(time.time()),
        "response": None,
        "response_date": None,
        "mediator_id": None
    }
    
    embed = discord.Embed(title="🤝 Mediasi Diajukan", color=0x0099ff)
    embed.add_field(name="👨‍💼 Pengaju", value=ctx.author.display_name, inline=True)
    embed.add_field(name="👤 Pihak Lawan", value=target.display_name, inline=True)
    embed.add_field(name="💰 Nilai Utang", value=f"Rp{debt_amount:,}", inline=True)
    embed.add_field(name="🤝 Proposal", value=proposal, inline=False)
    embed.add_field(name="📋 Status", value="Menunggu respon", inline=True)
    embed.add_field(name="🆔 Mediation ID", value=mediation_id[-8:], inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    # Notifikasi ke target
    mediation_notif = f"🤝 **TAWARAN MEDIASI**\n\n**{ctx.author.display_name}** mengajukan mediasi untuk menyelesaikan utang sebesar **Rp{debt_amount:,}**.\n\n💡 **Proposal:**\n{proposal}\n\n📋 **Pilihan:**\n`!responmediasi {mediation_id[-8:]} terima` - Terima proposal\n`!responmediasi {mediation_id[-8:]} tolak [alasan]` - Tolak/counter offer\n\n⏰ **Batas waktu:** 3 hari"
    await kirim_notif_dm(target_id, mediation_notif)

# !responmediasi - Respon terhadap tawaran mediasi
@bot.command()
async def responmediasi(ctx, mediation_id=None, respon=None, *, keterangan=""):
    if not mediation_id or not respon:
        await ctx.send("🤝 **Cara Respon Mediasi:**\n`!responmediasi [mediation_id] terima` - Terima proposal\n`!responmediasi [mediation_id] tolak [alasan]` - Tolak dengan alasan\n`!responmediasi [mediation_id] counter [proposal_baru]` - Counter offer")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    # Cari mediasi
    target_mediation = None
    full_mediation_id = None
    
    for med_id, med_data in data.get("mediations", {}).items():
        if med_id.endswith(mediation_id) or med_id[-8:] == mediation_id:
            if med_data["respondent_id"] == user_id:
                target_mediation = med_data
                full_mediation_id = med_id
                break
    
    if not target_mediation:
        await ctx.send(f"❌ Mediasi dengan ID `{mediation_id}` tidak ditemukan atau bukan untuk kamu.")
        return
    
    if target_mediation["status"] != "pending":
        await ctx.send("❌ Mediasi ini sudah diproses.")
        return
    
    # Cek timeout (3 hari)
    current_time = int(time.time())
    if current_time - target_mediation["proposed_date"] > 259200:  # 3 hari
        target_mediation["status"] = "expired"
        await ctx.send("❌ Mediasi sudah expired (batas waktu 3 hari).")
        save_data(data)
        return
    
    if respon.lower() == "terima":
        # Terima proposal mediasi
        target_mediation["status"] = "accepted"
        target_mediation["response"] = "accepted"
        target_mediation["response_date"] = current_time
        
        embed = discord.Embed(title="🤝 Mediasi Berhasil!", color=0x00ff00)
        embed.add_field(name="👥 Pihak", value=f"{target_mediation['proposer_name']} & {target_mediation['respondent_name']}", inline=True)
        embed.add_field(name="💰 Nilai Utang", value=f"Rp{target_mediation['debt_amount']:,}", inline=True)
        embed.add_field(name="🤝 Kesepakatan", value=target_mediation["proposal"], inline=False)
        embed.add_field(name="✅ Status", value="Mediasi berhasil - implementasi manual", inline=True)
        
        # Notifikasi sukses
        success_notif = f"🤝 **MEDIASI BERHASIL!**\n\n**{ctx.author.display_name}** menerima proposal mediasi!\n\n💰 **Nilai utang:** Rp{target_mediation['debt_amount']:,}\n🤝 **Kesepakatan:** {target_mediation['proposal']}\n\n✅ **Selanjutnya:** Implementasikan kesepakatan sesuai yang disepakati.\n\n🎉 **Selamat! Kasus terselesaikan tanpa ke pengadilan!**"
        await kirim_notif_dm(target_mediation["proposer_id"], success_notif)
        
    elif respon.lower() == "tolak":
        target_mediation["status"] = "rejected"
        target_mediation["response"] = f"rejected: {keterangan}"
        target_mediation["response_date"] = current_time
        
        embed = discord.Embed(title="🤝 Mediasi Ditolak", color=0xff0000)
        embed.add_field(name="👤 Responden", value=ctx.author.display_name, inline=True)
        embed.add_field(name="❌ Alasan", value=keterangan if keterangan else "Tidak menyetujui proposal", inline=False)
        
        # Notifikasi penolakan
        reject_notif = f"🤝 **MEDIASI DITOLAK**\n\n**{ctx.author.display_name}** menolak proposal mediasi.\n\n❌ **Alasan:** {keterangan if keterangan else 'Tidak menyetujui proposal'}\n\n📋 **Opsi selanjutnya:**\n• Ajukan proposal mediasi baru\n• Lanjut ke jalur pengadilan (!laporutang)"
        await kirim_notif_dm(target_mediation["proposer_id"], reject_notif)
        
    elif respon.lower() == "counter":
        target_mediation["status"] = "counter_offer"
        target_mediation["response"] = f"counter: {keterangan}"
        target_mediation["response_date"] = current_time
        
        embed = discord.Embed(title="🤝 Counter Offer", color=0xff9900)
        embed.add_field(name="👤 Counter dari", value=ctx.author.display_name, inline=True)
        embed.add_field(name="🔄 Proposal Baru", value=keterangan, inline=False)
        
        # Notifikasi counter offer
        counter_notif = f"🤝 **COUNTER OFFER**\n\n**{ctx.author.display_name}** memberikan counter offer:\n\n🔄 **Proposal Baru:**\n{keterangan}\n\n📋 **Kamu bisa:**\n• Terima counter offer ini\n• Buat mediasi baru dengan proposal lain\n• Lanjut ke jalur pengadilan"
        await kirim_notif_dm(target_mediation["proposer_id"], counter_notif)
        
    else:
        await ctx.send("❌ Respon tidak valid. Gunakan: terima, tolak, atau counter")
        return
    
    save_data(data)
    await ctx.send(embed=embed)

# Update menu untuk include Instagram features
# !menuinstagram - Menu Instagram features
@bot.command()
async def menuinstagram(ctx):
    embed = discord.Embed(title="📱 Menu Instagram Influencer", color=0x405DE6)
    
    embed.add_field(
        name="📝 **Content Creation (DM Only)**",
        value="💌 `/posting [caption]` - Post konten baru (DM Bot)\n⏰ Cooldown: 1 jam\n🔒 **Posting hanya di DM untuk privasi**",
        inline=False
    )
    
    embed.add_field(
        name="📊 **Analytics**",
        value="`/followers [@user]` - Cek status Instagram\n`/influencerrank` - Ranking influencer terbaik",
        inline=False
    )
    
    embed.add_field(
        name="🤝 **Monetization (DM Only)**",
        value="💌 `/sponsorship` - Cek tawaran sponsorship (DM Bot)\n💌 `/sponsorship terima` - Terima tawaran (DM Bot)",
        inline=False
    )
    
    embed.add_field(
        name="🔒 **Privacy Features**",
        value="• Semua posting dilakukan via DM Bot\n• Sponsorship deals private\n• Personal Instagram management\n• Results tetap publik di analytics",
        inline=False
    )
    
    embed.add_field(
        name="💡 **Tips & Mechanics**",
        value="• Quality content = more followers\n• High engagement = better sponsorships\n• Viral posts = massive follower boost\n• Daily income dari follower count\n• Level tinggi = content quality bonus",
        inline=False
    )
    
    embed.add_field(
        name="🏆 **Influence Levels**",
        value="🔸 Micro (1K+)\n⭐ Rising (10K+)\n🎯 Macro (100K+)\n💎 Mega (1M+)\n👑 Celebrity (10M+)",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: /menu | DM Bot untuk posting Instagram!")
    await ctx.send(embed=embed)

# !agent - Sistem real estate agent
@bot.command()
async def agent(ctx, action=None, *, params=None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_real_estate()
    
    agent_stats = data[user_id]["real_estate_portfolio"]["agent_stats"]
    
    if action is None:
        if agent_stats["is_agent"]:
            embed = discord.Embed(title="🏢 Real Estate Agent Dashboard", color=0x9b59b6)
            embed.add_field(name="📋 Status", value="Licensed Agent", inline=True)
            embed.add_field(name="📅 Licensed Since", value=f"{int((int(time.time()) - agent_stats['license_date']) / 86400)} hari", inline=True)
            embed.add_field(name="🏠 Sales Count", value=f"{agent_stats['sales_count']} properti", inline=True)
            embed.add_field(name="💰 Total Commission", value=f"Rp{agent_stats['total_commission']:,}", inline=True)
            embed.add_field(name="⭐ Rating", value=f"{agent_stats['rating']:.1f}/5.0", inline=True)
            embed.add_field(name="📊 Commission Rate", value="3% per transaksi", inline=True)
        else:
            embed = discord.Embed(title="🏢 Become Real Estate Agent", color=0x3498db)
            embed.add_field(name="💰 License Fee", value="Rp2.000.000", inline=True)
            embed.add_field(name="📊 Level Required", value="Level 15+", inline=True)
            embed.add_field(name="💼 Benefits", value="• 3% komisi per transaksi\n• Akses market insights\n• Networking dengan client\n• Passive income potential", inline=False)
            embed.add_field(name="📋 Commands", value="`!agent license` - Dapatkan lisensi\n`!agent market` - Market insights\n`!agent clients` - Manage clients", inline=False)
        
        await ctx.send(embed=embed)
        return
    
    if action == "license":
        if agent_stats["is_agent"]:
            await ctx.send("❌ Kamu sudah memiliki lisensi real estate agent.")
            return
        
        level = calculate_level(data[user_id]["xp"])
        if level < 15:
            await ctx.send(f"❌ Level kamu ({level}) belum cukup. Minimal level 15 untuk menjadi agent.")
            return
        
        license_fee = 2000000
        if data[user_id]["uang"] < license_fee:
            await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{license_fee:,} untuk lisensi.")
            return
        
        # Grant license
        data[user_id]["uang"] -= license_fee
        agent_stats["is_agent"] = True
        agent_stats["license_date"] = int(time.time())
        
        embed = discord.Embed(title="🎉 Lisensi Agent Berhasil!", color=0x00ff00)
        embed.add_field(name="📋 Status", value="Licensed Real Estate Agent", inline=True)
        embed.add_field(name="💰 Fee Paid", value=f"Rp{license_fee:,}", inline=True)
        embed.add_field(name="💼 Benefits", value="3% komisi dari setiap transaksi properti", inline=False)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    elif action == "market":
        if not agent_stats["is_agent"]:
            await ctx.send("❌ Kamu belum memiliki lisensi real estate agent.")
            return
        
        # Market insights untuk agent
        market_data = data["real_estate"]["market_trends"]
        total_listings = len(data["real_estate"]["market"])
        total_rentals = len([r for r in data["real_estate"]["rentals"].values() if r["status"] == "available"])
        total_auctions = len(data["real_estate"]["auctions"])
        
        # Calculate average prices
        if data["real_estate"]["market"]:
            avg_price = sum(listing["price"] for listing in data["real_estate"]["market"].values()) / len(data["real_estate"]["market"])
        else:
            avg_price = 0
        
        embed = discord.Embed(title="📊 Market Insights (Agent Only)", color=0x9b59b6)
        embed.add_field(name="🏠 Active Listings", value=f"{total_listings} properti", inline=True)
        embed.add_field(name="🏘️ Rentals Available", value=f"{total_rentals} properti", inline=True)
        embed.add_field(name="🔨 Active Auctions", value=f"{total_auctions} lelang", inline=True)
        embed.add_field(name="💰 Average Price", value=f"Rp{avg_price:,.0f}", inline=True)
        embed.add_field(name="📈 Market Trend", value=f"{market_data['price_multiplier']:.2f}x", inline=True)
        embed.add_field(name="💼 Your Commission", value=f"Rp{agent_stats['total_commission']:,}", inline=True)
        
        await ctx.send(embed=embed)
    
    elif action == "clients":
        # TODO: Client management system
        await ctx.send("🚧 Sistem manajemen klien sedang dalam pengembangan.")
    
    save_data(data)

# Finalize auction system (background task)
async def finalize_auctions():
    """Check dan finalize auction yang sudah berakhir"""
    current_time = int(time.time())
    
    # Initialize real estate system if not exists
    if "real_estate" not in data:
        init_real_estate()
        return
    
    if "auctions" not in data["real_estate"]:
        return
    
    finished_auctions = []
    for auction_id, auction_data in data["real_estate"]["auctions"].items():
        if current_time >= auction_data["end_time"]:
            finished_auctions.append((auction_id, auction_data))
    
    for auction_id, auction_data in finished_auctions:
        if auction_data["current_bidder"]:
            # Ada pemenang
            winner_id = auction_data["current_bidder"]
            seller_id = auction_data["seller_id"]
            final_price = auction_data["current_bid"]
            commission = int(final_price * 0.03)  # 3% commission
            seller_gets = final_price - commission
            
            # Transfer property ke pemenang
            property_data = auction_data["property_data"].copy()
            property_data["purchase_price"] = final_price
            property_data["purchase_date"] = current_time
            property_data["current_value"] = final_price
            property_data["previous_owner"] = seller_id
            
            if winner_id in data:
                data[winner_id]["real_estate_portfolio"]["owned_properties"][auction_data["property_id"]] = property_data
            
            # Pay seller
            if seller_id in data:
                data[seller_id]["uang"] += seller_gets
            
            # Distribute commission to agents
            # TODO: Add agent commission distribution
            
            # Notifikasi
            winner_notif = f"🎉 **LELANG MENANG!**\n\nSelamat! Kamu memenangkan lelang properti **{auction_data['property_name']}** dengan bid Rp{final_price:,}!\n\nProperti sudah ditransfer ke portfolio kamu."
            seller_notif = f"🔨 **Lelang Selesai!**\n\nProperti **{auction_data['property_name']}** terjual di lelang seharga Rp{final_price:,}!\n\n💰 **Diterima:** Rp{seller_gets:,} (setelah komisi 3%)"
            
            await kirim_notif_dm(winner_id, winner_notif)
            await kirim_notif_dm(seller_id, seller_notif)
        else:
            # Tidak ada pemenang, kembalikan properti ke seller
            seller_id = auction_data["seller_id"]
            if seller_id in data:
                data[seller_id]["real_estate_portfolio"]["owned_properties"][auction_data["property_id"]] = auction_data["property_data"]
            
            # Notifikasi
            seller_notif = f"🔨 **Lelang Berakhir**\n\nLelang properti **{auction_data['property_name']}** berakhir tanpa pemenang. Properti dikembalikan ke portfolio kamu."
            await kirim_notif_dm(seller_id, seller_notif)
        
        # Hapus auction
        del data["real_estate"]["auctions"][auction_id]
    
    save_data(data)

# Update passive income dari rental properties
async def update_rental_income():
    """Update passive income dari rental properties"""
    current_time = int(time.time())
    
    # Initialize real estate system if not exists
    if "real_estate" not in data:
        init_real_estate()
        return
    
    for user_id, user_data in list(data.items()):
        if user_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings"]:
            continue
        
        if "real_estate_portfolio" not in user_data:
            continue
        
        portfolio = user_data["real_estate_portfolio"]
        
        # Check each property untuk passive income
        for prop_id, prop_data in portfolio["owned_properties"].items():
            if prop_data["rental_status"] == "rented":
                # Check if it's time untuk collect rent
                last_rent_collection = prop_data.get("last_rent_collection", prop_data["purchase_date"])
                
                if current_time - last_rent_collection >= 2592000:  # 30 hari
                    rental_income = prop_data["rental_income"]
                    maintenance_cost = prop_data["maintenance_cost"]
                    net_income = rental_income - maintenance_cost
                    
                    user_data["uang"] += net_income
                    prop_data["total_income"] += net_income
                    prop_data["last_rent_collection"] = current_time
                    
                    # Notifikasi passive income
                    notif_msg = f"🏠 **Passive Income**\n\nProperti **{prop_data['property_name']}** menghasilkan rental income!\n\n💰 **Diterima:** Rp{net_income:,}\n(Rp{rental_income:,} - Rp{maintenance_cost:,} maintenance)"
                    await kirim_notif_dm(user_id, notif_msg)
    
    save_data(data)

# Add real estate tasks to the existing loops
@tasks.loop(hours=12)  # Cek setiap 12 jam
async def real_estate_management():
    await finalize_auctions()
    await update_rental_income()

# Update market trends randomly
@tasks.loop(hours=24)  # Update market trends setiap hari
async def update_market_trends():
    # Initialize real estate system if not exists
    if "real_estate" not in data:
        init_real_estate()
        return
        
    market_data = data.get("real_estate", {}).get("market_trends", {})
    if market_data:
        # Random market change -10% to +15%
        change = random.uniform(-0.1, 0.15)
        new_multiplier = max(0.5, min(2.0, market_data["price_multiplier"] + change))
        market_data["price_multiplier"] = new_multiplier
        market_data["last_update"] = int(time.time())
        save_data(data)

# !transfer - Transfer uang ke user lain
@bot.command()
async def transfer(ctx, target: discord.Member, jumlah: int):
    if jumlah <= 0:
        await ctx.send("❌ Jumlah transfer harus lebih dari 0.")
        return
    
    user_id = str(ctx.author.id)
    target_id = str(target.id)
    
    if user_id == target_id:
        await ctx.send("❌ Kamu tidak bisa transfer ke diri sendiri.")
        return
    
    create_user_profile(user_id)
    create_user_profile(target_id)
    
    if data[user_id]["uang"] < jumlah:
        await ctx.send("❌ Saldo tidak cukup untuk transfer.")
        return
    
    # Fee transfer 1%
    fee = max(1000, int(jumlah * 0.01))
    total_deduct = jumlah + fee
    
    if data[user_id]["uang"] < total_deduct:
        await ctx.send(f"❌ Saldo tidak cukup. Butuh Rp{total_deduct:,} (termasuk fee Rp{fee:,})")
        return
    
    data[user_id]["uang"] -= total_deduct
    data[target_id]["uang"] += jumlah
    
    embed = discord.Embed(title="💸 Transfer Berhasil", color=0x00ff00)
    embed.add_field(name="Dari", value=ctx.author.display_name, inline=True)
    embed.add_field(name="Ke", value=target.display_name, inline=True)
    embed.add_field(name="💰 Jumlah", value=f"Rp{jumlah:,}", inline=True)
    embed.add_field(name="💳 Fee", value=f"Rp{fee:,}", inline=True)
    embed.add_field(name="📊 Total", value=f"Rp{total_deduct:,}", inline=True)
    
    save_data(data)
    await ctx.send(embed=embed)
    
    # Notifikasi ke penerima
    pesan_notif = f"💰 **Transfer Diterima**\n\n**{ctx.author.display_name}** mengirim uang sebesar **Rp{jumlah:,}** ke kamu.\n\nSaldo baru: **Rp{data[target_id]['uang']:,}**"
    await kirim_notif_dm(target_id, pesan_notif)

# ===== BANKING SYSTEM =====

# Inisialisasi sistem perbankan
def init_banking_system():
    if "bank_settings" not in data:
        data["bank_settings"] = {
            "tabungan_rate": 0.05,  # 5% per bulan
            "investasi_rate": 0.12,  # 12% per tahun (risky)
            "pinjaman_rate": 0.08,  # 8% per bulan
            "last_interest_calc": int(time.time())
        }
    
    if "companies" not in data:
        data["companies"] = {}
    
    save_data(data)

# !tabung - Menabung uang ke bank
@bot.command()
async def tabung(ctx, jumlah: int = None):
    if jumlah is None:
        await ctx.send("💰 **Cara Menabung:**\n`!tabung [jumlah]` - Simpan uang ke bank\n`!tabung info` - Lihat saldo tabungan\n\n🏦 **Bunga:** 5% per bulan\n💳 **Minimum:** Rp10.000")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_banking_system()
    
    if "bank_account" not in data[user_id]:
        data[user_id]["bank_account"] = {
            "tabungan": 0,
            "investasi": 0,
            "last_deposit": 0,
            "total_interest": 0
        }
    
    if jumlah < 10000:
        await ctx.send("❌ Minimum tabungan Rp10.000")
        return
    
    if data[user_id]["uang"] < jumlah:
        await ctx.send("❌ Saldo tidak cukup untuk menabung.")
        return
    
    # Hitung bunga sebelum menabung baru
    calculate_bank_interest(user_id)
    
    data[user_id]["uang"] -= jumlah
    data[user_id]["bank_account"]["tabungan"] += jumlah
    data[user_id]["bank_account"]["last_deposit"] = int(time.time())
    
    embed = discord.Embed(title="🏦 Tabungan Berhasil", color=0x00ff00)
    embed.add_field(name="💰 Jumlah", value=f"Rp{jumlah:,}", inline=True)
    embed.add_field(name="💳 Total Tabungan", value=f"Rp{data[user_id]['bank_account']['tabungan']:,}", inline=True)
    embed.add_field(name="📈 Bunga", value="5% per bulan", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !tariktabungan - Tarik uang dari tabungan bank
@bot.command()
async def tariktabungan(ctx, jumlah_or_all=None):
    if jumlah_or_all is None:
        await ctx.send("💳 **Cara Tarik Tabungan:**\n`!tariktabungan [jumlah]` - Tarik uang dari tabungan\n`!tariktabungan semua` - Tarik semua tabungan\n\n⚠️ **Catatan:** Tarik sebelum 30 hari = penalty 2%")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_banking_system()
    
    if "bank_account" not in data[user_id]:
        await ctx.send("❌ Kamu belum punya rekening bank. Mulai dengan `!tabung [jumlah]`")
        return
    
    # Hitung bunga terlebih dahulu
    calculate_bank_interest(user_id)
    
    saldo_tabungan = data[user_id]["bank_account"]["tabungan"]
    if saldo_tabungan <= 0:
        await ctx.send("❌ Tidak ada uang di tabungan.")
        return
    
    if jumlah_or_all.lower() == "semua":
        jumlah = saldo_tabungan
    else:
        try:
            jumlah = int(jumlah_or_all)
        except ValueError:
            await ctx.send("❌ Jumlah harus berupa angka atau 'semua'")
            return
    
    if jumlah > saldo_tabungan:
        await ctx.send(f"❌ Saldo tabungan tidak cukup. Tersedia: Rp{saldo_tabungan:,}")
        return
    
    # Penalty jika tarik sebelum 30 hari
    last_deposit = data[user_id]["bank_account"]["last_deposit"]
    current_time = int(time.time())
    days_since_deposit = (current_time - last_deposit) // 86400
    
    penalty = 0
    if days_since_deposit < 30:
        penalty = int(jumlah * 0.02)  # 2% penalty
        jumlah_bersih = jumlah - penalty
    else:
        jumlah_bersih = jumlah
    
    data[user_id]["bank_account"]["tabungan"] -= jumlah
    data[user_id]["uang"] += jumlah_bersih
    
    embed = discord.Embed(title="💳 Penarikan Tabungan", color=0xff9900)
    embed.add_field(name="💰 Jumlah Tarik", value=f"Rp{jumlah:,}", inline=True)
    if penalty > 0:
        embed.add_field(name="⚠️ Penalty", value=f"Rp{penalty:,} (2%)", inline=True)
        embed.add_field(name="💵 Diterima", value=f"Rp{jumlah_bersih:,}", inline=True)
    else:
        embed.add_field(name="💵 Diterima", value=f"Rp{jumlah_bersih:,}", inline=True)
    embed.add_field(name="💳 Sisa Tabungan", value=f"Rp{data[user_id]['bank_account']['tabungan']:,}", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !tarikitem - Tarik item dari marketplace (existing function)
@bot.command()
async def tarikitem(ctx, listing_id):
    user_id = str(ctx.author.id)
    
    if "marketplace" not in data or not data["marketplace"]:
        await ctx.send("❌ Marketplace kosong.")
        return
    
    # Cari listing berdasarkan ID
    target_listing = None
    target_id = None
    
    for full_listing_id, listing in data["marketplace"].items():
        if full_listing_id.endswith(listing_id) or full_listing_id[-8:] == listing_id:
            if listing["seller_id"] == user_id:
                target_listing = listing
                target_id = full_listing_id
                break
    
    if not target_listing:
        await ctx.send(f"❌ Listing dengan ID `{listing_id}` tidak ditemukan atau bukan milik kamu.")
        return
    
    # Kembalikan item ke inventory
    item_name = target_listing["item"]
    if item_name not in data[user_id]["inventory"]:
        data[user_id]["inventory"][item_name] = 0
    data[user_id]["inventory"][item_name] += 1
    
    # Hapus dari marketplace
    del data["marketplace"][target_id]
    
    save_data(data)
    
    embed = discord.Embed(title="📦 Item Ditarik dari Marketplace", color=0xff9900)
    embed.add_field(name="📦 Item", value=item_name.title(), inline=True)
    embed.add_field(name="🆔 Listing ID", value=listing_id, inline=True)
    embed.add_field(name="✅ Status", value="Kembali ke inventory", inline=True)
    
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !investasi - Investasi uang dengan risiko
@bot.command()
async def investasi(ctx, action=None, jumlah: int = None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_banking_system()
    
    if "bank_account" not in data[user_id]:
        data[user_id]["bank_account"] = {
            "tabungan": 0,
            "investasi": 0,
            "last_deposit": 0,
            "total_interest": 0,
            "investasi_start": 0
        }
    
    if action is None:
        embed = discord.Embed(title="📈 Sistem Investasi", color=0x9b59b6)
        embed.add_field(name="Commands", value="`!investasi beli [jumlah]` - Beli investasi\n`!investasi jual` - Jual semua investasi\n`!investasi info` - Info investasi kamu", inline=False)
        embed.add_field(name="📊 Return", value="12% per tahun (volatile)", inline=True)
        embed.add_field(name="⚠️ Risiko", value="Bisa untung/rugi 20%", inline=True)
        embed.add_field(name="💰 Minimum", value="Rp50.000", inline=True)
        await ctx.send(embed=embed)
        return
    
    if action == "info":
        saldo_investasi = data[user_id]["bank_account"]["investasi"]
        if saldo_investasi <= 0:
            await ctx.send("📈 Kamu belum punya investasi. Mulai dengan `!investasi beli [jumlah]`")
            return
        
        # Calculate potential return
        investasi_start = data[user_id]["bank_account"].get("investasi_start", int(time.time()))
        days_invested = (int(time.time()) - investasi_start) // 86400
        yearly_return = int(saldo_investasi * 0.12 * (days_invested / 365))
        
        embed = discord.Embed(title="📈 Portfolio Investasi", color=0x9b59b6)
        embed.add_field(name="💰 Total Investasi", value=f"Rp{saldo_investasi:,}", inline=True)
        embed.add_field(name="📅 Hari", value=f"{days_invested} hari", inline=True)
        embed.add_field(name="📊 Estimasi Return", value=f"Rp{yearly_return:,}", inline=True)
        await ctx.send(embed=embed)
        return
    
    elif action == "beli":
        if jumlah is None or jumlah < 50000:
            await ctx.send("❌ Minimum investasi Rp50.000")
            return
        
        if data[user_id]["uang"] < jumlah:
            await ctx.send("❌ Saldo tidak cukup untuk investasi.")
            return
        
        data[user_id]["uang"] -= jumlah
        data[user_id]["bank_account"]["investasi"] += jumlah
        if data[user_id]["bank_account"].get("investasi_start", 0) == 0:
            data[user_id]["bank_account"]["investasi_start"] = int(time.time())
        
        embed = discord.Embed(title="📈 Investasi Berhasil", color=0x00ff00)
        embed.add_field(name="💰 Jumlah", value=f"Rp{jumlah:,}", inline=True)
        embed.add_field(name="📊 Total Investasi", value=f"Rp{data[user_id]['bank_account']['investasi']:,}", inline=True)
        embed.add_field(name="📈 Expected Return", value="12% per tahun", inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    elif action == "jual":
        saldo_investasi = data[user_id]["bank_account"]["investasi"]
        if saldo_investasi <= 0:
            await ctx.send("❌ Tidak ada investasi untuk dijual.")
            return
        
        # Calculate return with volatility
        investasi_start = data[user_id]["bank_account"].get("investasi_start", int(time.time()))
        days_invested = (int(time.time()) - investasi_start) // 86400
        
        # Base return (12% yearly)
        base_return = saldo_investasi * 0.12 * (days_invested / 365)
        
        # Market volatility (-20% to +20%)
        volatility = random.uniform(-0.20, 0.20)
        final_amount = int(saldo_investasi + base_return + (saldo_investasi * volatility))
        
        gain_loss = final_amount - saldo_investasi
        
        data[user_id]["bank_account"]["investasi"] = 0
        data[user_id]["bank_account"]["investasi_start"] = 0
        data[user_id]["uang"] += final_amount
        
        embed = discord.Embed(
            title="💹 Investasi Dijual", 
            color=0x00ff00 if gain_loss >= 0 else 0xff0000
        )
        embed.add_field(name="💰 Modal Awal", value=f"Rp{saldo_investasi:,}", inline=True)
        embed.add_field(name="📅 Durasi", value=f"{days_invested} hari", inline=True)
        embed.add_field(name="💵 Total Diterima", value=f"Rp{final_amount:,}", inline=True)
        embed.add_field(
            name="📊 Keuntungan/Kerugian", 
            value=f"{'📈 +' if gain_loss >= 0 else '📉 '}Rp{abs(gain_loss):,}", 
            inline=False
        )
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    save_data(data)

# !bank - Info rekening bank
@bot.command()
async def bank(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(user_id)
    init_banking_system()
    
    if "bank_account" not in data[user_id]:
        await ctx.send(f"🏦 {member.display_name} belum punya rekening bank. Buka dengan `!tabung [jumlah]`")
        return
    
    # Hitung bunga terbaru
    calculate_bank_interest(user_id)
    
    bank_data = data[user_id]["bank_account"]
    
    embed = discord.Embed(title=f"🏦 Bank Account {member.display_name}", color=0x0099ff)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    embed.add_field(name="💳 Tabungan", value=f"Rp{bank_data['tabungan']:,}", inline=True)
    embed.add_field(name="📈 Investasi", value=f"Rp{bank_data['investasi']:,}", inline=True)
    embed.add_field(name="🎁 Total Bunga", value=f"Rp{bank_data['total_interest']:,}", inline=True)
    
    # Calculate monthly savings interest potential
    monthly_interest = int(bank_data['tabungan'] * 0.05)
    embed.add_field(name="📊 Bunga Bulanan", value=f"Rp{monthly_interest:,}", inline=True)
    
    total_banking = bank_data['tabungan'] + bank_data['investasi']
    embed.add_field(name="💎 Total Asset", value=f"Rp{total_banking:,}", inline=True)
    
    await ctx.send(embed=embed)

def calculate_bank_interest(user_id):
    """Hitung bunga tabungan bulanan"""
    if "bank_account" not in data[user_id]:
        return
    
    current_time = int(time.time())
    last_interest = data[user_id]["bank_account"].get("last_interest_calc", current_time)
    
    # Hitung bunga setiap 30 hari
    months_passed = (current_time - last_interest) // (30 * 86400)
    
    if months_passed > 0:
        tabungan = data[user_id]["bank_account"]["tabungan"]
        interest = int(tabungan * 0.05 * months_passed)  # 5% per bulan
        
        data[user_id]["bank_account"]["tabungan"] += interest
        data[user_id]["bank_account"]["total_interest"] += interest
        data[user_id]["bank_account"]["last_interest_calc"] = current_time

# ===== COMPANY SYSTEM =====

# Command perusahaan sudah didefinisikan di bagian perusahaan system, menghapus duplikat ini

# ===== MARKETPLACE SYSTEM =====

# !jual - Jual item ke marketplace
@bot.command()
async def jual(ctx, harga: int, *, nama_item):
    if harga <= 0:
        await ctx.send("❌ Harga harus lebih dari 0.")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if "marketplace" not in data:
        data["marketplace"] = {}
    
    # Cek apakah user punya item tersebut
    if nama_item.lower() not in data[user_id]["inventory"]:
        await ctx.send(f"❌ Kamu tidak punya **{nama_item.title()}** di inventory.")
        return
    
    if data[user_id]["inventory"][nama_item.lower()] <= 0:
        await ctx.send(f"❌ Kamu tidak punya **{nama_item.title()}** yang cukup.")
        return
    
    # Generate listing ID
    listing_id = f"{user_id}_{int(time.time())}"
    
    # Kurangi item dari inventory
    data[user_id]["inventory"][nama_item.lower()] -= 1
    if data[user_id]["inventory"][nama_item.lower()] == 0:
        del data[user_id]["inventory"][nama_item.lower()]
    
    # Tambah ke marketplace
    data["marketplace"][listing_id] = {
        "seller_id": user_id,
        "seller_name": ctx.author.display_name,
        "item": nama_item.lower(),
        "price": harga,
        "timestamp": int(time.time())
    }
    
    save_data(data)
    
    embed = discord.Embed(title="🏪 Item Dijual ke Marketplace", color=0x00ff00)
    embed.add_field(name="📦 Item", value=nama_item.title(), inline=True)
    embed.add_field(name="💰 Harga", value=f"Rp{harga:,}", inline=True)
    embed.add_field(name="🆔 Listing ID", value=listing_id[-8:], inline=True)
    embed.add_field(name="ℹ️ Info", value="Item sekarang bisa dibeli oleh pemain lain di marketplace!", inline=False)
    
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !pasar - Lihat marketplace
@bot.command()
async def pasar(ctx, kategori=None):
    if "marketplace" not in data or not data["marketplace"]:
        await ctx.send("🏪 Marketplace masih kosong. Jual item pertama dengan `!jual [harga] [nama_item]`")
        return
    
    marketplace = data["marketplace"]
    
    # Filter berdasarkan kategori jika ada
    if kategori:
        if kategori.lower() == "makanan":
            filtered_items = {k: v for k, v in marketplace.items() if items.get(v["item"], {}).get("effect") == "food"}
        elif kategori.lower() == "minuman":
            filtered_items = {k: v for k, v in marketplace.items() if items.get(v["item"], {}).get("effect") == "drink"}
        elif kategori.lower() == "rumah":
            filtered_items = {k: v for k, v in marketplace.items() if items.get(v["item"], {}).get("effect") == "housing"}
        elif kategori.lower() == "obat":
            filtered_items = {k: v for k, v in marketplace.items() if items.get(v["item"], {}).get("effect") == "medicine"}
        else:
            filtered_items = {k: v for k, v in marketplace.items() if v["item"].lower().find(kategori.lower()) != -1}
    else:
        filtered_items = marketplace
    
    if not filtered_items:
        await ctx.send(f"❌ Tidak ada item yang dijual untuk kategori '{kategori}'." if kategori else "🏪 Marketplace kosong.")
        return
    
    # Sort berdasarkan timestamp (terbaru dulu)
    sorted_items = sorted(filtered_items.items(), key=lambda x: x[1]["timestamp"], reverse=True)
    
    embed = discord.Embed(title=f"🏪 Marketplace {('- ' + kategori.title()) if kategori else ''}", color=0x0099ff)
    
    # Tampilkan maksimal 10 item per halaman
    for i, (listing_id, listing) in enumerate(sorted_items[:15], 1):
        item_name = listing["item"].title()
        price = listing["price"]
        seller_name = listing["seller_name"]
        
        # Harga asli dari toko (jika ada)
        original_price = items.get(listing["item"], {}).get("harga", 0)
        price_comparison = ""
        if original_price > 0:
            if price < original_price:
                discount = int(((original_price - price) / original_price) * 100)
                price_comparison = f"\n💚 -{discount}% dari toko!"
            elif price > original_price:
                markup = int(((price - original_price) / original_price) * 100)
                price_comparison = f"\n🔴 +{markup}% dari toko"
        
        embed.add_field(
            name=f"{i}. {item_name}",
            value=f"💰 Rp{price:,}\n👤 {seller_name}\n🆔 {listing_id[-8:]}{price_comparison}",
            inline=True
        )
    
    embed.set_footer(text="!beli [listing_id] | !pasar [kategori] | Kategori: makanan, minuman, rumah, obat")
    await ctx.send(embed=embed)



# !myjual - Lihat item yang sedang dijual
@bot.command()
async def myjual(ctx):
    user_id = str(ctx.author.id)
    
    if "marketplace" not in data or not data["marketplace"]:
        await ctx.send("❌ Marketplace kosong.")
        return
    
    my_listings = {k: v for k, v in data["marketplace"].items() if v["seller_id"] == user_id}
    
    if not my_listings:
        await ctx.send("📦 Kamu tidak sedang menjual item apapun di marketplace.")
        return
    
    embed = discord.Embed(title=f"🏪 Item Dijual {ctx.author.display_name}", color=0xffd700)
    
    total_value = 0
    for listing_id, listing in my_listings.items():
        item_name = listing["item"].title()
        price = listing["price"]
        total_value += price
        
        embed.add_field(
            name=f"📦 {item_name}",
            value=f"💰 Rp{price:,}\n🆔 {listing_id[-8:]}\n⏰ {int((int(time.time()) - listing['timestamp']) / 86400)} hari lalu",
            inline=True
        )
    
    embed.add_field(name="💎 Total Nilai", value=f"Rp{total_value:,}", inline=False)
    embed.set_footer(text="!tarikitem [listing_id] untuk menarik item dari marketplace")
    await ctx.send(embed=embed)

# !tarik - Tarik item dari marketplace
@bot.command()
async def tarikkembali(ctx, listing_id):
    user_id = str(ctx.author.id)
    
    if "marketplace" not in data or not data["marketplace"]:
        await ctx.send("❌ Marketplace kosong.")
        return
    
    # Cari listing berdasarkan ID
    target_listing = None
    target_id = None
    
    for full_listing_id, listing in data["marketplace"].items():
        if full_listing_id.endswith(listing_id) or full_listing_id[-8:] == listing_id:
            if listing["seller_id"] == user_id:
                target_listing = listing
                target_id = full_listing_id
                break
    
    if not target_listing:
        await ctx.send(f"❌ Listing dengan ID `{listing_id}` tidak ditemukan atau bukan milik kamu.")
        return
    
    # Kembalikan item ke inventory
    item_name = target_listing["item"]
    if item_name not in data[user_id]["inventory"]:
        data[user_id]["inventory"][item_name] = 0
    data[user_id]["inventory"][item_name] += 1
    
    # Hapus dari marketplace
    del data["marketplace"][target_id]
    
    save_data(data)
    
    embed = discord.Embed(title="📦 Item Ditarik dari Marketplace", color=0xff9900)
    embed.add_field(name="📦 Item", value=item_name.title(), inline=True)
    embed.add_field(name="🆔 Listing ID", value=listing_id, inline=True)
    embed.add_field(name="✅ Status", value="Kembali ke inventory", inline=True)
    
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# Update menu marketplace
@bot.command()
async def menupasar(ctx):
    embed = discord.Embed(title="🏪 Menu Marketplace", color=0xe67e22)
    
    embed.add_field(
        name="🛒 **Membeli**",
        value="`!pasar` - Lihat semua item di marketplace\n`!pasar [kategori]` - Filter berdasarkan kategori\n`!beli [listing_id]` - Beli item dari player",
        inline=False
    )
    
    embed.add_field(
        name="💰 **Menjual**",
        value="`!jual [harga] [nama_item]` - Jual item ke marketplace\n`!myjual` - Lihat item yang sedang kamu jual\n`!tarik [listing_id]` - Tarik item dari marketplace",
        inline=False
    )
    
    embed.add_field(
        name="🔍 **Kategori Filter**",
        value="• `makanan` - Makanan untuk kenyang\n• `minuman` - Minuman untuk haus\n• `obat` - Obat-obatan untuk kesehatan\n• `rumah` - Tempat tinggal\n• `[nama]` - Cari berdasarkan nama item",
        inline=False
    )
    
    embed.add_field(
        name="💡 **Tips Trading**",
        value="• Cek harga toko sebelum beli/jual\n• Discount = harga lebih murah dari toko\n• Markup = harga lebih mahal dari toko\n• Listing ID 8 karakter terakhir unik\n• Notifikasi otomatis saat item terjual",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Contoh Penggunaan**",
        value="`!jual 20000 roti` - Jual roti seharga 20k\n`!pasar makanan` - Lihat makanan dijual\n`!beli a1b2c3d4` - Beli dengan listing ID",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu | Sistem beli dari toko tetap tersedia!")
    await ctx.send(embed=embed)

# ===== TRANSPORTATION SYSTEM =====

# Database kendaraan
vehicles = {
    "sepeda": {
        "nama": "Sepeda",
        "harga": 500000,
        "maintenance_cost": 10000,  # Per bulan
        "fuel_cost": 0,  # Per km
        "speed_bonus": 1.1,  # 10% lebih cepat
        "status_bonus": "Ramah Lingkungan",
        "kategori": "eco"
    },
    "motor": {
        "nama": "Motor Bebek",
        "harga": 15000000,
        "maintenance_cost": 100000,
        "fuel_cost": 500,  # Per km
        "speed_bonus": 1.3,
        "status_bonus": "Efisien",
        "kategori": "basic"
    },
    "motor_sport": {
        "nama": "Motor Sport",
        "harga": 45000000,
        "maintenance_cost": 200000,
        "fuel_cost": 800,
        "speed_bonus": 1.5,
        "status_bonus": "Keren",
        "kategori": "sport"
    },
    "mobil_city": {
        "nama": "Mobil City Car",
        "harga": 120000000,
        "maintenance_cost": 500000,
        "fuel_cost": 1000,
        "speed_bonus": 1.4,
        "status_bonus": "Nyaman",
        "kategori": "city"
    },
    "mobil_sedan": {
        "nama": "Mobil Sedan",
        "harga": 300000000,
        "maintenance_cost": 800000,
        "fuel_cost": 1200,
        "speed_bonus": 1.6,
        "status_bonus": "Elegan",
        "kategori": "luxury"
    },
    "mobil_suv": {
        "nama": "SUV",
        "harga": 500000000,
        "maintenance_cost": 1200000,
        "fuel_cost": 1500,
        "speed_bonus": 1.7,
        "status_bonus": "Mewah",
        "kategori": "luxury"
    },
    "bus": {
        "nama": "Bus Mini",
        "harga": 400000000,
        "maintenance_cost": 2000000,
        "fuel_cost": 2000,
        "speed_bonus": 1.2,
        "status_bonus": "Transportasi Umum",
        "kategori": "commercial"
    },
    "truk": {
        "nama": "Truk Angkutan",
        "harga": 600000000,
        "maintenance_cost": 2500000,
        "fuel_cost": 2500,
        "speed_bonus": 1.1,
        "status_bonus": "Bisnis Angkutan",
        "kategori": "commercial"
    }
}

# Initialize transportation system
def init_transportation():
    for user_id in data:
        if user_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings"]:
            continue
        if "transportation" not in data[user_id]:
            data[user_id]["transportation"] = {
                "owned_vehicles": {},
                "fuel_balance": 0,
                "total_distance": 0,
                "maintenance_due": {},
                "driver_license": {
                    "motor": False,
                    "mobil": False,
                    "komersial": False
                }
            }
    save_data(data)

# !kendaraan - Lihat daftar kendaraan
@bot.command()
async def kendaraan(ctx, kategori=None):
    init_transportation()
    
    embed = discord.Embed(title="🚗 Daftar Kendaraan", color=0x3498db)
    
    if kategori:
        filtered_vehicles = {k: v for k, v in vehicles.items() if v["kategori"] == kategori.lower()}
        if not filtered_vehicles:
            await ctx.send("❌ Kategori tidak ditemukan. Kategori: eco, basic, sport, city, luxury, commercial")
            return
    else:
        filtered_vehicles = vehicles
    
    for vehicle_key, vehicle_data in filtered_vehicles.items():
        embed.add_field(
            name=f"🚗 {vehicle_data['nama']}",
            value=f"💰 Rp{vehicle_data['harga']:,}\n🔧 Maintenance: Rp{vehicle_data['maintenance_cost']:,}/bulan\n⛽ BBM: Rp{vehicle_data['fuel_cost']:,}/km\n⚡ Speed: +{int((vehicle_data['speed_bonus']-1)*100)}%\n🏷️ {vehicle_data['kategori'].title()}\n🆔 {vehicle_key}",
            inline=True
        )
    
    embed.set_footer(text="!belimobil [vehicle_key] | Kategori: eco, basic, sport, city, luxury, commercial")
    await ctx.send(embed=embed)

# !belimobil - Beli kendaraan
@bot.command()
async def belimobil(ctx, vehicle_key=None):
    if not vehicle_key:
        await ctx.send("🚗 **Cara Beli Kendaraan:**\n`!belimobil [vehicle_key]` - Beli kendaraan\n\n📋 `!kendaraan` untuk lihat daftar")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_transportation()
    
    if vehicle_key not in vehicles:
        await ctx.send("❌ Kendaraan tidak ditemukan. Gunakan `!kendaraan` untuk melihat daftar.")
        return
    
    vehicle_data = vehicles[vehicle_key]
    
    if data[user_id]["uang"] < vehicle_data["harga"]:
        await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{vehicle_data['harga']:,}")
        return
    
    # Cek license requirement
    license_needed = None
    if "motor" in vehicle_key:
        license_needed = "motor"
    elif any(x in vehicle_key for x in ["mobil", "suv"]):
        license_needed = "mobil"
    elif vehicle_key in ["bus", "truk"]:
        license_needed = "komersial"
    
    if license_needed and not data[user_id]["transportation"]["driver_license"][license_needed]:
        await ctx.send(f"❌ Kamu butuh SIM {license_needed.title()} dulu. Gunakan `!sim {license_needed}` untuk mendapatkan SIM.")
        return
    
    # Proses pembelian
    vehicle_id = f"vehicle_{user_id}_{int(time.time())}"
    
    data[user_id]["uang"] -= vehicle_data["harga"]
    data[user_id]["transportation"]["owned_vehicles"][vehicle_id] = {
        "type": vehicle_key,
        "name": vehicle_data["nama"],
        "purchase_date": int(time.time()),
        "purchase_price": vehicle_data["harga"],
        "total_distance": 0,
        "condition": 100,  # 0-100
        "last_maintenance": int(time.time())
    }
    
    embed = discord.Embed(title="🎉 Kendaraan Berhasil Dibeli!", color=0x00ff00)
    embed.add_field(name="🚗 Kendaraan", value=vehicle_data["nama"], inline=True)
    embed.add_field(name="💰 Harga", value=f"Rp{vehicle_data['harga']:,}", inline=True)
    embed.add_field(name="🆔 Vehicle ID", value=vehicle_id[-8:], inline=True)
    embed.add_field(name="⚡ Speed Bonus", value=f"+{int((vehicle_data['speed_bonus']-1)*100)}%", inline=True)
    embed.add_field(name="🔧 Maintenance", value=f"Rp{vehicle_data['maintenance_cost']:,}/bulan", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !sim - Dapatkan SIM
@bot.command()
async def sim(ctx, license_type=None):
    if not license_type:
        await ctx.send("🪪 **Cara Buat SIM:**\n`!sim motor` - SIM A (Motor)\n`!sim mobil` - SIM B (Mobil)\n`!sim komersial` - SIM B1/B2 (Bus/Truk)\n\n💰 **Biaya:** Motor: Rp200k, Mobil: Rp500k, Komersial: Rp1jt")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_transportation()
    
    license_costs = {"motor": 200000, "mobil": 500000, "komersial": 1000000}
    license_requirements = {"motor": 5, "mobil": 10, "komersial": 15}
    
    if license_type not in license_costs:
        await ctx.send("❌ Jenis SIM tidak valid. Pilih: motor, mobil, komersial")
        return
    
    if data[user_id]["transportation"]["driver_license"][license_type]:
        await ctx.send(f"❌ Kamu sudah punya SIM {license_type.title()}.")
        return
    
    level = calculate_level(data[user_id]["xp"])
    if level < license_requirements[license_type]:
        await ctx.send(f"❌ Level kamu ({level}) belum cukup. Butuh minimal level {license_requirements[license_type]}.")
        return
    
    cost = license_costs[license_type]
    if data[user_id]["uang"] < cost:
        await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{cost:,}")
        return
    
    # Tes SIM (simulasi)
    test_score = random.randint(60, 100)
    if test_score >= 70:
        data[user_id]["uang"] -= cost
        data[user_id]["transportation"]["driver_license"][license_type] = True
        
        embed = discord.Embed(title="🎉 SIM Berhasil Didapat!", color=0x00ff00)
        embed.add_field(name="🪪 Jenis SIM", value=license_type.title(), inline=True)
        embed.add_field(name="📊 Skor Tes", value=f"{test_score}/100", inline=True)
        embed.add_field(name="💰 Biaya", value=f"Rp{cost:,}", inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
    else:
        await ctx.send(f"❌ Tes SIM gagal dengan skor {test_score}/100. Coba lagi nanti!")
    
    save_data(data)

# !garasiqu - Lihat kendaraan yang dimiliki
@bot.command()
async def garasiqu(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_transportation()
    
    owned_vehicles = data[user_id]["transportation"]["owned_vehicles"]
    
    if not owned_vehicles:
        await ctx.send("🚗 Kamu belum punya kendaraan. Beli dengan `!belimobil [vehicle_key]`")
        return
    
    embed = discord.Embed(title=f"🏠 Garasi {ctx.author.display_name}", color=0x9b59b6)
    
    total_value = 0
    for vehicle_id, vehicle_info in owned_vehicles.items():
        vehicle_data = vehicles[vehicle_info["type"]]
        current_value = int(vehicle_info["purchase_price"] * (vehicle_info["condition"] / 100))
        total_value += current_value
        
        condition_emoji = "🟢" if vehicle_info["condition"] >= 80 else "🟡" if vehicle_info["condition"] >= 50 else "🔴"
        
        embed.add_field(
            name=f"{condition_emoji} {vehicle_info['name']}",
            value=f"💎 Nilai: Rp{current_value:,}\n🔧 Kondisi: {vehicle_info['condition']}%\n📏 Jarak: {vehicle_info['total_distance']:,} km\n🆔 {vehicle_id[-8:]}",
            inline=True
        )
    
    embed.add_field(name="💰 Total Nilai Garasi", value=f"Rp{total_value:,}", inline=False)
    
    # License info
    licenses = data[user_id]["transportation"]["driver_license"]
    license_text = ""
    for license_type, has_license in licenses.items():
        status = "✅" if has_license else "❌"
        license_text += f"{status} SIM {license_type.title()}\n"
    
    embed.add_field(name="🪪 SIM yang Dimiliki", value=license_text, inline=True)
    
    await ctx.send(embed=embed)

# !perjalanan - Bepergian dengan kendaraan
@bot.command()
async def perjalanan(ctx, vehicle_id=None, jarak: int = None):
    if not vehicle_id or not jarak:
        await ctx.send("🗺️ **Cara Bepergian:**\n`!perjalanan [vehicle_id] [jarak_km]` - Bepergian dengan kendaraan\n\n📋 `!garasiqu` untuk lihat ID kendaraan")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_transportation()
    
    # Find vehicle
    target_vehicle = None
    full_vehicle_id = None
    
    for v_id, v_info in data[user_id]["transportation"]["owned_vehicles"].items():
        if v_id.endswith(vehicle_id) or v_id[-8:] == vehicle_id:
            target_vehicle = v_info
            full_vehicle_id = v_id
            break
    
    if not target_vehicle:
        await ctx.send(f"❌ Kendaraan dengan ID `{vehicle_id}` tidak ditemukan.")
        return
    
    if jarak <= 0:
        await ctx.send("❌ Jarak harus lebih dari 0 km.")
        return
    
    vehicle_data = vehicles[target_vehicle["type"]]
    
    # Calculate costs
    fuel_cost = jarak * vehicle_data["fuel_cost"]
    
    if data[user_id]["uang"] < fuel_cost:
        await ctx.send(f"❌ Uang tidak cukup untuk BBM. Butuh Rp{fuel_cost:,}")
        return
    
    # Proses perjalanan
    data[user_id]["uang"] -= fuel_cost
    target_vehicle["total_distance"] += jarak
    data[user_id]["transportation"]["total_distance"] += jarak
    
    # Kurangi kondisi kendaraan
    wear_rate = max(1, jarak // 100)  # 1% per 100km
    target_vehicle["condition"] = max(0, target_vehicle["condition"] - wear_rate)
    
    # Speed bonus affects work cooldown reduction
    work_bonus = ""
    if data[user_id].get("last_work"):
        last_work = datetime.fromisoformat(data[user_id]["last_work"])
        time_reduction = int(3600 / vehicle_data["speed_bonus"])  # Reduce cooldown
        new_time = last_work + timedelta(seconds=time_reduction)
        data[user_id]["last_work"] = new_time.isoformat()
        work_bonus = f"\n⚡ Cooldown kerja berkurang {time_reduction//60} menit!"
    
    embed = discord.Embed(title="🗺️ Perjalanan Selesai", color=0x00ff00)
    embed.add_field(name="🚗 Kendaraan", value=target_vehicle["name"], inline=True)
    embed.add_field(name="📏 Jarak", value=f"{jarak} km", inline=True)
    embed.add_field(name="⛽ BBM", value=f"Rp{fuel_cost:,}", inline=True)
    embed.add_field(name="🔧 Kondisi", value=f"{target_vehicle['condition']}%", inline=True)
    embed.add_field(name="📊 Total Jarak", value=f"{target_vehicle['total_distance']:,} km", inline=True)
    
    if work_bonus:
        embed.add_field(name="💼 Bonus", value=work_bonus, inline=False)
    
    if target_vehicle["condition"] <= 20:
        embed.add_field(name="⚠️ Peringatan", value="Kendaraan butuh maintenance segera!", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !bengkel - Service kendaraan
@bot.command()
async def bengkel(ctx, vehicle_id=None):
    if not vehicle_id:
        await ctx.send("🔧 **Cara Service Kendaraan:**\n`!bengkel [vehicle_id]` - Service kendaraan\n\n📋 `!garasiqu` untuk lihat ID kendaraan")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_transportation()
    
    # Find vehicle
    target_vehicle = None
    full_vehicle_id = None
    
    for v_id, v_info in data[user_id]["transportation"]["owned_vehicles"].items():
        if v_id.endswith(vehicle_id) or v_id[-8:] == vehicle_id:
            target_vehicle = v_info
            full_vehicle_id = v_id
            break
    
    if not target_vehicle:
        await ctx.send(f"❌ Kendaraan dengan ID `{vehicle_id}` tidak ditemukan.")
        return
    
    if target_vehicle["condition"] >= 90:
        await ctx.send("❌ Kendaraan masih dalam kondisi baik. Tidak perlu service.")
        return
    
    vehicle_data = vehicles[target_vehicle["type"]]
    
    # Calculate service cost
    condition_loss = 100 - target_vehicle["condition"]
    base_cost = vehicle_data["maintenance_cost"]
    service_cost = int(base_cost * (condition_loss / 100))
    
    if data[user_id]["uang"] < service_cost:
        await ctx.send(f"❌ Uang tidak cukup untuk service. Butuh Rp{service_cost:,}")
        return
    
    # Proses service
    data[user_id]["uang"] -= service_cost
    old_condition = target_vehicle["condition"]
    target_vehicle["condition"] = min(100, target_vehicle["condition"] + condition_loss)
    target_vehicle["last_maintenance"] = int(time.time())
    
    embed = discord.Embed(title="🔧 Service Selesai", color=0x00ff00)
    embed.add_field(name="🚗 Kendaraan", value=target_vehicle["name"], inline=True)
    embed.add_field(name="💰 Biaya", value=f"Rp{service_cost:,}", inline=True)
    embed.add_field(name="🔧 Kondisi", value=f"{old_condition}% → {target_vehicle['condition']}%", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# ===== EDUCATION SYSTEM =====

# Database universitas dan jurusan
universities = {
    "ui": {
        "nama": "Universitas Indonesia",
        "biaya_per_semester": 8000000,
        "prestige": 95,
        "jurusan": ["kedokteran", "teknik", "ekonomi", "hukum", "psikologi"]
    },
    "itb": {
        "nama": "Institut Teknologi Bandung",
        "biaya_per_semester": 7500000,
        "prestige": 90,
        "jurusan": ["teknik", "sains", "arsitektur", "seni"]
    },
    "ugm": {
        "nama": "Universitas Gadjah Mada",
        "biaya_per_semester": 7000000,
        "prestige": 88,
        "jurusan": ["kedokteran", "teknik", "ekonomi", "hukum", "pertanian"]
    },
    "its": {
        "nama": "Institut Teknologi Sepuluh Nopember",
        "biaya_per_semester": 6500000,
        "prestige": 85,
        "jurusan": ["teknik", "sains", "teknologi_informasi"]
    },
    "unpad": {
        "nama": "Universitas Padjadjaran",
        "biaya_per_semester": 6000000,
        "prestige": 82,
        "jurusan": ["kedokteran", "ekonomi", "hukum", "komunikasi"]
    },
    "universitas_swasta": {
        "nama": "Universitas Swasta",
        "biaya_per_semester": 5000000,
        "prestige": 70,
        "jurusan": ["ekonomi", "teknik", "komunikasi", "psikologi"]
    }
}

# Database jurusan dengan job unlock
majors = {
    "kedokteran": {
        "nama": "Kedokteran",
        "durasi": 7,  # semester
        "job_unlocks": ["dokter umum", "dokter gigi", "dokter anak", "dokter bedah"],
        "salary_bonus": 0.5,  # 50% bonus gaji
        "requirement_level": 15
    },
    "teknik": {
        "nama": "Teknik",
        "durasi": 8,
        "job_unlocks": ["programmer", "data analyst", "montir"],
        "salary_bonus": 0.3,
        "requirement_level": 10
    },
    "ekonomi": {
        "nama": "Ekonomi",
        "durasi": 6,
        "job_unlocks": ["cfo", "accounting", "staff_admin"],
        "salary_bonus": 0.25,
        "requirement_level": 8
    },
    "hukum": {
        "nama": "Hukum",
        "durasi": 8,
        "job_unlocks": ["hakim", "pengacara", "jaksa"],
        "salary_bonus": 0.4,
        "requirement_level": 12
    },
    "psikologi": {
        "nama": "Psikologi",
        "durasi": 6,
        "job_unlocks": ["hrd_manager", "customer_service"],
        "salary_bonus": 0.2,
        "requirement_level": 8
    },
    "komunikasi": {
        "nama": "Komunikasi",
        "durasi": 6,
        "job_unlocks": ["marketing_manager", "customer_service"],
        "salary_bonus": 0.15,
        "requirement_level": 6
    },
    "sains": {
        "nama": "Sains",
        "durasi": 6,
        "job_unlocks": ["data analyst", "dosen"],
        "salary_bonus": 0.25,
        "requirement_level": 10
    },
    "arsitektur": {
        "nama": "Arsitektur",
        "durasi": 8,
        "job_unlocks": ["supervisor"],
        "salary_bonus": 0.3,
        "requirement_level": 12
    },
    "seni": {
        "nama": "Seni",
        "durasi": 6,
        "job_unlocks": [],
        "salary_bonus": 0.1,
        "requirement_level": 5
    },
    "pertanian": {
        "nama": "Pertanian",
        "durasi": 6,
        "job_unlocks": [],
        "salary_bonus": 0.15,
        "requirement_level": 6
    },
    "teknologi_informasi": {
        "nama": "Teknologi Informasi",
        "durasi": 7,
        "job_unlocks": ["programmer", "data analyst", "it_manager"],
        "salary_bonus": 0.35,
        "requirement_level": 12
    }
}

# Initialize education system
def init_education():
    for user_id in data:
        if user_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings"]:
            continue
        if "education" not in data[user_id]:
            data[user_id]["education"] = {
                "enrolled": False,
                "university": None,
                "major": None,
                "semester": 0,
                "gpa": 0.0,
                "total_credits": 0,
                "tuition_paid": 0,
                "degrees": [],  # Gelar yang sudah diselesaikan
                "scholarships": [],
                "last_study": 0
            }
    save_data(data)

# !universitas - Lihat daftar universitas
@bot.command()
async def universitas(ctx):
    init_education()
    
    embed = discord.Embed(title="🎓 Daftar Universitas", color=0x2ecc71)
    
    for uni_key, uni_data in universities.items():
        jurusan_text = ", ".join([majors[j]["nama"] for j in uni_data["jurusan"]])
        
        embed.add_field(
            name=f"🏛️ {uni_data['nama']}",
            value=f"💰 Rp{uni_data['biaya_per_semester']:,}/semester\n⭐ Prestige: {uni_data['prestige']}/100\n📚 Jurusan: {jurusan_text}\n🆔 {uni_key}",
            inline=True
        )
    
    embed.set_footer(text="!daftar_kuliah [uni_id] [jurusan] untuk mendaftar")
    await ctx.send(embed=embed)

# !daftar_kuliah - Daftar kuliah
@bot.command()
async def daftar_kuliah(ctx, uni_id=None, jurusan=None):
    if not uni_id or not jurusan:
        await ctx.send("🎓 **Cara Daftar Kuliah:**\n`!daftar_kuliah [uni_id] [jurusan]` - Daftar kuliah\n\n📋 `!universitas` untuk lihat daftar universitas\n📖 `!jurusan` untuk info jurusan")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_education()
    
    if data[user_id]["education"]["enrolled"]:
        await ctx.send("❌ Kamu sudah kuliah. Selesaikan dulu atau keluar dengan `!keluar_kuliah`")
        return
    
    if uni_id not in universities:
        await ctx.send("❌ Universitas tidak ditemukan. Gunakan `!universitas` untuk melihat daftar.")
        return
    
    if jurusan not in majors:
        await ctx.send("❌ Jurusan tidak ditemukan. Gunakan `!jurusan` untuk melihat daftar.")
        return
    
    uni_data = universities[uni_id]
    major_data = majors[jurusan]
    
    if jurusan not in uni_data["jurusan"]:
        await ctx.send(f"❌ Jurusan {major_data['nama']} tidak tersedia di {uni_data['nama']}")
        return
    
    # Cek requirement level
    level = calculate_level(data[user_id]["xp"])
    if level < major_data["requirement_level"]:
        await ctx.send(f"❌ Level kamu ({level}) belum cukup. Butuh minimal level {major_data['requirement_level']}.")
        return
    
    # Biaya pendaftaran + semester pertama
    total_cost = uni_data["biaya_per_semester"] + 500000  # +500k biaya pendaftaran
    
    if data[user_id]["uang"] < total_cost:
        await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{total_cost:,}")
        return
    
    # Proses pendaftaran
    data[user_id]["uang"] -= total_cost
    data[user_id]["education"] = {
        "enrolled": True,
        "university": uni_id,
        "major": jurusan,
        "semester": 1,
        "gpa": 3.5,  # Starting GPA
        "total_credits": 0,
        "tuition_paid": uni_data["biaya_per_semester"],
        "degrees": data[user_id]["education"].get("degrees", []),
        "scholarships": [],
        "last_study": int(time.time())
    }
    
    embed = discord.Embed(title="🎉 Diterima Kuliah!", color=0x00ff00)
    embed.add_field(name="🏛️ Universitas", value=uni_data["nama"], inline=True)
    embed.add_field(name="📚 Jurusan", value=major_data["nama"], inline=True)
    embed.add_field(name="💰 Biaya", value=f"Rp{total_cost:,}", inline=True)
    embed.add_field(name="📊 Semester", value="1", inline=True)
    embed.add_field(name="⭐ GPA", value="3.5", inline=True)
    embed.add_field(name="⏰ Durasi", value=f"{major_data['durasi']} semester", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !belajar - Belajar untuk meningkatkan GPA
@bot.command()
async def belajar(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_education()
    
    if not data[user_id]["education"]["enrolled"]:
        await ctx.send("❌ Kamu tidak sedang kuliah. Daftar dulu dengan `!daftar_kuliah`")
        return
    
    # Cooldown 6 jam
    current_time = int(time.time())
    last_study = data[user_id]["education"]["last_study"]
    
    if current_time - last_study < 21600:  # 6 jam
        remaining = 21600 - (current_time - last_study)
        await ctx.send(f"⏰ Tunggu {remaining//3600} jam lagi untuk belajar.")
        return
    
    # Study session
    study_quality = random.uniform(0.5, 1.0)  # Kualitas belajar
    gpa_increase = study_quality * 0.1  # Max 0.1 increase
    credits_earned = random.randint(2, 4)
    
    old_gpa = data[user_id]["education"]["gpa"]
    data[user_id]["education"]["gpa"] = min(4.0, old_gpa + gpa_increase)
    data[user_id]["education"]["total_credits"] += credits_earned
    data[user_id]["education"]["last_study"] = current_time
    data[user_id]["xp"] += 25  # XP dari belajar
    
    embed = discord.Embed(title="📚 Sesi Belajar Selesai", color=0x3498db)
    embed.add_field(name="📈 GPA", value=f"{old_gpa:.2f} → {data[user_id]['education']['gpa']:.2f}", inline=True)
    embed.add_field(name="🎯 Credits", value=f"+{credits_earned} SKS", inline=True)
    embed.add_field(name="⭐ XP", value="+25", inline=True)
    embed.add_field(name="📊 Kualitas", value=f"{int(study_quality*100)}%", inline=True)
    
    # Cek apakah bisa naik semester
    major_data = majors[data[user_id]["education"]["major"]]
    credits_needed = 20 * data[user_id]["education"]["semester"]  # 20 SKS per semester
    
    if data[user_id]["education"]["total_credits"] >= credits_needed and data[user_id]["education"]["gpa"] >= 2.0:
        if data[user_id]["education"]["semester"] < major_data["durasi"]:
            data[user_id]["education"]["semester"] += 1
            embed.add_field(name="🎉 Naik Semester", value=f"Semester {data[user_id]['education']['semester']}", inline=False)
        elif data[user_id]["education"]["semester"] == major_data["durasi"]:
            # Lulus!
            await proses_kelulusan(ctx, user_id)
            return
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

async def proses_kelulusan(ctx, user_id):
    """Proses kelulusan kuliah"""
    education_data = data[user_id]["education"]
    uni_data = universities[education_data["university"]]
    major_data = majors[education_data["major"]]
    
    # Determine degree based on GPA
    if education_data["gpa"] >= 3.7:
        degree_honor = "Summa Cum Laude"
        bonus_multiplier = 2.0
    elif education_data["gpa"] >= 3.5:
        degree_honor = "Magna Cum Laude"
        bonus_multiplier = 1.5
    elif education_data["gpa"] >= 3.0:
        degree_honor = "Cum Laude"
        bonus_multiplier = 1.2
    else:
        degree_honor = "Lulus"
        bonus_multiplier = 1.0
    
    # Add degree to collection
    degree = {
        "major": education_data["major"],
        "major_name": major_data["nama"],
        "university": education_data["university"],
        "university_name": uni_data["nama"],
        "gpa": education_data["gpa"],
        "honor": degree_honor,
        "graduation_date": int(time.time()),
        "salary_bonus": major_data["salary_bonus"] * bonus_multiplier
    }
    
    data[user_id]["education"]["degrees"].append(degree)
    
    # Reset education status
    data[user_id]["education"]["enrolled"] = False
    data[user_id]["education"]["university"] = None
    data[user_id]["education"]["major"] = None
    data[user_id]["education"]["semester"] = 0
    
    # Graduation bonus
    graduation_bonus = uni_data["prestige"] * 10000 * bonus_multiplier
    data[user_id]["uang"] += int(graduation_bonus)
    data[user_id]["xp"] += 200
    
    embed = discord.Embed(title="🎓 SELAMAT LULUS!", color=0xffd700)
    embed.add_field(name="🏛️ Universitas", value=uni_data["nama"], inline=True)
    embed.add_field(name="📚 Jurusan", value=major_data["nama"], inline=True)
    embed.add_field(name="⭐ GPA", value=f"{education_data['gpa']:.2f}", inline=True)
    embed.add_field(name="🏆 Predikat", value=degree_honor, inline=True)
    embed.add_field(name="💰 Bonus", value=f"Rp{int(graduation_bonus):,}", inline=True)
    embed.add_field(name="💼 Job Unlock", value=", ".join([jobs[job]["nama"] if job in jobs else job.title() for job in major_data["job_unlocks"]]), inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !rapor - Lihat status pendidikan
@bot.command()
async def rapor(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    if user_id not in data:
        await ctx.send("User belum terdaftar.")
        return
    
    create_user_profile(user_id)
    init_education()
    
    education_data = data[user_id]["education"]
    
    embed = discord.Embed(title=f"🎓 Rapor Pendidikan {member.display_name}", color=0x2ecc71)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    if education_data["enrolled"]:
        # Currently studying
        uni_data = universities[education_data["university"]]
        major_data = majors[education_data["major"]]
        
        embed.add_field(name="📚 Status", value="Sedang Kuliah", inline=True)
        embed.add_field(name="🏛️ Universitas", value=uni_data["nama"], inline=True)
        embed.add_field(name="📖 Jurusan", value=major_data["nama"], inline=True)
        embed.add_field(name="📊 Semester", value=f"{education_data['semester']}/{major_data['durasi']}", inline=True)
        embed.add_field(name="⭐ GPA", value=f"{education_data['gpa']:.2f}/4.0", inline=True)
        embed.add_field(name="🎯 Credits", value=f"{education_data['total_credits']} SKS", inline=True)
        
        # Progress bar
        progress = (education_data['semester'] / major_data['durasi']) * 100
        embed.add_field(name="📈 Progress", value=f"{progress:.1f}%", inline=False)
    else:
        embed.add_field(name="📚 Status", value="Tidak sedang kuliah", inline=False)
    
    # Degrees earned
    if education_data["degrees"]:
        degree_text = ""
        total_salary_bonus = 0
        
        for degree in education_data["degrees"]:
            degree_text += f"🎓 {degree['major_name']} - {degree['university_name']}\n"
            degree_text += f"   GPA: {degree['gpa']:.2f} ({degree['honor']})\n"
            total_salary_bonus += degree['salary_bonus']
        
        embed.add_field(name="🏆 Gelar yang Dimiliki", value=degree_text[:1024], inline=False)
        embed.add_field(name="💰 Total Salary Bonus", value=f"+{total_salary_bonus*100:.1f}%", inline=True)
    
    await ctx.send(embed=embed)

# !jurusan - Info semua jurusan
@bot.command()
async def jurusan(ctx):
    embed = discord.Embed(title="📚 Daftar Jurusan", color=0x3498db)
    
    for major_key, major_data in majors.items():
        job_list = ", ".join([jobs[job]["deskripsi"][:20] if job in jobs else job.title() for job in major_data["job_unlocks"][:3]])
        if not job_list:
            job_list = "General career"
        
        embed.add_field(
            name=f"📖 {major_data['nama']}",
            value=f"⏰ {major_data['durasi']} semester\n💰 +{major_data['salary_bonus']*100:.0f}% gaji\n📊 Lv.{major_data['requirement_level']}+\n💼 Jobs: {job_list}\n🆔 {major_key}",
            inline=True
        )
    
    embed.set_footer(text="Jurusan membuka akses ke pekerjaan premium dengan gaji bonus!")
    await ctx.send(embed=embed)

# ===== SISTEM TABUNGAN & INVESTASI =====

# Command tabung sudah didefinisikan di atas, menghapus duplikat

# !tariuang - Tarik uang dari tabungan (renamed to avoid conflict)
@bot.command()
async def tariuang(ctx, jumlah_or_all=None):
    if jumlah_or_all is None:
        await ctx.send("💳 **Cara Tarik Uang:**\n`!tariuang [jumlah]` - Tarik dari tabungan\n`!tariuang semua` - Tarik semua")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_banking_system()
    
    if "bank_account" not in data[user_id]:
        await ctx.send("❌ Kamu belum punya rekening bank. Menabung dulu dengan `!tabung [jumlah]`")
        return
    
    # Hitung bunga terlebih dahulu
    calculate_bank_interest(user_id)
    
    saldo_tabungan = data[user_id]["bank_account"]["tabungan"]
    if saldo_tabungan <= 0:
        await ctx.send("❌ Tidak ada uang di tabungan.")
        return
    
    if jumlah_or_all.lower() == "semua":
        jumlah = saldo_tabungan
    else:
        try:
            jumlah = int(jumlah_or_all)
        except ValueError:
            await ctx.send("❌ Jumlah harus berupa angka atau 'semua'")
            return
    
    if jumlah > saldo_tabungan:
        await ctx.send(f"❌ Saldo tabungan tidak cukup. Tersedia: Rp{saldo_tabungan:,}")
        return
    
    # Penalty jika tarik sebelum 30 hari
    last_deposit = data[user_id]["bank_account"]["last_deposit"]
    current_time = int(time.time())
    days_since_deposit = (current_time - last_deposit) // 86400
    
    penalty = 0
    if days_since_deposit < 30:
        penalty = int(jumlah * 0.02)  # 2% penalty
        jumlah_bersih = jumlah - penalty
    else:
        jumlah_bersih = jumlah
    
    data[user_id]["bank_account"]["tabungan"] -= jumlah
    data[user_id]["uang"] += jumlah_bersih
    
    embed = discord.Embed(title="💳 Penarikan Tabungan", color=0xff9900)
    embed.add_field(name="💰 Jumlah Tarik", value=f"Rp{jumlah:,}", inline=True)
    if penalty > 0:
        embed.add_field(name="⚠️ Penalty", value=f"Rp{penalty:,} (2%)", inline=True)
        embed.add_field(name="💵 Diterima", value=f"Rp{jumlah_bersih:,}", inline=True)
    else:
        embed.add_field(name="💵 Diterima", value=f"Rp{jumlah_bersih:,}", inline=True)
    embed.add_field(name="💳 Sisa Tabungan", value=f"Rp{data[user_id]['bank_account']['tabungan']:,}", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !invest - Sistem investasi
@bot.command()
async def invest(ctx, action=None, jumlah: int = None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if "investments" not in data[user_id]:
        data[user_id]["investments"] = {
            "saham": 0,
            "emas": 0,
            "crypto": 0,
            "last_update": int(time.time()),
            "total_invested": 0,
            "total_profit": 0
        }
    
    if action is None:
        # Show investment portfolio
        inv_data = data[user_id]["investments"]
        current_time = int(time.time())
        
        # Update investment values (simulate market changes)
        if current_time - inv_data["last_update"] >= 3600:  # Update setiap jam
            # Random market changes (-10% to +15%)
            saham_change = random.uniform(-0.1, 0.15)
            emas_change = random.uniform(-0.05, 0.1)  # Emas lebih stabil
            crypto_change = random.uniform(-0.2, 0.3)  # Crypto lebih volatile
            
            inv_data["saham"] = int(inv_data["saham"] * (1 + saham_change))
            inv_data["emas"] = int(inv_data["emas"] * (1 + emas_change))
            inv_data["crypto"] = int(inv_data["crypto"] * (1 + crypto_change))
            inv_data["last_update"] = current_time
        
        total_value = inv_data["saham"] + inv_data["emas"] + inv_data["crypto"]
        profit_loss = total_value - inv_data["total_invested"]
        
        embed = discord.Embed(title="📈 Portfolio Investasi", color=0x9b59b6)
        embed.add_field(name="📊 Saham", value=f"Rp{inv_data['saham']:,}", inline=True)
        embed.add_field(name="🥇 Emas", value=f"Rp{inv_data['emas']:,}", inline=True)
        embed.add_field(name="₿ Crypto", value=f"Rp{inv_data['crypto']:,}", inline=True)
        embed.add_field(name="💎 Total Nilai", value=f"Rp{total_value:,}", inline=True)
        embed.add_field(name="💰 Total Invest", value=f"Rp{inv_data['total_invested']:,}", inline=True)
        
        if profit_loss >= 0:
            embed.add_field(name="📈 Profit", value=f"+Rp{profit_loss:,}", inline=True)
        else:
            embed.add_field(name="📉 Loss", value=f"-Rp{abs(profit_loss):,}", inline=True)
        
        embed.set_footer(text="!invest beli [saham/emas/crypto] [jumlah] | !invest jual [jenis] [jumlah]")
        await ctx.send(embed=embed)
        return
    
    if action == "beli":
        await ctx.send("📈 **Cara Investasi:**\n`!invest beli saham [jumlah]` - Beli saham\n`!invest beli emas [jumlah]` - Beli emas\n`!invest beli crypto [jumlah]` - Beli cryptocurrency\n\n💡 **Tips:** Diversifikasi untuk mengurangi risiko!")
        return
    
    await ctx.send("❌ Command tidak valid. Gunakan `!invest` untuk melihat portfolio atau `!invest beli` untuk investasi.")

# !investbeli - Beli investasi
@bot.command()
async def investbeli(ctx, jenis=None, jumlah: int = None):
    if not jenis or not jumlah:
        await ctx.send("📈 **Cara Beli Investasi:**\n`!investbeli saham [jumlah]`\n`!investbeli emas [jumlah]`\n`!investbeli crypto [jumlah]`")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if "investments" not in data[user_id]:
        data[user_id]["investments"] = {
            "saham": 0,
            "emas": 0,
            "crypto": 0,
            "last_update": int(time.time()),
            "total_invested": 0,
            "total_profit": 0
        }
    
    if jumlah <= 0:
        await ctx.send("❌ Jumlah investasi harus lebih dari 0.")
        return
    
    if data[user_id]["uang"] < jumlah:
        await ctx.send("❌ Uang tidak cukup untuk investasi.")
        return
    
    valid_types = ["saham", "emas", "crypto"]
    if jenis.lower() not in valid_types:
        await ctx.send(f"❌ Jenis investasi tidak valid. Pilih: {', '.join(valid_types)}")
        return
    
    # Fee investasi
    fee = int(jumlah * 0.02)  # 2% fee
    total_cost = jumlah + fee
    
    if data[user_id]["uang"] < total_cost:
        await ctx.send(f"❌ Uang tidak cukup. Butuh Rp{total_cost:,} (termasuk fee Rp{fee:,})")
        return
    
    data[user_id]["uang"] -= total_cost
    data[user_id]["investments"][jenis.lower()] += jumlah
    data[user_id]["investments"]["total_invested"] += jumlah
    
    risk_level = {"saham": "Menengah", "emas": "Rendah", "crypto": "Tinggi"}
    
    embed = discord.Embed(title="📈 Investasi Berhasil", color=0x00ff00)
    embed.add_field(name="💰 Jenis", value=jenis.title(), inline=True)
    embed.add_field(name="💵 Jumlah", value=f"Rp{jumlah:,}", inline=True)
    embed.add_field(name="💳 Fee", value=f"Rp{fee:,}", inline=True)
    embed.add_field(name="⚠️ Risiko", value=risk_level[jenis.lower()], inline=True)
    embed.add_field(name="📊 Total Investasi", value=f"Rp{data[user_id]['investments']['total_invested']:,}", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# ===== SISTEM PERUSAHAAN & JABATAN =====

# Database jabatan perusahaan
company_positions = {
    "ceo": {
        "nama": "Chief Executive Officer",
        "gaji": 10000000,
        "requirement_level": 40,
        "max_employees": 50,
        "can_hire": True,
        "can_fire": True,
        "deskripsi": "Memimpin seluruh perusahaan dan membuat keputusan strategis"
    },
    "coo": {
        "nama": "Chief Operating Officer", 
        "gaji": 8000000,
        "requirement_level": 35,
        "max_employees": 30,
        "can_hire": True,
        "can_fire": True,
        "deskripsi": "Mengawasi operasional harian perusahaan"
    },
    "cfo": {
        "nama": "Chief Financial Officer",
        "gaji": 8000000,
        "requirement_level": 35,
        "max_employees": 20,
        "can_hire": True,
        "can_fire": False,
        "deskripsi": "Mengelola keuangan dan strategi investasi perusahaan"
    },
    "hrd_manager": {
        "nama": "HRD Manager",
        "gaji": 5000000,
        "requirement_level": 25,
        "max_employees": 15,
        "can_hire": True,
        "can_fire": False,
        "deskripsi": "Mengelola sumber daya manusia dan rekrutmen"
    },
    "marketing_manager": {
        "nama": "Marketing Manager",
        "gaji": 4500000,
        "requirement_level": 20,
        "max_employees": 10,
        "can_hire": False,
        "can_fire": False,
        "deskripsi": "Mengembangkan strategi pemasaran dan brand awareness"
    },
    "it_manager": {
        "nama": "IT Manager",
        "gaji": 5000000,
        "requirement_level": 25,
        "max_employees": 15,
        "can_hire": False,
        "can_fire": False,
        "deskripsi": "Mengelola infrastruktur teknologi informasi"
    },
    "supervisor": {
        "nama": "Supervisor",
        "gaji": 3000000,
        "requirement_level": 15,
        "max_employees": 8,
        "can_hire": False,
        "can_fire": False,
        "deskripsi": "Mengawasi tim dan memastikan target tercapai"
    },
    "staff_admin": {
        "nama": "Staff Admin",
        "gaji": 2000000,
        "requirement_level": 10,
        "max_employees": 5,
        "can_hire": False,
        "can_fire": False,
        "deskripsi": "Menangani administrasi dan dokumentasi"
    },
    "customer_service": {
        "nama": "Customer Service",
        "gaji": 1800000,
        "requirement_level": 8,
        "max_employees": 3,
        "can_hire": False,
        "can_fire": False,
        "deskripsi": "Melayani keluhan dan pertanyaan pelanggan"
    },
    "accounting": {
        "nama": "Staff Accounting",
        "gaji": 2200000,
        "requirement_level": 12,
        "max_employees": 5,
        "can_hire": False,
        "can_fire": False,
        "deskripsi": "Mengelola pembukuan dan laporan keuangan"
    },
    "security": {
        "nama": "Security",
        "gaji": 1500000,
        "requirement_level": 5,
        "max_employees": 3,
        "can_hire": False,
        "can_fire": False,
        "deskripsi": "Menjaga keamanan kantor dan aset perusahaan"
    },
    "office_boy": {
        "nama": "Office Boy",
        "gaji": 1200000,
        "requirement_level": 3,
        "max_employees": 2,
        "can_hire": False,
        "can_fire": False,
        "deskripsi": "Membantu kebutuhan operasional kantor dan kebersihan"
    },
    "driver": {
        "nama": "Driver",
        "gaji": 1400000,
        "requirement_level": 5,
        "max_employees": 3,
        "can_hire": False,
        "can_fire": False,
        "deskripsi": "Mengantar karyawan dan menjalankan tugas transportasi"
    },
    "cleaning_service": {
        "nama": "Cleaning Service",
        "gaji": 1100000,
        "requirement_level": 1,
        "max_employees": 2,
        "can_hire": False,
        "can_fire": False,
        "deskripsi": "Menjaga kebersihan lingkungan kerja"
    }
}

# !buatperusahaan - Buat perusahaan baru
@bot.command()
async def buatperusahaan(ctx, *, nama_perusahaan=None):
    if not nama_perusahaan:
        await ctx.send("🏢 **Cara Buat Perusahaan:**\n`!buatperusahaan [nama]` - Buat perusahaan baru\n\n💰 **Biaya:** Rp50.000.000\n📊 **Requirement:** Level 30+\n👔 **Otomatis jadi CEO**")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    level = calculate_level(data[user_id]["xp"])
    if level < 30:
        await ctx.send(f"❌ Level kamu ({level}) belum cukup. Minimal level 30 untuk membuat perusahaan.")
        return
    
    company_cost = 50000000
    if data[user_id]["uang"] < company_cost:
        await ctx.send(f"❌ Uang tidak cukup. Kamu butuh Rp{company_cost:,} untuk membuat perusahaan.")
        return
    
    # Cek apakah sudah punya perusahaan atau bekerja di perusahaan
    if data[user_id].get("company_owned"):
        await ctx.send("❌ Kamu sudah memiliki perusahaan.")
        return
    
    if data[user_id].get("company_employee"):
        await ctx.send("❌ Kamu sudah bekerja di perusahaan lain. Resign dulu dengan `!resignperusahaan`")
        return
    
    # Create company
    company_id = f"company_{user_id}_{int(time.time())}"
    
    if "companies" not in data:
        data["companies"] = {}
    
    data["companies"][company_id] = {
        "name": nama_perusahaan,
        "owner_id": user_id,
        "founded": int(time.time()),
        "employees": {
            user_id: {
                "position": "ceo",
                "salary": company_positions["ceo"]["gaji"],
                "hire_date": int(time.time()),
                "hired_by": user_id
            }
        },
        "balance": 10000000,  # Modal awal
        "revenue": 0,
        "total_salary_cost": company_positions["ceo"]["gaji"],
        "last_salary_payment": int(time.time())
    }
    
    # Update user data
    data[user_id]["uang"] -= company_cost
    data[user_id]["company_owned"] = company_id
    data[user_id]["company_employee"] = {
        "company_id": company_id,
        "position": "ceo"
    }
    
    embed = discord.Embed(title="🏢 Perusahaan Berhasil Dibuat!", color=0xffd700)
    embed.add_field(name="🏢 Nama", value=nama_perusahaan, inline=True)
    embed.add_field(name="👔 Jabatan", value="CEO", inline=True)
    embed.add_field(name="💰 Modal Awal", value="Rp10.000.000", inline=True)
    embed.add_field(name="💵 Gaji CEO", value=f"Rp{company_positions['ceo']['gaji']:,}", inline=True)
    embed.add_field(name="📈 Status", value="Siap beroperasi!", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !perusahaan - Info perusahaan
@bot.command()
async def perusahaan(ctx, info_type=None):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if info_type == "jabatan":
        embed = discord.Embed(title="👔 Daftar Jabatan Perusahaan", color=0x9b59b6)
        
        exec_positions = "**👑 Executive Level:**\n"
        for pos_id, pos_data in company_positions.items():
            if pos_data["requirement_level"] >= 30:
                exec_positions += f"• {pos_data['nama']} (Rp{pos_data['gaji']:,}) - Lv.{pos_data['requirement_level']}\n"
        
        manager_positions = "**🎯 Manager Level:**\n"
        for pos_id, pos_data in company_positions.items():
            if 15 <= pos_data["requirement_level"] < 30:
                manager_positions += f"• {pos_data['nama']} (Rp{pos_data['gaji']:,}) - Lv.{pos_data['requirement_level']}\n"
        
        staff_positions = "**📋 Staff Level:**\n"
        for pos_id, pos_data in company_positions.items():
            if pos_data["requirement_level"] < 15:
                staff_positions += f"• {pos_data['nama']} (Rp{pos_data['gaji']:,}) - Lv.{pos_data['requirement_level']}\n"
        
        embed.add_field(name="\u200b", value=exec_positions, inline=True)
        embed.add_field(name="\u200b", value=manager_positions, inline=True)
        embed.add_field(name="\u200b", value=staff_positions, inline=True)
        
        embed.set_footer(text="!hire [user] [jabatan] untuk rekrut | !perusahaan untuk info perusahaan")
        await ctx.send(embed=embed)
        return
    
    # Info perusahaan user
    company_data = None
    company_id = None
    
    # Cek apakah punya perusahaan
    if data[user_id].get("company_owned"):
        company_id = data[user_id]["company_owned"]
        company_data = data.get("companies", {}).get(company_id)
        is_owner = True
    # Cek apakah employee
    elif data[user_id].get("company_employee"):
        company_id = data[user_id]["company_employee"]["company_id"]
        company_data = data.get("companies", {}).get(company_id)
        is_owner = False
    
    if not company_data:
        await ctx.send("❌ Kamu tidak terhubung dengan perusahaan manapun.\n\n🏢 `!buatperusahaan [nama]` - Buat perusahaan baru\n🔍 `!perusahaan jabatan` - Lihat daftar jabatan")
        return
    
    # Calculate company stats
    total_employees = len(company_data["employees"])
    monthly_salary_cost = company_data["total_salary_cost"]
    
    embed = discord.Embed(title=f"🏢 {company_data['name']}", color=0x0099ff)
    embed.add_field(name="👥 Total Karyawan", value=f"{total_employees} orang", inline=True)
    embed.add_field(name="💰 Saldo Perusahaan", value=f"Rp{company_data['balance']:,}", inline=True)
    embed.add_field(name="💵 Biaya Gaji/Bulan", value=f"Rp{monthly_salary_cost:,}", inline=True)
    
    if is_owner:
        embed.add_field(name="👑 Status", value="Owner (CEO)", inline=True)
        embed.add_field(name="📈 Revenue", value=f"Rp{company_data['revenue']:,}", inline=True)
        profit = company_data["revenue"] - monthly_salary_cost
        embed.add_field(name="📊 Profit/Loss", value=f"Rp{profit:,}", inline=True)
    else:
        user_employee_data = company_data["employees"].get(user_id)
        if user_employee_data:
            position_name = company_positions[user_employee_data["position"]]["nama"]
            embed.add_field(name="👔 Jabatan", value=position_name, inline=True)
            embed.add_field(name="💰 Gaji", value=f"Rp{user_employee_data['salary']:,}", inline=True)
    
    # List karyawan (max 10)
    employee_list = ""
    for emp_id, emp_data in list(company_data["employees"].items())[:10]:
        try:
            user = bot.get_user(int(emp_id))
            username = user.display_name if user else f"User {emp_id[:4]}..."
            position_name = company_positions[emp_data["position"]]["nama"]
            employee_list += f"• {username} - {position_name}\n"
        except:
            continue
    
    if employee_list:
        embed.add_field(name="👥 Karyawan", value=employee_list[:1024], inline=False)
    
    embed.set_footer(text="!hire [user] [jabatan] | !fire [user] | !gajiperusahaan | !perusahaan jabatan")
    await ctx.send(embed=embed)

# Initialize interview system
def init_interview_system():
    if "job_applications" not in data:
        data["job_applications"] = {}
    if "company_meetings" not in data:
        data["company_meetings"] = {}
    save_data(data)

# !lamarskerja - Lamar kerja ke perusahaan (realistic job application)
@bot.command()
async def lamarkerja(ctx, company_name=None, jabatan=None):
    if not company_name or not jabatan:
        await ctx.send("💼 **Cara Lamar Kerja:**\n`!lamarkerja [nama_perusahaan] [jabatan]`\n\n📋 `!perusahaanlist` - Lihat daftar perusahaan\n`!perusahaan jabatan` - Lihat daftar jabatan")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_interview_system()
    
    # Cek apakah sudah bekerja
    if data[user_id].get("company_employee"):
        await ctx.send("❌ Kamu sudah bekerja di perusahaan lain. Resign dulu jika ingin pindah.")
        return
    
    # Cari perusahaan berdasarkan nama
    target_company = None
    target_company_id = None
    
    for company_id, company_data in data.get("companies", {}).items():
        if company_data["name"].lower().find(company_name.lower()) != -1:
            target_company = company_data
            target_company_id = company_id
            break
    
    if not target_company:
        await ctx.send(f"❌ Perusahaan '{company_name}' tidak ditemukan. Gunakan `!perusahaanlist` untuk melihat daftar.")
        return
    
    # Validasi jabatan
    if jabatan.lower() not in company_positions:
        await ctx.send(f"❌ Jabatan '{jabatan}' tidak valid. Gunakan `!perusahaan jabatan` untuk melihat daftar.")
        return
    
    position_data = company_positions[jabatan.lower()]
    
    # Cek level requirement
    user_level = calculate_level(data[user_id]["xp"])
    if user_level < position_data["requirement_level"]:
        await ctx.send(f"❌ Level kamu ({user_level}) belum memenuhi syarat. Butuh minimal level {position_data['requirement_level']}.")
        return
    
    # Generate application ID
    application_id = f"app_{user_id}_{int(time.time())}"
    
    # Simpan lamaran kerja
    data["job_applications"][application_id] = {
        "applicant_id": user_id,
        "applicant_name": ctx.author.display_name,
        "company_id": target_company_id,
        "company_name": target_company["name"],
        "position": jabatan.lower(),
        "applied_date": int(time.time()),
        "status": "pending",  # pending, interview, meeting, accepted, rejected
        "interviewed_by": None,
        "interview_notes": "",
        "final_salary": 0
    }
    
    save_data(data)
    
    embed = discord.Embed(title="📨 Lamaran Kerja Dikirim", color=0x0099ff)
    embed.add_field(name="🏢 Perusahaan", value=target_company["name"], inline=True)
    embed.add_field(name="👔 Jabatan", value=position_data["nama"], inline=True)
    embed.add_field(name="🆔 Application ID", value=application_id[-8:], inline=True)
    embed.add_field(name="📋 Status", value="Menunggu HRD Interview", inline=False)
    embed.add_field(name="⏰ Info", value="Kamu akan menerima notifikasi DM tentang hasil lamaran", inline=False)
    
    await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    # Notifikasi ke HRD perusahaan
    for emp_id, emp_data in target_company["employees"].items():
        if emp_data["position"] == "hrd_manager":
            pesan_hrd = f"📨 **Lamaran Kerja Baru**\n\n**{ctx.author.display_name}** melamar sebagai **{position_data['nama']}** di **{target_company['name']}**.\n\n🆔 **Application ID:** {application_id[-8:]}\n📊 **Level Pelamar:** {user_level}\n\nGunakan `!interview {application_id[-8:]}` untuk melakukan interview."
            await kirim_notif_dm(emp_id, pesan_hrd)
            break

# !interview - HRD melakukan interview (DM only)
@bot.command()
async def interview(ctx, application_id=None):
    # Cek apakah command digunakan di DM
    if ctx.guild is not None:
        await ctx.send("🔒 **Interview hanya bisa dilakukan di DM Bot!**\n\n💌 Kirim pesan langsung ke bot:\n`/interview [application_id]`")
        return
    
    if not application_id:
        await ctx.send("💼 **Cara Interview:**\n`/interview [application_id]` - Mulai interview pelamar\n\n📋 Hanya HRD Manager yang bisa melakukan interview")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_interview_system()
    
    # Cek apakah user adalah HRD
    if not data[user_id].get("company_employee"):
        await ctx.send("❌ Kamu tidak bekerja di perusahaan manapun.")
        return
    
    user_position = data[user_id]["company_employee"]["position"]
    if user_position != "hrd_manager":
        await ctx.send("❌ Hanya HRD Manager yang bisa melakukan interview.")
        return
    
    # Cari application
    target_application = None
    full_app_id = None
    
    for app_id, app_data in data["job_applications"].items():
        if app_id.endswith(application_id) or app_id[-8:] == application_id:
            if app_data["company_id"] == data[user_id]["company_employee"]["company_id"]:
                target_application = app_data
                full_app_id = app_id
                break
    
    if not target_application:
        await ctx.send(f"❌ Application dengan ID `{application_id}` tidak ditemukan atau bukan untuk perusahaan kamu.")
        return
    
    if target_application["status"] != "pending":
        await ctx.send(f"❌ Application ini sudah diproses. Status: {target_application['status']}")
        return
    
    # Proses interview otomatis
    applicant_level = calculate_level(data[target_application["applicant_id"]]["xp"])
    position_data = company_positions[target_application["position"]]
    
    # Interview scoring (berdasarkan level, random factor, dan experience)
    base_score = min(90, 50 + (applicant_level * 2))  # Base dari level
    random_factor = random.randint(-20, 20)  # Faktor keberuntungan
    interview_score = max(0, min(100, base_score + random_factor))
    
    # Tentukan hasil interview
    if interview_score >= 70:
        # Lulus interview
        target_application["status"] = "interview_passed"
        target_application["interviewed_by"] = user_id
        target_application["interview_notes"] = f"Skor interview: {interview_score}/100. Kandidat memenuhi syarat."
        
        # Jika jabatan penting (manager ke atas), perlu meeting
        important_positions = ["ceo", "coo", "cfo", "hrd_manager", "marketing_manager", "it_manager"]
        if target_application["position"] in important_positions:
            target_application["status"] = "need_meeting"
            next_step = "Perlu meeting dengan management"
            meeting_msg = f"\n\n📋 **Tahap selanjutnya:** Meeting management untuk jabatan penting ini."
        else:
            target_application["status"] = "ready_for_hiring"
            next_step = "Siap untuk direkrut"
            meeting_msg = ""
        
        embed = discord.Embed(title="✅ Interview LULUS", color=0x00ff00)
        embed.add_field(name="👤 Pelamar", value=target_application["applicant_name"], inline=True)
        embed.add_field(name="👔 Jabatan", value=position_data["nama"], inline=True)
        embed.add_field(name="📊 Skor", value=f"{interview_score}/100", inline=True)
        embed.add_field(name="📋 Status", value=next_step, inline=False)
        
        # Notifikasi ke pelamar
        pesan_pelamar = f"🎉 **Interview LULUS!**\n\nSelamat! Kamu lulus interview untuk posisi **{position_data['nama']}** di **{target_application['company_name']}**!\n\n📊 **Skor Interview:** {interview_score}/100\n👤 **Interviewer:** {ctx.author.display_name}{meeting_msg}\n\nKamu akan segera dihubungi untuk tahap selanjutnya!"
        
    else:
        # Gagal interview
        target_application["status"] = "rejected"
        target_application["interviewed_by"] = user_id
        target_application["interview_notes"] = f"Skor interview: {interview_score}/100. Kandidat belum memenuhi syarat."
        
        embed = discord.Embed(title="❌ Interview GAGAL", color=0xff0000)
        embed.add_field(name="👤 Pelamar", value=target_application["applicant_name"], inline=True)
        embed.add_field(name="👔 Jabatan", value=position_data["nama"], inline=True)
        embed.add_field(name="📊 Skor", value=f"{interview_score}/100", inline=True)
        embed.add_field(name="📋 Status", value="Ditolak", inline=False)
        
        # Notifikasi ke pelamar
        pesan_pelamar = f"😔 **Interview Tidak Lulus**\n\nMaaf, kamu belum lulus interview untuk posisi **{position_data['nama']}** di **{target_application['company_name']}**.\n\n📊 **Skor Interview:** {interview_score}/100\n👤 **Interviewer:** {ctx.author.display_name}\n\nJangan menyerah! Tingkatkan skill dan coba lagi di lain waktu. 💪"
    
    save_data(data)
    await ctx.send(embed=embed)
    await kirim_notif_dm(target_application["applicant_id"], pesan_pelamar)

# !meeting - Meeting management untuk jabatan penting
@bot.command()
async def meeting(ctx, application_id=None, *, keputusan=None):
    if not application_id:
        await ctx.send("🏛️ **Cara Meeting Management:**\n`!meeting [application_id] [terima/tolak] [gaji_jika_terima]`\n\n👔 Hanya CEO, COO, CFO yang bisa meeting\n📋 `!pending` - Lihat lamaran yang butuh meeting")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    # Cek apakah user adalah management
    if not data[user_id].get("company_employee"):
        await ctx.send("❌ Kamu tidak bekerja di perusahaan manapun.")
        return
    
    user_position = data[user_id]["company_employee"]["position"]
    management_positions = ["ceo", "coo", "cfo"]
    
    if user_position not in management_positions:
        await ctx.send("❌ Hanya CEO, COO, atau CFO yang bisa melakukan meeting management.")
        return
    
    # Cari application
    target_application = None
    full_app_id = None
    
    for app_id, app_data in data["job_applications"].items():
        if app_id.endswith(application_id) or app_id[-8:] == application_id:
            if app_data["company_id"] == data[user_id]["company_employee"]["company_id"]:
                target_application = app_data
                full_app_id = app_id
                break
    
    if not target_application:
        await ctx.send(f"❌ Application dengan ID `{application_id}` tidak ditemukan.")
        return
    
    if target_application["status"] != "need_meeting":
        await ctx.send(f"❌ Application ini tidak membutuhkan meeting. Status: {target_application['status']}")
        return
    
    if not keputusan:
        # Show meeting info
        position_data = company_positions[target_application["position"]]
        
        embed = discord.Embed(title="🏛️ Meeting Management", color=0x9b59b6)
        embed.add_field(name="👤 Kandidat", value=target_application["applicant_name"], inline=True)
        embed.add_field(name="👔 Jabatan", value=position_data["nama"], inline=True)
        embed.add_field(name="💰 Gaji Standard", value=f"Rp{position_data['gaji']:,}", inline=True)
        embed.add_field(name="📊 Interview Notes", value=target_application["interview_notes"], inline=False)
        embed.add_field(name="📋 Keputusan", value="`!meeting [app_id] terima [gaji]` atau `!meeting [app_id] tolak`", inline=False)
        
        await ctx.send(embed=embed)
        return
    
    keputusan_parts = keputusan.split()
    decision = keputusan_parts[0].lower()
    
    if decision == "terima":
        # Parse gaji jika ada
        if len(keputusan_parts) > 1:
            try:
                final_salary = int(keputusan_parts[1])
            except ValueError:
                await ctx.send("❌ Format gaji salah. Gunakan: `!meeting [app_id] terima [gaji]`")
                return
        else:
            final_salary = company_positions[target_application["position"]]["gaji"]
        
        # Proses penerimaan
        company_id = target_application["company_id"]
        company_data = data["companies"][company_id]
        applicant_id = target_application["applicant_id"]
        
        # Cek saldo perusahaan
        new_salary_cost = company_data["total_salary_cost"] + final_salary
        if company_data["balance"] < new_salary_cost:
            await ctx.send(f"❌ Saldo perusahaan tidak cukup. Butuh Rp{new_salary_cost:,}")
            return
        
        # Rekrut karyawan
        company_data["employees"][applicant_id] = {
            "position": target_application["position"],
            "salary": final_salary,
            "hire_date": int(time.time()),
            "hired_by": user_id,
            "interview_score": target_application["interview_notes"]
        }
        
        company_data["total_salary_cost"] = new_salary_cost
        
        data[applicant_id]["company_employee"] = {
            "company_id": company_id,
            "position": target_application["position"]
        }
        
        target_application["status"] = "accepted"
        target_application["final_salary"] = final_salary
        
        position_data = company_positions[target_application["position"]]
        
        embed = discord.Embed(title="🎉 KARYAWAN DITERIMA!", color=0x00ff00)
        embed.add_field(name="👤 Karyawan Baru", value=target_application["applicant_name"], inline=True)
        embed.add_field(name="👔 Jabatan", value=position_data["nama"], inline=True)
        embed.add_field(name="💰 Gaji Final", value=f"Rp{final_salary:,}", inline=True)
        embed.add_field(name="👨‍💼 Diputuskan oleh", value=f"{ctx.author.display_name} ({user_position.upper()})", inline=True)
        
        # Notifikasi ke karyawan baru
        pesan_diterima = f"🎉 **SELAMAT! KAMU DITERIMA KERJA!**\n\n**{target_application['company_name']}** resmi menerima kamu sebagai **{position_data['nama']}**!\n\n💰 **Gaji:** Rp{final_salary:,}\n👨‍💼 **Diputuskan oleh:** {ctx.author.display_name} ({user_position.upper()})\n🏢 **Status:** Resmi menjadi karyawan\n\nSelamat datang di tim! Gunakan `!gajiperusahaan` untuk ambil gaji bulanan. 🎊"
        
    elif decision == "tolak":
        target_application["status"] = "rejected"
        
        embed = discord.Embed(title="❌ DITOLAK MANAGEMENT", color=0xff0000)
        embed.add_field(name="👤 Kandidat", value=target_application["applicant_name"], inline=True)
        embed.add_field(name="👔 Jabatan", value=company_positions[target_application["position"]]["nama"], inline=True)
        embed.add_field(name="👨‍💼 Ditolak oleh", value=f"{ctx.author.display_name} ({user_position.upper()})", inline=True)
        
        # Notifikasi ke pelamar
        pesan_ditolak = f"😔 **Lamaran Ditolak Management**\n\nMaaf, setelah meeting management, **{target_application['company_name']}** memutuskan untuk tidak melanjutkan proses rekrutmen kamu untuk posisi **{company_positions[target_application['position']]['nama']}**.\n\n👨‍💼 **Keputusan oleh:** {ctx.author.display_name} ({user_position.upper()})\n\nTerima kasih sudah melamar. Jangan menyerah dan tetap semangat! 💪"
        
    else:
        await ctx.send("❌ Keputusan tidak valid. Gunakan 'terima' atau 'tolak'")
        return
    
    save_data(data)
    await ctx.send(embed=embed)
    await kirim_notif_dm(target_application["applicant_id"], pesan_diterima if decision == "terima" else pesan_ditolak)

# !setgaji - CEO/COO/CFO set gaji karyawan
@bot.command()
async def setgaji(ctx, target: discord.Member, gaji_baru: int):
    user_id = str(ctx.author.id)
    target_id = str(target.id)
    
    if gaji_baru <= 0:
        await ctx.send("❌ Gaji harus lebih dari 0.")
        return
    
    create_user_profile(user_id)
    create_user_profile(target_id)
    
    # Cek apakah user adalah management
    if not data[user_id].get("company_employee"):
        await ctx.send("❌ Kamu tidak bekerja di perusahaan manapun.")
        return
    
    user_position = data[user_id]["company_employee"]["position"]
    management_positions = ["ceo", "coo", "cfo"]
    
    if user_position not in management_positions:
        await ctx.send("❌ Hanya CEO, COO, atau CFO yang bisa menetapkan gaji.")
        return
    
    company_id = data[user_id]["company_employee"]["company_id"]
    company_data = data["companies"][company_id]
    
    # Cek apakah target adalah karyawan di perusahaan yang sama
    if target_id not in company_data["employees"]:
        await ctx.send(f"❌ {target.display_name} bukan karyawan di perusahaan ini.")
        return
    
    # Tidak bisa ubah gaji CEO jika bukan CEO
    target_position = company_data["employees"][target_id]["position"]
    if target_position == "ceo" and user_position != "ceo":
        await ctx.send("❌ Hanya CEO yang bisa mengubah gaji CEO.")
        return
    
    # Update gaji
    old_salary = company_data["employees"][target_id]["salary"]
    company_data["employees"][target_id]["salary"] = gaji_baru
    
    # Update total salary cost
    company_data["total_salary_cost"] = company_data["total_salary_cost"] - old_salary + gaji_baru
    
    embed = discord.Embed(title="💰 Gaji Diubah", color=0x00ff00)
    embed.add_field(name="👤 Karyawan", value=target.display_name, inline=True)
    embed.add_field(name="👔 Jabatan", value=company_positions[target_position]["nama"], inline=True)
    embed.add_field(name="💵 Gaji Lama", value=f"Rp{old_salary:,}", inline=True)
    embed.add_field(name="💰 Gaji Baru", value=f"Rp{gaji_baru:,}", inline=True)
    embed.add_field(name="👨‍💼 Ditetapkan oleh", value=f"{ctx.author.display_name} ({user_position.upper()})", inline=True)
    
    save_data(data)
    await ctx.send(embed=embed)
    
    # Notifikasi ke karyawan
    selisih = gaji_baru - old_salary
    if selisih > 0:
        status_gaji = f"NAIK Rp{selisih:,} 📈"
        emoji = "🎉"
    elif selisih < 0:
        status_gaji = f"TURUN Rp{abs(selisih):,} 📉"
        emoji = "😔"
    else:
        status_gaji = "TETAP"
        emoji = "📊"
    
    pesan_notif = f"{emoji} **Gaji Diubah**\n\nGaji kamu di **{company_data['name']}** telah diubah!\n\n💰 **Gaji Lama:** Rp{old_salary:,}\n💵 **Gaji Baru:** Rp{gaji_baru:,}\n📊 **Status:** {status_gaji}\n👨‍💼 **Ditetapkan oleh:** {ctx.author.display_name} ({user_position.upper()})"
    await kirim_notif_dm(target_id, pesan_notif)

# !pending - Lihat lamaran yang pending
@bot.command()
async def pending(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if not data[user_id].get("company_employee"):
        await ctx.send("❌ Kamu tidak bekerja di perusahaan manapun.")
        return
    
    user_position = data[user_id]["company_employee"]["position"]
    company_id = data[user_id]["company_employee"]["company_id"]
    
    pending_applications = []
    
    for app_id, app_data in data.get("job_applications", {}).items():
        if app_data["company_id"] == company_id:
            # HRD lihat yang butuh interview
            if user_position == "hrd_manager" and app_data["status"] == "pending":
                pending_applications.append((app_id, app_data, "Butuh Interview"))
            # Management lihat yang butuh meeting
            elif user_position in ["ceo", "coo", "cfo"] and app_data["status"] == "need_meeting":
                pending_applications.append((app_id, app_data, "Butuh Meeting"))
    
    if not pending_applications:
        if user_position == "hrd_manager":
            await ctx.send("📋 Tidak ada lamaran yang butuh interview.")
        else:
            await ctx.send("📋 Tidak ada lamaran yang butuh meeting management.")
        return
    
    embed = discord.Embed(title="📋 Lamaran Pending", color=0xff9900)
    
    for app_id, app_data, status in pending_applications[:10]:
        position_name = company_positions[app_data["position"]]["nama"]
        
        embed.add_field(
            name=f"👤 {app_data['applicant_name']}",
            value=f"👔 {position_name}\n🆔 {app_id[-8:]}\n📋 {status}\n⏰ {int((int(time.time()) - app_data['applied_date']) / 86400)} hari lalu",
            inline=True
        )
    
    if user_position == "hrd_manager":
        embed.set_footer(text="Gunakan /interview [app_id] untuk interview (DM only)")
    else:
        embed.set_footer(text="Gunakan !meeting [app_id] untuk meeting management")
    
    await ctx.send(embed=embed)

# !perusahaanlist - Daftar semua perusahaan
@bot.command()
async def perusahaanlist(ctx):
    if "companies" not in data or not data["companies"]:
        await ctx.send("🏢 Belum ada perusahaan yang terdaftar.")
        return
    
    embed = discord.Embed(title="🏢 Daftar Perusahaan", color=0x3498db)
    
    sorted_companies = sorted(data["companies"].items(), key=lambda x: len(x[1]["employees"]), reverse=True)[:15]
    
    for company_id, company_data in sorted_companies:
        # Cari CEO
        ceo_name = "Unknown"
        for emp_id, emp_data in company_data["employees"].items():
            if emp_data["position"] == "ceo":
                try:
                    user = bot.get_user(int(emp_id))
                    ceo_name = user.display_name if user else f"User {emp_id[:4]}..."
                except:
                    pass
                break
        
        employees_count = len(company_data["employees"])
        
        embed.add_field(
            name=f"🏢 {company_data['name']}",
            value=f"👑 CEO: {ceo_name}\n👥 Karyawan: {employees_count}\n💰 Revenue: Rp{company_data.get('revenue', 0):,}",
            inline=True
        )
    
    embed.set_footer(text="!lamarkerja [nama_perusahaan] [jabatan] untuk melamar")
    await ctx.send(embed=embed)

# Update menu perusahaan
@bot.command()
async def menuperusahaanrealistics(ctx):
    embed = discord.Embed(title="🏢 Menu Sistem Perusahaan Realistis", color=0x9b59b6)
    
    embed.add_field(
        name="💼 **Melamar Kerja**",
        value="`!lamarkerja [perusahaan] [jabatan]` - Lamar kerja\n`!perusahaanlist` - Lihat daftar perusahaan\n📨 Notifikasi hasil ke DM",
        inline=False
    )
    
    embed.add_field(
        name="🎤 **Interview & Meeting**",
        value="💌 `/interview [app_id]` - HRD interview (DM only)\n`!meeting [app_id] [terima/tolak]` - Meeting management\n`!pending` - Lihat lamaran pending",
        inline=False
    )
    
    embed.add_field(
        name="💰 **Manajemen Gaji**",
        value="`!setgaji @user [jumlah]` - CEO/COO/CFO set gaji\n`!gajiperusahaan` - Ambil gaji bulanan\n💼 Gaji bisa disesuaikan sesuai keputusan management",
        inline=False
    )
    
    embed.add_field(
        name="🏗️ **Untuk Owner**",
        value="`!buatperusahaan [nama]` - Buat perusahaan\n`!fire @user` - Pecat karyawan\n`!perusahaan` - Info perusahaan",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Alur Kerja Realistis**",
        value="1️⃣ Pelamar kirim lamaran\n2️⃣ HRD interview via DM\n3️⃣ Jabatan penting → Meeting management\n4️⃣ CEO/COO/CFO tentukan gaji final\n5️⃣ Notifikasi hasil ke DM pelamar\n6️⃣ Karyawan ambil gaji bulanan",
        inline=False
    )
    
    embed.add_field(
        name="👔 **Wewenang Jabatan**",
        value="👑 **CEO:** Set gaji semua, hire/fire\n🎯 **COO/CFO:** Set gaji staff, meeting\n👤 **HRD:** Interview pelamar\n📋 **Lainnya:** Fokus ke pekerjaan",
        inline=False
    )
    
    embed.set_footer(text="Sistem 100% realistis seperti dunia kerja!")
    await ctx.send(embed=embed)

# !fire - Pecat karyawan
@bot.command()
async def fire(ctx, target: discord.Member):
    user_id = str(ctx.author.id)
    target_id = str(target.id)
    
    if user_id == target_id:
        await ctx.send("❌ Kamu tidak bisa memecat diri sendiri. Gunakan `!resignperusahaan` untuk resign.")
        return
    
    create_user_profile(user_id)
    create_user_profile(target_id)
    
    # Cek apakah user bisa memecat
    if not data[user_id].get("company_employee"):
        await ctx.send("❌ Kamu tidak bekerja di perusahaan manapun.")
        return
    
    company_id = data[user_id]["company_employee"]["company_id"]
    company_data = data.get("companies", {}).get(company_id)
    user_position = data[user_id]["company_employee"]["position"]
    
    if not company_data:
        await ctx.send("❌ Perusahaan tidak ditemukan.")
        return
    
    # Cek permission untuk fire
    if not company_positions[user_position].get("can_fire", False):
        await ctx.send("❌ Jabatan kamu tidak memiliki wewenang untuk memecat karyawan.")
        return
    
    # Cek apakah target adalah karyawan
    if target_id not in company_data["employees"]:
        await ctx.send(f"❌ {target.display_name} bukan karyawan perusahaan ini.")
        return
    
    # Tidak bisa pecat CEO
    target_position = company_data["employees"][target_id]["position"]
    if target_position == "ceo":
        await ctx.send("❌ Tidak bisa memecat CEO.")
        return
    
    # Proses pemecatan
    salary = company_data["employees"][target_id]["salary"]
    del company_data["employees"][target_id]
    company_data["total_salary_cost"] -= salary
    
    # Hapus dari data target
    if "company_employee" in data[target_id]:
        del data[target_id]["company_employee"]
    
    # Severance pay (pesangon) 1 bulan gaji
    severance = salary
    data[target_id]["uang"] += severance
    company_data["balance"] -= severance
    
    embed = discord.Embed(title="🚫 Karyawan Dipecat", color=0xff0000)
    embed.add_field(name="👤 Karyawan", value=target.display_name, inline=True)
    embed.add_field(name="👔 Jabatan", value=company_positions[target_position]["nama"], inline=True)
    embed.add_field(name="💸 Pesangon", value=f"Rp{severance:,}", inline=True)
    
    save_data(data)
    await ctx.send(embed=embed)
    
    # Notifikasi ke target
    pesan_notif = f"🚫 **Pemberitahuan PHK**\n\nKamu telah dipecat dari **{company_data['name']}** oleh **{ctx.author.display_name}**.\n\n💸 **Pesangon:** Rp{severance:,}\n\nTerima kasih atas kontribusimu!"
    await kirim_notif_dm(target_id, pesan_notif)

# !gajiperusahaan - Ambil gaji perusahaan
@bot.command()
async def gajiperusahaan(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if not data[user_id].get("company_employee"):
        await ctx.send("❌ Kamu tidak bekerja di perusahaan manapun.")
        return
    
    company_id = data[user_id]["company_employee"]["company_id"]
    company_data = data.get("companies", {}).get(company_id)
    
    if not company_data:
        await ctx.send("❌ Perusahaan tidak ditemukan.")
        return
    
    employee_data = company_data["employees"].get(user_id)
    if not employee_data:
        await ctx.send("❌ Data karyawan tidak ditemukan.")
        return
    
    # Cek cooldown gaji (30 hari)
    current_time = int(time.time())
    last_salary = company_data.get("last_salary_payment", 0)
    
    if current_time - last_salary < 2592000:  # 30 hari
        remaining = 2592000 - (current_time - last_salary)
        days_left = remaining // 86400
        await ctx.send(f"⏰ Tunggu {days_left} hari lagi untuk gajian bulanan.")
        return
    
    # Cek apakah perusahaan mampu bayar
    total_salary_cost = company_data["total_salary_cost"]
    if company_data["balance"] < total_salary_cost:
        await ctx.send("❌ Perusahaan sedang krisis keuangan. Saldo tidak cukup untuk menggaji semua karyawan.")
        return
    
    # Bayar gaji ke semua karyawan
    successful_payments = 0
    for emp_id, emp_data in company_data["employees"].items():
        if emp_id in data:
            data[emp_id]["uang"] += emp_data["salary"]
            successful_payments += 1
    
    company_data["balance"] -= total_salary_cost
    company_data["last_salary_payment"] = current_time
    
    # Tambah revenue otomatis (simulasi bisnis)
    monthly_revenue = total_salary_cost * random.uniform(1.2, 2.0)  # 120-200% dari biaya gaji
    company_data["balance"] += int(monthly_revenue)
    company_data["revenue"] += int(monthly_revenue)
    
    position_name = company_positions[employee_data["position"]]["nama"]
    salary = employee_data["salary"]
    
    embed = discord.Embed(title="💰 Gajian Bulanan", color=0x00ff00)
    embed.add_field(name="🏢 Perusahaan", value=company_data["name"], inline=True)
    embed.add_field(name="👔 Jabatan", value=position_name, inline=True)
    embed.add_field(name="💵 Gaji", value=f"Rp{salary:,}", inline=True)
    embed.add_field(name="👥 Total Karyawan Dibayar", value=f"{successful_payments} orang", inline=True)
    embed.add_field(name="💼 Total Biaya Gaji", value=f"Rp{total_salary_cost:,}", inline=True)
    embed.add_field(name="📈 Revenue Bulan Ini", value=f"Rp{int(monthly_revenue):,}", inline=True)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !resignperusahaan - Resign dari perusahaan
@bot.command()
async def resignperusahaan(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if not data[user_id].get("company_employee"):
        await ctx.send("❌ Kamu tidak bekerja di perusahaan manapun.")
        return
    
    company_id = data[user_id]["company_employee"]["company_id"]
    company_data = data.get("companies", {}).get(company_id)
    user_position = data[user_id]["company_employee"]["position"]
    
    # Jika CEO resign, perusahaan ditutup
    if user_position == "ceo" and data[user_id].get("company_owned"):
        # Tutup perusahaan
        for emp_id in company_data["employees"]:
            if emp_id in data and "company_employee" in data[emp_id]:
                del data[emp_id]["company_employee"]
        
        # Liquidation - bagi sisa saldo ke CEO
        liquidation_amount = company_data["balance"]
        data[user_id]["uang"] += liquidation_amount
        
        del data["companies"][company_id]
        del data[user_id]["company_owned"]
        del data[user_id]["company_employee"]
        
        embed = discord.Embed(title="🏢 Perusahaan Ditutup", color=0xff9900)
        embed.add_field(name="Status", value="CEO resign, perusahaan dilikuidasi", inline=True)
        embed.add_field(name="💰 Liquidation", value=f"Rp{liquidation_amount:,}", inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
    else:
        # Resign biasa
        salary = company_data["employees"][user_id]["salary"]
        del company_data["employees"][user_id]
        company_data["total_salary_cost"] -= salary
        del data[user_id]["company_employee"]
        
        embed = discord.Embed(title="👋 Resign Berhasil", color=0xff9900)
        embed.add_field(name="🏢 Perusahaan", value=company_data["name"], inline=True)
        embed.add_field(name="👔 Jabatan", value=company_positions[user_position]["nama"], inline=True)
        
        await ctx.send(f"{ctx.author.mention}", embed=embed)
    
    save_data(data)

# Duplicate menubank command removed - already defined earlier in the code

@bot.command()
async def menuperusahaan(ctx):
    embed = discord.Embed(title="🏢 Menu Sistem Perusahaan", color=0x9b59b6)
    
    embed.add_field(
        name="🏗️ **Membangun Perusahaan**",
        value="`!buatperusahaan [nama]` - Buat perusahaan baru\n💰 Biaya: Rp50jt, Level 30+\n👑 Otomatis jadi CEO",
        inline=False
    )
    
    embed.add_field(
        name="👥 **Manajemen Karyawan**",
        value="`!hire @user [jabatan]` - Rekrut karyawan\n`!fire @user` - Pecat karyawan\n`!perusahaan` - Info perusahaan\n`!perusahaan jabatan` - Daftar jabatan",
        inline=False
    )
    
    embed.add_field(
        name="💰 **Keuangan**",
        value="`!gajiperusahaan` - Ambil gaji bulanan\n`!resignperusahaan` - Resign dari perusahaan\n📈 Revenue otomatis dari operasional",
        inline=False
    )
    
    embed.add_field(
        name="👔 **Hierarki Jabatan**",
        value="👑 CEO → COO → CFO\n🎯 Manager → Supervisor\n📋 Staff → Office Boy\n💼 Setiap jabatan punya gaji & wewenang berbeda",
        inline=False
    )
    
    embed.add_field(
        name="🔑 **Permission System**",
        value="• CEO: Hire & Fire semua\n• COO/CFO: Hire staff level\n• Manager: Hire terbatas\n• Staff: Tidak bisa hire/fire",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# Update menu utama
@bot.command()
async def menunewfeatures(ctx):
    embed = discord.Embed(title="🆕 Menu Fitur Terbaru", color=0xe74c3c)
    
    embed.add_field(
        name="🏦 **Banking & Investment**",
        value="`!menubank` - Tabungan, investasi, bunga bank\n💳 Sistem perbankan lengkap dengan bunga harian",
        inline=False
    )
    
    embed.add_field(
        name="🏢 **Corporate System**",
        value="`!menuperusahaan` - Sistem perusahaan & jabatan\n👔 Buat perusahaan, rekrut karyawan, kelola bisnis",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Highlights**",
        value="• 14 jabatan perusahaan (CEO sampai Office Boy)\n• Sistem tabungan dengan bunga 2% per hari\n• Investasi saham, emas, crypto\n• Permission system untuk hire/fire\n• Revenue otomatis untuk perusahaan\n• Gaji bulanan untuk semua karyawan",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu")
    await ctx.send(embed=embed)

# ===== JOB SKILLS SYSTEM =====

# Initialize job skills cooldown
def init_job_skills():
    for user_id in data:
        if user_id in ["real_estate", "court_cases", "court_settings", "companies", "marketplace", "bank_settings", "job_applications", "company_meetings"]:
            continue
        if "job_skills" not in data[user_id]:
            data[user_id]["job_skills"] = {}
    save_data(data)

# Generic job skill command
@bot.command()
async def skill(ctx, skill_command=None, target: discord.Member = None):
    """Generic skill command that handles all job-specific skills"""
    if skill_command is None:
        await show_available_skills(ctx)
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    init_job_skills()
    
    # Get user's current job
    user_job = data[user_id].get("pekerjaan")
    if not user_job:
        await ctx.send("❌ Kamu harus bekerja dulu untuk menggunakan skill pekerjaan!")
        return
    
    # Find job skill
    job_data = jobs.get(user_job)
    if not job_data or "skill" not in job_data:
        await ctx.send("❌ Pekerjaan kamu tidak memiliki skill khusus.")
        return
    
    skill_data = job_data["skill"]
    if skill_command.lower() != skill_data["command"]:
        await ctx.send(f"❌ Skill tidak valid. Gunakan `!{skill_data['command']}` untuk skill {skill_data['name']}.")
        return
    
    # Check if skill is DM only
    if skill_data.get("dm_only", False) and ctx.guild is not None:
        await ctx.send(f"🔒 **{skill_data['name']} hanya bisa digunakan di DM Bot!**\n\n💌 Kirim pesan langsung ke bot:\n`/{skill_data['command']}`")
        return
    
    # Check cooldown
    current_time = int(time.time())
    last_used = data[user_id]["job_skills"].get(skill_command, 0)
    cooldown = skill_data["cooldown"]
    
    if current_time - last_used < cooldown:
        remaining = cooldown - (current_time - last_used)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        await ctx.send(f"⏰ Tunggu {hours} jam {minutes} menit lagi untuk menggunakan {skill_data['name']}.")
        return
    
    # Execute skill effect
    await execute_job_skill(ctx, skill_data, user_id, target)
    
    # Update cooldown
    data[user_id]["job_skills"][skill_command] = current_time
    save_data(data)

async def show_available_skills(ctx):
    """Show available skills for user's job"""
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    user_job = data[user_id].get("pekerjaan")
    if not user_job:
        embed = discord.Embed(title="💼 Job Skills", color=0x9b59b6)
        embed.add_field(name="📋 Status", value="Kamu harus bekerja dulu untuk menggunakan skill pekerjaan!", inline=False)
        embed.add_field(name="💡 Info", value="Setiap pekerjaan memiliki skill unik dengan cooldown masing-masing", inline=False)
        await ctx.send(embed=embed)
        return
    
    job_data = jobs.get(user_job)
    if not job_data or "skill" not in job_data:
        await ctx.send("❌ Pekerjaan kamu tidak memiliki skill khusus.")
        return
    
    skill_data = job_data["skill"]
    
    # Check cooldown
    current_time = int(time.time())
    last_used = data[user_id].get("job_skills", {}).get(skill_data["command"], 0)
    cooldown = skill_data["cooldown"]
    
    if current_time - last_used < cooldown:
        remaining = cooldown - (current_time - last_used)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        status = f"⏰ Cooldown: {hours}j {minutes}m"
    else:
        status = "✅ Siap digunakan"
    
    embed = discord.Embed(title=f"💼 Skill: {job_data['deskripsi']}", color=0x0099ff)
    embed.add_field(name="🎯 Skill", value=skill_data["name"], inline=True)
    embed.add_field(name="📋 Status", value=status, inline=True)
    embed.add_field(name="⏰ Cooldown", value=f"{cooldown//3600} jam", inline=True)
    embed.add_field(name="📝 Deskripsi", value=skill_data["description"], inline=False)
    embed.add_field(name="🎮 Cara Pakai", value=f"`!{skill_data['command']}`" + (" (DM only)" if skill_data.get("dm_only") else ""), inline=False)
    
    await ctx.send(embed=embed)

async def execute_job_skill(ctx, skill_data, user_id, target=None):
    """Execute specific job skill effects"""
    effect = skill_data["effect"]
    
    if effect == "medical_treatment":
        await medical_treatment_skill(ctx, user_id, target)
    elif effect == "investigate_crime":
        await investigate_crime_skill(ctx, user_id)
    elif effect == "legal_advice":
        await legal_advice_skill(ctx, user_id)
    elif effect == "resolve_conflict":
        await resolve_conflict_skill(ctx, user_id)
    elif effect == "dental_care":
        await dental_care_skill(ctx, user_id)
    elif effect == "child_therapy":
        await child_therapy_skill(ctx, user_id)
    elif effect == "emergency_surgery":
        await emergency_surgery_skill(ctx, user_id)
    elif effect == "tutoring":
        await tutoring_skill(ctx, user_id)
    elif effect == "character_development":
        await character_development_skill(ctx, user_id)
    elif effect == "career_counseling":
        await career_counseling_skill(ctx, user_id)
    elif effect == "academic_research":
        await academic_research_skill(ctx, user_id)
    elif effect == "programming_bonus":
        await programming_bonus_skill(ctx, user_id)
    elif effect == "data_insights":
        await data_insights_skill(ctx, user_id)
    elif effect == "fast_travel":
        await fast_travel_skill(ctx, user_id)
    elif effect == "premium_service":
        await premium_service_skill(ctx, user_id)
    elif effect == "cargo_delivery":
        await cargo_delivery_skill(ctx, user_id)
    elif effect == "inventory_management":
        await inventory_management_skill(ctx, user_id)
    elif effect == "fast_transaction":
        await fast_transaction_skill(ctx, user_id)
    elif effect == "coffee_brewing":
        await coffee_brewing_skill(ctx, user_id)
    elif effect == "vehicle_service":
        await vehicle_service_skill(ctx, user_id)

# Skill implementations
async def medical_treatment_skill(ctx, user_id, target):
    """Dokter umum - pengobatan medis gratis"""
    if target:
        target_id = str(target.id)
        create_user_profile(target_id)
        patient_name = target.display_name
    else:
        target_id = user_id
        patient_name = "diri sendiri"
    
    # Apply life effects first
    data[target_id] = apply_life_effects(data[target_id])
    
    # Heal target
    old_health = data[target_id]["kesehatan"]
    health_restore = random.randint(60, 90)
    data[target_id]["kesehatan"] = min(100, old_health + health_restore)
    
    # Doctor gets XP and small payment
    doctor_xp = random.randint(30, 60)
    doctor_payment = random.randint(50000, 150000)
    data[user_id]["xp"] += doctor_xp
    data[user_id]["uang"] += doctor_payment
    
    embed = discord.Embed(title="🩺 Pengobatan Medis", color=0x00ff00)
    embed.add_field(name="👨‍⚕️ Dokter", value=ctx.author.display_name, inline=True)
    embed.add_field(name="🤒 Pasien", value=patient_name, inline=True)
    embed.add_field(name="❤️ Kesehatan", value=f"{old_health} → {data[target_id]['kesehatan']} (+{health_restore})", inline=True)
    embed.add_field(name="💰 Honor Dokter", value=f"Rp{doctor_payment:,}", inline=True)
    embed.add_field(name="⭐ XP Dokter", value=f"+{doctor_xp}", inline=True)
    embed.add_field(name="💊 Diagnosa", value="Pengobatan berhasil, pasien sudah sehat!", inline=False)
    
    await ctx.send(embed=embed)

async def investigate_crime_skill(ctx, user_id):
    """Jaksa - investigasi kriminal (DM only)"""
    # Random investigation results
    cases = [
        {"name": "Kasus Korupsi", "reward": 500000, "xp": 100},
        {"name": "Kasus Penipuan", "reward": 300000, "xp": 75},
        {"name": "Kasus Narkoba", "reward": 800000, "xp": 150},
        {"name": "Kasus Pencucian Uang", "reward": 1000000, "xp": 200},
        {"name": "Kasus Suap", "reward": 600000, "xp": 120}
    ]
    
    case = random.choice(cases)
    success_rate = random.randint(60, 90)
    
    if success_rate >= 70:
        # Investigation successful
        data[user_id]["uang"] += case["reward"]
        data[user_id]["xp"] += case["xp"]
        
        embed = discord.Embed(title="🕵️ Investigasi Berhasil!", color=0x00ff00)
        embed.add_field(name="📋 Kasus", value=case["name"], inline=True)
        embed.add_field(name="📊 Success Rate", value=f"{success_rate}%", inline=True)
        embed.add_field(name="💰 Reward", value=f"Rp{case['reward']:,}", inline=True)
        embed.add_field(name="⭐ XP", value=f"+{case['xp']}", inline=True)
        embed.add_field(name="🎯 Status", value="Kasus berhasil diungkap!", inline=False)
    else:
        # Investigation failed
        embed = discord.Embed(title="🕵️ Investigasi Gagal", color=0xff0000)
        embed.add_field(name="📋 Kasus", value=case["name"], inline=True)
        embed.add_field(name="📊 Success Rate", value=f"{success_rate}%", inline=True)
        embed.add_field(name="❌ Status", value="Bukti tidak cukup, kasus ditutup sementara", inline=False)
    
    await ctx.send(embed=embed)

async def legal_advice_skill(ctx, user_id):
    """Pengacara - konsultasi hukum"""
    consultation_fee = random.randint(200000, 500000)
    xp_gained = random.randint(40, 80)
    
    data[user_id]["uang"] += consultation_fee
    data[user_id]["xp"] += xp_gained
    
    legal_cases = [
        "Konsultasi Perceraian",
        "Sengketa Tanah",
        "Masalah Warisan",
        "Kontrak Bisnis",
        "Kasus Ketenagakerjaan"
    ]
    
    case_type = random.choice(legal_cases)
    
    embed = discord.Embed(title="⚖️ Konsultasi Hukum", color=0x0099ff)
    embed.add_field(name="👨‍💼 Pengacara", value=ctx.author.display_name, inline=True)
    embed.add_field(name="📋 Jenis Kasus", value=case_type, inline=True)
    embed.add_field(name="💰 Fee Konsultasi", value=f"Rp{consultation_fee:,}", inline=True)
    embed.add_field(name="⭐ XP", value=f"+{xp_gained}", inline=True)
    embed.add_field(name="✅ Hasil", value="Konsultasi selesai, klien puas dengan advice yang diberikan!", inline=False)
    
    await ctx.send(embed=embed)

async def resolve_conflict_skill(ctx, user_id):
    """Hakim - vonis keadilan"""
    case_value = random.randint(1000000, 5000000)
    judge_fee = int(case_value * 0.1)  # 10% dari nilai kasus
    xp_gained = random.randint(80, 150)
    
    data[user_id]["uang"] += judge_fee
    data[user_id]["xp"] += xp_gained
    
    cases = [
        "Sengketa Bisnis",
        "Kasus Perdata",
        "Masalah Kontrak",
        "Sengketa Warisan",
        "Kasus Ganti Rugi"
    ]
    
    case_type = random.choice(cases)
    verdict = random.choice(["Menang", "Kalah", "Damai"])
    
    embed = discord.Embed(title="⚖️ Vonis Keadilan", color=0x9b59b6)
    embed.add_field(name="👨‍⚖️ Hakim", value=ctx.author.display_name, inline=True)
    embed.add_field(name="📋 Kasus", value=case_type, inline=True)
    embed.add_field(name="💰 Nilai Kasus", value=f"Rp{case_value:,}", inline=True)
    embed.add_field(name="💵 Fee Hakim", value=f"Rp{judge_fee:,}", inline=True)
    embed.add_field(name="⭐ XP", value=f"+{xp_gained}", inline=True)
    embed.add_field(name="⚖️ Putusan", value=f"Kasus diputus {verdict}", inline=True)
    embed.add_field(name="✅ Status", value="Keadilan telah ditegakkan!", inline=False)
    
    await ctx.send(embed=embed)

async def programming_bonus_skill(ctx, user_id):
    """Programmer - coding session"""
    projects = [
        {"name": "Website E-commerce", "pay": 800000, "xp": 120},
        {"name": "Mobile App", "pay": 1200000, "xp": 150},
        {"name": "Database System", "pay": 600000, "xp": 100},
        {"name": "AI Algorithm", "pay": 1500000, "xp": 200},
        {"name": "Game Development", "pay": 1000000, "xp": 140}
    ]
    
    project = random.choice(projects)
    completion_rate = random.randint(70, 95)
    
    if completion_rate >= 80:
        final_pay = project["pay"]
        final_xp = project["xp"]
        status = "✅ Project Completed"
    else:
        final_pay = int(project["pay"] * 0.7)
        final_xp = int(project["xp"] * 0.7)
        status = "⚠️ Project Partially Completed"
    
    data[user_id]["uang"] += final_pay
    data[user_id]["xp"] += final_xp
    
    embed = discord.Embed(title="💻 Coding Session", color=0x00ff00)
    embed.add_field(name="👨‍💻 Programmer", value=ctx.author.display_name, inline=True)
    embed.add_field(name="📋 Project", value=project["name"], inline=True)
    embed.add_field(name="📊 Completion", value=f"{completion_rate}%", inline=True)
    embed.add_field(name="💰 Payment", value=f"Rp{final_pay:,}", inline=True)
    embed.add_field(name="⭐ XP", value=f"+{final_xp}", inline=True)
    embed.add_field(name="🎯 Status", value=status, inline=True)
    
    await ctx.send(embed=embed)

async def coffee_brewing_skill(ctx, user_id):
    """Barista - racik kopi special"""
    coffee_types = [
        {"name": "Espresso Premium", "energy": 40, "pay": 100000},
        {"name": "Cappuccino Deluxe", "energy": 35, "pay": 80000},
        {"name": "Latte Art Special", "energy": 30, "pay": 90000},
        {"name": "Cold Brew Signature", "energy": 45, "pay": 120000},
        {"name": "Mocha Supreme", "energy": 38, "pay": 110000}
    ]
    
    coffee = random.choice(coffee_types)
    
    # Apply life effects first
    data[user_id] = apply_life_effects(data[user_id])
    
    # Energy boost
    old_health = data[user_id]["kesehatan"]
    data[user_id]["kesehatan"] = min(100, old_health + coffee["energy"])
    data[user_id]["uang"] += coffee["pay"]
    data[user_id]["xp"] += 40
    
    # Reduce work cooldown
    if data[user_id].get("last_work"):
        last_work = datetime.fromisoformat(data[user_id]["last_work"])
        new_time = last_work - timedelta(minutes=30)  # Reduce 30 minutes
        data[user_id]["last_work"] = new_time.isoformat()
    
    embed = discord.Embed(title="☕ Racik Kopi Special", color=0x8B4513)
    embed.add_field(name="👨‍🍳 Barista", value=ctx.author.display_name, inline=True)
    embed.add_field(name="☕ Kopi", value=coffee["name"], inline=True)
    embed.add_field(name="⚡ Energy Boost", value=f"+{coffee['energy']} kesehatan", inline=True)
    embed.add_field(name="💰 Tips", value=f"Rp{coffee['pay']:,}", inline=True)
    embed.add_field(name="⭐ XP", value="+40", inline=True)
    embed.add_field(name="⏰ Bonus", value="Work cooldown -30 menit", inline=True)
    
    await ctx.send(embed=embed)

# Add individual skill commands for easier access
@bot.command()
async def vonis(ctx):
    """Hakim skill"""
    await skill(ctx, "vonis")

@bot.command()
async def investigasi(ctx):
    """Jaksa skill - DM only"""
    await skill(ctx, "investigasi")

@bot.command()
async def konsultasi(ctx):
    """Pengacara skill"""
    await skill(ctx, "konsultasi")

@bot.command()
async def obati(ctx, target: discord.Member = None):
    """Dokter umum skill"""
    await skill(ctx, "obati", target)

@bot.command()
async def coding(ctx):
    """Programmer skill"""
    await skill(ctx, "coding")

@bot.command()
async def racikkopi(ctx):
    """Barista skill"""
    await skill(ctx, "racikkopi")

# Implement remaining skills with similar patterns...
async def dental_care_skill(ctx, user_id):
    """Dokter gigi - perawatan gigi"""
    data[user_id] = apply_life_effects(data[user_id])
    
    old_health = data[user_id]["kesehatan"]
    health_boost = random.randint(40, 70)
    data[user_id]["kesehatan"] = min(100, old_health + health_boost)
    
    payment = random.randint(150000, 300000)
    data[user_id]["uang"] += payment
    data[user_id]["xp"] += 50
    
    embed = discord.Embed(title="🦷 Perawatan Gigi", color=0x00ff00)
    embed.add_field(name="👨‍⚕️ Dokter Gigi", value=ctx.author.display_name, inline=True)
    embed.add_field(name="❤️ Kesehatan", value=f"{old_health} → {data[user_id]['kesehatan']} (+{health_boost})", inline=True)
    embed.add_field(name="💰 Honor", value=f"Rp{payment:,}", inline=True)
    embed.add_field(name="🦷 Hasil", value="Gigi bersih, nafas segar!", inline=False)
    
    await ctx.send(embed=embed)

async def fast_travel_skill(ctx, user_id):
    """Pilot - penerbangan cepat"""
    destinations = [
        {"name": "Jakarta-Bali", "pay": 500000},
        {"name": "Jakarta-Medan", "pay": 400000},
        {"name": "Jakarta-Makassar", "pay": 450000},
        {"name": "Jakarta-Surabaya", "pay": 350000}
    ]
    
    flight = random.choice(destinations)
    data[user_id]["uang"] += flight["pay"]
    data[user_id]["xp"] += 80
    
    # Reset all cooldowns (fast travel benefit)
    current_time = int(time.time())
    if "last_work" in data[user_id]:
        data[user_id]["last_work"] = datetime.fromtimestamp(current_time - 3600).isoformat()
    if "last_crime" in data[user_id]:
        data[user_id]["last_crime"] = current_time - 7200
    
    embed = discord.Embed(title="✈️ Penerbangan Express", color=0x0099ff)
    embed.add_field(name="👨‍✈️ Pilot", value=ctx.author.display_name, inline=True)
    embed.add_field(name="🗺️ Rute", value=flight["name"], inline=True)
    embed.add_field(name="💰 Payment", value=f"Rp{flight['pay']:,}", inline=True)
    embed.add_field(name="⚡ Bonus", value="Semua cooldown direset!", inline=False)
    
    await ctx.send(embed=embed)

# !menutransportasi - Menu sistem transportasi
@bot.command()
async def menutransportasi(ctx):
    embed = discord.Embed(title="🚗 Menu Sistem Transportasi", color=0x3498db)
    
    embed.add_field(
        name="🪪 **SIM & Lisensi**",
        value="`!sim motor` - SIM A (Motor) Lv5+, Rp200k\n`!sim mobil` - SIM B (Mobil) Lv10+, Rp500k\n`!sim komersial` - SIM B1/B2 (Bus/Truk) Lv15+, Rp1jt",
        inline=False
    )
    
    embed.add_field(
        name="🛒 **Beli Kendaraan**",
        value="`!kendaraan` - Lihat daftar kendaraan\n`!kendaraan [kategori]` - Filter berdasarkan kategori\n`!belimobil [vehicle_key]` - Beli kendaraan",
        inline=False
    )
    
    embed.add_field(
        name="🏠 **Manajemen Garasi**",
        value="`!garasiqu` - Lihat kendaraan yang dimiliki\n🚗 Vehicle ID untuk command lainnya\n💎 Total nilai garasi investasi",
        inline=False
    )
    
    embed.add_field(
        name="🗺️ **Perjalanan & Maintenance**",
        value="`!perjalanan [vehicle_id] [jarak]` - Bepergian dengan kendaraan\n`!bengkel [vehicle_id]` - Service kendaraan\n⚡ Speed bonus mengurangi cooldown kerja",
        inline=False
    )
    
    embed.add_field(
        name="🚗 **Kategori Kendaraan**",
        value="🌱 **Eco:** Sepeda (ramah lingkungan)\n🏍️ **Basic/Sport:** Motor bebek & sport\n🚙 **City/Luxury:** City car, sedan, SUV\n🚌 **Commercial:** Bus & truk (bisnis angkutan)",
        inline=False
    )
    
    embed.add_field(
        name="💡 **Tips Transportasi**",
        value="• Kendaraan lebih mahal = speed bonus lebih tinggi\n• Speed bonus mengurangi cooldown kerja\n• Service rutin jaga kondisi kendaraan\n• Kendaraan komersial untuk bisnis angkutan\n• BBM berbeda tiap kendaraan",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Manfaat Speed Bonus**",
        value="• Cooldown kerja freelance berkurang\n• Efisiensi waktu perjalanan\n• Status symbol di komunitas\n• Investasi jangka panjang",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu | Start with !sim motor untuk SIM pertama!")
    await ctx.send(embed=embed)

# !menueducation - Menu sistem pendidikan
@bot.command()
async def menueducation(ctx):
    embed = discord.Embed(title="🎓 Menu Sistem Pendidikan", color=0x2ecc71)
    
    embed.add_field(
        name="🏛️ **Universitas & Pendaftaran**",
        value="`!universitas` - Lihat daftar universitas\n`!jurusan` - Info semua jurusan\n`!daftar_kuliah [uni_id] [jurusan]` - Daftar kuliah",
        inline=False
    )
    
    embed.add_field(
        name="📚 **Akademik**",
        value="`!belajar` - Belajar untuk meningkatkan GPA\n`!rapor [@user]` - Lihat status pendidikan\n⏰ Cooldown belajar: 6 jam",
        inline=False
    )
    
    embed.add_field(
        name="🏆 **Sistem Kelulusan**",
        value="📊 **GPA 3.7+:** Summa Cum Laude (+100% salary bonus)\n📊 **GPA 3.5+:** Magna Cum Laude (+50% salary bonus)\n📊 **GPA 3.0+:** Cum Laude (+20% salary bonus)\n📊 **GPA 2.0+:** Lulus (bonus standar)",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Universitas Terbaik**",
        value="🏛️ **UI:** Prestige 95, Rp8jt/semester\n🏛️ **ITB:** Prestige 90, Rp7.5jt/semester\n🏛️ **UGM:** Prestige 88, Rp7jt/semester\n🏛️ **ITS:** Prestige 85, Rp6.5jt/semester",
        inline=False
    )
    
    embed.add_field(
        name="💼 **Job Unlocks**",
        value="🩺 **Kedokteran:** Unlock dokter spesialis\n⚖️ **Hukum:** Unlock hakim, pengacara, jaksa\n💻 **Teknik/TI:** Unlock programmer, IT manager\n💰 **Ekonomi:** Unlock CFO, accounting\n👥 **Psikologi:** Unlock HRD manager",
        inline=False
    )
    
    embed.add_field(
        name="💡 **Tips Kuliah**",
        value="• Universitas prestige tinggi = bonus kelulusan besar\n• GPA tinggi = salary bonus seumur hidup\n• Gelar unlock pekerjaan premium\n• Belajar rutin untuk maintain GPA\n• Selesaikan minimal 2.0 GPA untuk lulus",
        inline=False
    )
    
    embed.add_field(
        name="🏅 **Contoh Career Path**",
        value="🩺 SMA → UI Kedokteran → Dokter Bedah (Rp2.2jt + 50% bonus)\n💻 SMA → ITB Teknik → IT Manager (Rp5jt + 30% bonus)\n⚖️ SMA → UGM Hukum → Hakim (Rp1.5jt + 40% bonus)",
        inline=False
    )
    
    embed.set_footer(text="Kembali ke menu utama: !menu | Education is investment in yourself! 📚")
    await ctx.send(embed=embed)

# ===== SISTEM EVENT BULANAN & TAHUNAN =====

# Database event
events = {
    "tahun_baru": {
        "nama": "Tahun Baru",
        "start_month": 1,
        "start_day": 1,
        "end_month": 1,
        "end_day": 7,
        "type": "yearly",
        "rewards": {
            "daily_bonus_multiplier": 3.0,
            "work_bonus_multiplier": 2.0,
            "special_gift": 1000000,
            "xp_bonus": 500
        },
        "activities": ["fireworks", "resolution", "party"],
        "description": "Rayakan tahun baru dengan bonus fantastis!"
    },
    "valentine": {
        "nama": "Valentine Day",
        "start_month": 2,
        "start_day": 14,
        "end_month": 2,
        "end_day": 14,
        "type": "yearly",
        "rewards": {
            "daily_bonus_multiplier": 2.0,
            "marriage_discount": 0.5,
            "love_gift": 500000
        },
        "activities": ["date", "gift", "proposal"],
        "description": "Hari kasih sayang dengan bonus spesial untuk pasangan!"
    },
    "ramadan": {
        "nama": "Ramadan",
        "start_month": 3,
        "start_day": 10,
        "end_month": 4,
        "end_day": 10,
        "type": "yearly",
        "rewards": {
            "daily_bonus_multiplier": 1.5,
            "charity_bonus": 2.0,
            "spiritual_xp": 50
        },
        "activities": ["charity", "fasting", "prayer"],
        "description": "Bulan suci dengan berkah dan pahala berlipat!"
    },
    "kemerdekaan": {
        "nama": "Hari Kemerdekaan",
        "start_month": 8,
        "start_day": 17,
        "end_month": 8,
        "end_day": 17,
        "type": "yearly",
        "rewards": {
            "daily_bonus_multiplier": 2.5,
            "patriot_bonus": 1000000,
            "flag_ceremony_xp": 300
        },
        "activities": ["flag_ceremony", "competition", "parade"],
        "description": "Peringati kemerdekaan Indonesia dengan semangat nasionalisme!"
    },
    "halloween": {
        "nama": "Halloween",
        "start_month": 10,
        "start_day": 31,
        "end_month": 10,
        "end_day": 31,
        "type": "yearly",
        "rewards": {
            "crime_success_bonus": 1.5,
            "mystery_box": True,
            "spooky_xp": 200
        },
        "activities": ["trick_treat", "costume", "haunted"],
        "description": "Malam yang menyeramkan dengan kejutan misterius!"
    },
    "christmas": {
        "nama": "Christmas",
        "start_month": 12,
        "start_day": 24,
        "end_month": 12,
        "end_day": 26,
        "type": "yearly",
        "rewards": {
            "daily_bonus_multiplier": 2.5,
            "christmas_gift": 800000,
            "family_bonus": 1.2
        },
        "activities": ["gift_exchange", "santa", "tree"],
        "description": "Natal penuh kebahagiaan dan hadiah!"
    },
    "gajian_nasional": {
        "nama": "Gajian Nasional",
        "start_day": 25,
        "end_day": 28,
        "type": "monthly",
        "rewards": {
            "salary_bonus_multiplier": 1.5,
            "work_efficiency": 1.3
        },
        "activities": ["bonus_work", "celebration"],
        "description": "Minggu gajian dengan bonus produktivitas!"
    },
    "weekend_party": {
        "nama": "Weekend Party",
        "start_day": 6,  # Saturday
        "end_day": 7,    # Sunday
        "type": "weekly",
        "rewards": {
            "entertainment_bonus": 1.2,
            "social_xp": 20
        },
        "activities": ["party", "relax"],
        "description": "Akhir pekan santai dengan bonus sosial!"
    }
}

def get_current_events():
    """Dapatkan event yang sedang aktif"""
    now = datetime.now()
    current_month = now.month
    current_day = now.day
    current_weekday = now.weekday() + 1  # 1=Monday, 7=Sunday
    
    active_events = []
    
    for event_id, event_data in events.items():
        is_active = False
        
        if event_data["type"] == "yearly":
            # Event tahunan
            start_date = datetime(now.year, event_data["start_month"], event_data["start_day"])
            end_date = datetime(now.year, event_data["end_month"], event_data["end_day"])
            
            # Handle cross-year events
            if event_data["start_month"] > event_data["end_month"]:
                end_date = datetime(now.year + 1, event_data["end_month"], event_data["end_day"])
            
            if start_date <= now <= end_date:
                is_active = True
                
        elif event_data["type"] == "monthly":
            # Event bulanan
            if event_data["start_day"] <= current_day <= event_data["end_day"]:
                is_active = True
                
        elif event_data["type"] == "weekly":
            # Event mingguan
            if event_data["start_day"] <= current_weekday <= event_data["end_day"]:
                is_active = True
        
        if is_active:
            active_events.append((event_id, event_data))
    
    return active_events

def apply_event_bonuses(base_amount, bonus_type, user_id=None):
    """Terapkan bonus dari event yang aktif"""
    active_events = get_current_events()
    if not active_events:
        return base_amount
    
    total_multiplier = 1.0
    
    for event_id, event_data in active_events:
        rewards = event_data.get("rewards", {})
        
        if bonus_type in rewards:
            if bonus_type.endswith("_multiplier"):
                total_multiplier *= rewards[bonus_type]
            else:
                # Fixed bonus
                base_amount += rewards[bonus_type]
    
    return int(base_amount * total_multiplier)

# !event - Lihat event yang sedang aktif
@bot.command()
async def event(ctx):
    active_events = get_current_events()
    
    if not active_events:
        # Cari event terdekat
        now = datetime.now()
        upcoming_events = []
        
        for event_id, event_data in events.items():
            if event_data["type"] == "yearly":
                try:
                    next_date = datetime(now.year, event_data["start_month"], event_data["start_day"])
                    if next_date < now:
                        next_date = datetime(now.year + 1, event_data["start_month"], event_data["start_day"])
                    
                    days_until = (next_date - now).days
                    upcoming_events.append((event_id, event_data, days_until))
                except:
                    continue
        
        upcoming_events.sort(key=lambda x: x[2])
        
        embed = discord.Embed(title="🎉 Tidak Ada Event Aktif", color=0x808080)
        embed.add_field(name="📅 Status", value="Tidak ada event yang sedang berlangsung", inline=False)
        
        if upcoming_events:
            next_event = upcoming_events[0]
            embed.add_field(
                name="⏰ Event Berikutnya",
                value=f"🎊 **{next_event[1]['nama']}**\n📅 {next_event[2]} hari lagi\n📝 {next_event[1]['description']}",
                inline=False
            )
        
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(title="🎉 Event Aktif Sekarang!", color=0xffd700)
    
    for event_id, event_data in active_events:
        rewards_text = ""
        for reward_key, reward_value in event_data["rewards"].items():
            if isinstance(reward_value, float) and reward_value > 1:
                rewards_text += f"• {reward_key.replace('_', ' ').title()}: {reward_value}x\n"
            elif isinstance(reward_value, int):
                rewards_text += f"• {reward_key.replace('_', ' ').title()}: +{reward_value:,}\n"
            elif reward_value == True:
                rewards_text += f"• {reward_key.replace('_', ' ').title()}: Tersedia\n"
        
        activities_text = ", ".join([act.replace('_', ' ').title() for act in event_data.get("activities", [])])
        
        embed.add_field(
            name=f"🎊 {event_data['nama']}",
            value=f"📝 {event_data['description']}\n\n🎁 **Bonus:**\n{rewards_text}\n🎯 **Aktivitas:** {activities_text}",
            inline=False
        )
    
    embed.set_footer(text="Nikmati bonus event yang tersedia! 🎈")
    await ctx.send(embed=embed)

# !fireworks - Aktivitas kembang api (Tahun Baru)
@bot.command()
async def fireworks(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    # Cek apakah event tahun baru aktif
    active_events = get_current_events()
    new_year_active = any(event_id == "tahun_baru" for event_id, _ in active_events)
    
    if not new_year_active:
        await ctx.send("🎆 Kembang api hanya tersedia saat event Tahun Baru!")
        return
    
    # Cooldown 1 jam
    current_time = int(time.time())
    last_fireworks = data[user_id].get("last_fireworks", 0)
    
    if current_time - last_fireworks < 3600:
        remaining = 3600 - (current_time - last_fireworks)
        await ctx.send(f"⏰ Tunggu {remaining//60} menit lagi untuk menyalakan kembang api.")
        return
    
    # Efek kembang api
    fireworks_cost = 100000
    if data[user_id]["uang"] < fireworks_cost:
        await ctx.send(f"❌ Kamu butuh Rp{fireworks_cost:,} untuk membeli kembang api.")
        return
    
    data[user_id]["uang"] -= fireworks_cost
    
    # Reward random
    happiness_bonus = random.randint(200, 500)
    xp_bonus = random.randint(50, 150)
    money_bonus = random.randint(50000, 200000)
    
    data[user_id]["xp"] += xp_bonus
    data[user_id]["uang"] += money_bonus
    data[user_id]["last_fireworks"] = current_time
    
    fireworks_types = ["🎆", "🎇", "✨", "🌟", "💫"]
    chosen_fireworks = random.choice(fireworks_types)
    
    embed = discord.Embed(title=f"{chosen_fireworks} Kembang Api Tahun Baru!", color=0xffd700)
    embed.add_field(name="💰 Biaya", value=f"Rp{fireworks_cost:,}", inline=True)
    embed.add_field(name="😊 Happiness", value=f"+{happiness_bonus}", inline=True)
    embed.add_field(name="⭐ XP", value=f"+{xp_bonus}", inline=True)
    embed.add_field(name="🎁 Money Bonus", value=f"+Rp{money_bonus:,}", inline=True)
    embed.add_field(name="🎉 Effect", value="Semangat tahun baru yang membara!", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !charity - Aktivitas amal (Ramadan)
@bot.command()
async def charity(ctx, jumlah: int = None):
    if jumlah is None:
        await ctx.send("💝 **Cara Beramal:**\n`!charity [jumlah]` - Berikan sedekah\n\n📿 Bonus 2x saat Ramadan\n💫 Mendapat berkah dan pahala")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if jumlah <= 0:
        await ctx.send("❌ Jumlah sedekah harus lebih dari 0.")
        return
    
    if data[user_id]["uang"] < jumlah:
        await ctx.send("❌ Uang tidak cukup untuk bersedekah.")
        return
    
    # Cek apakah Ramadan aktif
    active_events = get_current_events()
    ramadan_active = any(event_id == "ramadan" for event_id, _ in active_events)
    
    # Charity multiplier
    charity_multiplier = 2.0 if ramadan_active else 1.0
    
    data[user_id]["uang"] -= jumlah
    
    # Reward berkah (XP dan kemungkinan rejeki)
    spiritual_xp = int(jumlah / 1000 * charity_multiplier)  # 1 XP per 1000 sedekah
    data[user_id]["xp"] += spiritual_xp
    
    # Random blessing (30% chance)
    blessing = None
    if random.randint(1, 100) <= 30:
        blessing_amount = int(jumlah * random.uniform(1.5, 3.0) * charity_multiplier)
        data[user_id]["uang"] += blessing_amount
        blessing = blessing_amount
    
    embed = discord.Embed(title="💝 Sedekah Diterima", color=0x00ff00)
    embed.add_field(name="💰 Jumlah Sedekah", value=f"Rp{jumlah:,}", inline=True)
    embed.add_field(name="⭐ Spiritual XP", value=f"+{spiritual_xp}", inline=True)
    
    if ramadan_active:
        embed.add_field(name="📿 Bonus Ramadan", value="2x Pahala", inline=True)
    
    if blessing:
        embed.add_field(name="🌟 Berkah Allah", value=f"+Rp{blessing:,}", inline=False)
        embed.add_field(name="💫 Pesan", value="Sedekah yang diberikan akan kembali berlipat ganda!", inline=False)
    else:
        embed.add_field(name="💫 Pesan", value="Sedekah tidak akan mengurangi harta, semoga mendapat berkah!", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !gift_exchange - Tukar hadiah Christmas
@bot.command()
async def gift_exchange(ctx, target: discord.Member, *, gift_item=None):
    if not gift_item:
        await ctx.send("🎁 **Cara Tukar Hadiah:**\n`!gift_exchange @user [nama_item]` - Berikan hadiah dari inventory\n\n🎄 Bonus khusus saat Christmas!\n💝 Penerima dan pemberi dapat reward")
        return
    
    user_id = str(ctx.author.id)
    target_id = str(target.id)
    
    if user_id == target_id:
        await ctx.send("❌ Kamu tidak bisa memberi hadiah ke diri sendiri.")
        return
    
    create_user_profile(user_id)
    create_user_profile(target_id)
    
    # Cek Christmas event
    active_events = get_current_events()
    christmas_active = any(event_id == "christmas" for event_id, _ in active_events)
    
    # Cek item di inventory
    if gift_item.lower() not in data[user_id]["inventory"]:
        await ctx.send(f"❌ Kamu tidak punya **{gift_item.title()}** di inventory.")
        return
    
    if data[user_id]["inventory"][gift_item.lower()] <= 0:
        await ctx.send(f"❌ Kamu tidak punya **{gift_item.title()}** yang cukup.")
        return
    
    # Transfer item
    data[user_id]["inventory"][gift_item.lower()] -= 1
    if data[user_id]["inventory"][gift_item.lower()] == 0:
        del data[user_id]["inventory"][gift_item.lower()]
    
    # Add to target inventory
    if gift_item.lower() not in data[target_id]["inventory"]:
        data[target_id]["inventory"][gift_item.lower()] = 0
    data[target_id]["inventory"][gift_item.lower()] += 1
    
    # Christmas bonus
    if christmas_active:
        # Bonus untuk pemberi
        giver_bonus = random.randint(100000, 500000)
        giver_xp = random.randint(50, 200)
        data[user_id]["uang"] += giver_bonus
        data[user_id]["xp"] += giver_xp
        
        # Bonus untuk penerima
        receiver_bonus = random.randint(50000, 300000)
        receiver_xp = random.randint(25, 100)
        data[target_id]["uang"] += receiver_bonus
        data[target_id]["xp"] += receiver_xp
        
        embed = discord.Embed(title="🎄 Christmas Gift Exchange!", color=0xff0000)
        embed.add_field(name="🎁 Hadiah", value=gift_item.title(), inline=True)
        embed.add_field(name="👤 Dari", value=ctx.author.display_name, inline=True)
        embed.add_field(name="👤 Untuk", value=target.display_name, inline=True)
        embed.add_field(name="🎅 Bonus Pemberi", value=f"Rp{giver_bonus:,} + {giver_xp} XP", inline=True)
        embed.add_field(name="🎁 Bonus Penerima", value=f"Rp{receiver_bonus:,} + {receiver_xp} XP", inline=True)
        embed.add_field(name="🎄 Christmas Magic", value="Ho ho ho! Santa memberikan bonus untuk kebaikan hati!", inline=False)
    else:
        embed = discord.Embed(title="🎁 Gift Exchange", color=0x9b59b6)
        embed.add_field(name="🎁 Hadiah", value=gift_item.title(), inline=True)
        embed.add_field(name="👤 Dari", value=ctx.author.display_name, inline=True)
        embed.add_field(name="👤 Untuk", value=target.display_name, inline=True)
        embed.add_field(name="💝 Pesan", value="Berbagi itu indah!", inline=False)
    
    save_data(data)
    await ctx.send(embed=embed)
    
    # Notifikasi ke penerima
    if christmas_active:
        pesan_notif = f"🎄 **Christmas Gift!**\n\n**{ctx.author.display_name}** memberikan hadiah **{gift_item.title()}** untuk kamu!\n\n🎅 **Christmas Bonus:** Rp{receiver_bonus:,} + {receiver_xp} XP\n\nSelamat Natal! 🎁"
    else:
        pesan_notif = f"🎁 **Hadiah Diterima!**\n\n**{ctx.author.display_name}** memberikan **{gift_item.title()}** untuk kamu!\n\nTerima kasih atas kebaikan hatinya! 💝"
    
    await kirim_notif_dm(target_id, pesan_notif)

# !resolution - Resolusi tahun baru
@bot.command()
async def resolution(ctx, *, resolusi_text=None):
    if not resolusi_text:
        await ctx.send("📋 **Cara Buat Resolusi:**\n`!resolution [text]` - Buat resolusi tahun baru\n\n✨ Hanya tersedia saat event Tahun Baru\n🎯 Dapatkan motivasi dan bonus XP")
        return
    
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    # Cek tahun baru event
    active_events = get_current_events()
    new_year_active = any(event_id == "tahun_baru" for event_id, _ in active_events)
    
    if not new_year_active:
        await ctx.send("📋 Resolusi tahun baru hanya bisa dibuat saat event Tahun Baru!")
        return
    
    # Cooldown sekali per tahun
    current_year = datetime.now().year
    last_resolution_year = data[user_id].get("last_resolution_year", 0)
    
    if last_resolution_year == current_year:
        await ctx.send("❌ Kamu sudah membuat resolusi untuk tahun ini.")
        return
    
    # Simpan resolusi
    if "resolutions" not in data[user_id]:
        data[user_id]["resolutions"] = []
    
    resolution_data = {
        "year": current_year,
        "text": resolusi_text,
        "created_date": int(time.time()),
        "completed": False
    }
    
    data[user_id]["resolutions"].append(resolution_data)
    data[user_id]["last_resolution_year"] = current_year
    
    # Bonus motivasi
    motivation_xp = random.randint(200, 500)
    determination_bonus = random.randint(100000, 300000)
    
    data[user_id]["xp"] += motivation_xp
    data[user_id]["uang"] += determination_bonus
    
    embed = discord.Embed(title="✨ Resolusi Tahun Baru", color=0xffd700)
    embed.add_field(name="📅 Tahun", value=str(current_year), inline=True)
    embed.add_field(name="📋 Resolusi", value=f"*\"{resolusi_text}\"*", inline=False)
    embed.add_field(name="💪 Motivasi XP", value=f"+{motivation_xp}", inline=True)
    embed.add_field(name="🎯 Determination Bonus", value=f"+Rp{determination_bonus:,}", inline=True)
    embed.add_field(name="✨ Pesan", value="Semoga resolusi tahun ini tercapai! Tetap semangat!", inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# !myresolutions - Lihat resolusi yang pernah dibuat
@bot.command()
async def myresolutions(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    if "resolutions" not in data[user_id] or not data[user_id]["resolutions"]:
        await ctx.send("📋 Kamu belum pernah membuat resolusi. Tunggu event Tahun Baru!")
        return
    
    embed = discord.Embed(title=f"📋 Resolusi {ctx.author.display_name}", color=0x3498db)
    
    for resolution in sorted(data[user_id]["resolutions"], key=lambda x: x["year"], reverse=True)[:5]:
        status = "✅ Selesai" if resolution.get("completed", False) else "⏳ Dalam Progress"
        embed.add_field(
            name=f"📅 {resolution['year']}",
            value=f"📝 *\"{resolution['text']}\"*\n📊 Status: {status}",
            inline=False
        )
    
    await ctx.send(embed=embed)

# Modifikasi command !daily untuk apply event bonus
@bot.command()
async def daily_event(ctx):
    user_id = str(ctx.author.id)
    create_user_profile(user_id)
    
    current_time = int(time.time())
    last_daily = data[user_id].get("last_daily", 0)
    
    if current_time - last_daily < 86400:  # 24 jam
        remaining = 86400 - (current_time - last_daily)
        await ctx.send(f"⏰ Tunggu {remaining//3600} jam lagi untuk daily bonus.")
        return
    
    # Base daily bonus
    base_daily = 50000
    level = calculate_level(data[user_id]["xp"])
    level_bonus = level * 5000
    
    # Streak bonus
    if current_time - last_daily <= 172800:  # Dalam 2 hari
        data[user_id]["daily_streak"] = data[user_id].get("daily_streak", 0) + 1
    else:
        data[user_id]["daily_streak"] = 1
    
    streak_bonus = min(data[user_id]["daily_streak"] * 10000, 100000)
    
    # Apply event bonus
    total_bonus = apply_event_bonuses(base_daily + level_bonus + streak_bonus, "daily_bonus_multiplier", user_id)
    
    # Special event gifts
    active_events = get_current_events()
    special_gifts = []
    
    for event_id, event_data in active_events:
        rewards = event_data.get("rewards", {})
        for reward_key, reward_value in rewards.items():
            if reward_key not in ["daily_bonus_multiplier"] and isinstance(reward_value, int):
                special_gifts.append((reward_key.replace('_', ' ').title(), reward_value))
                data[user_id]["uang"] += reward_value
    
    data[user_id]["uang"] += total_bonus
    data[user_id]["last_daily"] = current_time
    data[user_id]["xp"] += 20
    
    embed = discord.Embed(title="🎁 Daily Bonus dengan Event!", color=0x00ff00)
    embed.add_field(name="💰 Base", value=f"Rp{base_daily:,}", inline=True)
    embed.add_field(name="📊 Level Bonus", value=f"Rp{level_bonus:,}", inline=True)
    embed.add_field(name="🔥 Streak Bonus", value=f"Rp{streak_bonus:,}", inline=True)
    
    if total_bonus > (base_daily + level_bonus + streak_bonus):
        event_bonus = total_bonus - (base_daily + level_bonus + streak_bonus)
        embed.add_field(name="🎉 Event Bonus", value=f"Rp{event_bonus:,}", inline=True)
    
    embed.add_field(name="💎 Total", value=f"Rp{total_bonus:,}", inline=False)
    
    if special_gifts:
        gifts_text = "\n".join([f"• {name}: +Rp{value:,}" for name, value in special_gifts])
        embed.add_field(name="🎁 Special Event Gifts", value=gifts_text, inline=False)
    
    if active_events:
        events_text = "\n".join([f"🎊 {event_data['nama']}" for event_id, event_data in active_events])
        embed.add_field(name="✨ Event Aktif", value=events_text, inline=False)
    
    save_data(data)
    await ctx.send(f"{ctx.author.mention}", embed=embed)

# Update menu untuk include event system
@bot.command()
async def menuevent(ctx):
    embed = discord.Embed(title="🎉 Menu Sistem Event", color=0xffd700)
    
    embed.add_field(
        name="📅 **Event Management**",
        value="`!event` - Lihat event yang sedang aktif\n📊 Event tahunan, bulanan, dan mingguan\n🎁 Bonus dan reward khusus",
        inline=False
    )
    
    embed.add_field(
        name="🎆 **Event Tahunan**",
        value="🎊 **Tahun Baru** (1-7 Jan): Fireworks, resolusi, bonus 3x\n💝 **Valentine** (14 Feb): Date activities, marriage discount\n📿 **Ramadan** (Mar-Apr): Charity bonus 2x, spiritual XP\n🇮🇩 **Kemerdekaan** (17 Aug): Flag ceremony, patriot bonus\n🎃 **Halloween** (31 Oct): Trick treat, mystery box\n🎄 **Christmas** (24-26 Des): Gift exchange, family bonus",
        inline=False
    )
    
    embed.add_field(
        name="🗓️ **Event Bulanan & Mingguan**",
        value="💰 **Gajian Nasional** (25-28): Salary bonus 1.5x\n🎉 **Weekend Party** (Sabtu-Minggu): Entertainment bonus",
        inline=False
    )
    
    embed.add_field(
        name="🎯 **Aktivitas Event**",
        value="`!fireworks` - Kembang api (Tahun Baru)\n`!charity [jumlah]` - Beramal (Ramadan bonus 2x)\n`!gift_exchange @user [item]` - Tukar hadiah (Christmas)\n`!resolution [text]` - Buat resolusi (Tahun Baru)\n`!myresolutions` - Lihat resolusi yang pernah dibuat",
        inline=False
    )
    
    embed.add_field(
    name="🎁 **Jenis Bonus Event**",
    value="💰 Daily bonus multiplier\n💼 Work bonus multiplier\n🎊 Special gifts dan hadiah\n⭐ XP bonus events\n🏠 Discount untuk item khusus\n🎯 Aktivitas unik per event",
    inline=False
)
    
    embed.add_field(
        name="✨ **Auto Features**",
        value="• Bonus otomatis diterapkan saat event aktif\n• Notifikasi DM untuk event baru\n• Daily bonus enhanced saat event\n• Work rewards meningkat\n• Marriage discount saat Valentine\n• Crime success bonus saat Halloween",
        inline=False
    )
    
    embed.set_footer(text="Event memberikan pengalaman bermain yang lebih menarik sepanjang tahun! 🎈")
    await ctx.send(embed=embed)
   
from discord.ext.commands import MissingRequiredArgument, CommandNotFound

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("❌ Format salah. Pastikan kamu menulis perintah dengan lengkap.")
    elif isinstance(error, CommandNotFound):
        await ctx.send("❌ Perintah tidak ditemukan. Cek daftar perintah dengan `!menu` atau `!help`.")
    else:
        raise error  # biar error lainnya tetap muncul di console saat develop

# Get token from environment
TOKEN = os.environ['TOKEN']
bot.run(TOKEN)