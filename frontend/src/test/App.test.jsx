import { render, screen, waitFor, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import App from '../App'

// Mock fetch globally
global.fetch = vi.fn()

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock successful ping response by default
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'pong' })
    })
  })

  it('renders the main title', () => {
    render(<App />)
    expect(screen.getByText('Stryde')).toBeInTheDocument()
    expect(screen.getByText('Your Personal Running Coach')).toBeInTheDocument()
  })

  it('renders ping backend button after initial load', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Ping Backend')).toBeInTheDocument()
    })
  })

  it('renders connect with strava button when not logged in', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Connect with Strava')).toBeInTheDocument()
    })
  })

  it('shows loading state when fetching data', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Ping Backend')).toBeInTheDocument()
    })
    
    const button = screen.getByText('Ping Backend')
    
    // Mock slow response
    global.fetch.mockResolvedValueOnce(new Promise(resolve => 
      setTimeout(() => resolve({
        ok: true,
        json: async () => ({ message: 'pong' })
      }), 100)
    ))

    act(() => {
      button.click()
    })
    
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('displays backend response after ping', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Ping Backend')).toBeInTheDocument()
    })
    
    const button = screen.getByText('Ping Backend')
    
    // Mock successful response
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'pong' })
    })

    act(() => {
      button.click()
    })
    
    await waitFor(() => {
      expect(screen.getByText(/Backend response:/)).toBeInTheDocument()
      expect(screen.getByText('pong')).toBeInTheDocument()
    })
  })

  it('handles backend connection error', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Ping Backend')).toBeInTheDocument()
    })
    
    const button = screen.getByText('Ping Backend')
    
    // Mock error response
    global.fetch.mockRejectedValueOnce(new Error('Network error'))

    act(() => {
      button.click()
    })
    
    await waitFor(() => {
      expect(screen.getByText(/Backend response:/)).toBeInTheDocument()
      expect(screen.getByText('Error connecting to backend')).toBeInTheDocument()
    })
  })
})
