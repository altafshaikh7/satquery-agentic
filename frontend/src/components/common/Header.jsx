import { Satellite } from "lucide-react";

function Header() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        {/* Logo and Project Name */}
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 shadow-lg shadow-blue-500/20">
            <Satellite size={24} className="text-white" />
          </div>

          <div>
            <h1 className="text-lg font-bold tracking-tight text-white sm:text-xl">
              SatQuery AI
            </h1>

            <p className="text-xs text-slate-400">
              Agentic Vision-Language Assistant
            </p>
          </div>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden items-center gap-6 md:flex">
          <span className="text-sm text-slate-400">
            Remote Sensing Intelligence
          </span>

          <a
            href="#query"
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition duration-200 hover:border-blue-500 hover:bg-blue-500/10 hover:text-white"
          >
            Start Analysis
          </a>
        </div>

        {/* GitHub Link */}
        <a
          href="https://github.com"
          target="_blank"
          rel="noreferrer"
          aria-label="Open GitHub"
          className="rounded-lg border border-slate-700 px-3 py-2 text-sm font-medium text-slate-300 transition duration-200 hover:border-blue-500 hover:bg-slate-800 hover:text-white"
        >
          GitHub
        </a>
      </div>
    </header>
  );
}

export default Header;