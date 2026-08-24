import { Image, Maximize2, Calendar, Cloud } from "lucide-react";

const SatelliteImageCard = ({
  image = null,
  title = "Satellite Image",
  metadata = {},
}) => {
  if (!image) {
    return (
      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <div className="flex items-center gap-3">
          <Image className="h-5 w-5 text-slate-400" />
          <div>
            <h3 className="font-semibold text-white">{title}</h3>
            <p className="mt-1 text-sm text-slate-400">
              No satellite image available for this analysis.
            </p>
          </div>
        </div>
      </section>
    );
  }

  const imageUrl =
    typeof image === "string"
      ? image
      : image.url || image.path || image.image_url;

  return (
    <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 p-5">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-cyan-500/10 p-2">
            <Image className="h-5 w-5 text-cyan-400" />
          </div>

          <div>
            <h3 className="text-lg font-semibold text-white">{title}</h3>
            <p className="text-sm text-slate-400">
              Sentinel satellite imagery
            </p>
          </div>
        </div>

        {imageUrl && (
          <a
            href={imageUrl}
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-slate-700 p-2 text-slate-400 transition hover:border-cyan-500/50 hover:text-cyan-400"
            title="Open full image"
          >
            <Maximize2 className="h-4 w-4" />
          </a>
        )}
      </div>

      {/* Image */}
      <div className="bg-slate-950 p-4">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={title}
            className="max-h-[450px] w-full rounded-lg object-contain"
          />
        ) : (
          <div className="flex min-h-[250px] items-center justify-center rounded-lg border border-dashed border-slate-700">
            <p className="text-sm text-slate-500">
              Image URL not available
            </p>
          </div>
        )}
      </div>

      {/* Metadata */}
      {(metadata.date || metadata.cloud_cover !== undefined) && (
        <div className="flex flex-wrap gap-4 border-t border-slate-800 px-5 py-4 text-sm text-slate-400">
          {metadata.date && (
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-cyan-400" />
              <span>{metadata.date}</span>
            </div>
          )}

          {metadata.cloud_cover !== undefined && (
            <div className="flex items-center gap-2">
              <Cloud className="h-4 w-4 text-cyan-400" />
              <span>Cloud cover: {metadata.cloud_cover}%</span>
            </div>
          )}
        </div>
      )}
    </section>
  );
};

export default SatelliteImageCard;