import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { interviewAPI } from '../services/api'
import { Mic, Send, CheckCircle } from 'lucide-react'

export default function InterviewPage() {
  const { interview_id } = useParams()
  const navigate = useNavigate()
  const [interview, setInterview] = useState(null)
  const [questions, setQuestions] = useState([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [feedback, setFeedback] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const mediaRecorderRef = useState(null)[1]

  useEffect(() => {
    fetchInterview()
  }, [interview_id])

  const fetchInterview = async () => {
    try {
      const response = await interviewAPI.getInterview(interview_id)
      const interviewData = response.data
      setInterview(interviewData)
      setQuestions(interviewData.questions || [])
      
      if (interviewData.status === 'scheduled') {
        await startInterview()
      }
    } catch (error) {
      console.error('Failed to fetch interview:', error)
    } finally {
      setLoading(false)
    }
  }

  const startInterview = async () => {
    try {
      await interviewAPI.startInterview(interview_id)
      const nextQRes = await interviewAPI.getNextQuestion(interview_id)
      console.log('Next question:', nextQRes.data)
    } catch (error) {
      console.error('Failed to start interview:', error)
    }
  }

  const handleSubmitAnswer = async (e) => {
    e.preventDefault()
    if (!answer.trim()) return

    setSubmitting(true)
    try {
      const response = await interviewAPI.submitAnswer(interview_id, {
        question_number: currentQuestionIndex + 1,
        answer_text: answer,
      })
      
      setFeedback(response.data)
      setAnswer('')
      
      // Check if more questions available
      setTimeout(() => {
        if (currentQuestionIndex < 2) {
          setCurrentQuestionIndex(currentQuestionIndex + 1)
          setFeedback(null)
          getNextQuestion()
        } else {
          // Interview complete
          completeInterview()
        }
      }, 3000)
    } catch (error) {
      console.error('Failed to submit answer:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const getNextQuestion = async () => {
    try {
      const response = await interviewAPI.getNextQuestion(interview_id)
      console.log('Next question received:', response.data)
    } catch (error) {
      if (error.response?.status === 400) {
        completeInterview()
      }
    }
  }

  const completeInterview = async () => {
    try {
      const response = await interviewAPI.completeInterview(interview_id)
      navigate(`/candidate/interview-results/${interview_id}`)
    } catch (error) {
      console.error('Failed to complete interview:', error)
    }
  }

  const toggleRecording = async () => {
    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        const mediaRecorder = new MediaRecorder(stream)
        const audioChunks = []

        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data)
        }

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
          const reader = new FileReader()
          reader.onloadend = () => {
            // Could save audio file path here
            console.log('Audio recorded:', audioBlob)
          }
          reader.readAsDataURL(audioBlob)
        }

        mediaRecorder.start()
        mediaRecorderRef.current = mediaRecorder
        setIsRecording(true)
      } catch (error) {
        console.error('Failed to access microphone:', error)
      }
    } else {
      mediaRecorderRef.current?.stop()
      setIsRecording(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading interview...</div>
  }

  if (!interview) {
    return <div className="flex items-center justify-center h-screen">Interview not found</div>
  }

  const currentQuestion = questions[currentQuestionIndex] || { question_text: 'Loading...' }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {interview.domain.name} - {interview.role.name}
            </h1>
            <p className="text-gray-600">
              Question {currentQuestionIndex + 1} of 3
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Difficulty: {interview.difficulty}</p>
            <p className="text-sm text-gray-600">Type: {interview.interview_type.toUpperCase()}</p>
          </div>
        </div>
      </div>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Question */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              {currentQuestion.question_text}
            </h2>
          </div>

          {/* Feedback Display */}
          {feedback && (
            <div className="mb-8 p-6 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-start gap-3">
                <CheckCircle className="text-green-600 mt-1" size={24} />
                <div>
                  <p className="font-bold text-gray-900">Feedback Received</p>
                  <p className="text-gray-700 mt-2">{feedback.ai_feedback}</p>
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Score</p>
                      <p className="text-2xl font-bold text-green-600">{feedback.score}/10</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Status</p>
                      <p className="text-lg font-bold text-gray-900">
                        {feedback.is_correct ? '✓ Correct' : '✗ Incorrect'}
                      </p>
                    </div>
                  </div>
                  {feedback.weak_area && (
                    <p className="text-sm text-yellow-700 mt-3">
                      ⚠️ Weak Area: {feedback.weak_area}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Answer Form */}
          {!feedback && (
            <form onSubmit={handleSubmitAnswer} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Your Answer
                </label>
                <textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer here..."
                  rows={6}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={toggleRecording}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium ${
                    isRecording
                      ? 'bg-red-600 text-white hover:bg-red-700'
                      : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                  }`}
                >
                  <Mic size={18} />
                  {isRecording ? 'Stop Recording' : 'Record Audio'}
                </button>

                <button
                  type="submit"
                  disabled={!answer.trim() || submitting}
                  className="flex items-center gap-2 ml-auto bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-medium transition"
                >
                  <Send size={18} />
                  {submitting ? 'Submitting...' : 'Submit Answer'}
                </button>
              </div>
            </form>
          )}

          {feedback && currentQuestionIndex < 2 && (
            <div className="text-center text-gray-600 italic">
              Moving to next question in 3 seconds...
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
