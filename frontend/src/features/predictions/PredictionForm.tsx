import { useEffect, useRef, useState, type FormEvent } from 'react'

import {
  CLASSIFICATION_MODEL_OPTIONS,
  usePredictionWorkflow,
  type ClassificationModelId,
} from './PredictionWorkflowState'

const THINKING_MESSAGES = [
  'Analisando as asas com bastante carinho.',
  'Buscando pistas no pólen digital da imagem.',
  'Conferindo listras, reflexos e aquele brilho metálico.',
  'Você sabia? Existem mais de 20 mil espécies de abelhas descritas no mundo.',
  'Perguntando para a central do néctar qual parece ser essa espécie.',
  'Comparando a foto com nosso jardim de referências.',
  'Observando o formato do corpo com olhar de apicultor experiente.',
  'Decifrando padrões como quem lê o mapa de um jardim secreto.',
  'Checando antenas, olhos e pequenos detalhes dourados.',
  'Explorando o universo das abelhas pixel por pixel.',
  'Buscando semelhanças no nosso arquivo cheio de zumbidos.',
  'Analisando cores como se fossem flores em primavera.',
  'Tentando ouvir o zumbido só de olhar a imagem.',
  'Conectando pistas como uma colmeia bem organizada.',
  'Revisando cada detalhe com precisão de abelha operária.',
  'Você sabia? Algumas abelhas conseguem reconhecer rostos humanos.',
  'Afinando o radar para encontrar a espécie certa.',
  'Explorando cada cantinho da imagem em busca de pistas.',
  'Consultando especialistas do mundo das flores.',
  'Identificando padrões com a calma de um voo suave.',
  'Quase lá… só mais um voo de análise!'
]

function getRandomThinkingMessageIndex(currentIndex?: number) {
  if (THINKING_MESSAGES.length <= 1) {
    return 0
  }

  const availableIndexes = THINKING_MESSAGES
    .map((_, index) => index)
    .filter((index) => index !== currentIndex)

  return availableIndexes[Math.floor(Math.random() * availableIndexes.length)]
}

export function PredictionForm() {
  const [selectedName, setSelectedName] = useState<string>('Nenhum arquivo selecionado')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [selectedModel, setSelectedModel] = useState<ClassificationModelId>('specific')
  const [thinkingMessageIndex, setThinkingMessageIndex] = useState(() =>
    getRandomThinkingMessageIndex(),
  )
  const { errorMessage, isPending, pendingModel, runAnalysis } = usePredictionWorkflow()
  const previewUrlRef = useRef<string | null>(null)

  useEffect(() => {
    if (!isPending) {
      return
    }

    const interval = window.setInterval(() => {
      setThinkingMessageIndex((current) => getRandomThinkingMessageIndex(current))
    }, 2800)

    return () => window.clearInterval(interval)
  }, [isPending])

  useEffect(() => {
    return () => {
      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current)
      }
    }
  }, [])

  const handleFileChange = (file: File | null) => {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current)
      previewUrlRef.current = null
    }
    setSelectedFile(file)
    setSelectedName(file?.name ?? 'Nenhum arquivo selecionado')
    if (file) {
      const url = URL.createObjectURL(file)
      previewUrlRef.current = url
      setPreviewUrl(url)
    } else {
      setPreviewUrl(null)
    }
  }

  const submitSearch = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!selectedFile || isPending) {
      return
    }

    setThinkingMessageIndex((current) => getRandomThinkingMessageIndex(current))
    await runAnalysis(selectedFile, selectedModel)
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Nova análise</h2>
        <p>Envie uma imagem JPG ou PNG e escolha qual modelo deve avaliar a foto.</p>
      </div>

      <form className="stack-md" onSubmit={submitSearch}>
        <label className="file-input upload-dropzone" htmlFor="bee-image">
          <span className="field-label">Imagem da abelha</span>
          <span className="upload-title">Selecione uma foto para classificar</span>
          <strong>{selectedName}</strong>
          <input
            id="bee-image"
            type="file"
            accept=".jpg,.jpeg,.png,image/png,image/jpeg"
            onChange={(event) => handleFileChange(event.currentTarget.files?.[0] ?? null)}
          />
        </label>

        {previewUrl ? (
          <div className="image-preview-wrap">
            <img src={previewUrl} alt="Pré-visualização da imagem selecionada" />
          </div>
        ) : null}

        <div className="model-search-row">
          <label htmlFor="classification-model">
            <span className="field-label">Modelo</span>
            <select
              id="classification-model"
              value={selectedModel}
              onChange={(event) => setSelectedModel(event.target.value as ClassificationModelId)}
              disabled={isPending}
            >
              {CLASSIFICATION_MODEL_OPTIONS.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <button className="primary-button" type="submit" disabled={!selectedFile || isPending}>
            {isPending
              ? pendingModel === 'openai'
                ? 'Consultando...'
                : 'Classificando...'
              : 'Pesquisar'}
          </button>
        </div>

        {isPending ? (
          <div className="thinking-card" aria-live="polite">
            <span className="thinking-orbit" aria-hidden="true" />
            <div>
              <strong>
                {pendingModel === 'openai'
                  ? 'O identificador global está pensando...'
                  : 'Nosso modelo está pensando...'}
              </strong>
              <p>{THINKING_MESSAGES[thinkingMessageIndex]}</p>
            </div>
          </div>
        ) : null}

        {errorMessage ? <p className="feedback error">{errorMessage}</p> : null}
      </form>
    </section>
  )
}
