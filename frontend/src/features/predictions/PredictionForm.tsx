import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import axios from 'axios'

import { api } from '../../lib/http'
import type { GlobalIdentificationResponse, PredictionResponse } from '../../types/api'

type UploadFormValues = {
  file: FileList
}

type PredictionFormProps = {
  onGlobalSuccess: (identification: GlobalIdentificationResponse) => void
  onSpecificSuccess: (prediction: PredictionResponse) => void
}

export function PredictionForm({ onGlobalSuccess, onSpecificSuccess }: PredictionFormProps) {
  const [selectedName, setSelectedName] = useState<string>('Nenhum arquivo selecionado')
  const { handleSubmit, register } = useForm<UploadFormValues>()

  const specificMutation = useMutation({
    mutationFn: async (file: File) => {
      const payload = new FormData()
      payload.append('file', file)
      const response = await api.post<PredictionResponse>('/predictions', payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: (data) => {
      onSpecificSuccess(data)
    },
  })

  const globalMutation = useMutation({
    mutationFn: async (file: File) => {
      const payload = new FormData()
      payload.append('file', file)
      const response = await api.post<GlobalIdentificationResponse>('/global-identifications', payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: (data) => {
      onGlobalSuccess(data)
    },
  })

  const submitSpecific = handleSubmit((values) => {
    const file = values.file?.[0]
    if (!file) {
      return
    }
    specificMutation.mutate(file)
  })

  const submitGlobal = handleSubmit((values) => {
    const file = values.file?.[0]
    if (!file) {
      return
    }
    globalMutation.mutate(file)
  })

  const specificErrorMessage = axios.isAxiosError(specificMutation.error)
    ? (specificMutation.error.response?.data as { detail?: string } | undefined)?.detail ??
      specificMutation.error.message
    : specificMutation.error instanceof Error
      ? specificMutation.error.message
      : null

  const globalErrorMessage = axios.isAxiosError(globalMutation.error)
    ? (globalMutation.error.response?.data as { detail?: string } | undefined)?.detail ??
      globalMutation.error.message
    : globalMutation.error instanceof Error
      ? globalMutation.error.message
      : null

  const isPending = specificMutation.isPending || globalMutation.isPending

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Nova análise</h2>
        <p>Envie uma imagem JPG ou PNG e escolha qual modelo deve avaliar a foto.</p>
      </div>

      <form className="stack-md">
        <label className="file-input upload-dropzone" htmlFor="bee-image">
          <span className="field-label">Imagem da abelha</span>
          <span className="upload-title">Selecione uma foto para classificar</span>
          <strong>{selectedName}</strong>
          <input
            id="bee-image"
            type="file"
            accept=".jpg,.jpeg,.png,image/png,image/jpeg"
            {...register('file', {
              required: true,
              onChange: (event) => {
                const file = (event.target as HTMLInputElement).files?.[0]
                setSelectedName(file?.name ?? 'Nenhum arquivo selecionado')
              },
            })}
          />
        </label>

        <div className="form-footer">
          <button className="primary-button" type="button" disabled={isPending} onClick={submitSpecific}>
            {specificMutation.isPending ? 'Classificando...' : 'Executar classificação específica'}
          </button>
          <button className="secondary-button" type="button" disabled={isPending} onClick={submitGlobal}>
            {globalMutation.isPending ? 'Consultando...' : 'Usar identificador global'}
          </button>
        </div>

        {specificErrorMessage ? <p className="feedback error">{specificErrorMessage}</p> : null}
        {globalErrorMessage ? <p className="feedback error">{globalErrorMessage}</p> : null}
      </form>
    </section>
  )
}
