// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error no types for react-plotly.js
import Plot from 'react-plotly.js'

interface PlotlyChartProps {
  config: {
    data: object[]
    layout?: object
  }
  className?: string
}

export default function PlotlyChart({ config, className = '' }: PlotlyChartProps) {
  return (
    <Plot
      data={config.data || []}
      layout={{ autosize: true, margin: { t: 30, r: 20, b: 40, l: 50 }, ...(config.layout || {}) }}
      useResizeHandler
      style={{ width: '100%', minHeight: 300 }}
      className={className}
    />
  )
}
