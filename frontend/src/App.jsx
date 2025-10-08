import { useState, useEffect } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'https://backend-joshua-payapullis-projects.vercel.app'
console.log('API_URL:', API_URL, 'VITE_API_URL:', import.meta.env.VITE_API_URL)

function App() {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState(null)
  const [, setAuthState] = useState(null)
  const [fitnessData, setFitnessData] = useState(null)
  const [fitnessLoading, setFitnessLoading] = useState(false)
  const [currentView, setCurrentView] = useState('overview') // 'overview' or 'calendar'

  const fetchPing = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/ping`)
      const data = await response.json()
      setMessage(data.message)
    } catch {
      setMessage('Error connecting to backend')
    } finally {
      setLoading(false)
    }
  }

  const initiateStravaAuth = async () => {
    try {
      const response = await fetch(`${API_URL}/auth/strava`)
      const data = await response.json()
      setAuthState(data.state)
      window.location.href = data.auth_url
    } catch (error) {
      console.error('Error initiating Strava auth:', error)
    }
  }

  const fetchUserProfile = async (state) => {
    try {
      const response = await fetch(`${API_URL}/user/profile?state=${state}`)
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      }
    } catch (error) {
      console.error('Error fetching user profile:', error)
    }
  }

  const fetchTrainingVolume = async (state) => {
    if (!state) return
    setFitnessLoading(true)
    try {
        const response = await fetch(`${API_URL}/training/volume?state=${state}`)
        if (response.ok) {
          const trainingData = await response.json()
          console.log('🔍 DEBUG: Training data received:', trainingData)
          console.log('🔍 DEBUG: Calendar data:', trainingData.calendar)
          setFitnessData(trainingData)
        } else {
          console.error('❌ DEBUG: Failed to fetch training data:', response.status, response.statusText)
        }
    } catch (error) {
      console.error('Error fetching training volume:', error)
    } finally {
      setFitnessLoading(false)
    }
  }

  useEffect(() => {
    fetchPing()
    
    const urlParams = new URLSearchParams(window.location.search)
    const authSuccess = urlParams.get('auth_success')
    const state = urlParams.get('state')
    
    if (authSuccess === 'true' && state) {
      setAuthState(state)
      fetchUserProfile(state)
      fetchTrainingVolume(state)
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [])

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0a0a0a',
      padding: '40px 20px',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'flex-start',
      width: '100vw',
      margin: 0,
      position: 'relative'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '800px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        margin: '0 auto'
      }}>
        {/* Header */}
        <div className="header">
      <h1>Stryde</h1>
          <p>Your Personal Running Coach</p>
        </div>
      
        {/* Backend Status */}
        <div className="section" style={{ textAlign: 'center', width: '100%', maxWidth: '100%' }}>
        <button onClick={fetchPing} disabled={loading}>
          {loading ? 'Loading...' : 'Ping Backend'}
        </button>
          <p style={{ marginTop: 15, color: '#aaa' }}>
            Backend response: <strong style={{ color: '#ff6b35' }}>{message}</strong>
          </p>
      </div>

        {/* Logged in content */}
        {user ? (
          <>
            {/* Welcome Card */}
            <div className="section" style={{ textAlign: 'center', width: '100%', maxWidth: '100%' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '20px', flexWrap: 'wrap' }}>
            {user.profile_medium && (
              <img 
                src={user.profile_medium} 
                alt="Profile" 
                    style={{
                      width: 80,
                      height: 80,
                      borderRadius: '50%',
                      border: '2px solid #333'
                    }}
                  />
                )}
                <div>
                  <h2 style={{ margin: '0 0 5px 0', fontSize: '1.8rem', color: 'white' }}>
                    Welcome back, {user.firstname}
                  </h2>
                  <p style={{ margin: '0', color: '#888', fontSize: '14px' }}>
                    @{user.username}
                  </p>
                </div>
              </div>
            </div>

            {/* Tab Navigation */}
            <div className="section" style={{ textAlign: 'center', width: '100%', maxWidth: '100%' }}>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                <button
                  onClick={() => setCurrentView('overview')}
                  style={{
                    background: currentView === 'overview' ? '#ff6b35' : '#2b2b2b',
                    border: 'none',
                    color: 'white',
                    padding: '10px 20px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: '600'
                  }}
                >
                  Overview
                </button>
                <button
                  onClick={() => setCurrentView('calendar')}
                  style={{
                    background: currentView === 'calendar' ? '#ff6b35' : '#2b2b2b',
                    border: 'none',
                    color: 'white',
                    padding: '10px 20px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: '600'
                  }}
                >
                  AI Calendar
                </button>
              </div>
            </div>

            {/* Overview Tab Content */}
            {currentView === 'overview' && fitnessData && (
              <>
                {/* Training Overview */}
              <div className="section">
                <h3 style={{ textAlign: 'center', marginBottom: '24px' }}>Training Overview</h3>
                <div className="card-grid">
                  <div className="card">
                    <h3>Total Runs</h3>
                    <div className="value">{fitnessData.total_activities}</div>
                  </div>
                  <div className="card">
                    <h3>Runs This Week</h3>
                    <div className="value">{fitnessData.weekly_volume[0]?.runs || 0}</div>
                  </div>
                  <div className="card">
                    <h3>Distance This Week</h3>
                    <div className="value">
                      {fitnessData.weekly_volume[0]?.distance_km.toFixed(1) || '0.0'} km
                    </div>
                  </div>
                  <div className="card">
                    <h3>Distance This Month</h3>
                    <div className="value">
                      {fitnessData.monthly_volume[0]?.distance_km.toFixed(1) || '0.0'} km
                    </div>
                  </div>
                </div>
              </div>

              {/* Weekly Volume */}
              <div className="section">
                <h3 style={{ textAlign: 'center', marginBottom: '24px' }}>Weekly Volume (Last 8 weeks)</h3>
                <div className="card-grid">
                  {fitnessData.weekly_volume.map((week, index) => (
                    <div key={index} className="card" style={{ textAlign: 'left' }}>
                      <h3 style={{ color: '#ff6b35', marginBottom: '15px' }}>
                        Week of {week.week_start}
                      </h3>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div>
                          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'white' }}>{week.runs}</div>
                          <div style={{ fontSize: '12px', color: '#888' }}>Runs</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'white' }}>{week.distance_km.toFixed(1)}</div>
                          <div style={{ fontSize: '12px', color: '#888' }}>km</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'white' }}>{Math.round(week.time_minutes / 60)}</div>
                          <div style={{ fontSize: '12px', color: '#888' }}>hours</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'white' }}>{week.time_minutes.toFixed(0)}</div>
                          <div style={{ fontSize: '12px', color: '#888' }}>minutes</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Monthly Volume */}
              <div className="section">
                <h3 style={{ textAlign: 'center', marginBottom: '24px' }}>Monthly Volume (Last 6 months)</h3>
                <div className="card-grid">
                  {fitnessData.monthly_volume.map((month, index) => (
                    <div key={index} className="card" style={{ textAlign: 'left' }}>
                      <h3 style={{ color: '#ff6b35', marginBottom: '15px' }}>
                        {month.month}
                      </h3>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <div>
                          <div style={{ fontSize: '1.8rem', fontWeight: '700', color: 'white' }}>{month.runs}</div>
                          <div style={{ fontSize: '12px', color: '#888' }}>Runs</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '1.8rem', fontWeight: '700', color: 'white' }}>{month.distance_km.toFixed(1)}</div>
                          <div style={{ fontSize: '12px', color: '#888' }}>km</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '1.8rem', fontWeight: '700', color: 'white' }}>{Math.round(month.time_minutes / 60)}</div>
                          <div style={{ fontSize: '12px', color: '#888' }}>hours</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '1.8rem', fontWeight: '700', color: 'white' }}>{month.time_minutes.toFixed(0)}</div>
                          <div style={{ fontSize: '12px', color: '#888' }}>minutes</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              </>
            )}

            {/* Calendar Tab Content */}
            {currentView === 'calendar' && fitnessData && (
              <div className="section">
                <h3 style={{ textAlign: 'center', marginBottom: '24px' }}>AI Training Calendar</h3>
                {fitnessData.calendar && !fitnessData.calendar.error ? (
                  <div>
                    <div style={{ textAlign: 'center', marginBottom: '20px', color: '#888' }}>
                      Week of {fitnessData.calendar.week_of}
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                      {fitnessData.calendar.days.map((day, index) => (
                        <div key={index} className="card" style={{ textAlign: 'left' }}>
                          <h3 style={{ color: '#ff6b35', marginBottom: '10px' }}>
                            {day.day}
                          </h3>
                          <div style={{ fontSize: '12px', color: '#888', marginBottom: '10px' }}>
                            {day.date}
                          </div>
                          <div style={{ fontSize: '1.1rem', fontWeight: '600', color: 'white', marginBottom: '10px' }}>
                            {day.workout}
                          </div>
                          <div style={{ fontSize: '14px', color: '#888', fontStyle: 'italic' }}>
                            {day.reason}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', color: '#888' }}>
                    {fitnessData.calendar?.error ? (
                      <div>
                        <p>{fitnessData.calendar.error}</p>
                        <p style={{ fontSize: '14px' }}>{fitnessData.calendar.message}</p>
                      </div>
                    ) : (
                      <p>No calendar data available</p>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Loading State */}
            {fitnessLoading && (
              <div className="section" style={{ textAlign: 'center', width: '100%', maxWidth: '100%' }}>
                <div style={{ fontSize: '1.5rem', color: '#ff6b35', marginBottom: '10px' }}>⏳</div>
                <p style={{ color: '#888' }}>Loading your training data...</p>
          </div>
            )}
          </>
        ) : (
          /* Logged out state */
          <div className="section" style={{ textAlign: 'center' }}>
            <h2 style={{ margin: '0 0 20px 0', fontSize: '1.8rem', color: 'white' }}>
              Ready to start your journey?
            </h2>
            <p style={{ margin: '0 0 30px 0', fontSize: '1rem', color: '#888' }}>
              Connect your Strava account to get personalized training insights
            </p>
            <button onClick={initiateStravaAuth}>Connect with Strava</button>
          </div>
        )}
      </div>
    </div>
  )
}

export default App