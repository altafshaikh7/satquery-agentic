import {
  BadgeCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ShieldCheck,
} from "lucide-react";

const VerificationCard = ({ verification = null }) => {
  if (!verification) {
    return (
      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <h3 className="text-lg font-semibold text-white">
          Verification Status
        </h3>

        <p className="mt-2 text-sm text-slate-400">
          Verification details will appear after the agent completes analysis.
        </p>
      </section>
    );
  }

  const isVerified =
    verification.verified === true ||
    verification.status === "verified" ||
    verification.status === "success";

  const isFailed = verification.status === "failed";

  const getStatusConfig = () => {
    if (isVerified) {
      return {
        label: "Verified",
        icon: <CheckCircle2 className="h-6 w-6 text-emerald-400" />,
        badgeClass:
          "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
      };
    }

    if (isFailed) {
      return {
        label: "Verification Failed",
        icon: <XCircle className="h-6 w-6 text-red-400" />,
        badgeClass: "border-red-500/30 bg-red-500/10 text-red-400",
      };
    }

    return {
      label: "Needs Review",
      icon: <AlertTriangle className="h-6 w-6 text-amber-400" />,
      badgeClass:
        "border-amber-500/30 bg-amber-500/10 text-amber-400",
    };
  };

  const status = getStatusConfig();

  const confidence =
    verification.confidence !== undefined
      ? Math.round(
          verification.confidence <= 1
            ? verification.confidence * 100
            : verification.confidence
        )
      : null;

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-violet-500/10 p-2">
            <ShieldCheck className="h-5 w-5 text-violet-400" />
          </div>

          <div>
            <h3 className="text-lg font-semibold text-white">
              Verification Status
            </h3>

            <p className="text-sm text-slate-400">
              Agent validation and result reliability
            </p>
          </div>
        </div>

        <div
          className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-medium ${status.badgeClass}`}
        >
          {status.icon}
          <span>{status.label}</span>
        </div>
      </div>

      <div className="space-y-4">
        {confidence !== null && (
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-sm text-slate-400">
                Verification Confidence
              </span>

              <span className="font-semibold text-white">
                {confidence}%
              </span>
            </div>

            <div className="h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all duration-500"
                style={{
                  width: `${Math.min(Math.max(confidence, 0), 100)}%`,
                }}
              />
            </div>
          </div>
        )}

        {verification.reason && (
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
            <div className="mb-2 flex items-center gap-2">
              <BadgeCheck className="h-4 w-4 text-cyan-400" />

              <span className="text-sm font-medium text-slate-200">
                Verification Summary
              </span>
            </div>

            <p className="text-sm leading-relaxed text-slate-400">
              {verification.reason}
            </p>
          </div>
        )}

        {verification.details && (
          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
            <p className="text-sm leading-relaxed text-slate-400">
              {verification.details}
            </p>
          </div>
        )}

        {verification.checks &&
          Array.isArray(verification.checks) &&
          verification.checks.length > 0 && (
            <div>
              <h4 className="mb-3 text-sm font-medium text-slate-200">
                Validation Checks
              </h4>

              <div className="space-y-2">
                {verification.checks.map((check, index) => {
                  const passed =
                    check.passed === true || check.status === "passed";

                  return (
                    <div
                      key={check.id || index}
                      className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-950/50 p-3"
                    >
                      {passed ? (
                        <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                      ) : (
                        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
                      )}

                      <div>
                        <p className="text-sm font-medium text-slate-200">
                          {check.name || check.title || `Check ${index + 1}`}
                        </p>

                        {check.message && (
                          <p className="mt-1 text-xs text-slate-400">
                            {check.message}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
      </div>
    </section>
  );
};

export default VerificationCard;