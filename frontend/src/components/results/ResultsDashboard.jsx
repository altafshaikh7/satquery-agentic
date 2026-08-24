import AnswerCard from "./AnswerCard";
import EvidencePanel from "./EvidencePanel";
import RouteCard from "./RouteCard";
import TaskTimeline from "./TaskTimeline";
import VerificationCard from "./VerificationCard";

const ResultsDashboard = ({ result }) => {
  if (!result) {
    return null;
  }

  return (
    <section className="mt-8 space-y-6">
      {/* Main Answer */}
      <AnswerCard
        answer={result.answer}
        confidence={result.confidence}
      />

      {/* Analysis Overview */}
      <div className="grid gap-6 lg:grid-cols-2">
        <RouteCard route={result.route} />

        <VerificationCard
          verification={result.verification}
        />
      </div>

      {/* Evidence */}
      <EvidencePanel
        evidence={result.evidence || []}
      />

      {/* Agent Execution Timeline */}
      <TaskTimeline
        tasks={result.tasks || result.timeline || []}
      />
    </section>
  );
};

export default ResultsDashboard;