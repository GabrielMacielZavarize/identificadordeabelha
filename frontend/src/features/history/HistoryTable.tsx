import type { IdentificationHistoryItem } from '../../types/api'

function confidenceClass(value: number): string {
  if (value >= 0.8) return 'confidence-high'
  if (value >= 0.5) return 'confidence-mid'
  return 'confidence-low'
}

type HistoryTableProps = {
  items: IdentificationHistoryItem[]
}

export function HistoryTable({ items }: HistoryTableProps) {
  if (items.length === 0) {
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
            <th>Origem</th>
            <th>Resultado</th>
            <th>Confiança</th>
            <th>Modelo</th>
            <th>Tempo</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={`${item.source}-${item.item_id}`}>
              <td data-label="Data">{new Date(item.created_at).toLocaleString('pt-BR')}</td>
              <td data-label="Origem">
                <span className={`source-badge source-badge-${item.source}`}>
                  {item.source_label}
                </span>
              </td>
              <td data-label="Resultado">
                <strong>{item.predicted_scientific_name}</strong>
                <div className="cell-subtitle">
                  {item.predicted_common_name
                    ? `${item.predicted_code} · ${item.predicted_common_name}`
                    : item.predicted_code}
                </div>
              </td>
              <td data-label="Confiança">
                <strong className={confidenceClass(item.confidence)}>
                  {(item.confidence * 100).toFixed(2)}%
                </strong>
              </td>
              <td data-label="Modelo">{item.model_name}</td>
              <td data-label="Tempo">
                {item.inference_ms === null ? 'Não informado' : `${item.inference_ms.toFixed(1)} ms`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
