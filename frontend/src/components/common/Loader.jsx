import { LoaderCircle, Satellite } from "lucide-react";

function Loader({
  title = "Analyzing satellite data...",
  description = "SatQuery AI is processing your request using agentic workflows.",
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <div className="relative mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-blue-500/10">
          <Satellite
            size={28}
            className="absolute text-blue-400 opacity-40"
          />

          <LoaderCircle
            size={42}
            className="animate-spin text-blue-500"
          />
        </div>

        <h3 className="text-lg font-semibold text-white">
          {title}
        </h3>

        <p className="mt-2 max-w-md text-sm leading-6 text-slate-400">
          {description}
        </p>

        <div className="mt-6 flex items-center gap-2 text-xs text-slate-500">
          <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />
          Agent workflow in progress
        </div>
      </div>
    </div>
  );
}

export default Loader;