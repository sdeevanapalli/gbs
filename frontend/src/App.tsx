import { useState, useEffect } from 'react'
import axios from 'axios'
import './index.css'

interface DashboardSummary {
  total_resources: number
  total_trials: number
  therapeutic_areas: string[]
  quarters: string[]
  overall_utilization: number
}

function App() {
  const [backendStatus, setBackendStatus] = useState('Connecting...')
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        // Test basic connection
        const healthResponse = await axios.get('http://localhost:8000/health')
        setBackendStatus('Connected ✅')
        
        // Load dashboard summary
        const summaryResponse = await axios.get<DashboardSummary>('http://localhost:8000/api/dashboard-summary')
        setDashboardData(summaryResponse.data)
        
        setLoading(false)
      } catch (error) {
        setBackendStatus('Connection failed ❌')
        setLoading(false)
        console.error('Connection error:', error)
      }
    }
    loadData()
  }, [])

  const uploadSampleData = async () => {
    try {
      // Create sample data for upload
      const sampleData = {
        "resources": [
          {
            "name": "Dr. Sarah Smith",
            "area": "Cardiology", 
            "Q3-2025": 0.8,
            "Q4-2025": 1.2,
            "Q1-2026": 0.5,
            "Q2-2026": 0.9
          },
          {
            "name": "Dr. Michael Johnson",
            "area": "Diabetes",
            "Q3-2025": 1.0,
            "Q4-2025": 0.7,
            "Q1-2026": 1.1,
            "Q2-2026": 0.8
          }
        ],
        "trials": [
          {
            "name": "CARDIO-2025-001",
            "area": "Cardiology",
            "subjects": 1300,
            "start_date": "2025-01-15",
            "end_date": "2025-12-30"
          }
        ]
      }

      const blob = new Blob([JSON.stringify(sampleData, null, 2)], { type: 'application/json' })
      const formData = new FormData()
      formData.append('file', blob, 'sample_data.json')

      await axios.post('http://localhost:8000/api/upload-data', formData)
      
      // Refresh dashboard data
      const summaryResponse = await axios.get<DashboardSummary>('http://localhost:8000/api/dashboard-summary')
      setDashboardData(summaryResponse.data)
      
      alert('Sample data uploaded successfully!')
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed')
    }
  }

  return (
    <div className="container">
      <h1 style={{fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '2rem', textAlign: 'center'}}>
        Clinical Trials Resource Dashboard
      </h1>
      
      {/* Connection Status */}
      <div className="card">
        <h2 style={{fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem'}}>
          System Status
        </h2>
        <p style={{color: '#666', marginBottom: '1rem'}}>Backend: {backendStatus}</p>
        
        {(!dashboardData?.total_resources || dashboardData.total_resources === 0) && !loading && (
          <button className="btn" onClick={uploadSampleData}>
            Load Sample Data
          </button>
        )}
      </div>

      {/* Dashboard Summary */}
      {loading ? (
        <div className="card">
          <p>Loading dashboard data...</p>
        </div>
      ) : dashboardData ? (
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px'}}>
          
          <div className="card">
            <h3 style={{color: '#007bff', fontSize: '2rem', marginBottom: '0.5rem'}}>
              {dashboardData.total_resources}
            </h3>
            <p style={{color: '#666'}}>Total Resources</p>
          </div>

          <div className="card">
            <h3 style={{color: '#28a745', fontSize: '2rem', marginBottom: '0.5rem'}}>
              {dashboardData.total_trials}
            </h3>
            <p style={{color: '#666'}}>Active Trials</p>
          </div>

          <div className="card">
            <h3 style={{color: '#ffc107', fontSize: '2rem', marginBottom: '0.5rem'}}>
              {dashboardData.overall_utilization}%
            </h3>
            <p style={{color: '#666'}}>Overall Utilization</p>
          </div>

          <div className="card">
            <h3 style={{color: '#6f42c1', fontSize: '2rem', marginBottom: '0.5rem'}}>
              {dashboardData.therapeutic_areas?.length || 0}
            </h3>
            <p style={{color: '#666'}}>Therapeutic Areas</p>
          </div>

        </div>
      ) : (
        <div className="card">
          <p>No data available. Upload some data to get started!</p>
        </div>
      )}

      {/* Quarters Display */}
      {dashboardData && dashboardData.quarters && dashboardData.quarters.length > 0 && (
        <div className="card">
          <h3 style={{fontSize: '1.2rem', fontWeight: '600', marginBottom: '1rem'}}>
            Current Quarters
          </h3>
          <div style={{display: 'flex', gap: '10px', flexWrap: 'wrap'}}>
            {dashboardData.quarters.map(quarter => (
              <span 
                key={quarter}
                style={{
                  background: '#e9ecef', 
                  padding: '5px 12px', 
                  borderRadius: '4px',
                  fontSize: '0.9rem'
                }}
              >
                {quarter}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Therapeutic Areas */}
      {dashboardData && dashboardData.therapeutic_areas && dashboardData.therapeutic_areas.length > 0 && (
        <div className="card">
          <h3 style={{fontSize: '1.2rem', fontWeight: '600', marginBottom: '1rem'}}>
            Therapeutic Areas
          </h3>
          <div style={{display: 'flex', gap: '10px', flexWrap: 'wrap'}}>
            {dashboardData.therapeutic_areas.map(area => (
              <span 
                key={area}
                style={{
                  background: '#007bff', 
                  color: 'white',
                  padding: '8px 16px', 
                  borderRadius: '20px',
                  fontSize: '0.9rem'
                }}
              >
                {area}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
