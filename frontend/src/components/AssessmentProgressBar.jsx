/**
 * AssessmentProgressBar
 *
 * A fixed, glassmorphism-styled progress strip that sits just below the top nav
 * during the assessment. Shows:
 *   - Question X of N
 *   - A smooth progress bar
 *   - Live elapsed time (⏱ HH:MM:SS)
 *
 * Design principles:
 *   - Never covers assessment content (48px fixed strip)
 *   - Updates every second via the timer passed from the parent
 *   - Fully responsive (collapses to compact layout on mobile)
 *   - Uses the existing TINS/GOAT CSS variables
 */

export default function AssessmentProgressBar({ step, total, elapsedFormatted }) {
  const currentQuestion = step + 1;
  const pct = total > 0 ? Math.min(100, Math.round((currentQuestion / total) * 100)) : 0;

  return (
    <div className="assessment-progress-strip" role="status" aria-label="Assessment progress">
      {/* Left: Question counter */}
      <div className="aps-question-label">
        <span className="aps-q-current">{currentQuestion}</span>
        <span className="aps-q-sep"> of </span>
        <span className="aps-q-total">{total}</span>
        <span className="aps-q-word"> questions</span>
      </div>

      {/* Center: Progress bar */}
      <div className="aps-bar-wrap" aria-hidden="true">
        <div
          className="aps-bar-fill"
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Right: Timer */}
      <div className="aps-timer" aria-label={`Elapsed time: ${elapsedFormatted}`}>
        <span className="aps-timer-icon" aria-hidden="true">⏱</span>
        <span className="aps-timer-value">{elapsedFormatted}</span>
      </div>
    </div>
  );
}
