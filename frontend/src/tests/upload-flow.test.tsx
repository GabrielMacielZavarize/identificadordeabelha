import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import { PredictionWorkflowProvider } from '../features/predictions/PredictionWorkflowContext'
import { UploadPage } from '../pages/UploadPage'

const apiGet = vi.fn()
const apiPost = vi.fn()

vi.mock('../lib/http', () => ({
  api: {
    get: (...args: unknown[]) => apiGet(...args),
    post: (...args: unknown[]) => apiPost(...args),
  },
}))

describe('UploadPage', () => {
  it('submits an image and renders the prediction result', async () => {
    apiGet.mockResolvedValueOnce({
      data: [
        {
          id: 1,
          version: 'dinov2_base_mlp_v001',
          encoder_name: 'facebook/dinov2-base',
          classifier_type: 'mlp',
          artifact_dir: '/tmp/model',
          metrics_json: '{}',
          is_active: true,
          created_at: '2026-04-17T12:00:00',
        },
      ],
    })
    apiPost.mockResolvedValueOnce({
      data: {
        prediction_id: 1,
        image_url: '/uploads/test.png',
        predicted_species: {
          id: 1,
          code: 'aug_smaragdina',
          scientific_name: 'Augochloropsis smaragdina',
        },
        confidence: 0.91,
        probabilities: [
          {
            species_code: 'aug_smaragdina',
            scientific_name: 'Augochloropsis smaragdina',
            probability: 0.91,
          },
        ],
        model_version: {
          id: 1,
          version: 'dinov2_base_mlp_v001',
          encoder_name: 'facebook/dinov2-base',
          classifier_type: 'mlp',
        },
        created_at: '2026-04-17T12:00:00',
        inference_ms: 42,
        user_feedback: null,
      },
    })

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    })
    render(
      <QueryClientProvider client={queryClient}>
        <PredictionWorkflowProvider>
          <UploadPage />
        </PredictionWorkflowProvider>
      </QueryClientProvider>,
    )

    const user = userEvent.setup()
    expect((await screen.findAllByText(/DINOv2 Base \+ MLP/i)).length).toBeGreaterThan(0)

    const submitButton = screen.getByRole('button', { name: /pesquisar/i })
    expect(submitButton).toBeDisabled()

    const fileInput = screen.getByLabelText(/imagem da abelha/i)
    const file = new File(['bee'], 'bee.png', { type: 'image/png' })
    await user.upload(fileInput, file)
    expect(submitButton).toBeEnabled()
    await user.click(submitButton)

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledTimes(1)
    })
    expect(apiPost).toHaveBeenCalledWith(
      '/predictions',
      expect.any(FormData),
      expect.objectContaining({
        params: { model_version: 'dinov2_base_mlp_v001' },
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    )
    expect(
      await screen.findByRole('heading', { level: 3, name: 'Augochloropsis smaragdina' }),
    ).toBeInTheDocument()
    expect(screen.getAllByText(/91.00%/i).length).toBeGreaterThan(0)
  })
})
