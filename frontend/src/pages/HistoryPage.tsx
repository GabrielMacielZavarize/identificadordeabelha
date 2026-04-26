import { useQuery } from '@tanstack/react-query'

import { HistoryTable } from '../features/history/HistoryTable'
import { api } from '../lib/http'
import type { PredictionResponse } from '../types/api'

export function HistoryPage() {
  const predictionsQuery = useQuery({
    queryKey: ['predictions-history'],
    queryFn: async () => {
      const response = await api.get<PredictionResponse[]>('/predictions')
      return response.data
    },
  })

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Histórico de classificações</h2>
        <p>Resultados persistidos no SQLite com timestamp, modelo e confiança.</p>
      </div>

      {predictionsQuery.isLoading ? <p>Carregando histórico...</p> : null}
      {predictionsQuery.data ? <HistoryTable predictions={predictionsQuery.data} /> : null}
      {predictionsQuery.isError ? (
        <p className="feedback error">Não foi possível consultar o histórico.</p>
      ) : null}
    </section>
  )
}
