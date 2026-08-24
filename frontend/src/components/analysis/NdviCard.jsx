import { Leaf, TrendingUp, Activity } from "lucide-react";

const NdviCard = ({ ndvi = null }) => {
  if (!ndvi) {
    return (
      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <h3 className="text-lg font-semibold text-white">
          NDVI Analysis
        </h3>

        <p className="mt-2 text-sm text-slate-400">
          Vegetation analysis results will appear here after processing.
        </p>
      </section>
    );
  }

  const beforeImage =
    ndvi.before_image ||
    ndvi.before ||
    ndvi.beforeImage ||
    null;

  const afterImage =
    ndvi.after_image ||
    ndvi.after ||
    ndvi.afterImage ||
    null;

  const ndviChange =
    ndvi.change ??
    ndvi.ndvi_change ??
    ndvi.difference ??
    null;

  const beforeValue =
    ndvi.before_value ??
    ndvi.before_ndvi ??
    null;

  const afterValue =
    ndvi.after_value ??
    ndvi.after_ndvi ??
    null;

  const isPositiveChange =
    typeof ndviChange === "number" && ndviChange >= 0;

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg">
      {/* Header */}
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-emerald-500/10 p-2">
            <Leaf className="h-5 w-5 text-emerald-400" />
          </div>

          <div>
            <h3 className="text-lg font-semibold text-white">
              NDVI Analysis
            </h3>

            <p className="text-sm text-slate-400">
              Normalized Difference Vegetation Index
            </p>
          </div>
        </div>

        {ndviChange !== null && (
          <div
            className={`rounded-full border px-3 py-1 text-sm font-medium ${
              isPositiveChange
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border-red-500/30 bg-red-500/10 text-red-400"
            }`}
          >
            {isPositiveChange ? "+" : ""}
            {Number(ndviChange).toFixed(3)} NDVI Change
          </div>
        )}
      </div>

      {/* NDVI Images */}
      {(beforeImage || afterImage) && (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/50">
            <div className="border-b border-slate-800 px-4 py-3">
              <span className="text-sm font-medium text-slate-200">
                Previous NDVI
              </span>
            </div>

            {beforeImage ? (
              <img
                src={beforeImage}
                alt="Previous NDVI analysis"
                className="h-64 w-full object-contain"
              />
            ) : (
              <div className="flex h-64 items-center justify-center text-sm text-slate-500">
                Previous NDVI image unavailable
              </div>
            )}
          </div>

          <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/50">
            <div className="border-b border-slate-800 px-4 py-3">
              <span className="text-sm font-medium text-slate-200">
                Latest NDVI
              </span>
            </div>

            {afterImage ? (
              <img
                src={afterImage}
                alt="Latest NDVI analysis"
                className="h-64 w-full object-contain"
              />
            ) : (
              <div className="flex h-64 items-center justify-center text-sm text-slate-500">
                Latest NDVI image unavailable
              </div>
            )}
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="mt-5 grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Activity className="h-4 w-4 text-cyan-400" />
            <span className="text-sm">Previous NDVI</span>
          </div>

          <p className="mt-2 text-xl font-semibold text-white">
            {beforeValue !== null
              ? Number(beforeValue).toFixed(3)
              : "N/A"}
          </p>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Leaf className="h-4 w-4 text-emerald-400" />
            <span className="text-sm">Latest NDVI</span>
          </div>

          <p className="mt-2 text-xl font-semibold text-white">
            {afterValue !== null
              ? Number(afterValue).toFixed(3)
              : "N/A"}
          </p>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
          <div className="flex items-center gap-2 text-slate-400">
            <TrendingUp
              className={`h-4 w-4 ${
                isPositiveChange
                  ? "text-emerald-400"
                  : "text-red-400"
              }`}
            />
            <span className="text-sm">NDVI Difference</span>
          </div>

          <p
            className={`mt-2 text-xl font-semibold ${
              isPositiveChange
                ? "text-emerald-400"
                : "text-red-400"
            }`}
          >
            {ndviChange !== null
              ? `${isPositiveChange ? "+" : ""}${Number(
                  ndviChange
                ).toFixed(3)}`
              : "N/A"}
          </p>
        </div>
      </div>

      {/* Summary */}
      {ndvi.summary && (
        <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950/50 p-4">
          <h4 className="mb-2 text-sm font-medium text-slate-200">
            Vegetation Analysis Summary
          </h4>

          <p className="text-sm leading-relaxed text-slate-400">
            {ndvi.summary}
          </p>
        </div>
      )}
    </section>
  );
};

export default NdviCard;