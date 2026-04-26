import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'

import { SpeciesForm, type SpeciesFormValues } from '../features/species/SpeciesForm'
import { SpeciesTable } from '../features/species/SpeciesTable'
import { api } from '../lib/http'
import type { Species } from '../types/api'

export function SpeciesPage() {
  const queryClient = useQueryClient()
  const [editingSpecies, setEditingSpecies] = useState<Species | null>(null)
  const [feedback, setFeedback] = useState<string | null>(null)

  const speciesQuery = useQuery({
    queryKey: ['species', 'all'],
    queryFn: async () => {
      const response = await api.get<Species[]>('/species', {
        params: { include_inactive: true },
      })
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: async (values: SpeciesFormValues) => {
      const response = await api.post<Species>('/species', values)
      return response.data
    },
    onSuccess: () => {
      setFeedback('Espécie cadastrada com sucesso.')
      queryClient.invalidateQueries({ queryKey: ['species'] })
    },
    onError: (error) => {
      setFeedback(
        axios.isAxiosError(error)
          ? ((error.response?.data as { detail?: string } | undefined)?.detail ?? error.message)
          : 'Falha ao cadastrar espécie.',
      )
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, values }: { id: number; values: Omit<SpeciesFormValues, 'code'> }) => {
      const response = await api.put<Species>(`/species/${id}`, values)
      return response.data
    },
    onSuccess: () => {
      setEditingSpecies(null)
      setFeedback('Espécie atualizada.')
      queryClient.invalidateQueries({ queryKey: ['species'] })
    },
    onError: () => setFeedback('Falha ao atualizar espécie.'),
  })

  const deleteMutation = useMutation({
    mutationFn: async (species: Species) => {
      const response = await api.delete<Species>(`/species/${species.id}`)
      return response.data
    },
    onSuccess: () => {
      setEditingSpecies(null)
      setFeedback('Espécie desativada.')
      queryClient.invalidateQueries({ queryKey: ['species'] })
    },
    onError: () => setFeedback('Falha ao desativar espécie.'),
  })

  const handleSubmit = (values: SpeciesFormValues) => {
    setFeedback(null)
    if (editingSpecies) {
      updateMutation.mutate({
        id: editingSpecies.id,
        values: {
          scientific_name: values.scientific_name,
          description: values.description,
        },
      })
      return
    }
    createMutation.mutate(values)
  }

  return (
    <div className="stack-lg">
      <section className="panel">
        <div className="panel-header">
          <h2>Cadastro de espécies</h2>
          <p>Fonte de verdade do runtime para mapear códigos de saída do classificador.</p>
        </div>

        <SpeciesForm
          initialValue={editingSpecies}
          isPending={createMutation.isPending || updateMutation.isPending}
          onSubmit={handleSubmit}
          onCancel={() => setEditingSpecies(null)}
        />
        {feedback ? <p className="feedback">{feedback}</p> : null}
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Espécies registradas</h2>
          <p>Lista ativa e inativa armazenada no SQLite do MVP.</p>
        </div>

        {speciesQuery.isLoading ? <p>Carregando espécies...</p> : null}
        {speciesQuery.data ? (
          <SpeciesTable
            species={speciesQuery.data}
            onEdit={setEditingSpecies}
            onDeactivate={(species) => deleteMutation.mutate(species)}
          />
        ) : null}
      </section>
    </div>
  )
}
