import { useEffect, useState } from "react";
import {
  Calendar,
  ImagePlus,
  Search,
  Send,
  Upload,
  X,
} from "lucide-react";

import BBoxInput from "./BBoxInput";
import ExampleQueries from "./ExampleQueries";
import { uploadImage } from "../../api/uploadApi";
import { QUERY_PLACEHOLDER } from "../../utils/constants";

const initialBBox = {
  minLon: "",
  minLat: "",
  maxLon: "",
  maxLat: "",
};

function QueryForm({
  onSubmit,
  loading,
  initialQuery = "",
}) {
  const [query, setQuery] = useState(initialQuery);

  const [bbox, setBBox] = useState(initialBBox);

  const [beforeDate, setBeforeDate] = useState("");
  const [afterDate, setAfterDate] = useState("");

  const [selectedFile, setSelectedFile] =
    useState(null);

  const [imagePreview, setImagePreview] =
    useState("");

  const [uploadedImagePath, setUploadedImagePath] =
    useState("");

  const [uploading, setUploading] =
    useState(false);

  const [formError, setFormError] =
    useState("");

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
    }
  }, [initialQuery]);

  useEffect(() => {
    return () => {
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
      }
    };
  }, [imagePreview]);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    const fileName =
      file.name.toLowerCase();

    const validExtensions = [
      ".png",
      ".jpg",
      ".jpeg",
      ".tif",
      ".tiff",
    ];

    const hasValidExtension =
      validExtensions.some((extension) =>
        fileName.endsWith(extension)
      );

    if (!hasValidExtension) {
      setFormError(
        "Please select a PNG, JPG, JPEG, TIF, or TIFF image."
      );

      event.target.value = "";
      return;
    }

    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }

    setSelectedFile(file);

    setImagePreview(
      URL.createObjectURL(file)
    );

    setUploadedImagePath("");
    setFormError("");

    event.target.value = "";
  };

  const removeImage = () => {
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }

    setSelectedFile(null);
    setImagePreview("");
    setUploadedImagePath("");
    setFormError("");
  };

  const validateBBox = () => {
    const bboxValues = [
      bbox.minLon,
      bbox.minLat,
      bbox.maxLon,
      bbox.maxLat,
    ];

    const hasAnyBBoxValue =
      bboxValues.some(
        (value) => value !== ""
      );

    const hasCompleteBBox =
      bboxValues.every(
        (value) => value !== ""
      );

    if (
      hasAnyBBoxValue &&
      !hasCompleteBBox
    ) {
      throw new Error(
        "Fill all four Bounding Box values or leave all of them empty."
      );
    }

    if (!hasCompleteBBox) {
      return null;
    }

    const numericBBox = bboxValues.map(
      (value) => Number(value)
    );

    if (
      numericBBox.some(
        (value) =>
          Number.isNaN(value) ||
          !Number.isFinite(value)
      )
    ) {
      throw new Error(
        "Bounding Box values must be valid numbers."
      );
    }

    const [
      minLon,
      minLat,
      maxLon,
      maxLat,
    ] = numericBBox;

    if (
      minLon < -180 ||
      minLon > 180 ||
      maxLon < -180 ||
      maxLon > 180
    ) {
      throw new Error(
        "Longitude values must be between -180 and 180."
      );
    }

    if (
      minLat < -90 ||
      minLat > 90 ||
      maxLat < -90 ||
      maxLat > 90
    ) {
      throw new Error(
        "Latitude values must be between -90 and 90."
      );
    }

    if (minLon >= maxLon) {
      throw new Error(
        "Min Longitude must be smaller than Max Longitude."
      );
    }

    if (minLat >= maxLat) {
      throw new Error(
        "Min Latitude must be smaller than Max Latitude."
      );
    }

    return numericBBox;
  };

  const validateDates = () => {
    const hasBeforeDate =
      beforeDate.trim() !== "";

    const hasAfterDate =
      afterDate.trim() !== "";

    if (
      hasBeforeDate &&
      !hasAfterDate
    ) {
      throw new Error(
        "Please select an After Date."
      );
    }

    if (
      !hasBeforeDate &&
      hasAfterDate
    ) {
      throw new Error(
        "Please select a Before Date."
      );
    }

    if (
      hasBeforeDate &&
      hasAfterDate &&
      new Date(beforeDate) >=
        new Date(afterDate)
    ) {
      throw new Error(
        "Before Date must be earlier than After Date."
      );
    }

    return {
      hasBeforeDate,
      hasAfterDate,
    };
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedQuery =
      query.trim();

    if (
      !trimmedQuery ||
      loading ||
      uploading
    ) {
      return;
    }

    setFormError("");

    try {
      const validatedBBox =
        validateBBox();

      const {
        hasBeforeDate,
        hasAfterDate,
      } = validateDates();

      const payload = {
        query: trimmedQuery,
      };

      if (validatedBBox) {
        payload.bbox =
          validatedBBox;
      }

      if (
        hasBeforeDate &&
        hasAfterDate
      ) {
        payload.before_date =
          beforeDate;

        payload.after_date =
          afterDate;
      }

      let imagePath =
        uploadedImagePath;

      if (
        selectedFile &&
        !imagePath
      ) {
        setUploading(true);

        const uploadResult =
          await uploadImage(
            selectedFile
          );

        imagePath =
          uploadResult?.image_path;

        if (!imagePath) {
          throw new Error(
            "Image upload succeeded, but no image path was returned by the backend."
          );
        }

        setUploadedImagePath(
          imagePath
        );
      }

      if (imagePath) {
        payload.image_urls = [
          imagePath,
        ];
      }

      console.log(
        "FINAL SATQUERY PAYLOAD:",
        JSON.stringify(
          payload,
          null,
          2
        )
      );

      await onSubmit(payload);

    } catch (error) {
      console.error(
        "SatQuery request failed:",
        error
      );

      setFormError(
        error?.message ||
          "Something went wrong while processing the request."
      );

    } finally {
      setUploading(false);
    }
  };

  const handleExampleSelect = (
    selectedQuery
  ) => {
    setQuery(selectedQuery);
    setFormError("");
  };

  const isBusy =
    loading || uploading;

  return (
    <section
      id="query"
      className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/70 shadow-xl"
    >
      {/* HEADER */}

      <div className="border-b border-slate-800 bg-slate-900 px-5 py-5 sm:px-6">
        <div className="flex items-start gap-3">
          <div className="rounded-xl bg-blue-500/10 p-3 text-blue-400">
            <Search size={22} />
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white">
              Satellite Intelligence
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Ask a question, optionally upload an
              image, and analyze it with SatQuery AI.
            </p>
          </div>
        </div>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-6 p-5 sm:p-6"
      >
        {/* ERROR */}

        {formError && (
          <div
            role="alert"
            className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300"
          >
            {formError}
          </div>
        )}

        {/* QUESTION */}

        <div>
          <label
            htmlFor="satellite-query"
            className="mb-2 block text-sm font-medium text-slate-200"
          >
            Your Question
          </label>

          <textarea
            id="satellite-query"
            value={query}
            onChange={(event) => {
              setQuery(
                event.target.value
              );

              setFormError("");
            }}
            placeholder={
              QUERY_PLACEHOLDER
            }
            rows={4}
            disabled={isBusy}
            className="w-full resize-none rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60"
          />
        </div>

        {/* IMAGE UPLOAD */}

        <div>
          <div className="mb-2 flex items-center gap-2">
            <ImagePlus
              size={18}
              className="text-blue-400"
            />

            <label
              htmlFor="satellite-image"
              className="text-sm font-medium text-slate-200"
            >
              Satellite or Aerial Image
            </label>

            <span className="text-xs text-slate-500">
              Optional
            </span>
          </div>

          {!selectedFile ? (
            <label
              htmlFor="satellite-image"
              className="flex cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-950/60 px-5 py-8 transition hover:border-blue-500 hover:bg-blue-500/5"
            >
              <Upload
                size={28}
                className="mb-3 text-blue-400"
              />

              <span className="text-sm font-medium text-slate-200">
                Click to upload an image
              </span>

              <span className="mt-1 text-xs text-slate-500">
                PNG, JPG, JPEG, TIF or TIFF
              </span>

              <input
                id="satellite-image"
                type="file"
                accept=".png,.jpg,.jpeg,.tif,.tiff,image/png,image/jpeg,image/tiff"
                onChange={
                  handleFileChange
                }
                disabled={isBusy}
                className="hidden"
              />
            </label>
          ) : (
            <div className="overflow-hidden rounded-xl border border-slate-700 bg-slate-950">
              {imagePreview && (
                <div className="max-h-72 overflow-hidden bg-black">
                  <img
                    src={imagePreview}
                    alt="Selected satellite imagery"
                    className="mx-auto max-h-72 w-auto object-contain"
                  />
                </div>
              )}

              <div className="flex items-center justify-between gap-3 px-4 py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-white">
                    {selectedFile.name}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    {(
                      selectedFile.size /
                      1024 /
                      1024
                    ).toFixed(2)}{" "}
                    MB
                  </p>
                </div>

                <button
                  type="button"
                  onClick={
                    removeImage
                  }
                  disabled={isBusy}
                  className="rounded-lg p-2 text-slate-400 transition hover:bg-red-500/10 hover:text-red-400 disabled:cursor-not-allowed disabled:opacity-50"
                  aria-label="Remove image"
                >
                  <X size={18} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ADVANCED OPTIONS */}

        <details className="rounded-xl border border-slate-800 bg-slate-950/40">
          <summary className="cursor-pointer px-4 py-4 text-sm font-medium text-slate-300">
            Advanced Geospatial Options
          </summary>

          <div className="space-y-5 border-t border-slate-800 p-4">
            <BBoxInput
              value={bbox}
              onChange={setBBox}
            />

            <div>
              <div className="mb-3 flex items-center gap-2">
                <Calendar
                  size={18}
                  className="text-cyan-400"
                />

                <div>
                  <h3 className="text-sm font-semibold text-slate-200">
                    Comparison Dates
                  </h3>

                  <p className="mt-1 text-xs text-slate-500">
                    Optional. Use only when comparing
                    two different dates.
                  </p>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label
                    htmlFor="before-date"
                    className="mb-2 block text-sm text-slate-400"
                  >
                    Before Date
                  </label>

                  <input
                    id="before-date"
                    type="date"
                    value={beforeDate}
                    onChange={(event) => {
                      setBeforeDate(
                        event.target.value
                      );

                      setFormError("");
                    }}
                    disabled={isBusy}
                    className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:opacity-60"
                  />
                </div>

                <div>
                  <label
                    htmlFor="after-date"
                    className="mb-2 block text-sm text-slate-400"
                  >
                    After Date
                  </label>

                  <input
                    id="after-date"
                    type="date"
                    value={afterDate}
                    onChange={(event) => {
                      setAfterDate(
                        event.target.value
                      );

                      setFormError("");
                    }}
                    disabled={isBusy}
                    min={
                      beforeDate ||
                      undefined
                    }
                    className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:opacity-60"
                  />
                </div>
              </div>
            </div>
          </div>
        </details>

        {/* EXAMPLE QUERIES */}

        <ExampleQueries
          onSelect={
            handleExampleSelect
          }
        />

        {/* SUBMIT */}

        <button
          type="submit"
          disabled={
            !query.trim() || isBusy
          }
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {uploading ? (
            <>
              <Upload size={18} />
              Uploading Image...
            </>
          ) : loading ? (
            <>
              <Search size={18} />
              Analyzing...
            </>
          ) : (
            <>
              <Send size={18} />
              Analyze Image & Query
            </>
          )}
        </button>
      </form>
    </section>
  );
}

export default QueryForm;