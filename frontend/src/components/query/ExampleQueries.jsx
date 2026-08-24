import { Sparkles } from "lucide-react";
import { EXAMPLE_QUERIES } from "../../utils/constants";

function ExampleQueries({ onSelect }) {
  return (
    <div className="mt-5">
      <div className="mb-3 flex items-center gap-2">
        <Sparkles size={16} className="text-blue-400" />

        <span className="text-sm font-medium text-slate-300">
          Try an example
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        {EXAMPLE_QUERIES.map((query) => (
          <button
            key={query}
            type="button"
            onClick={() => onSelect(query)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-left text-xs text-slate-400 transition hover:border-blue-500 hover:bg-blue-500/10 hover:text-blue-300"
          >
            {query}
          </button>
        ))}
      </div>
    </div>
  );
}

export default ExampleQueries;