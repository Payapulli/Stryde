# Stryde

A React frontend with FastAPI backend featuring Strava OAuth integration.

## Architecture

- **Frontend**: React + Vite (port 5173 by default)
- **Backend**: FastAPI + Uvicorn (port 8000)
- **Authentication**: Strava OAuth 2.0
- **API**: Strava API v3

## Setup Instructions

### Strava App Setup (Required First)

1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Click "Create App" or "My API Application"
3. Fill in the required fields:
   - **Application Name**: Stryde (or your preferred name)
   - **Category**: Other
   - **Club**: Leave blank
   - **Website**: `http://localhost:5173`
   - **Authorization Callback Domain**: `localhost`
4. After creating, note down your **Client ID** and **Client Secret**

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   export STRAVA_CLIENT_ID="your_client_id_here"
   export STRAVA_CLIENT_SECRET="your_client_secret_here"
   ```
   
   Or create a `.env` file in the backend directory:
   ```
   STRAVA_CLIENT_ID=your_client_id_here
   STRAVA_CLIENT_SECRET=your_client_secret_here
   ```

5. Run the backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## Testing the Setup

1. **Set up Strava app** (see Strava App Setup above)
2. **Start the backend server** (see Backend Setup above)
3. **Start the frontend server** (see Frontend Setup above)
4. **Open** `http://localhost:5173` in your browser
5. **Click "Connect with Strava"** button
6. **Authorize** the app on Strava
7. **You should see** your Strava username and profile displayed!

## API Endpoints

- `GET /ping` - Returns `{"message": "pong"}`
- `GET /auth/strava` - Initiates Strava OAuth flow
- `GET /auth/callback` - Handles Strava OAuth callback
- `GET /user/profile?state={state}` - Returns authenticated user's profile

## OAuth Flow

1. User clicks "Connect with Strava"
2. Frontend calls `/auth/strava` to get authorization URL
3. User is redirected to Strava for authorization
4. Strava redirects back to `/auth/callback` with authorization code
5. Backend exchanges code for access token and fetches user data
6. User is redirected back to frontend with success state
7. Frontend fetches user profile and displays username

## Next Steps

- Add activity fetching and display
- Implement proper session management with JWT tokens
- Add user activity visualization
- Deploy to production with proper environment variables
