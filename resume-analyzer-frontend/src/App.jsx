import { useState } from 'react'
import './App.css'

const ProgressBar = ({ label, percentage, type }) => {
  return (
    <div className="metric-item">
      <div className="metric-header">
        <span className="metric-label">{label}</span>
        <span className="metric-value">{percentage}%</span>
      </div>
      <div className="progress-bar-container">
        <div 
          className={`progress-bar ${type}-bar`} 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  )
}

const SkillBadge = ({ skill, type }) => {
  return (
    <span className={`badge ${type}`}>
      {skill}
    </span>
  )
}

const ResultCard = ({ result }) => {
  if (!result) return null;

  return (
    <div className="result-card">
      <div className="result-header">
        <h3>Analysis Audit</h3>
      </div>
      
      <div className="metrics-section">
        <ProgressBar 
          label="Resume Score Alignment" 
          percentage={result.skill_match_percentage} 
          type="match" 
        />
      </div>

      <div className="skills-section">
        <div className="skill-group">
          <h4>Detected Skills</h4>
          <div className="badges">
            {result.present_skills && result.present_skills.length > 0 ? (
              result.present_skills.map((skill, i) => (
                <SkillBadge key={`present-${i}`} skill={skill} type="present" />
              ))
            ) : (
              <span className="badge empty">None detected</span>
            )}
          </div>
        </div>
        
        <div className="skill-group" style={{marginTop: '25px'}}>
          <h4>Missing Skills</h4>
          <div className="badges">
            {result.missing_skills && result.missing_skills.length > 0 ? (
              result.missing_skills.map((skill, i) => (
                <SkillBadge key={`missing-${i}`} skill={skill} type="missing" />
              ))
            ) : (
              <span className="badge empty">None missing</span>
            )}
          </div>
        </div>
      </div>

      {result.recommendations && result.recommendations.length > 0 && (
        <div className="recommendations-section">
          <h4>Recommendations</h4>
          <ul>
            {result.recommendations.map((rec, i) => (
              <li key={`rec-${i}`}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function App() {
  const [file, setFile] = useState(null)
  const [company, setCompany] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleAnalyze = async () => {
    if (!file) {
      setError('Upload a PDF first!')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('company', company)
    formData.append('jobDescription', jobDescription)

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'https://resume-and-skill-gap-analyzer-backend.onrender.com'
      const response = await fetch(`${apiUrl}/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Connection Error: Server returned ${response.status}`)
      }

      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.error)
      }
      
      setResult(data)
    } catch (err) {
      console.error('Error analyzing resume:', err)
      setError(err.message || 'Failed to analyze resume.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-wrapper">
      <div className="container">
        
        <div className="header">
          <h1>AI Resume Audit</h1>
          <br/>
          <p>Identify critical skill gaps and align your resume instantly.</p>
        </div>
        
        <div className="main-card">
          <div className="form-group">
            <label>Target Company</label>
            <input 
              type="text" 
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Stripe, Google..."
            />
          </div>
          
          <div className="form-group">
            <label>Job Description</label>
            <textarea 
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the raw requirements here..."
              rows={5}
            ></textarea>
          </div>

          <div className="form-group">
            <div className="file-upload-zone">
              <input 
                type="file" 
                accept=".pdf" 
                onChange={handleFileChange} 
              />
              {file ? "PDF LOADED: " + file.name : "DROP RESUME PDF HERE"}
            </div>
          </div>

          {error && <div className="error-message">
            ERROR: {error}
          </div>}

          <button 
            className={`analyze-btn ${loading ? 'loading' : ''}`} 
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? 'AUDITING...' : 'START AUDIT'}
          </button>
        </div>

        <ResultCard result={result} />
        
      </div>
    </div>
  )
}

export default App
