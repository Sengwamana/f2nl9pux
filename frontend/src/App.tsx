import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { fetchAnalysis } from './api'
import type { AnalysisPoint, AnalysisReport } from './types'

const MONTH_START = '2026-01-01'
const MONTH_END = '2026-01-31'
const PAGE_SIZE = 12

function formatMw(value: number | null | undefined, digits = 0): string {
  if (value == null || !Number.isFinite(value)) return '—'
  return `${new Intl.NumberFormat('en-GB', { maximumFractionDigits: digits }).format(value)} MW`
}

function formatLocalTime(value: string | null | undefined, options?: Intl.DateTimeFormatOptions): string {
  if (!value) return '—'
  const date = new Date(value)
  return new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    ...options,
  }).format(date)
}

function formatBias(value: number | null): string {
  if (value == null) return '—'
  const prefix = value > 0 ? '+' : value < 0 ? '−' : ''
  return `${prefix}${formatMw(Math.abs(value), 0)}`
}

function Chart({ points }: { points: AnalysisPoint[] }) {
  const data = points.filter((point) => point.forecast_mw != null && point.actual_mw != null)
  if (!data.length) {
    return <div className="chart-empty">No matched forecast and actual intervals in this range.</div>
  }

  const width = 1120
  const height = 340
  const margin = { top: 24, right: 32, bottom: 48, left: 80 }
  const plotWidth = width - margin.left - margin.right
  const plotHeight = height - margin.top - margin.bottom
  const maxValue = Math.max(...data.flatMap((point) => [point.forecast_mw ?? 0, point.actual_mw ?? 0]))
  const ceiling = Math.max(5000, Math.ceil(maxValue / 5000) * 5000)
  const x = (index: number) => margin.left + (index / Math.max(1, data.length - 1)) * plotWidth
  const y = (value: number) => margin.top + (1 - value / ceiling) * plotHeight
  const linePath = (key: 'forecast_mw' | 'actual_mw') =>
    data
      .map((point, index) => `${index === 0 ? 'M' : 'L'} ${x(index).toFixed(1)} ${y(point[key] ?? 0).toFixed(1)}`)
      .join(' ')
  const tickCount = 5
  const ticks = Array.from({ length: tickCount + 1 }, (_, index) => (ceiling / tickCount) * index)
  const labelCount = Math.min(8, data.length)
  const labels = Array.from({ length: labelCount }, (_, index) => {
    const pointIndex = Math.round((index / Math.max(1, labelCount - 1)) * (data.length - 1))
    return { pointIndex, label: formatLocalTime(data[pointIndex].delivery_start, { year: undefined }) }
  })

  return (
    <figure className="chart-figure" aria-labelledby="chart-title">
      <div className="chart-scroll">
        <svg
          className="trend-chart"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-labelledby="chart-title chart-description"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#60a5fa" />
              <stop offset="100%" stopColor="#2563eb" />
            </linearGradient>
            <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#34d399" />
              <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
          </defs>
          <title id="chart-title">Hourly wind forecast compared with actual generation</title>
          <desc id="chart-description">
            {data.length} hourly observations. The blue line is the forecast and the green line is actual generation.
          </desc>
          {ticks.map((tick) => (
            <g key={tick} className="chart-gridline">
              <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} />
              <text x={margin.left - 12} y={y(tick) + 4} textAnchor="end">
                {new Intl.NumberFormat('en-GB', { notation: 'compact', maximumFractionDigits: 0 }).format(tick)}
              </text>
            </g>
          ))}
          <path className="forecast-line" d={linePath('forecast_mw')} />
          <path className="actual-line" d={linePath('actual_mw')} />
          {labels.map(({ pointIndex, label }) => (
            <text
              key={`${pointIndex}-${label}`}
              className="chart-x-label"
              x={x(pointIndex)}
              y={height - 16}
              textAnchor={pointIndex === 0 ? 'start' : pointIndex === data.length - 1 ? 'end' : 'middle'}
            >
              {label}
            </text>
          ))}
        </svg>
      </div>
      <figcaption>Hourly average generation (MW) · Delivery timestamps in Europe/London</figcaption>
    </figure>
  )
}

