import { createBrowserRouter } from 'react-router-dom'

import { AppLayout } from './AppLayout'
import { ProtectedRoute } from '../features/auth/ProtectedRoute'
import { HistoryPage } from '../pages/HistoryPage'
import { LandingPage } from '../pages/LandingPage'
import { LoginPage } from '../pages/LoginPage'
import { RegisterPage } from '../pages/RegisterPage'
import { SpeciesPage } from '../pages/SpeciesPage'
import { UploadPage } from '../pages/UploadPage'

export const router = createBrowserRouter([
  { path: '/', element: <LandingPage /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: '/app',
        element: <AppLayout />,
        children: [
          { index: true, element: <UploadPage /> },
          { path: 'history', element: <HistoryPage /> },
          { path: 'species', element: <SpeciesPage /> },
        ],
      },
    ],
  },
])
