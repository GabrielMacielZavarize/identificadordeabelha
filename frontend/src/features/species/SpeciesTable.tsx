import type { Species } from '../../types/api'

type SpeciesTableProps = {
  species: Species[]
  onEdit: (item: Species) => void
  onDeactivate: (item: Species) => void
}

export function SpeciesTable({ species, onEdit, onDeactivate }: SpeciesTableProps) {
  if (species.length === 0) {
    return (
      <div className="empty-state">
        <p>Nenhuma espécie cadastrada.</p>
      </div>
    )
  }

  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>Código</th>
            <th>Nome científico</th>
            <th>Status</th>
            <th>Descrição</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {species.map((item) => (
            <tr key={item.id}>
              <td data-label="Código">{item.code}</td>
              <td data-label="Nome científico">{item.scientific_name}</td>
              <td data-label="Status">
                <span
                  className={item.is_active ? 'status-badge status-active' : 'status-badge status-inactive'}
                >
                  {item.is_active ? 'Ativa' : 'Inativa'}
                </span>
              </td>
              <td data-label="Descrição">{item.description ?? 'Sem descrição.'}</td>
              <td data-label="Ações">
                <div className="inline-actions">
                  <button className="secondary-button" type="button" onClick={() => onEdit(item)}>
                    Editar
                  </button>
                  <button className="danger-button" type="button" onClick={() => onDeactivate(item)}>
                    Desativar
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
