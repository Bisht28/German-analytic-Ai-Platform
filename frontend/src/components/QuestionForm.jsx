import { useEffect, useState } from "react";

export default function QuestionForm({
  onSubmit,
  loading,
  selectedQuestion
}) {
  const [question, setQuestion] = useState("");

  useEffect(() => {
    if (selectedQuestion) {
      setQuestion(selectedQuestion);
    }
  }, [selectedQuestion]);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!question.trim()) {
      return;
    }

    onSubmit(question);
  };

  return (
    <form className="question-form" onSubmit={handleSubmit}>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question about German traffic accidents..."
      />

      <button
        className="ask-btn"
        type="submit"
        disabled={loading}
      >
        {loading ? "Processing..." : "Ask Question"}
      </button>
    </form>
  );
}