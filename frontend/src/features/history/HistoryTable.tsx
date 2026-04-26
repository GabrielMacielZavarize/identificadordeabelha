import type { PredictionResponse } from '../../types/api'

type HistoryTableProps = {
  predictions: PredictionResponse[]
}

export function HistoryTable({ predictions }: HistoryTableProps) {
  if (predictions.length === 0) {
    return (
      <div className="empty-state">
        <p>Nenhum resultado registrado até o momento.</p>
      </div>
    )
  }

  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>Data</th>
            <th>Espécie prevista</th>
            <th>Confiança</th>
            <th>Modelo</th>
            <th>Tempo</th>
          </tr>
        </thead>
        <tbody>
          {predictions.map((prediction) => (
            <tr key={prediction.prediction_id}>
              <td data-label="Data">{new Date(prediction.created_at).toLocaleString('pt-BR')}</td>
              <td data-label="Espécie prevista">
                <strong>{prediction.predicted_species.scientific_name}</strong>
                <div className="cell-subtitle">{prediction.predicted_species.code}</div>
              </td>
              <td data-label="Confiança">{(prediction.confidence * 100).toFixed(2)}%</td>
              <td data-label="Modelo">{prediction.model_version.version}</td>
              <td data-label="Tempo">{prediction.inference_ms.toFixed(1)} ms</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
