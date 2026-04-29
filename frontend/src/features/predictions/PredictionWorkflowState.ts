import { createContext, useContext } from 'react'

import type { GlobalIdentificationResponse, ModelVersion, PredictionResponse } from '../../types/api'

export type ProjectModelId = `project:${string}`
export type ClassificationModelId = ProjectModelId | 'openai'

export const OPENAI_MODEL_ID = 'openai' satisfies ClassificationModelId

const MODEL_LABELS: Array<[string, string]> = [
  ['dinov3-vits16plus', 'DINOv3 ViT-S+/16'],
  ['dinov3-vits16', 'DINOv3 ViT-S/16'],
  ['dinov3-vitb16', 'DINOv3 ViT-B/16'],
  ['dinov3-vitl16', 'DINOv3 ViT-L/16'],
  ['dinov3-vith16plus', 'DINOv3 ViT-H+/16'],
  ['dinov3-vit7b16', 'DINOv3 ViT-7B/16'],
  ['dinov3-convnext-tiny', 'DINOv3 ConvNeXt Tiny'],
  ['dinov3-convnext-small', 'DINOv3 ConvNeXt Small'],
  ['dinov3-convnext-base', 'DINOv3 ConvNeXt Base'],
  ['dinov3-convnext-large', 'DINOv3 ConvNeXt Large'],
  ['dinov2-small', 'DINOv2 Small'],
  ['dinov2-base', 'DINOv2 Base'],
  ['dinov2-large', 'DINOv2 Large'],
  ['dinov2-giant', 'DINOv2 Giant'],
]

export function createProjectModelId(version: string): ProjectModelId {
  return `project:${version}`
}

export function isProjectModelId(modelId: ClassificationModelId): modelId is ProjectModelId {
  return modelId.startsWith('project:')
}

export function getProjectModelVersion(modelId: ProjectModelId): string {
  return modelId.replace(/^project:/, '')
}

export function formatProjectModelLabel(
  model: Pick<ModelVersion, 'version' | 'encoder_name' | 'classifier_type'>,
): string {
  const encoderName = model.encoder_name.toLowerCase()
  const baseLabel = MODEL_LABELS.find(([needle]) => encoderName.includes(needle))?.[1]
  const classifier = model.classifier_type.toUpperCase()

  if (baseLabel) {
    return `${baseLabel} + ${classifier}`
  }

  return `${model.version.replace(/_/g, ' ')} + ${classifier}`
}

export function formatProjectModelOptionLabel(model: ModelVersion): string {
  const label = formatProjectModelLabel(model)
  return model.is_active ? `${label} (ativo)` : label
}

export type PredictionWorkflowContextValue = {
  prediction: PredictionResponse | null
  projectPredictions: Record<string, PredictionResponse>
  latestProjectVersion: string | null
  globalIdentification: GlobalIdentificationResponse | null
  isPending: boolean
  pendingModel: ClassificationModelId | null
  errorMessage: string | null
  runAnalysis: (file: File, modelId: ClassificationModelId) => Promise<void>
}

export const PredictionWorkflowContext =
  createContext<PredictionWorkflowContextValue | null>(null)

export function usePredictionWorkflow() {
  const context = useContext(PredictionWorkflowContext)
  if (!context) {
    throw new Error('usePredictionWorkflow must be used within PredictionWorkflowProvider.')
  }
  return context
}
