import { QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'

import { router } from './app/router'
import { AuthProvider } from './features/auth/AuthContext'
import { PredictionWorkflowProvider } from './features/predictions/PredictionWorkflowContext'
import { queryClient } from './lib/queryClient'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <PredictionWorkflowProvider>
          <RouterProvider router={router} />
        </PredictionWorkflowProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
