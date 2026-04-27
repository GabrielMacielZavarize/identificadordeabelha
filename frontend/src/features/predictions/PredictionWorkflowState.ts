import { createContext, useContext } from 'react'

import type { GlobalIdentificationResponse, PredictionResponse } from '../../types/api'

export type ClassificationModelId = 'specific' | 'openai'

export const CLASSIFICATION_MODEL_OPTIONS: Array<{
  id: ClassificationModelId
  label: string
}> = [
  { id: 'specific', label: 'Nosso modelo' },
  { id: 'openai', label: 'OpenAI CLIP' },
]

export type PredictionWorkflowContextValue = {
  prediction: PredictionResponse | null
  globalIdentification: GlobalIdentificationResponse | null
  isPending: boolean
  pendingModel: ClassificationModelId | null
  errorMessage: string | null
  runAnalysis: (file: File, modelId: ClassificationModelId) => Promise<void>
}

export const PredictionWorkflowContext =
  createContext<PredictionWorkflowContextValue | null>(null)

export function usePredictionWorkflow() {
  const context = useContext(PredictionWorkflowContext)
  if (!context) {
    throw new Error('usePredictionWorkflow must be used within PredictionWorkflowProvider.')
  }
  return context
}
