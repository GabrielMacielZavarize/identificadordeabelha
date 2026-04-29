import { createBrowserRouter } from 'react-router-dom'

import { AppLayout } from './AppLayout'
import { HistoryPage } from '../pages/HistoryPage'
import { LandingPage } from '../pages/LandingPage'
import { SpeciesPage } from '../pages/SpeciesPage'
import { UploadPage } from '../pages/UploadPage'

export const router = createBrowserRouter([
  { path: '/', element: <LandingPage /> },
  {
    path: '/app',
    element: <AppLayout />,
    children: [
      { index: true, element: <UploadPage /> },
      { path: 'history', element: <HistoryPage /> },
      { path: 'species', element: <SpeciesPage /> },
    ],
  },
])
