import { ArrowRight, TrendingDown, TrendingUp } from "lucide-react";

const ChangeAnalysisCard = ({ changeAnalysis = null }) => {
  if (!changeAnalysis) {
    return (
      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <h3 className="text-lg font-semibold text-white">
          Change Analysis
        </h3>

        <p className="mt-2 text-sm text-slate-400">
          Change detection results will appear here after analysis.
        </p>
      </section>
    );
  }

  const beforeImage =
    changeAnalysis.before_image ||
    changeAnalysis.before ||
    changeAnalysis.beforeImage;

  const afterImage =
    changeAnalysis.after_image ||
    changeAnalysis.after ||
    changeAnalysis.afterImage;

  const changeMask =
    changeAnalysis.change_mask ||
    changeAnalysis.mask ||
    changeAnalysis.changeMask;

  const changePercentage =
    changeAnalysis.change_percentage ??
    changeAnalysis.percentage ??
    changeAnalysis.changePercent;

  const changeDetected =
    changeAnalysis.change_detected ??
    changeAnalysis.detected ??
    false;

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg">
      {/* Header */}
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">
            Change Analysis
          </h3>

          <p className="mt-1 text-sm text-slate-400">
            Before and after satellite image comparison
          </p>
        </div>

        <div
          className={`rounded-full border px-3 py-1 text-sm font-medium ${
            changeDetected
              ? "border-amber-500/30 bg-amber-500/10 text-amber-400"
              : "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
          }`}
        >
          {changeDetected ? "Change Detected" : "No Major Change"}
        </div>
      </div>

      {/* Images */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Before */}
        <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/50">
          <div className="border-b border-slate-800 px-4 py-3">
            <span className="text-sm font-medium text-slate-200">
              Before
            </span>
          </div>

          {beforeImage ? (
            <img
              src={beforeImage}
              alt="Satellite image before change"
              className="h-64 w-full object-cover"
            />
          ) : (
            <div className="flex h-64 items-center justify-center text-sm text-slate-500">
              Before image not available
            </div>
          )}
        </div>

        {/* After */}
        <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/50">
          <div className="border-b border-slate-800 px-4 py-3">
            <span className="text-sm font-medium text-slate-200">
              After
            </span>
          </div>

          {afterImage ? (
            <img
              src={afterImage}
              alt="Satellite image after change"
              className="h-64 w-full object-cover"
            />
          ) : (
            <div className="flex h-64 items-center justify-center text-sm text-slate-500">
              After image not available
            </div>
          )}
        </div>
      </div>

      {/* Change Mask */}
      {changeMask && (
        <div className="mt-4 overflow-hidden rounded-lg border border-slate-800 bg-slate-950/50">
          <div className="border-b border-slate-800 px-4 py-3">
            <span className="text-sm font-medium text-slate-200">
              Detected Change Mask
            </span>
          </div>

          <img
            src={changeMask}
            alt="Detected change mask"
            className="max-h-96 w-full object-contain"
          />
        </div>
      )}

      {/* Statistics */}
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
          <div className="flex items-center gap-2">
            {changeDetected ? (
              <TrendingUp className="h-5 w-5 text-amber-400" />
            ) : (
              <TrendingDown className="h-5 w-5 text-emerald-400" />
            )}

            <span className="text-sm text-slate-400">
              Change Status
            </span>
          </div>

          <p className="mt-2 text-xl font-semibold text-white">
            {changeDetected ? "Detected" : "Stable"}
          </p>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
          <div className="flex items-center gap-2">
            <ArrowRight className="h-5 w-5 text-cyan-400" />

            <span className="text-sm text-slate-400">
              Changed Area
            </span>
          </div>

          <p className="mt-2 text-xl font-semibold text-white">
            {changePercentage !== undefined && changePercentage !== null
              ? `${Number(changePercentage).toFixed(2)}%`
              : "N/A"}
          </p>
        </div>
      </div>

      {/* Summary */}
      {changeAnalysis.summary && (
        <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950/50 p-4">
          <h4 className="mb-2 text-sm font-medium text-slate-200">
            Analysis Summary
          </h4>

          <p className="text-sm leading-relaxed text-slate-400">
            {changeAnalysis.summary}
          </p>
        </div>
      )}
    </section>
  );
};

export default ChangeAnalysisCard;