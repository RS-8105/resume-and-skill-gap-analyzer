import { useState } from 'react'
import html2pdf from 'html2pdf.js'
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

  const compOverview = result.companyOverview || result.company_overview;
  const compGrowth = result.companyGrowth || result.company_growth;
  const roleResp = result.roleResponsibilities || result.role_responsibilities;
  const avgSalary = result.averageSalary || result.average_salary;
  const optResume = result.optimizedResume || result.optimized_resume;
  const companies = result.recommendedCompanies || result.recommended_companies || [];

  const downloadResume = () => {
    const element = document.getElementById('resume-document');
    if (!element) return;
    const opt = {
      margin:       10,
      filename:     'Optimized_Resume.pdf',
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2 },
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
  };

  const renderStyledResume = (rawText) => {
    if (!rawText) return null;
    let data = {};
    try {
      const match = rawText.match(/\{[\s\S]*\}/);
      data = JSON.parse(match ? match[0] : rawText);
    } catch(e) {
      return <pre style={{whiteSpace: 'pre-wrap'}}>{rawText}</pre>;
    }

    const SectionHeader = ({title}) => (
      <div style={{ color: '#0d47a1', borderBottom: '1.5px solid #0d47a1', margin: '8px 0 4px 0' }}>
        <h4 style={{ margin: 0, fontSize: '11pt', textTransform: 'uppercase', fontWeight: 'bold' }}>{title}</h4>
      </div>
    );

    return (
      <div id="resume-document" style={{
        backgroundColor: '#fff',
        padding: '0.6in',
        fontFamily: 'Arial, sans-serif',
        textAlign: 'left',
        color: '#000',
        fontSize: '10pt',
        lineHeight: '1.3',
        maxWidth: '800px',
        margin: '0 auto'
      }}>
        <div style={{ marginBottom: '15px' }}>
          <div className="name">{data.name || 'YOUR NAME'}</div>
          <div className="contact">
            {[data.phone, data.email, data.linkedin, data.github, data.portfolio].filter(Boolean).join(' | ')}
          </div>
          <div className="divider"></div>
        </div>

        {data.objective && (
          <div>
            <SectionHeader title="Objective" />
            <p style={{ margin: '2px 0' }}>{data.objective}</p>
          </div>
        )}

        {data.education && (
          <div>
            <SectionHeader title="Education" />
            <p style={{ margin: '2px 0' }}>{data.education}</p>
          </div>
        )}

        {data.skills && Object.keys(data.skills).some(k => data.skills[k]) && (
          <div>
            <SectionHeader title="Technical Skills" />
            {Object.entries(data.skills).map(([k, v]) => v ? (
              <div key={k} style={{ margin: '3px 0' }}>
                <strong>{k.charAt(0).toUpperCase() + k.slice(1)}:</strong> {v}
              </div>
            ) : null)}
          </div>
        )}

        {data.projects && data.projects.length > 0 && (
          <div>
            <SectionHeader title="Projects" />
            {data.projects.map((proj, i) => (
              <div key={i} style={{ marginBottom: '6px' }}>
                <div style={{ fontWeight: 'bold' }}>{proj.title}</div>
                {proj.description && proj.description.length > 0 && (
                  <ul style={{ margin: '3px 0 3px 20px', padding: 0 }}>
                    {proj.description.map((desc, d) => <li key={d}>{desc}</li>)}
                  </ul>
                )}
                {proj.tech_stack && <div style={{ color: '#555', fontSize: '9pt', marginTop: '2px' }}><strong>Tech Stack:</strong> {proj.tech_stack}</div>}
              </div>
            ))}
          </div>
        )}

        {data.exposure && data.exposure.length > 0 && (
          <div>
            <SectionHeader title="Practical Exposure" />
            <ul style={{ margin: '3px 0 3px 20px', padding: 0 }}>
              {data.exposure.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        )}

        {data.achievements && data.achievements.length > 0 && (
          <div>
            <SectionHeader title="Achievements" />
            <ul style={{ margin: '3px 0 3px 20px', padding: 0 }}>
              {data.achievements.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        )}

        {data.activities && data.activities.length > 0 && (
          <div>
            <SectionHeader title="Activities" />
            <ul style={{ margin: '3px 0 3px 20px', padding: 0 }}>
              {data.activities.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        )}

        {data.strengths && (
          <div>
            <SectionHeader title="Strengths" />
            <p style={{ margin: '2px 0' }}>{data.strengths}</p>
          </div>
        )}
      </div>
    );
  };

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

      {(compOverview || compGrowth || roleResp || avgSalary) && (
        <div className="recommendations-section" style={{marginTop: '25px'}}>
          <h4>Company & Role Insights</h4>
          {compOverview && (
            <div style={{marginBottom: '15px'}}>
              <strong>Company Overview</strong>
              <p style={{margin: '5px 0 0 0', lineHeight: '1.5'}}>{compOverview}</p>
            </div>
          )}
          {compGrowth && (
            <div style={{marginBottom: '15px'}}>
              <strong>Company Growth</strong>
              <p style={{margin: '5px 0 0 0', lineHeight: '1.5'}}>{compGrowth}</p>
            </div>
          )}
          {roleResp && (
            <div style={{marginBottom: '15px'}}>
              <strong>Role Responsibilities</strong>
              <p style={{margin: '5px 0 0 0', lineHeight: '1.5'}}>{roleResp}</p>
            </div>
          )}
          {avgSalary && (
            <div>
              <strong>Average Salary</strong>
              <p style={{margin: '5px 0 0 0', lineHeight: '1.5'}}>{avgSalary}</p>
            </div>
          )}
        </div>
      )}
      {companies.length > 0 && (
        <div className="recommendations-section" style={{marginTop: '25px'}}>
          <h4>Better Company Matches</h4>
          {companies.map((c, i) => (
            <div key={i} className="company-card">
              <b>{c.company}</b>
              <p>{c.reason}</p>
            </div>
          ))}
        </div>
      )}

      {optResume && (
        <div className="optimized-resume">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h3 style={{ margin: 0 }}>Optimized Resume</h3>
            <button className="analyze-btn" style={{ padding: '10px 20px', fontSize: '1rem' }} onClick={downloadResume}>
              Download (.pdf)
            </button>
          </div>
          <div style={{ border: '1px solid #ddd', maxHeight: '500px', overflowY: 'auto', backgroundColor: '#f9f9f9' }}>
            {renderStyledResume(optResume)}
          </div>
        </div>
      )}
    </div>
  )
}

function App() {
  const [file, setFile] = useState(null)
  const [company, setCompany] = useState('')
  const [role, setRole] = useState('')
  const [experience, setExperience] = useState('Beginner')
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
    formData.append('resume', file)
    formData.append('company', company)
    formData.append('role', role || 'the specified role')
    formData.append('experience', experience)

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080'
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
      
      console.log("Analysis Result:", data)
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
            <label>Target Role</label>
            <input 
              type="text" 
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Software Engineer..."
            />
          </div>

          <div className="form-group">
            <label>Experience Level</label>
            <select 
              value={experience} 
              onChange={(e) => setExperience(e.target.value)}
            >
              <option value="Beginner">Beginner (0-2 years)</option>
              <option value="Intermediate">Intermediate (3-5 years)</option>
              <option value="Experienced">Experienced (5+ years)</option>
            </select>
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
