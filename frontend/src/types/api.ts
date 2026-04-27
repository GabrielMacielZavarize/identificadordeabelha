export type Species = {
  id: number
  code: string
  scientific_name: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type ModelVersion = {
  id: number
  version: string
  encoder_name: string
  classifier_type: string
  artifact_dir: string
  metrics_json: string
  is_active: boolean
  created_at: string
}

export type PredictionProbability = {
  species_code: string
  scientific_name: string | null
  probability: number
}

export type PredictionResponse = {
  prediction_id: number
  image_url: string
  predicted_species: {
    id: number
    code: string
    scientific_name: string
  }
  confidence: number
  probabilities: PredictionProbability[]
  model_version: {
    id: number
    version: string
    encoder_name: string
    classifier_type: string
  }
  created_at: string
  inference_ms: number
}

export type GlobalIdentificationProbability = {
  code: string
  scientific_name: string
  common_name: string
  probability: number
}

export type GlobalIdentificationResponse = {
  global_identification_id: number
  image_url: string
  predicted_code: string
  predicted_scientific_name: string
  predicted_common_name: string
  confidence: number
  probabilities: GlobalIdentificationProbability[]
  model_name: string
  created_at: string
  inference_ms: number
  note: string
}

export type HistorySource = 'specific' | 'openai'
export type HistorySourceFilter = 'all' | HistorySource

export type IdentificationHistoryItem = {
  item_id: number
  source: HistorySource
  source_label: string
  image_url: string
  predicted_code: string
  predicted_scientific_name: string
  predicted_common_name: string | null
  confidence: number
  model_name: string
  inference_ms: number | null
  created_at: string
}

export type IdentificationHistoryPage = {
  items: IdentificationHistoryItem[]
  total: number
  limit: number
  offset: number
}
