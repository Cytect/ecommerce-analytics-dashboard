# Proyek Analisis Data: E-Commerce Public Dataset

Submission proyek akhir untuk kelas **Belajar Analisis Data dengan Python (Dicoding Academy 555)**. 
Mencakup Data Wrangling, EDA, Visualisasi Data, Analisis RFM & Geospatial, serta Dashboard Interaktif berbasis Streamlit.

## Struktur Direktori
```text
Submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   └── (file-file csv dataset mentah)
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Menjalankan Dashboard di Komputer Lokal

1. Buka terminal pada folder proyek:
   ```bash
   cd "path/ke/submission"
   ```
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan server Streamlit:
   ```bash
   streamlit run dashboard/dashboard.py
   ```
4. Buka browser pada alamat `http://localhost:8501`.