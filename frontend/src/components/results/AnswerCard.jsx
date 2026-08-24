import { Sparkles } from "lucide-react";

export default function AnswerCard({ answer }) {
  if (!answer) {
    return null;
  }

  return (
    <section className="result-card">
      <div className="result-card-header">
        <div className="result-card-icon">
          <Sparkles size={20} />
        </div>

        <div>
          <h2>AI Analysis</h2>
          <p>SatQuery agent-generated response</p>
        </div>
      </div>

      <div className="answer-content">
        {answer}
      </div>
    </section>
  );
}