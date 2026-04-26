import { useEffect } from 'react'
import { useForm } from 'react-hook-form'

import type { Species } from '../../types/api'

export type SpeciesFormValues = {
  code: string
  scientific_name: string
  description: string
}

type SpeciesFormProps = {
  initialValue?: Species | null
  isPending?: boolean
  onSubmit: (values: SpeciesFormValues) => void
  onCancel?: () => void
}

export function SpeciesForm({ initialValue, isPending = false, onSubmit, onCancel }: SpeciesFormProps) {
  const { handleSubmit, register, reset } = useForm<SpeciesFormValues>({
    defaultValues: {
      code: initialValue?.code ?? '',
      scientific_name: initialValue?.scientific_name ?? '',
      description: initialValue?.description ?? '',
    },
  })

  useEffect(() => {
    reset({
      code: initialValue?.code ?? '',
      scientific_name: initialValue?.scientific_name ?? '',
      description: initialValue?.description ?? '',
    })
  }, [initialValue, reset])

  return (
    <form
      className="stack-md"
      onSubmit={handleSubmit((values) =>
        onSubmit({
          code: values.code.trim(),
          scientific_name: values.scientific_name.trim(),
          description: values.description.trim(),
        }),
      )}
    >
      <div className="form-grid">
        <label>
          <span>Código da espécie</span>
          <input
            type="text"
            placeholder="aug_smaragdina"
            disabled={Boolean(initialValue)}
            {...register('code', { required: true })}
          />
        </label>
        <label>
          <span>Nome científico</span>
          <input
            type="text"
            placeholder="Augochloropsis smaragdina"
            {...register('scientific_name', { required: true })}
          />
        </label>
      </div>

      <label>
        <span>Descrição</span>
        <textarea
          rows={4}
          placeholder="Observações de identificação ou notas taxonômicas."
          {...register('description')}
        />
      </label>

      <div className="inline-actions">
        <button className="primary-button" type="submit" disabled={isPending}>
          {isPending ? 'Salvando...' : initialValue ? 'Salvar edição' : 'Cadastrar espécie'}
        </button>
        {initialValue && onCancel ? (
          <button className="secondary-button" type="button" onClick={onCancel}>
            Cancelar edição
          </button>
        ) : null}
      </div>
    </form>
  )
}
