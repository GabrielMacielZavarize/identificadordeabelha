import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

import { PredictionForm } from '../features/predictions/PredictionForm'
import { PredictionResult } from '../features/predictions/PredictionResult'
import { api } from '../lib/http'
import type { ModelVersion, PredictionResponse } from '../types/api'

export function UploadPage() {
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null)

  const activeModelQuery = useQuery({
    queryKey: ['active-model'],
    queryFn: async () => {
      const response = await api.get<ModelVersion>('/models/active')
      return response.data
    },
  })

  const modelMessage = axios.isAxiosError(activeModelQuery.error)
    ? (activeModelQuery.error.response?.data as { detail?: string } | undefined)?.detail ??
      'Modelo indisponível.'
    : null

  return (
    <div className="stack-lg">
      <section className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">Identificação visual</p>
          <h2>Classifique imagens com mais organização</h2>
          <p>
            Envie uma foto, consulte a espécie prevista e confira a confiança do modelo em uma
            tela preparada para análise rápida.
          </p>
          <div className="hero-tags" aria-label="Recursos disponíveis">
            <span>JPG e PNG</span>
            <span>Histórico salvo</span>
            <span>Espécies editáveis</span>
          </div>
        </div>
        <aside className="model-box" aria-label="Status do modelo ativo">
          <p className="model-label">Status do modelo</p>
          {activeModelQuery.data ? (
            <>
              <span className="status-badge status-active">Ativo</span>
              <strong>{activeModelQuery.data.version}</strong>
              <p className="model-helper">{activeModelQuery.data.encoder_name}</p>
            </>
          ) : (
            <>
              <span className="status-badge status-inactive">Pendente</span>
              <strong>Sem modelo ativo</strong>
              <p className="model-helper">
                {modelMessage ?? 'Registre um artefato treinado para habilitar a inferência.'}
              </p>
            </>
          )}
        </aside>
      </section>

      <div className="two-column-grid">
        <PredictionForm onSuccess={setPrediction} />
        <PredictionResult prediction={prediction} />
      </div>
    </div>
  )
}
