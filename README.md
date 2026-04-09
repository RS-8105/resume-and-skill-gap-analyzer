# Resume & Skill Gap Analyzer

An intelligent, AI-powered application that analyzes resumes against specific job descriptions. This tool leverages the Google Gemini API to identify missing skills, compare candidate qualifications with job requirements, and output a detailed skill gap analysis.

## Project Structure

This project uses a microservices architecture:
*   **resume-analyzer-frontend**: A React application powered by Vite, featuring a sleek, responsive UI.
*   **resume-analyzer-backend**: A Spring Boot Java service handling file uploads (PDF extraction) and orchestrating requests.
*   **resume-analyzer-nlp-service**: A FastAPI Python service that securely integrates with Google Gemini to perform the NLP-based skill extraction and comparison.

## Setup Instructions

### 1. NLP Service (Python)
1.  Navigate to `resume-analyzer-nlp-service`.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file containing your Gemini API Key:
    ```env
    GEMINI_API_KEY=your_google_gemini_api_key
    ```
4.  Run the application:
    ```bash
    uvicorn main:app --reload
    ```
    *The service will start on port 8000.*

### 2. Backend Service (Spring Boot)
1.  Navigate to `resume-analyzer-backend`.
2.  Run the Spring Boot application using Maven:
    ```bash
    ./mvnw spring-boot:run
    ```
    *The service will start on port 8080.*

### 3. Frontend Service (React)
1.  Navigate to `resume-analyzer-frontend`.
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    *The frontend will be accessible at http://localhost:5173.*

## Deployment

The application components are configured to be deployed independently.
*   **Frontend**: Set up your Vercel/Netlify environment variable `VITE_API_URL` to point to the Spring Boot backend instance.
*   **Backend**: Ensure the Spring Boot backend `NLP_SERVICE_URL` variable addresses your deployed FastAPI service.
*   **NLP**: Provide the `GEMINI_API_KEY` configuration directly in your hosting provider's variables (e.g., Render/Railway).
