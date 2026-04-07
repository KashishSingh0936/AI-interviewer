import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,

      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),
      setLoading: (loading) => set({ loading }),

      login: (user, token) => {
        set({
          user,
          token,
          isAuthenticated: true,
        })
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      isCandidate: () => get().user?.role === 'candidate',
      isInterviewer: () => get().user?.role === 'interviewer',
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

export const useInterviewStore = create((set, get) => ({
  currentInterview: null,
  interviews: [],
  currentQuestionIndex: 0,
  answers: [],

  setCurrentInterview: (interview) => set({ currentInterview: interview }),
  setInterviews: (interviews) => set({ interviews }),
  setCurrentQuestionIndex: (index) => set({ currentQuestionIndex: index }),
  addAnswer: (answer) => {
    const answers = [...get().answers, answer]
    set({ answers })
  },
  resetAnswers: () => set({ answers: [] }),
}))

export const useDomainStore = create((set) => ({
  domains: [],
  selectedDomain: null,
  selectedRole: null,

  setDomains: (domains) => set({ domains }),
  setSelectedDomain: (domain) => set({ selectedDomain: domain }),
  setSelectedRole: (role) => set({ selectedRole: role }),
}))
