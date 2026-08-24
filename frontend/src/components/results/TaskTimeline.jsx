import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const TaskTimeline = ({ tasks = [] }) => {
  if (!tasks || tasks.length === 0) {
    return (
      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <h3 className="text-lg font-semibold text-white">
          Agent Task Timeline
        </h3>

        <p className="mt-2 text-sm text-slate-400">
          Task execution details will appear here after you run a query.
        </p>
      </section>
    );
  }

  const getStatusIcon = (status) => {
    if (status === "completed" || status === "success") {
      return <CheckCircle2 className="h-5 w-5 text-emerald-400" />;
    }

    if (status === "running" || status === "in_progress") {
      return <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />;
    }

    return <Circle className="h-5 w-5 text-slate-500" />;
  };

  const getStatusText = (status) => {
    if (status === "completed" || status === "success") {
      return "Completed";
    }

    if (status === "running" || status === "in_progress") {
      return "Running";
    }

    if (status === "failed") {
      return "Failed";
    }

    return "Pending";
  };

  const getStatusClass = (status) => {
    if (status === "completed" || status === "success") {
      return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    }

    if (status === "running" || status === "in_progress") {
      return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
    }

    if (status === "failed") {
      return "bg-red-500/10 text-red-400 border-red-500/30";
    }

    return "bg-slate-800 text-slate-400 border-slate-700";
  };

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white">
          Agent Task Timeline
        </h3>

        <p className="mt-1 text-sm text-slate-400">
          Execution flow of the SatQuery AI agent
        </p>
      </div>

      <div className="relative">
        {tasks.map((task, index) => (
          <div key={task.id || index} className="relative flex gap-4 pb-6">
            {index !== tasks.length - 1 && (
              <div className="absolute left-[9px] top-7 h-full w-px bg-slate-800" />
            )}

            <div className="relative z-10 mt-1">
              {getStatusIcon(task.status)}
            </div>

            <div className="flex-1 rounded-lg border border-slate-800 bg-slate-950/50 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h4 className="font-medium text-slate-100">
                    {task.name || task.title || `Task ${index + 1}`}
                  </h4>

                  {task.description && (
                    <p className="mt-1 text-sm text-slate-400">
                      {task.description}
                    </p>
                  )}
                </div>

                <span
                  className={`rounded-full border px-3 py-1 text-xs font-medium ${getStatusClass(
                    task.status
                  )}`}
                >
                  {getStatusText(task.status)}
                </span>
              </div>

              {task.tool && (
                <div className="mt-3 text-xs text-slate-500">
                  Tool:{" "}
                  <span className="font-medium text-slate-300">
                    {task.tool}
                  </span>
                </div>
              )}

              {task.duration !== undefined && (
                <div className="mt-1 text-xs text-slate-500">
                  Duration:{" "}
                  <span className="font-medium text-slate-300">
                    {task.duration}
                    {typeof task.duration === "number" ? " ms" : ""}
                  </span>
                </div>
              )}

              {task.error && (
                <p className="mt-3 rounded-md border border-red-500/20 bg-red-500/10 p-2 text-xs text-red-300">
                  {task.error}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default TaskTimeline;