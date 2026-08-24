import { useEffect, useState } from "react";
import { Search, Send, Calendar } from "lucide-react";

import BBoxInput from "./BBoxInput";
import ExampleQueries from "./ExampleQueries";
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

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
    }
  }, [initialQuery]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedQuery = query.trim();

    if (!trimmedQuery || loading) {
      return;
    }

    // ==========================================
    // BBOX VALIDATION
    // ==========================================

    const bboxValues = [
      bbox.minLon,
      bbox.minLat,
      bbox.maxLon,
      bbox.maxLat,
    ];

    const hasAnyBBoxValue = bboxValues.some(
      (value) => value !== ""
    );

    const hasCompleteBBox = bboxValues.every(
      (value) => value !== ""
    );

    if (hasAnyBBoxValue && !hasCompleteBBox) {
      alert(
        "Please fill all four Bounding Box values or leave all of them empty."
      );
      return;
    }

    // ==========================================
    // DATE VALIDATION
    // ==========================================

    const hasBeforeDate = beforeDate.trim() !== "";
    const hasAfterDate = afterDate.trim() !== "";

    if (hasBeforeDate && !hasAfterDate) {
      alert("Please select an After Date.");
      return;
    }

    if (!hasBeforeDate && hasAfterDate) {
      alert("Please select a Before Date.");
      return;
    }

    if (
      hasBeforeDate &&
      hasAfterDate &&
      new Date(beforeDate) >= new Date(afterDate)
    ) {
      alert(
        "Before Date must be earlier than After Date."
      );
      return;
    }

    // ==========================================
    // DETECT CHANGE ANALYSIS
    // ==========================================

    const changeKeywords = [
      "change",
      "compare",
      "comparison",
      "difference",
      "different",
      "changed",
      "before",
      "after",
      "between",
      "compared",
      "increase",
      "decrease",
      "gain",
      "loss",
    ];

    const lowerQuery = trimmedQuery.toLowerCase();

    const isChangeQuery = changeKeywords.some(
      (keyword) => lowerQuery.includes(keyword)
    );

    // ==========================================
    // CHANGE ANALYSIS REQUIREMENTS
    // ==========================================

    if (isChangeQuery) {
      if (!hasCompleteBBox) {
        alert(
          "Change Analysis requires all four Bounding Box values."
        );
        return;
      }

      if (!hasBeforeDate || !hasAfterDate) {
        alert(
          "Change Analysis requires both Before Date and After Date."
        );
        return;
      }
    }

    // ==========================================
    // CREATE PAYLOAD
    // ==========================================

    const payload = {
      query: trimmedQuery,
    };

    // ==========================================
    // ADD + VALIDATE BBOX
    // ==========================================

    if (hasCompleteBBox) {
      const numericBBox = [
        Number(bbox.minLon),
        Number(bbox.minLat),
        Number(bbox.maxLon),
        Number(bbox.maxLat),
      ];

      if (
        numericBBox.some((value) =>
          Number.isNaN(value)
        )
      ) {
        alert(
          "Bounding Box values must be valid numbers."
        );
        return;
      }

      const [
        minLon,
        minLat,
        maxLon,
        maxLat,
      ] = numericBBox;

      // Validate Longitude
      if (minLon >= maxLon) {
        alert(
          `Invalid Bounding Box:\nMin Longitude (${minLon}) must be smaller than Max Longitude (${maxLon}).`
        );
        return;
      }

      // Validate Latitude
      if (minLat >= maxLat) {
        alert(
          `Invalid Bounding Box:\nMin Latitude (${minLat}) must be smaller than Max Latitude (${maxLat}).`
        );
        return;
      }

      payload.bbox = numericBBox;

      console.log("FINAL BBOX:", {
        minLon,
        minLat,
        maxLon,
        maxLat,
      });
    }

    // ==========================================
    // ADD DATES
    // ==========================================

    if (hasBeforeDate && hasAfterDate) {
      payload.before_date = beforeDate;
      payload.after_date = afterDate;
    }

    // ==========================================
    // DEBUG FINAL PAYLOAD
    // ==========================================

    console.log(
      "Sending FINAL query payload:",
      JSON.stringify(payload, null, 2)
    );

    // ==========================================
    // SUBMIT
    // ==========================================

    try {
      await onSubmit(payload);
    } catch (error) {
      console.error(
        "Query submission failed:",
        error
      );
    }
  };

  const handleExampleSelect = (selectedQuery) => {
    setQuery(selectedQuery);
  };

  return (
    <section
      id="query"
      className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl sm:p-6"
    >
      {/* HEADER */}

      <div className="mb-6 flex items-start gap-3">
        <div className="rounded-xl bg-blue-500/10 p-3 text-blue-400">
          <Search size={22} />
        </div>

        <div>
          <h2 className="text-xl font-semibold text-white">
            Satellite Intelligence Query
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Ask SatQuery AI to analyze satellite imagery
            and geospatial data.
          </p>
        </div>
      </div>

      {/* FORM */}

      <form
        onSubmit={handleSubmit}
        className="space-y-5"
      >
        {/* QUERY */}

        <div>
          <label
            htmlFor="satellite-query"
            className="mb-2 block text-sm font-medium text-slate-300"
          >
            Your Question
          </label>

          <textarea
            id="satellite-query"
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
            placeholder={QUERY_PLACEHOLDER}
            rows={5}
            disabled={loading}
            className="w-full resize-none rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60"
          />
        </div>

        {/* BOUNDING BOX */}

        <BBoxInput
          value={bbox}
          onChange={setBBox}
        />

        {/* CHANGE ANALYSIS DATES */}

        <div className="rounded-xl border border-slate-700 bg-slate-950/50 p-4">
          <div className="mb-4 flex items-center gap-2">
            <Calendar
              size={18}
              className="text-cyan-400"
            />

            <div>
              <h3 className="text-sm font-semibold text-slate-200">
                Change Analysis Dates
              </h3>

              <p className="mt-1 text-xs text-slate-500">
                Required only when comparing satellite
                imagery across two time periods.
              </p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {/* BEFORE DATE */}

            <div>
              <label
                htmlFor="before-date"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Before Date
              </label>

              <input
                id="before-date"
                type="date"
                value={beforeDate}
                onChange={(event) =>
                  setBeforeDate(event.target.value)
                }
                disabled={loading}
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {/* AFTER DATE */}

            <div>
              <label
                htmlFor="after-date"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                After Date
              </label>

              <input
                id="after-date"
                type="date"
                value={afterDate}
                onChange={(event) =>
                  setAfterDate(event.target.value)
                }
                disabled={loading}
                min={beforeDate || undefined}
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>
          </div>
        </div>

        {/* EXAMPLE QUERIES */}

        <ExampleQueries
          onSelect={handleExampleSelect}
        />

        {/* SUBMIT */}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!query.trim() || loading}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Send size={17} />

            {loading
              ? "Analyzing..."
              : "Analyze Query"}
          </button>
        </div>
      </form>
    </section>
  );
}

export default QueryForm;