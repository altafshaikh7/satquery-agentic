import { Route, CheckCircle2 } from "lucide-react";

function RouteCard({ route, intent, tools = [] }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10">
          <Route size={20} className="text-blue-400" />
        </div>

        <div>
          <h3 className="font-semibold text-white">Agent Route</h3>
          <p className="text-sm text-slate-400">
            Query routing and execution strategy
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {intent && (
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Detected Intent
            </p>
            <p className="mt-1 text-sm text-slate-200">{intent}</p>
          </div>
        )}

        {route && (
          <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Selected Route
            </p>
            <p className="mt-1 break-words text-sm text-cyan-300">
              {typeof route === "string"
                ? route
                : route.name || route.route || "Agent execution route"}
            </p>
          </div>
        )}

        {tools.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
              Selected Tools
            </p>

            <div className="flex flex-wrap gap-2">
              {tools.map((tool, index) => (
                <span
                  key={`${tool}-${index}`}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-blue-500/20 bg-blue-500/10 px-2.5 py-1.5 text-xs text-blue-300"
                >
                  <CheckCircle2 size={13} />
                  {typeof tool === "string"
                    ? tool
                    : tool.name || tool.tool_name || `Tool ${index + 1}`}
                </span>
              ))}
            </div>
          </div>
        )}

        {!route && !intent && tools.length === 0 && (
          <p className="text-sm text-slate-400">
            Route information will appear after the agent processes the query.
          </p>
        )}
      </div>
    </div>
  );
}

export default RouteCard;