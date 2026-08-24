import { useState } from "react";

import Header from "./components/common/Header";
import QueryForm from "./components/query/QueryForm";
import ResultsDashboard from "./components/results/ResultsDashboard";
import Loader from "./components/common/Loader";
import ErrorMessage from "./components/common/ErrorMessage";

import { useQuery } from "./hooks/useQuery";

function App() {
  const [selectedExample, setSelectedExample] = useState("");

  const {
    result,
    loading,
    error,
    submitQuery,
    clearError,
  } = useQuery();

  const handleSubmit = async (queryData) => {
    setSelectedExample("");

    try {
      await submitQuery(queryData);
    } catch (error) {
      console.error("Query submission failed:", error);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Header />

      <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* HERO */}

        <section className="mb-10 text-center sm:mb-12">
          <div className="mx-auto mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-300">
            Agentic Vision-Language Assistant
          </div>

          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Ask Questions About

            <span className="block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Satellite Imagery
            </span>
          </h1>

          <p className="mx-auto mt-4 max-w-3xl text-base leading-7 text-slate-400 sm:text-lg">
            Upload satellite imagery or ask a geospatial question.
            SatQuery AI analyzes scenes, detects changes, and provides
            evidence-backed results.
          </p>
        </section>

        {/* MAIN LAYOUT */}

        <section className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_340px]">
          {/* LEFT */}

          <div className="min-w-0 space-y-6">
            <QueryForm
              onSubmit={handleSubmit}
              loading={loading}
              initialQuery={selectedExample}
            />

            {error && (
              <ErrorMessage
                message={error}
                onDismiss={clearError}
              />
            )}

            {loading && (
              <Loader
                title="SatQuery is analyzing your request"
                description="Processing your image, planning analysis tasks, and verifying evidence."
              />
            )}

            {!loading && result && (
              <ResultsDashboard
                result={result}
              />
            )}
          </div>

          {/* RIGHT SIDEBAR */}

          <aside className="space-y-6">
            <div className="sticky top-6 rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg">
              <h2 className="text-lg font-semibold text-white">
                What SatQuery Can Do
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                AI-powered tools for understanding and analyzing
                satellite and aerial imagery.
              </p>

              <div className="mt-6 space-y-5">
                <Capability
                  number="01"
                  title="Scene Understanding"
                  description="Identify objects, terrain, land use, and visible activities."
                />

                <Capability
                  number="02"
                  title="Image Analysis"
                  description="Analyze an uploaded satellite or aerial image using vision AI."
                />

                <Capability
                  number="03"
                  title="Change Detection"
                  description="Compare geospatial conditions across different time periods."
                />

                <Capability
                  number="04"
                  title="NDVI Analysis"
                  description="Evaluate vegetation conditions and environmental patterns."
                />

                <Capability
                  number="05"
                  title="Evidence Verification"
                  description="Support answers with extracted evidence and confidence information."
                />
              </div>
            </div>
          </aside>
        </section>
      </main>
    </div>
  );
}

function Capability({
  number,
  title,
  description,
}) {
  return (
    <div className="flex gap-4">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-cyan-500/30 bg-cyan-500/10 text-xs font-semibold text-cyan-400">
        {number}
      </div>

      <div>
        <h3 className="font-medium text-slate-200">
          {title}
        </h3>

        <p className="mt-1 text-sm leading-6 text-slate-400">
          {description}
        </p>
      </div>
    </div>
  );
}

export default App;