## 🏥 Medical Note Structurer

**AI-powered app** to convert unstructured doctor notes into structured clinical data using a local LLM (LLaMA 2 via Ollama). Built with **FastAPI** (backend), **Streamlit** (frontend), and **Pandas** for data handling.

---

### 🚀 Features

- Extracts structured clinical data from unstructured doctor notes:
  - ✅ Symptoms
  - ✅ Diagnosis
  - ✅ Medications
  - ✅ Follow-up Instructions
- Upload CSV files with `doctor_notes` column
- Download cleaned, structured results as CSV
- Works entirely offline using **Ollama + LLaMA 2**
- Full-stack Python app with FastAPI + Streamlit

---

### 🧠 Skills & Concepts Practiced

- 🧱 Full-stack app development (FastAPI + Streamlit)
- 🤖 Prompt Engineering for clinical text extraction
- 🦙 Local inference using **Ollama** + **LLaMA 2**
- 🔄 JSON handling and response validation with Pydantic
- 📊 CSV upload, row-wise processing, and result export

---

### 📂 Project Structure

```
medical-note-structurer/
│
├── backend/                    # FastAPI backend
│   └── main.py
│
├── frontend/                   # Streamlit frontend
│   └── app.py
│
├── requirements.txt            # Dependencies
└── README.md
```

---

### ⚙️ Setup Instructions

1. **Install Ollama & Pull Model**
   ```bash
   ollama run llama2
   ```

2. **Start Ollama Server**
   ```bash
   ollama serve
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Backend**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

5. **Run Frontend**
   ```bash
   streamlit run app.py
   ```

---

### 📥 Sample Input CSV

| patient_id | doctor_notes |
|------------|--------------|
| 001        | Patient complains of headaches and nausea. Prescribed ibuprofen. Follow-up in 2 weeks. |

---

### ✅ Output Example

```json
{
  "symptoms": ["headaches", "nausea"],
  "diagnosis": "Migraine",
  "medication": ["ibuprofen"],
  "follow_up": "Follow-up in 2 weeks"
}
```

---

### 📌 To-Do / Future Improvements

- [ ] Add user authentication
- [ ] Model fine-tuning for clinical data
- [ ] Batch processing for large CSVs
- [ ] Dockerize app for deployment

---

### 🙋‍♂️ Author

**Nicholas**  
Aspiring AI Engineer | FastAPI & Streamlit Enthusiast  
