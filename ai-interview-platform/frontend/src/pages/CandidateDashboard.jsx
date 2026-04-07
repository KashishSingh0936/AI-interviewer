import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { interviewAPI, domainAPI } from '../services/api'
import { useAuthStore } from '../context/AuthContext'
import { Calendar, Play, Eye, LogOut } from 'lucide-react'

export default function CandidateDashboard() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)
  const [interviews, setInterviews] = useState([])
  const [domains, setDomains] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    domain_id: '',
    role_id: '',
    difficulty: 'intermediate',
  })
  const [roles, setRoles] = useState([])

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [interviewsRes, domainsRes] = await Promise.all([
        interviewAPI.getInterviews(),
        domainAPI.getDomains(),
      ])
      setInterviews(interviewsRes.data)
      setDomains(domainsRes.data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDomainChange = async (e) => {
    const domainId = e.target.value
    setFormData({ ...formData, domain_id: domainId, role_id: '' })
    
    if (domainId) {
      const domain = domains.find((d) => d.id === parseInt(domainId))
      setRoles(domain?.roles || [])
    }
  }

  const handleCreateInterview = async (e) => {
    e.preventDefault()
    try {
      const response = await interviewAPI.createInterview({
        ...formData,
        domain_id: parseInt(formData.domain_id),
        role_id: parseInt(formData.role_id),
        interview_type: 'mock',
      })
      setInterviews([...interviews, response.data])
      setShowCreateForm(false)
      setFormData({ domain_id: '', role_id: '', difficulty: 'intermediate' })
    } catch (error) {
      console.error('Failed to create interview:', error)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Candidate Dashboard</h1>
            <p className="text-gray-600">Welcome, {user?.full_name}</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Create Interview Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 font-medium"
          >
            + Create Mock Interview
          </button>

          {showCreateForm && (
            <form onSubmit={handleCreateInterview} className="mt-6 p-6 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Domain</label>
                  <select
                    value={formData.domain_id}
                    onChange={handleDomainChange}
                    required
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="">Select Domain</option>
                    {domains.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Role</label>
                  <select
                    value={formData.role_id}
                    onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
                    required
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="">Select Role</option>
                    {roles.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Difficulty</label>
                  <select
                    value={formData.difficulty}
                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
              </div>

              <div className="mt-4 flex gap-2">
                <button
                  type="submit"
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 font-medium"
                >
                  Create Interview
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-gray-400 text-white px-6 py-2 rounded-lg hover:bg-gray-500 font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Interviews List */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Your Interviews ({interviews.length})
          </h2>

          {interviews.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
              No interviews yet. Create a mock interview to get started!
            </div>
          ) : (
            <div className="grid gap-6">
              {interviews.map((interview) => (
                <div
                  key={interview.id}
                  className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                          {interview.interview_type.toUpperCase()}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          interview.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : interview.status === 'in_progress'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {interview.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-gray-900">
                        {interview.domain.name} - {interview.role.name}
                      </h3>
                      <p className="text-gray-600 text-sm">
                        Difficulty: <span className="font-medium">{interview.difficulty}</span>
                      </p>
                    </div>
                    {interview.status === 'completed' && (
                      <div className="text-right">
                        <p className="text-3xl font-bold text-green-600">
                          {interview.overall_score}/10
                        </p>
                        <p className="text-gray-600 text-sm">{interview.accuracy_percentage}% Accuracy</p>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-3">
                    {interview.status === 'scheduled' && (
                      <button
                        onClick={() => navigate(`/candidate/interview/${interview.id}`)}
                        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium"
                      >
                        <Play size={18} />
                        Start Interview
                      </button>
                    )}
                    {interview.status === 'completed' && (
                      <button
                        onClick={() => navigate(`/candidate/interview/${interview.id}`)}
                        className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 font-medium"
                      >
                        <Eye size={18} />
                        View Results
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
