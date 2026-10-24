export interface AnalysisPoint {
  delivery_start: string
  cutoff_local: string
  cutoff_utc: string
  forecast_publish_time: string | null
  forecast_mw: number | null
  actual_mw: number | null
  error_mw: number | null
  absolute_error_mw: number | null
  status: string
}

export interface AnalysisReport {
  period: { start_date: string; end_date: string }
  decision_rule: {
    cutoff_hour: number
    cutoff_timezone: string
    description: string
  }
  alignment: string
  metrics: {
    unit: string
    error_definition: string
    matched_pairs: number
    expected_hours: number
    coverage: number
    mae: number | null
    mean_bias: number | null
  }
  status_counts: Record<string, number>
  points: AnalysisPoint[]
  sources: {
    actuals: string
    actual_rows_received: number
    forecasts: string
    forecast_rows_received: number
    forecast_publish_window: { from: string; to: string }
  }
}
