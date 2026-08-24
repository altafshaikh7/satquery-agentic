import { MapPinned } from "lucide-react";

function BBoxInput({ value, onChange }) {
  const handleChange = (field, fieldValue) => {
    onChange({
      ...value,
      [field]: fieldValue,
    });
  };

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-4">
      <div className="mb-4 flex items-center gap-2">
        <MapPinned size={18} className="text-blue-400" />

        <div>
          <h3 className="text-sm font-semibold text-white">
            Area of Interest
          </h3>

          <p className="text-xs text-slate-400">
            Enter the bounding box coordinates for satellite analysis.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-400">
            Min Longitude
          </span>

          <input
            type="number"
            step="any"
            value={value.minLon}
            onChange={(event) =>
              handleChange("minLon", event.target.value)
            }
            placeholder="73.85"
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500"
          />
        </label>

        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-400">
            Min Latitude
          </span>

          <input
            type="number"
            step="any"
            value={value.minLat}
            onChange={(event) =>
              handleChange("minLat", event.target.value)
            }
            placeholder="16.70"
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500"
          />
        </label>

        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-400">
            Max Longitude
          </span>

          <input
            type="number"
            step="any"
            value={value.maxLon}
            onChange={(event) =>
              handleChange("maxLon", event.target.value)
            }
            placeholder="74.05"
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500"
          />
        </label>

        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-400">
            Max Latitude
          </span>

          <input
            type="number"
            step="any"
            value={value.maxLat}
            onChange={(event) =>
              handleChange("maxLat", event.target.value)
            }
            placeholder="16.90"
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500"
          />
        </label>
      </div>
    </div>
  );
}

export default BBoxInput;