import { useState } from "react";

import Header from "./components/common/Header";
import QueryForm from "./components/query/QueryForm";
import ExampleQueries from "./components/query/ExampleQueries";
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

  const handleExampleSelect = (example) => {
    setSelectedExample(example.query);
    clearError();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Header />

      <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <section className="mb-10 text-center">
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
            SatQuery AI combines satellite data, geospatial intelligence,
            and agentic AI to analyze scenes, detect changes, estimate
            confidence, and provide evidence-backed answers.
          </p>
        </section>

        {/* Main Layout */}
        <section className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_380px]">
          {/* Left Section */}
          <div className="space-y-6">
            <QueryForm
              onSubmit={handleSubmit}
              loading={loading}
              initialQuery={selectedExample}
            />

            {/* Error */}
            {error && (
              <ErrorMessage
                message={error}
                onDismiss={clearError}
              />
            )}

            {/* Loading */}
            {loading && (
              <Loader
                title="SatQuery is analyzing your request"
                description="The agent is planning tasks, processing satellite data, and verifying evidence."
              />
            )}

            {/* Results */}
            {!loading && result && (
              <ResultsDashboard
                result={result}
              />
            )}
          </div>

          {/* Right Section */}
          <aside className="space-y-6">
            <ExampleQueries
              onSelect={handleExampleSelect}
            />

            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
              <h2 className="text-lg font-semibold text-white">
                SatQuery Capabilities
              </h2>

              <div className="mt-5 space-y-4">
                <Capability
                  title="Scene Understanding"
                  description="Describe and interpret objects, terrain, and activities visible in satellite imagery."
                />

                <Capability
                  title="Change Detection"
                  description="Compare imagery across time periods and identify meaningful changes."
                />

                <Capability
                  title="NDVI Analysis"
                  description="Analyze vegetation conditions and environmental patterns."
                />

                <Capability
                  title="Evidence Verification"
                  description="Generate answers supported by extracted evidence and confidence scores."
                />
              </div>
            </div>
          </aside>
        </section>
      </main>
    </div>
  );
}

function Capability({ title, description }) {
  return (
    <div className="border-l-2 border-cyan-500/60 pl-4">
      <h3 className="font-medium text-slate-200">
        {title}
      </h3>

      <p className="mt-1 text-sm leading-6 text-slate-400">
        {description}
      </p>
    </div>
  );
}

export default App;