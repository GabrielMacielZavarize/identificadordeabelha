import { useCallback, useMemo, useState, type ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import axios from 'axios'

import { api } from '../../lib/http'
import type { GlobalIdentificationResponse, PredictionResponse } from '../../types/api'
import {
  getProjectModelVersion,
  isProjectModelId,
  PredictionWorkflowContext,
  type ClassificationModelId,
} from './PredictionWorkflowState'

const PROJECT_PREDICTIONS_STORAGE_KEY = 'augochloropsis.projectPredictions'
const LATEST_PROJECT_VERSION_STORAGE_KEY = 'augochloropsis.latestProjectVersion'
const GLOBAL_IDENTIFICATION_STORAGE_KEY = 'augochloropsis.latestGlobalIdentification'

function readStoredResult<T>(key: string): T | null {
  try {
    const storedValue = window.sessionStorage.getItem(key)
    return storedValue ? (JSON.parse(storedValue) as T) : null
  } catch {
    return null
  }
}

function storeResult(key: string, value: unknown) {
  try {
    window.sessionStorage.setItem(key, JSON.stringify(value))
  } catch {
    return
  }
}

function resolveErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const httpStatus = error.response?.status
    const detail = (error.response?.data as { detail?: string } | undefined)?.detail

    if (!error.response) {
      return 'Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.'
    }
    if (httpStatus === 503) {
      return 'O modelo ainda não está pronto. Tente novamente em alguns instantes.'
    }
    if (httpStatus === 400 || httpStatus === 422) {
      return 'A imagem não foi aceita. Verifique se é um arquivo JPG ou PNG válido e tente novamente.'
    }
    return detail ?? 'Não conseguimos identificar a abelha. Tente uma foto mais nítida com fundo neutro.'
  }

  return error instanceof Error
    ? error.message
    : 'Não conseguimos identificar a abelha. Tente uma foto mais nítida com fundo neutro.'
}

export function PredictionWorkflowProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [projectPredictions, setProjectPredictions] = useState<Record<string, PredictionResponse>>(
    () => readStoredResult<Record<string, PredictionResponse>>(PROJECT_PREDICTIONS_STORAGE_KEY) ?? {},
  )
  const [latestProjectVersion, setLatestProjectVersion] = useState<string | null>(() =>
    readStoredResult<string>(LATEST_PROJECT_VERSION_STORAGE_KEY),
  )
  const [globalIdentification, setGlobalIdentification] =
    useState<GlobalIdentificationResponse | null>(() =>
      readStoredResult<GlobalIdentificationResponse>(GLOBAL_IDENTIFICATION_STORAGE_KEY),
    )
  const [isPending, setIsPending] = useState(false)
  const [pendingModel, setPendingModel] = useState<ClassificationModelId | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const runAnalysis = useCallback(async (file: File, modelId: ClassificationModelId) => {
    const payload = new FormData()
    payload.append('file', file)

    setIsPending(true)
    setPendingModel(modelId)
    setErrorMessage(null)

    try {
      if (isProjectModelId(modelId)) {
        const selectedVersion = getProjectModelVersion(modelId)
        const response = await api.post<PredictionResponse>('/predictions', payload, {
          params: { model_version: selectedVersion },
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        const responseVersion = response.data.model_version.version
        setProjectPredictions((current) => {
          const next = { ...current, [responseVersion]: response.data }
          storeResult(PROJECT_PREDICTIONS_STORAGE_KEY, next)
          return next
        })
        setLatestProjectVersion(responseVersion)
        storeResult(LATEST_PROJECT_VERSION_STORAGE_KEY, responseVersion)
      } else {
        const response = await api.post<GlobalIdentificationResponse>(
          '/global-identifications',
          payload,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
          },
        )
        setGlobalIdentification(response.data)
        storeResult(GLOBAL_IDENTIFICATION_STORAGE_KEY, response.data)
      }

      await queryClient.invalidateQueries({ queryKey: ['identification-history'] })
    } catch (error) {
      setErrorMessage(resolveErrorMessage(error))
    } finally {
      setIsPending(false)
      setPendingModel(null)
    }
  }, [queryClient])

  const value = useMemo(
    () => {
      const prediction = latestProjectVersion
        ? projectPredictions[latestProjectVersion] ?? null
        : Object.values(projectPredictions)[0] ?? null

      return {
        prediction,
        projectPredictions,
        latestProjectVersion,
        globalIdentification,
        isPending,
        pendingModel,
        errorMessage,
        runAnalysis,
      }
    },
    [
      errorMessage,
      globalIdentification,
      isPending,
      latestProjectVersion,
      pendingModel,
      projectPredictions,
      runAnalysis,
    ],
  )

  return (
    <PredictionWorkflowContext.Provider value={value}>
      {children}
    </PredictionWorkflowContext.Provider>
  )
}
