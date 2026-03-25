# AI Resume Skill Gap Analyzer

An AI-powered full-stack application that analyzes resume alignment with target job roles using NLP techniques.

## 🚀 Tech Stack

- Frontend: React (Vite)
- Backend: Spring Boot (Java)
- NLP Service: FastAPI (Python)
- Machine Learning: scikit-learn (TF-IDF + Cosine Similarity)

---

## 🏗 Architecture

Frontend (React)
        ↓
Spring Boot Backend
        ↓
FastAPI NLP Microservice

---

## ✨ Features

- Resume PDF upload
- Skill gap detection
- TF-IDF similarity scoring
- Present & missing skills visualization
- Progress bars for match metrics
- Microservice architecture

---

## 📊 How It Works

1. User uploads resume.
2. Spring Boot extracts text from PDF.
3. Backend sends resume text to FastAPI service.
4. NLP service:
   - Detects present/missing skills
   - Calculates skill match percentage
   - Computes cosine similarity
5. Results displayed in React UI.

---

## 🛠 Setup Instructions

### Backend (Spring Boot)

```bash
cd backend
./mvnw spring-boot:run

```
Runs on: http://localhost:8080

NLP Service (FastAPI)
cd nlp-service
uvicorn main:app --reload

Runs on: http://localhost:8000

Frontend (React)
cd frontend
npm install
npm run dev

Runs on: http://localhost:5173

📈 Future Improvements

Add authentication

Store resume analysis history

Deploy using Docker

Add embeddings (Sentence Transformers)

Support more job roles

👨‍💻 Author

Built as a full-stack AI portfolio project.


---

# 📌 Create requirements.txt (NLP folder)

Inside `nlp-service/requirements.txt`:


fastapi
uvicorn
scikit-learn
pydantic


---

# 📌 Add .gitignore Files

### Root `.gitignore`


node_modules/
venv/
target/
pycache/
*.class
.env


---

# 🚀 How To Create Repo

In your root project folder:

```bash
git init
git add .
git commit -m "Initial commit - AI Resume Skill Gap Analyzer"

Then:

Go to GitHub

Create new repository

Copy remote URL

Then:

git remote add origin https://github.com/yourusername/ai-resume-skill-gap-analyzer.git
git branch -M main
git push -u origin main


