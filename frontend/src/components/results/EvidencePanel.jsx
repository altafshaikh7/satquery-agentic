import { FileText, Image, MapPin, Calendar, Database } from "lucide-react";

const EvidencePanel = ({ evidence = [] }) => {
  if (!evidence || evidence.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <div className="flex items-center gap-3">
          <FileText className="h-5 w-5 text-slate-400" />
          <div>
            <h3 className="font-semibold text-white">Evidence</h3>
            <p className="mt-1 text-sm text-slate-400">
              No evidence was returned for this query.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg">
      <div className="mb-5 flex items-center gap-3">
        <div className="rounded-lg bg-cyan-500/10 p-2">
          <Database className="h-5 w-5 text-cyan-400" />
        </div>

        <div>
          <h3 className="text-lg font-semibold text-white">
            Evidence & Sources
          </h3>
          <p className="text-sm text-slate-400">
            Supporting information collected during analysis
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {evidence.map((item, index) => (
          <div
            key={item.id || index}
            className="rounded-lg border border-slate-800 bg-slate-950/50 p-4"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <div className="rounded-md bg-slate-800 p-2">
                  {item.type === "image" ? (
                    <Image className="h-4 w-4 text-cyan-400" />
                  ) : (
                    <FileText className="h-4 w-4 text-blue-400" />
                  )}
                </div>

                <div>
                  <h4 className="font-medium text-slate-100">
                    {item.title || `Evidence ${index + 1}`}
                  </h4>

                  {item.description && (
                    <p className="mt-1 text-sm leading-relaxed text-slate-400">
                      {item.description}
                    </p>
                  )}
                </div>
              </div>

              {item.confidence !== undefined && (
                <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
                  Confidence: {Math.round(item.confidence * 100)}%
                </span>
              )}
            </div>

            {(item.location || item.date || item.source) && (
              <div className="mt-4 flex flex-wrap gap-4 border-t border-slate-800 pt-3 text-xs text-slate-500">
                {item.location && (
                  <div className="flex items-center gap-1.5">
                    <MapPin className="h-3.5 w-3.5" />
                    <span>{item.location}</span>
                  </div>
                )}

                {item.date && (
                  <div className="flex items-center gap-1.5">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>{item.date}</span>
                  </div>
                )}

                {item.source && (
                  <div className="flex items-center gap-1.5">
                    <Database className="h-3.5 w-3.5" />
                    <span>{item.source}</span>
                  </div>
                )}
              </div>
            )}

            {item.url && (
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
                className="mt-3 inline-block text-sm font-medium text-cyan-400 transition hover:text-cyan-300"
              >
                View source →
              </a>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};

export default EvidencePanel;