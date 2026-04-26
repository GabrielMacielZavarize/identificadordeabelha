import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import axios from 'axios'

import { api } from '../../lib/http'
import type { PredictionResponse } from '../../types/api'

type UploadFormValues = {
  file: FileList
}

type PredictionFormProps = {
  onSuccess: (prediction: PredictionResponse) => void
}

export function PredictionForm({ onSuccess }: PredictionFormProps) {
  const [selectedName, setSelectedName] = useState<string>('Nenhum arquivo selecionado')
  const { handleSubmit, register, reset } = useForm<UploadFormValues>()

  const mutation = useMutation({
    mutationFn: async (file: File) => {
      const payload = new FormData()
      payload.append('file', file)
      const response = await api.post<PredictionResponse>('/predictions', payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: (data) => {
      onSuccess(data)
      reset()
      setSelectedName('Nenhum arquivo selecionado')
    },
  })

  const submitForm = handleSubmit((values) => {
    const file = values.file?.[0]
    if (!file) {
      return
    }
    mutation.mutate(file)
  })

  const errorMessage = axios.isAxiosError(mutation.error)
    ? (mutation.error.response?.data as { detail?: string } | undefined)?.detail ??
      mutation.error.message
    : mutation.error instanceof Error
      ? mutation.error.message
      : null

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Nova classificação</h2>
        <p>Envie uma imagem JPG ou PNG para inferência do modelo ativo.</p>
      </div>

      <form className="stack-md" onSubmit={submitForm}>
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
          <button className="primary-button" type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Classificando...' : 'Executar classificação'}
          </button>
        </div>

        {errorMessage ? <p className="feedback error">{errorMessage}</p> : null}
      </form>
    </section>
  )
}
