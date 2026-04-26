import type { PredictionResponse } from '../../types/api'

type PredictionResultProps = {
  prediction: PredictionResponse | null
}

export function PredictionResult({ prediction }: PredictionResultProps) {
  if (!prediction) {
    return (
      <section className="panel">
        <div className="panel-header">
          <h2>Resultado</h2>
          <p>A predição aparecerá aqui após o upload.</p>
        </div>
        <div className="empty-state empty-state-center">
          <span className="empty-icon" aria-hidden="true" />
          <p>Sem inferência executada nesta sessão.</p>
        </div>
      </section>
    )
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Resultado da inferência</h2>
        <p>Predição principal, confiança e distribuição de probabilidades.</p>
      </div>

      <div className="result-highlight">
        <p className="eyebrow">Espécie prevista</p>
        <h3>{prediction.predicted_species.scientific_name}</h3>
        <p>{prediction.predicted_species.code}</p>
        <p className="confidence">
          Confiança: <strong>{(prediction.confidence * 100).toFixed(2)}%</strong>
        </p>
        <div className="confidence-meter" aria-hidden="true">
          <span style={{ width: `${Math.max(prediction.confidence * 100, 2)}%` }} />
        </div>
      </div>

      <div className="stack-md">
        <img
          className="prediction-image"
          src={prediction.image_url}
          alt={`Imagem processada para ${prediction.predicted_species.scientific_name}`}
        />

        <dl className="metadata-grid">
          <div>
            <dt>Modelo</dt>
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
    </section>
  )
}
