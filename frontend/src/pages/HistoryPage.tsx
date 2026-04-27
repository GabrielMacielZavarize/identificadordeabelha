import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'

import { HistoryTable } from '../features/history/HistoryTable'
import { api } from '../lib/http'
import type { HistorySourceFilter, IdentificationHistoryPage } from '../types/api'

const PAGE_SIZE = 10
const FILTER_OPTIONS: Array<{ value: HistorySourceFilter; label: string }> = [
  { value: 'all', label: 'Todos' },
  { value: 'specific', label: 'Nosso modelo' },
  { value: 'openai', label: 'OpenAI' },
]

function normalizeFilter(value: string | null): HistorySourceFilter {
  return value === 'specific' || value === 'openai' ? value : 'all'
}

function normalizePage(value: string | null) {
  const parsed = Number(value)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 1
}

export function HistoryPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [isExporting, setIsExporting] = useState(false)
  const source = normalizeFilter(searchParams.get('source'))
  const page = normalizePage(searchParams.get('page'))
  const offset = (page - 1) * PAGE_SIZE

  const historyQuery = useQuery({
    queryKey: ['identification-history', source, page],
    queryFn: async () => {
      const response = await api.get<IdentificationHistoryPage>('/history', {
        params: { source, limit: PAGE_SIZE, offset },
      })
      return response.data
    },
  })

  const total = historyQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  useEffect(() => {
    if (historyQuery.data && page > totalPages) {
      setSearchParams((current) => {
        const next = new URLSearchParams(current)
        next.set('page', String(totalPages))
        if (source === 'all') {
          next.delete('source')
        } else {
          next.set('source', source)
        }
        return next
      })
    }
  }, [historyQuery.data, page, setSearchParams, source, totalPages])

  const updateFilter = (nextSource: HistorySourceFilter) => {
    setSearchParams((current) => {
      const next = new URLSearchParams(current)
      next.set('page', '1')
      if (nextSource === 'all') {
        next.delete('source')
      } else {
        next.set('source', nextSource)
      }
      return next
    })
  }

  const updatePage = (nextPage: number) => {
    setSearchParams((current) => {
      const next = new URLSearchParams(current)
      next.set('page', String(nextPage))
      if (source === 'all') {
        next.delete('source')
      } else {
        next.set('source', source)
      }
      return next
    })
  }

  const handleExportCsv = async () => {
    setIsExporting(true)
    try {
      const response = await api.get<IdentificationHistoryPage>('/history', {
        params: { source, limit: 1000, offset: 0 },
      })
      const items = response.data.items
      const headers = [
        'Data',
        'Origem',
        'Espécie',
        'Código',
        'Nome comum',
        'Confiança (%)',
        'Modelo',
        'Tempo (ms)',
      ]
      const rows = items.map((item) => [
        new Date(item.created_at).toLocaleString('pt-BR'),
        item.source_label,
        item.predicted_scientific_name,
        item.predicted_code,
        item.predicted_common_name ?? '',
        (item.confidence * 100).toFixed(2),
        item.model_name,
        item.inference_ms?.toFixed(1) ?? '',
      ])
      const csv = [headers, ...rows]
        .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        .join('\n')
      const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `historico-abelhas-${new Date().toISOString().slice(0, 10)}.csv`
      anchor.click()
      URL.revokeObjectURL(url)
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Histórico de classificações</h2>
        <p>Resultados persistidos no SQLite com origem, modelo, timestamp e confiança.</p>
      </div>

      <div className="history-toolbar">
        <label htmlFor="history-source-filter">
          <span className="field-label">Origem</span>
          <select
            id="history-source-filter"
            value={source}
            onChange={(event) => updateFilter(event.target.value as HistorySourceFilter)}
          >
            {FILTER_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        {total > 0 ? (
          <button
            type="button"
            className="secondary-button"
            disabled={isExporting}
            onClick={handleExportCsv}
            style={{ alignSelf: 'flex-end' }}
          >
            {isExporting ? 'Exportando...' : 'Baixar histórico (.csv)'}
          </button>
        ) : null}
      </div>

      {historyQuery.isLoading ? <p>Carregando histórico...</p> : null}
      {historyQuery.data ? <HistoryTable items={historyQuery.data.items} /> : null}
      {historyQuery.data && historyQuery.data.total > 0 ? (
        <div className="pagination-controls" aria-label="Paginação do histórico">
          <button
            className="secondary-button"
            type="button"
            disabled={page <= 1}
            onClick={() => updatePage(page - 1)}
          >
            Anterior
          </button>
          <span>
            Página {page} de {totalPages}
          </span>
          <button
            className="secondary-button"
            type="button"
            disabled={page >= totalPages}
            onClick={() => updatePage(page + 1)}
          >
            Próxima
          </button>
        </div>
      ) : null}
      {historyQuery.isError ? (
        <p className="feedback error">Não foi possível consultar o histórico.</p>
      ) : null}
    </section>
  )
}
