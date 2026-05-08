import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

import { PredictionForm } from '../features/predictions/PredictionForm'
import { ResultPanel } from '../features/predictions/ResultPanel'
import { formatProjectModelLabel } from '../features/predictions/PredictionWorkflowState'
import { api } from '../lib/http'
import type { ModelVersion } from '../types/api'

function modelBadge(model: ModelVersion): { label: string; className: string } {
  const status = model.display_name?.match(/\(([^)]+)\)/)?.[1]
  if (status) {
    const className =
      status === 'Depreciado' ? 'status-inactive' :
      status === 'Novo' ? 'status-new' :
      'status-active'
    return { label: status, className }
  }
  return {
    label: model.is_active ? 'Ativo' : 'Comparação',
    className: model.is_active ? 'status-active' : 'status-inactive',
  }
}

export function UploadPage() {
  const modelsQuery = useQuery({
    queryKey: ['models'],
    queryFn: async () => {
      const response = await api.get<ModelVersion[]>('/models')
      return response.data
    },
  })

  const modelVersions = modelsQuery.data ?? []
  const modelMessage = axios.isAxiosError(modelsQuery.error)
    ? (modelsQuery.error.response?.data as { detail?: string } | undefined)?.detail ??
      'Modelo indisponível.'
    : null

  return (
    <div className="stack-lg">
      <section className="model-status-panel" aria-label="Modelos disponíveis">
        {modelVersions.length > 0 ? (
          modelVersions.map((model) => (
            <aside className="model-box" aria-label={`Status de ${model.version}`} key={model.id}>
              <p className="model-label">Modelo DINO</p>
              <span className={`status-badge ${modelBadge(model).className}`}>
                {modelBadge(model).label}
              </span>
              <strong>{formatProjectModelLabel(model)}</strong>
              <p className="model-helper">{model.encoder_name}</p>
            </aside>
          ))
        ) : (
          <aside className="model-box" aria-label="Status dos modelos DINO">
            <p className="model-label">Modelo DINO</p>
            <span className="status-badge status-inactive">Pendente</span>
            <strong>{modelsQuery.isLoading ? 'Carregando modelos' : 'Sem modelo DINO registrado'}</strong>
            <p className="model-helper">
              {modelMessage ?? 'Registre um artefato treinado para habilitar a inferência DINO.'}
            </p>
          </aside>
        )}
        <aside className="model-box model-box-global" aria-label="Status do identificador OpenAI">
          <p className="model-label">OpenAI</p>
          <span className="status-badge status-active">Disponível</span>
          <strong>OpenAI CLIP global</strong>
          <p className="model-helper">Identificador amplo para comparar com os modelos DINO treinados.</p>
        </aside>
      </section>

      <div className="two-column-grid">
        <PredictionForm modelVersions={modelVersions} isLoadingModels={modelsQuery.isLoading} />
        <ResultPanel modelVersions={modelVersions} />
      </div>
    </div>
  )
}
