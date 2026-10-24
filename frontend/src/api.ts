import type { AnalysisReport } from './types'

export interface AnalysisRequest {
  startDate: string
  endDate: string
  cutoffHour: number
}

export async function fetchAnalysis(
  request: AnalysisRequest,
  signal?: AbortSignal,
): Promise<AnalysisReport> {
  const query = new URLSearchParams({
    start_date: request.startDate,
    end_date: request.endDate,
    cutoff_hour: String(request.cutoffHour),
    timezone: 'Europe/London',
  })
  const response = await fetch(`/api/analysis?${query.toString()}`, { signal })
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const payload = (await response.json()) as { detail?: string }
      if (payload.detail) detail = payload.detail
    } catch {
      // Keep the HTTP status message when the server does not return JSON.
    }
    throw new Error(detail)
  }
  return (await response.json()) as AnalysisReport
}
