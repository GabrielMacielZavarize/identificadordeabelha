import { QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'

import { router } from './app/router'
import { PredictionWorkflowProvider } from './features/predictions/PredictionWorkflowContext'
import { queryClient } from './lib/queryClient'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <PredictionWorkflowProvider>
        <RouterProvider router={router} />
      </PredictionWorkflowProvider>
    </QueryClientProvider>
  )
}

export default App
