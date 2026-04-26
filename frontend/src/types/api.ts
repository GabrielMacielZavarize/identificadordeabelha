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
