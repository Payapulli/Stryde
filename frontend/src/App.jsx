import { useState, useEffect } from 'react'
import './App.css'

// Get API URL from environment variable or default to backend
const API_URL = import.meta.env.VITE_API_URL || 'https://backend-joshua-payapullis-projects.vercel.app'
console.log('API_URL:', API_URL, 'VITE_API_URL:', import.meta.env.VITE_API_URL)

function App() {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState(null)
  const [authState, setAuthState] = useState(null)

  const fetchPing = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/ping`)
      const data = await response.json()
      setMessage(data.message)
    } catch (error) {
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
      // Redirect to Strava OAuth
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

  useEffect(() => {
    fetchPing()
    
    // Check if we're returning from OAuth callback
    const urlParams = new URLSearchParams(window.location.search)
    const authSuccess = urlParams.get('auth_success')
    const state = urlParams.get('state')
    
    if (authSuccess === 'true' && state) {
      setAuthState(state)
      fetchUserProfile(state)
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [])

  return (
    <div className="App">
      <h1>Stryde</h1>
      
      <div className="card">
        <button onClick={fetchPing} disabled={loading}>
          {loading ? 'Loading...' : 'Ping Backend'}
        </button>
        <p>Backend response: <strong>{message}</strong></p>
      </div>

      <div className="card">
        {user ? (
          <div>
            <h2>Welcome, {user.firstname}!</h2>
            <p>Username: <strong>{user.username}</strong></p>
            <p>Name: {user.firstname} {user.lastname}</p>
            {user.profile_medium && (
              <img 
                src={user.profile_medium} 
                alt="Profile" 
                style={{ width: 50, height: 50, borderRadius: '50%' }}
              />
            )}
          </div>
        ) : (
          <div>
            <button onClick={initiateStravaAuth}>
              Connect with Strava
            </button>
            <p>Connect your Strava account to get started</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
