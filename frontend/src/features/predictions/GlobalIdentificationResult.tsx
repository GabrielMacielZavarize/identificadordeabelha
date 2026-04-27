import type { GlobalIdentificationResponse } from '../../types/api'

type GlobalIdentificationResultProps = {
  identification: GlobalIdentificationResponse | null
}

export function GlobalIdentificationResult({ identification }: GlobalIdentificationResultProps) {
  if (!identification) {
    return (
      <section className="panel">
        <div className="panel-header">
          <h2>Identificador global</h2>
          <p>O resultado do modelo abrangente aparecerá aqui.</p>
        </div>
        <div className="empty-state empty-state-center">
          <span className="empty-icon" aria-hidden="true" />
          <p>Nenhuma consulta global executada nesta sessão.</p>
        </div>
      </section>
    )
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Identificador global</h2>
        <p>Baseline separado para comparação com o modelo específico do projeto.</p>
      </div>

      <div className="result-highlight result-highlight-global">
        <p className="eyebrow">Melhor sugestão global</p>
        <h3>{identification.predicted_scientific_name}</h3>
        <p>{identification.predicted_common_name}</p>
        <p className="confidence">
          Confiança: <strong>{(identification.confidence * 100).toFixed(2)}%</strong>
        </p>
        <div className="confidence-meter" aria-hidden="true">
          <span style={{ width: `${Math.max(identification.confidence * 100, 2)}%` }} />
        </div>
      </div>

      <div className="stack-md">
        <img
          className="prediction-image"
          src={identification.image_url}
          alt={`Imagem avaliada pelo identificador global como ${identification.predicted_scientific_name}`}
        />

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
    </section>
  )
}
