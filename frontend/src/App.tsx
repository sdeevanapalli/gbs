import { useState, useEffect } from 'react'
import axios from 'axios'
import './index.css'

function App() {
  const [backendStatus, setBackendStatus] = useState('Connecting...')

  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/test')
        setBackendStatus(response.data.message)
      } catch (error) {
        setBackendStatus('Backend connection failed')
      }
    }
    testConnection()
  }, [])

  return (
    <div className="container">
      <h1 style={{fontSize: '2rem', fontWeight: 'bold', marginBottom: '2rem'}}>
        Clinical Trials Resource Dashboard
      </h1>
      <div className="card">
        <h2 style={{fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem'}}>
          System Status
        </h2>
        <p style={{color: '#666'}}>Backend: {backendStatus}</p>
      </div>
    </div>
  )
}

export default App
