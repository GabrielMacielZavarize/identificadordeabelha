import { useState } from 'react'

import { api } from '../../lib/http'
import type { GlobalIdentificationResponse, ModelVersion, PredictionResponse } from '../../types/api'
import {
  createProjectModelId,
  formatProjectModelLabel,
  isProjectModelId,
  OPENAI_MODEL_ID,
  usePredictionWorkflow,
  type ClassificationModelId,
  type ProjectModelId,
} from './PredictionWorkflowState'

type ProjectResultTab = {
  id: ProjectModelId
  label: string
  prediction: PredictionResponse | null
}

function confidenceClass(value: number): string {
  if (value >= 0.8) return 'confidence-high'
  if (value >= 0.5) return 'confidence-mid'
  return 'confidence-low'
}

function FeedbackRow({
  feedback,
  isSending,
  onFeedback,
}: {
  feedback: boolean | null
  isSending: boolean
  onFeedback: (value: boolean) => void
}) {
  return (
    <div className="feedback-row">
      <span className="feedback-label">Isso está correto?</span>
      <button
        type="button"
        className={`feedback-btn feedback-btn-correct${feedback === true ? ' feedback-active' : ''}`}
        disabled={isSending}
        onClick={() => onFeedback(true)}
      >
        ✓ Correto
      </button>
      <button
        type="button"
        className={`feedback-btn feedback-btn-wrong${feedback === false ? ' feedback-active' : ''}`}
        disabled={isSending}
        onClick={() => onFeedback(false)}
      >
        ✗ Incorreto
      </button>
    </div>
  )
}

