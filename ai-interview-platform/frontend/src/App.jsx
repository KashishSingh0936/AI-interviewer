import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './context/AuthContext'

// Pages
import Login from './pages/Login'
import Register from './pages/Register'
import CandidateDashboard from './pages/CandidateDashboard'
import InterviewPage from './pages/InterviewPage'

// Protected Route Component
function ProtectedRoute({ children, requiredRole }) {
  const user = useAuthStore((state) => state.user)
  const token = useAuthStore((state) => state.token)

  if (!token || !user) {
    return <Navigate to="/login" />
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to={user.role === 'candidate' ? '/candidate/dashboard' : '/interviewer/dashboard'} />
  }

  return children
}

function App() {
  const user = useAuthStore((state) => state.user)
  const token = useAuthStore((state) => state.token)

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={token ? <Navigate to={user?.role === 'candidate' ? '/candidate/dashboard' : '/interviewer/dashboard'} /> : <Login />} />
        <Route path="/register" element={token ? <Navigate to={user?.role === 'candidate' ? '/candidate/dashboard' : '/interviewer/dashboard'} /> : <Register />} />

        {/* Candidate Routes */}
        <Route
          path="/candidate/dashboard"
          element={
            <ProtectedRoute requiredRole="candidate">
              <CandidateDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/candidate/interview/:interview_id"
          element={
            <ProtectedRoute requiredRole="candidate">
              <InterviewPage />
            </ProtectedRoute>
          }
        />

        {/* Interviewer Routes */}
        <Route
          path="/interviewer/dashboard"
          element={
            <ProtectedRoute requiredRole="interviewer">
              <div className="flex items-center justify-center h-screen text-2xl">
                Interviewer Dashboard (Coming Soon)
              </div>
            </ProtectedRoute>
          }
        />

        {/* Redirect root to appropriate dashboard */}
        <Route
          path="/"
          element={
            token ? (
              <Navigate to={user?.role === 'candidate' ? '/candidate/dashboard' : '/interviewer/dashboard'} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        
        {/* 404 */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  )
}

export default App
