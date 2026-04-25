"""Assessment Agent — generates quizzes and evaluates answers.

Uses QUIZ_GENERATOR_PROMPT and ANSWER_EVALUATION_PROMPT verbatim
from MASTER_PLAN Section 10.3.
"""

import structlog

from app.agents.base_agent import BaseAgent
from app.utils.prompts import ANSWER_EVALUATION_PROMPT, QUIZ_GENERATOR_PROMPT

logger = structlog.get_logger(__name__)


class AssessmentAgent(BaseAgent):
    """Generates AI quizzes and evaluates user answers with Gemini."""

    async def generate_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_types: list[str] | None = None,
    ) -> dict:
        """Generate a quiz with the specified parameters.

        Args:
            topic: The topic to quiz on.
            num_questions: How many questions to generate.
            difficulty: easy | medium | hard
            question_types: List of types (mcq, short_answer, etc.)

        Returns:
            Parsed quiz dict with 'quiz_title' and 'questions'.
        """
        types = question_types or ["mcq", "short_answer"]
        types_str = ", ".join(types)

        prompt = QUIZ_GENERATOR_PROMPT.format(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            question_types=types_str,
        )

        logger.info(
            "Generating quiz",
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty,
        )

        # Use Flash for quiz generation (structured JSON, fast)
        quiz = self._generate_json(prompt, use_pro=False)
        quiz.setdefault("quiz_title", f"{topic} Quiz")
        quiz.setdefault("questions", [])

        # Ensure question IDs are set
        for i, q in enumerate(quiz.get("questions", []), start=1):
            q.setdefault("id", f"q{i}")
            q.setdefault("difficulty", difficulty)
            q.setdefault("options", None)
            q.setdefault("explanation", "")

        return quiz

    async def evaluate_submission(
        self,
        questions: list[dict],
        answers: list[dict],
    ) -> dict:
        """Evaluate submitted answers and return scores + feedback.

        Args:
            questions: List of quiz question dicts (from Firestore).
            answers: List of {question_id, answer} dicts from the user.

        Returns:
            dict with score (0-100), feedback list, and weak_areas.
        """
        answer_map = {a["question_id"]: a["answer"] for a in answers}
        feedback = []
        weak_topics: list[str] = []
        total_score = 0.0

        for question in questions:
            q_id = question.get("id", "")
            user_answer = answer_map.get(q_id, "")
            correct_answer = question.get("correct_answer", "")
            q_type = question.get("type", "mcq")

            if q_type in {"mcq", "true_false"}:
                # Rule-based check for objective questions
                is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
                score = 1.0 if is_correct else 0.0
                explanation = question.get("explanation", "")
            else:
                # Gemini semantic evaluation for subjective answers
                eval_result = self._evaluate_with_gemini(
                    question=question.get("question", ""),
                    correct_answer=correct_answer,
                    user_answer=user_answer,
                )
                is_correct = eval_result.get("is_correct", False)
                score = eval_result.get("score", 0.0)
                explanation = eval_result.get("explanation", "")

            total_score += score

            if not is_correct:
                topic = question.get("question", "")[:50]
                weak_topics.append(topic)

            feedback.append({
                "question_id": q_id,
                "correct": is_correct,
                "explanation": explanation,
                "score": score,
            })

        num_questions = len(questions) if questions else 1
        percentage = round((total_score / num_questions) * 100, 1)
        correct_count = sum(1 for f in feedback if f["correct"])

        return {
            "score": percentage,
            "total_questions": num_questions,
            "correct_count": correct_count,
            "feedback": feedback,
            "weak_areas": list(set(weak_topics))[:5],
        }

    def _evaluate_with_gemini(
        self, question: str, correct_answer: str, user_answer: str
    ) -> dict:
        """Use Gemini Flash to semantically evaluate a short answer."""
        if not user_answer.strip():
            return {
                "is_correct": False,
                "score": 0.0,
                "explanation": "No answer provided.",
                "partial_credit": False,
            }

        prompt = ANSWER_EVALUATION_PROMPT.format(
            question=question,
            correct_answer=correct_answer,
            user_answer=user_answer,
        )

        try:
            result = self._generate_json(prompt, use_pro=False)
            result.setdefault("is_correct", False)
            result.setdefault("score", 0.0)
            result.setdefault("explanation", "")
            result.setdefault("partial_credit", False)
            return result
        except Exception as exc:
            logger.error("Gemini answer evaluation failed", error=str(exc))
            # Fallback to simple string match
            is_correct = correct_answer.lower() in user_answer.lower()
            return {
                "is_correct": is_correct,
                "score": 1.0 if is_correct else 0.0,
                "explanation": "Evaluated based on keyword match (AI evaluation unavailable).",
                "partial_credit": False,
            }