function SpecificContent({
  prediction,
  modelLabel,
}: {
  prediction: PredictionResponse
  modelLabel: string
}) {
  const [feedback, setFeedback] = useState<boolean | null>(prediction.user_feedback ?? null)
  const [isSending, setIsSending] = useState(false)

  const sendFeedback = async (value: boolean) => {
    if (isSending) return
    setIsSending(true)
    try {
      await api.patch(`/predictions/${prediction.prediction_id}/feedback`, { user_feedback: value })
      setFeedback(value)
    } catch {
      // best-effort
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="stack-md panel-fade-in">
      <div className="result-highlight">
        <p className="eyebrow">Espécie prevista</p>
        <h3>{prediction.predicted_species.scientific_name}</h3>
        <p>{prediction.predicted_species.code}</p>
        <p className={`confidence ${confidenceClass(prediction.confidence)}`}>
          Confiança: <strong>{(prediction.confidence * 100).toFixed(2)}%</strong>
        </p>
        <div className="confidence-meter" aria-hidden="true">
          <span style={{ width: `${Math.max(prediction.confidence * 100, 2)}%` }} />
        </div>
      </div>

      <img
        className="prediction-image"
        src={prediction.image_url}
        alt={`Imagem processada para ${prediction.predicted_species.scientific_name}`}
      />

      <FeedbackRow feedback={feedback} isSending={isSending} onFeedback={sendFeedback} />

      <details className="details-technical">
        <summary>Detalhes técnicos</summary>
        <dl className="metadata-grid">
          <div>
            <dt>Modelo</dt>
            <dd>{modelLabel}</dd>
          </div>
          <div>
            <dt>Versão</dt>
            <dd>{prediction.model_version.version}</dd>
          </div>
          <div>
            <dt>Encoder</dt>
            <dd>{prediction.model_version.encoder_name}</dd>
          </div>
          <div>
            <dt>Inferência</dt>
            <dd>{prediction.inference_ms.toFixed(1)} ms</dd>
          </div>
          <div>
            <dt>Executado em</dt>
            <dd>{new Date(prediction.created_at).toLocaleString('pt-BR')}</dd>
          </div>
        </dl>
      </details>

      <div>
        <h4>Probabilidades por classe</h4>
        <div className="probability-list">
          {prediction.probabilities.map((item) => (
            <div className="probability-item" key={item.species_code}>
              <div>
                <strong>{item.scientific_name ?? item.species_code}</strong>
                <span>{item.species_code}</span>
              </div>
              <div className="probability-bar">
                <div
                  className="probability-fill"
                  style={{ width: `${Math.max(item.probability * 100, 2)}%` }}
                />
              </div>
              <span>{(item.probability * 100).toFixed(2)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function GlobalContent({ identification }: { identification: GlobalIdentificationResponse }) {
  const [feedback, setFeedback] = useState<boolean | null>(identification.user_feedback ?? null)
  const [isSending, setIsSending] = useState(false)

  const sendFeedback = async (value: boolean) => {
    if (isSending) return
    setIsSending(true)
    try {
      await api.patch(
        `/global-identifications/${identification.global_identification_id}/feedback`,
        { user_feedback: value },
      )
      setFeedback(value)
    } catch {
      // best-effort
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="stack-md panel-fade-in">
      <div className="result-highlight result-highlight-global">
        <p className="eyebrow">Melhor sugestão global</p>
        <h3>{identification.predicted_scientific_name}</h3>
        <p>{identification.predicted_common_name}</p>
        <p className={`confidence ${confidenceClass(identification.confidence)}`}>
          Confiança: <strong>{(identification.confidence * 100).toFixed(2)}%</strong>
        </p>
        <div className="confidence-meter" aria-hidden="true">
          <span style={{ width: `${Math.max(identification.confidence * 100, 2)}%` }} />
        </div>
      </div>

      <img
        className="prediction-image"
        src={identification.image_url}
        alt={`Imagem avaliada como ${identification.predicted_scientific_name}`}
      />

      <FeedbackRow feedback={feedback} isSending={isSending} onFeedback={sendFeedback} />

      <details className="details-technical">
        <summary>Detalhes técnicos</summary>
        <dl className="metadata-grid">
          <div>
            <dt>Modelo</dt>
            <dd>{identification.model_name}</dd>
          </div>
          <div>
            <dt>Inferência</dt>
            <dd>{identification.inference_ms.toFixed(1)} ms</dd>
          </div>
          <div>
            <dt>Executado em</dt>
            <dd>{new Date(identification.created_at).toLocaleString('pt-BR')}</dd>
          </div>
        </dl>
      </details>

      <div>
        <h4>Ranking global</h4>
        <div className="probability-list">
          {identification.probabilities.map((item) => (
            <div className="probability-item" key={item.code}>
              <div>
                <strong>{item.scientific_name}</strong>
                <span>{item.common_name}</span>
              </div>
              <div className="probability-bar">
                <div
                  className="probability-fill"
                  style={{ width: `${Math.max(item.probability * 100, 2)}%` }}
                />
              </div>
              <span>{(item.probability * 100).toFixed(2)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function buildStoredProjectTabs(
  projectPredictions: Record<string, PredictionResponse>,
  listedVersions: Set<string>,
  modelVersions: ModelVersion[],
): ProjectResultTab[] {
  return Object.entries(projectPredictions)
    .filter(([version]) => !listedVersions.has(version))
    .map(([version, prediction]) => {
      const knownModel = modelVersions.find((m) => m.version === version)
      return {
        id: createProjectModelId(version),
        label: formatProjectModelLabel(
          knownModel ?? {
            version,
            encoder_name: prediction.model_version.encoder_name,
            classifier_type: prediction.model_version.classifier_type,
          },
        ),
        prediction,
      }
    })
}

export function ResultPanel({ modelVersions }: { modelVersions: ModelVersion[] }) {
  const { projectPredictions, latestProjectVersion, globalIdentification } = usePredictionWorkflow()
  const [selectedTab, setSelectedTab] = useState<ClassificationModelId | null>(null)

  const listedVersions = new Set(modelVersions.map((model) => model.version))
  const projectTabs: ProjectResultTab[] = [
    ...modelVersions.map((model) => ({
      id: createProjectModelId(model.version),
      label: formatProjectModelLabel(model),
      prediction: projectPredictions[model.version] ?? null,
    })),
    ...buildStoredProjectTabs(projectPredictions, listedVersions, modelVersions),
  ]
  const latestProjectTab =
    latestProjectVersion && projectTabs.some((tab) => tab.id === createProjectModelId(latestProjectVersion))
      ? createProjectModelId(latestProjectVersion)
      : null
  const activeModel = modelVersions.find((model) => model.is_active) ?? modelVersions[0]
  const fallbackTab =
    latestProjectTab ??
    (activeModel ? createProjectModelId(activeModel.version) : projectTabs[0]?.id) ??
    OPENAI_MODEL_ID
  const selectedTabIsAvailable =
    selectedTab === OPENAI_MODEL_ID ||
    (selectedTab !== null && isProjectModelId(selectedTab) && projectTabs.some((tab) => tab.id === selectedTab))
  const activeTab = selectedTab && selectedTabIsAvailable ? selectedTab : fallbackTab

  const hasGlobal = globalIdentification !== null
  const activeProjectTab = isProjectModelId(activeTab)
    ? projectTabs.find((tab) => tab.id === activeTab) ?? null
    : null

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Resultado</h2>
        <p>Alterne entre os modelos para comparar as análises.</p>
      </div>

      <div className="result-tabs" role="tablist">
        {projectTabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            className={`result-tab${activeTab === tab.id ? ' result-tab-active' : ''}`}
            onClick={() => setSelectedTab(tab.id)}
          >
            {tab.label}
            {tab.prediction && <span className="tab-dot" aria-hidden="true" />}
          </button>
        ))}
        <button
          type="button"
          role="tab"
          aria-selected={activeTab === OPENAI_MODEL_ID}
          className={`result-tab${activeTab === OPENAI_MODEL_ID ? ' result-tab-active result-tab-active-global' : ''}`}
          onClick={() => setSelectedTab(OPENAI_MODEL_ID)}
        >
          OpenAI CLIP global
          {hasGlobal && <span className="tab-dot tab-dot-global" aria-hidden="true" />}
        </button>
      </div>

      {activeProjectTab ? (
        activeProjectTab.prediction ? (
          <SpecificContent
            key={activeProjectTab.prediction.prediction_id}
            prediction={activeProjectTab.prediction}
            modelLabel={activeProjectTab.label}
          />
        ) : (
          <div className="empty-state empty-state-center">
            <span className="empty-icon" aria-hidden="true" />
            <p>Execute uma análise com <strong>{activeProjectTab.label}</strong> para ver o resultado aqui.</p>
          </div>
        )
      ) : (
        hasGlobal ? (
          <GlobalContent key={globalIdentification.global_identification_id} identification={globalIdentification} />
        ) : (
          <div className="empty-state empty-state-center">
            <span className="empty-icon" aria-hidden="true" />
            <p>Execute uma análise com <strong>OpenAI CLIP global</strong> para ver o resultado aqui.</p>
          </div>
        )
      )}
    </section>
  )
}