function MetricCard({
  label,
  value,
  supporting,
  tone = 'blue',
}: {
  label: string
  value: string
  supporting: string
  tone?: 'blue' | 'green' | 'amber' | 'violet'
}) {
  return (
    <article className={`metric-card metric-${tone}`}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-support">{supporting}</div>
    </article>
  )
}

function AnalysisTable({ points }: { points: AnalysisPoint[] }) {
  const [page, setPage] = useState(0)
  const matchedPoints = useMemo(() => points, [points])
  const pageCount = Math.max(1, Math.ceil(matchedPoints.length / PAGE_SIZE))
  const rows = matchedPoints.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  useEffect(() => setPage(0), [points])

  if (!points.length) {
    return <div className="table-empty">No intervals are available for the selected dates.</div>
  }

  return (
    <>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th scope="col">Delivery start</th>
              <th scope="col">Forecast</th>
              <th scope="col">Actual</th>
              <th scope="col">Error</th>
              <th scope="col">Forecast issue</th>
              <th scope="col">Match status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((point) => (
              <tr key={point.delivery_start}>
                <td className="delivery-cell">{formatLocalTime(point.delivery_start, { year: undefined })}</td>
                <td>{formatMw(point.forecast_mw)}</td>
                <td>{formatMw(point.actual_mw)}</td>
                <td className={point.error_mw != null && point.error_mw > 0 ? 'error-positive' : 'error-neutral'}>
                  {point.error_mw == null ? '—' : formatBias(point.error_mw)}
                </td>
                <td>{formatLocalTime(point.forecast_publish_time)}</td>
                <td>
                  <span className={`status-pill ${point.status === 'matched' ? 'status-matched' : 'status-missing'}`}>
                    {point.status === 'matched' ? 'Matched' : point.status.replaceAll('_', ' ')}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="table-footer">
        <span>
          Showing {matchedPoints.length ? page * PAGE_SIZE + 1 : 0}–{Math.min((page + 1) * PAGE_SIZE, matchedPoints.length)} of {matchedPoints.length} hourly intervals
        </span>
        <div className="pagination" aria-label="Table pages">
          <button className="button button-subtle" onClick={() => setPage((current) => Math.max(0, current - 1))} disabled={page === 0}>
            Previous
          </button>
          <span className="page-number">{page + 1} / {pageCount}</span>
          <button className="button button-subtle" onClick={() => setPage((current) => Math.min(pageCount - 1, current + 1))} disabled={page >= pageCount - 1}>
            Next
          </button>
        </div>
      </div>
    </>
  )
}

export default function App() {
  const [startDate, setStartDate] = useState(MONTH_START)
  const [endDate, setEndDate] = useState(MONTH_END)
  const [cutoffHour, setCutoffHour] = useState(10)
  const [request, setRequest] = useState({ startDate: MONTH_START, endDate: MONTH_END, cutoffHour: 10 })
  const [report, setReport] = useState<AnalysisReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setError(null)
    fetchAnalysis(request, controller.signal)
      .then((result) => {
        setReport(result)
      })
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') return
        setError(reason instanceof Error ? reason.message : 'Unable to load wind data.')
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [request])

  const latestIssue = useMemo(() => {
    const timestamps = report?.points
      .map((point) => point.forecast_publish_time)
      .filter((value): value is string => value != null)
      .sort()
    return timestamps?.at(-1) ?? null
  }, [report])

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (startDate > endDate) {
      setError('Start date must be on or before end date.')
      return
    }
    setRequest({ startDate, endDate, cutoffHour })
  }

  const metrics = report?.metrics
  const appliedCutoffHour = report?.decision_rule.cutoff_hour ?? request.cutoffHour
  const cutoffLabel = `${String(appliedCutoffHour).padStart(2, '0')}:00 Europe/London on the previous day`

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Gridbricks Wind Desk home">
          <span className="brand-mark" aria-hidden="true"><span /><span /><span /></span>
          <span className="brand-copy"><strong>Gridbricks</strong><small>WIND PROCUREMENT DESK</small></span>
        </a>
        <div className="topbar-right">
          <span className="period-badge"><span /> HISTORICAL PILOT · JANUARY 2026</span>
          <span className="topbar-divider" />
          <span className="topbar-date">Great Britain · Elexon BMRS</span>
        </div>
      </header>

      <main id="top" className="page-content">
        <section className="page-heading">
          <div>
            <div className="eyebrow"><span className="eyebrow-line" /> DAY-AHEAD PROCUREMENT PILOT</div>
            <h1>Wind forecast vs actuals</h1>
            <p className="page-intro">Inspect the latest eligible national wind forecast for each delivery hour and quantify its accuracy against observed generation.</p>
          </div>
          <div className="data-source-badge">
            <span className="source-dot" />
            <span><strong>Elexon BMRS</strong><small>FUELHH (WIND) · WINDFOR</small></span>
          </div>
        </section>

        <section className="controls-card" aria-label="Analysis controls">
          <form className="filter-form" onSubmit={applyFilters}>
            <div className="filter-field">
              <label htmlFor="start-date">Delivery period</label>
              <div className="date-range">
                <input id="start-date" type="date" min={MONTH_START} max={MONTH_END} value={startDate} onChange={(event) => setStartDate(event.target.value)} />
                <span className="date-separator">to</span>
                <input aria-label="Delivery period end date" type="date" min={MONTH_START} max={MONTH_END} value={endDate} onChange={(event) => setEndDate(event.target.value)} />
              </div>
            </div>
            <div className="filter-field cutoff-field">
              <label htmlFor="cutoff-hour">Decision cutoff <span className="assumption-label">PILOT ASSUMPTION</span></label>
              <select id="cutoff-hour" value={cutoffHour} onChange={(event) => setCutoffHour(Number(event.target.value))}>
                {Array.from({ length: 24 }, (_, hour) => (
                  <option key={hour} value={hour}>{String(hour).padStart(2, '0')}:00 Europe/London</option>
                ))}
              </select>
            </div>
            <button className="button button-primary" type="submit" disabled={loading}>
              <span className="refresh-icon" aria-hidden="true">↻</span>
              {loading ? 'Loading…' : 'Update analysis'}
            </button>
          </form>
          <div className="controls-footnote">
            <span className="info-icon" aria-hidden="true">i</span>
            <span>The analysis below uses the latest forecast published by {cutoffLabel}. This is a working assumption, not a confirmed market gate.</span>
          </div>
        </section>

        {error && (
          <div className="notice notice-error" role="alert">
            <span className="notice-symbol" aria-hidden="true">!</span>
            <div><strong>Analysis could not be loaded</strong><p>{error}</p></div>
            <button className="button button-subtle" onClick={() => setRequest({ ...request })}>Retry</button>
          </div>
        )}

        {loading && !report && (
          <section className="loading-state" aria-live="polite">
            <span className="loader" aria-hidden="true" />
            <div><strong>Retrieving Elexon records</strong><p>Loading forecast vintages and matching generation outturn.</p></div>
          </section>
        )}

        {!error && report && (
          <>
            <section className="summary-row" aria-label="Analysis summary">
              <div className="section-intro">
                <div className="section-kicker">PERFORMANCE SNAPSHOT</div>
                <h2>Forecast accuracy</h2>
                <p>{new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long' }).format(new Date(`${report.period.start_date}T12:00:00`))} – {new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(`${report.period.end_date}T12:00:00`))} · Europe/London</p>
              </div>
              <div className="sample-context">
                <span className="sample-context-mark" aria-hidden="true">H</span>
                Historical Elexon sample
              </div>
            </section>

            {metrics && (
              <section className="metrics-grid" aria-label="Forecast accuracy metrics">
                <MetricCard
                  label="Matched hours"
                  value={`${metrics.matched_pairs.toLocaleString('en-GB')} / ${metrics.expected_hours.toLocaleString('en-GB')}`}
                  supporting="complete forecast–actual pairs"
                  tone="blue"
                />
                <MetricCard
                  label="Data coverage"
                  value={`${(metrics.coverage * 100).toFixed(0)}%`}
                  supporting={`${metrics.expected_hours.toLocaleString('en-GB')} expected hours in range`}
                  tone="green"
                />
                <MetricCard
                  label="Mean absolute error"
                  value={formatMw(metrics.mae)}
                  supporting="mean absolute error across matched hours"
                  tone="amber"
                />
                <MetricCard
                  label="Mean bias (forecast − actual)"
                  value={formatBias(metrics.mean_bias)}
                  supporting={metrics.mean_bias == null ? 'Not available' : metrics.mean_bias > 0 ? 'Forecast tends to over-predict' : metrics.mean_bias < 0 ? 'Forecast tends to under-predict' : 'Near-zero average bias'}
                  tone="violet"
                />
              </section>
            )}

            {metrics && metrics.coverage < 1 && (
              <div className="notice notice-warning" role="status">
                <span className="notice-symbol" aria-hidden="true">!</span>
                <div><strong>Partial interval coverage</strong><p>Accuracy metrics use only complete forecast/actual pairs. Missing intervals are shown in the table.</p></div>
              </div>
            )}

            <section className="panel chart-panel">
              <div className="panel-heading">
                <div><div className="section-kicker">GENERATION PROFILE</div><h2>Forecast vs actual generation</h2><p>Hourly delivery intervals aligned to Elexon timestamps</p></div>
                <div className="chart-legend" aria-label="Chart legend">
                  <span><i className="legend-swatch legend-forecast" /> Forecast (WINDFOR)</span>
                  <span><i className="legend-swatch legend-actual" /> Actual (FUELHH mean)</span>
                </div>
              </div>
              {loading && <div className="inline-loading"><span className="loader loader-small" /> Updating analysis…</div>}
              <Chart points={report.points} />
              <div className="chart-footnote">
                <span>Hourly resolution</span><span className="footnote-dot" /><span>Actual = mean of two consecutive half-hour FUELHH average-MW values</span><span className="footnote-dot" /><span>{report.decision_rule.description} (provisional assumption)</span>
              </div>
            </section>

            <section className="panel table-panel">
              <div className="panel-heading table-heading">
                <div><div className="section-kicker">INTERVAL DETAIL</div><h2>Delivery timeline</h2><p>Selected forecast issue time is shown for every delivery hour.</p></div>
                <div className="latest-issue">
                  <span className="latest-issue-label">LATEST ISSUE USED</span>
                  <strong>{formatLocalTime(latestIssue)}</strong>
                </div>
              </div>
              <AnalysisTable points={report.points} />
            </section>

            <section className="method-note">
              <div className="method-icon" aria-hidden="true">↗</div>
              <div>
                <strong>How to read this analysis</strong>
                <p>Positive bias means the forecast was higher than observed generation. Elexon’s wind outturn excludes embedded generation and some unmetered wind farms, so these figures represent Elexon-reported monitored GB wind rather than all wind generation.</p>
                <div className="source-links">
                  <a href="https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream" target="_blank" rel="noreferrer">WINDFOR documentation <span aria-hidden="true">↗</span></a>
                  <a href="https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream" target="_blank" rel="noreferrer">FUELHH documentation <span aria-hidden="true">↗</span></a>
                </div>
              </div>
            </section>
          </>
        )}
      </main>
      <footer className="site-footer"><span>GRIDBRICKS · WIND PROCUREMENT PILOT · ELEXON BMRS</span><span>Wind-only analysis supports decisions; it does not calculate a complete procurement position.</span></footer>
    </div>
  )
}
