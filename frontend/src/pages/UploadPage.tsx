import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

import { PredictionForm } from '../features/predictions/PredictionForm'
import { ResultPanel } from '../features/predictions/ResultPanel'
import { api } from '../lib/http'
import type { ModelVersion } from '../types/api'

export function UploadPage() {
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
      <section className="model-status-panel" aria-label="Modelos disponíveis">
        <aside className="model-box" aria-label="Status do modelo do projeto">
          <p className="model-label">Nosso modelo</p>
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
        <aside className="model-box model-box-global" aria-label="Status do identificador OpenAI">
          <p className="model-label">OpenAI</p>
          <span className="status-badge status-active">Disponível</span>
          <strong>CLIP global</strong>
          <p className="model-helper">Identificador amplo para comparação com o modelo do projeto.</p>
        </aside>
      </section>

      <div className="two-column-grid">
        <PredictionForm />
        <ResultPanel />
      </div>
    </div>
  )
}
