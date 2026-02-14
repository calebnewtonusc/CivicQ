"""
LLM Service for AI-powered features using Claude API.

Provides intelligent question analysis, categorization, and content moderation.
"""

import os
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
from pydantic import BaseModel


class QuestionAnalysis(BaseModel):
    """Analysis result for a question"""
    quality_score: float  # 0-100
    is_appropriate: bool
    category: str
    subcategory: Optional[str]
    issues: List[str]
    suggestions: List[str]
    improved_version: Optional[str]


class DuplicateCheckResult(BaseModel):
    """Result of duplicate question detection"""
    is_duplicate: bool
    similarity_score: float  # 0-1
    matched_question_id: Optional[int]
    explanation: str


class AnswerAnalysis(BaseModel):
    """Analysis of a candidate's video answer"""
    key_points: List[str]
    stance: str  # "for", "against", "neutral", "complex"
    specificity_score: float  # 0-100
    claims: List[str]
    potential_issues: List[str]
    summary: str


class LLMService:
    """Service for Claude AI integration"""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
        self.enabled = os.getenv("ENABLE_AI_FEATURES", "true").lower() == "true"

    def analyze_question(
        self,
        question_text: str,
        contest_type: str,
        contest_title: str,
        city_name: str
    ) -> QuestionAnalysis:
        """
        Analyze a question for quality, appropriateness, and categorization.

        Args:
            question_text: The question to analyze
            contest_type: Type of contest ("race", "measure")
            contest_title: Title of the contest
            city_name: Name of the city

        Returns:
            QuestionAnalysis with scores and suggestions
        """
        if not self.enabled:
            return self._default_analysis()

        prompt = f"""Analyze this question submitted for a local election in {city_name}.

Contest: {contest_title} ({contest_type})
Question: "{question_text}"

Provide a JSON response with:
1. quality_score (0-100): Overall quality considering clarity, specificity, and relevance
2. is_appropriate (boolean): Is it civil, on-topic, and appropriate for public discourse?
3. category: Main topic (e.g., "Housing", "Public Safety", "Education", "Infrastructure", "Budget", "Environment", "Transportation", "Health", "Economy", "Governance")
4. subcategory: More specific topic if applicable
5. issues: List of problems (vague wording, loaded language, too broad, etc.)
6. suggestions: List of ways to improve the question
7. improved_version: A better phrasing of the question (only if score < 70)

Respond with ONLY valid JSON, no additional text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            content = response.content[0].text
            import json
            result = json.loads(content)

            return QuestionAnalysis(**result)

        except Exception as e:
            print(f"LLM analysis error: {e}")
            return self._default_analysis()

    def check_duplicate(
        self,
        new_question: str,
        existing_questions: List[Dict[str, Any]]
    ) -> DuplicateCheckResult:
        """
        Check if a question is a duplicate of existing questions.

        Args:
            new_question: The new question text
            existing_questions: List of existing questions with 'id' and 'text'

        Returns:
            DuplicateCheckResult indicating if it's a duplicate
        """
        if not self.enabled or not existing_questions:
            return DuplicateCheckResult(
                is_duplicate=False,
                similarity_score=0.0,
                matched_question_id=None,
                explanation="No existing questions to compare"
            )

        # Format existing questions
        questions_list = "\n".join([
            f"{i+1}. (ID: {q['id']}) {q['text']}"
            for i, q in enumerate(existing_questions[:20])  # Limit to 20 for context
        ])

        prompt = f"""Check if this new question is a duplicate or very similar to any existing questions.

New Question: "{new_question}"

Existing Questions:
{questions_list}

Provide a JSON response with:
1. is_duplicate (boolean): Is this a duplicate or near-duplicate?
2. similarity_score (0-1): How similar is it to the most similar existing question?
3. matched_question_id (number or null): ID of most similar question if is_duplicate is true
4. explanation: Brief explanation of your decision

Consider questions duplicates if they ask essentially the same thing, even if worded differently.

Respond with ONLY valid JSON, no additional text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            import json
            result = json.loads(content)

            return DuplicateCheckResult(**result)

        except Exception as e:
            print(f"Duplicate check error: {e}")
            return DuplicateCheckResult(
                is_duplicate=False,
                similarity_score=0.0,
                matched_question_id=None,
                explanation=f"Error checking duplicates: {str(e)}"
            )

    def analyze_answer(
        self,
        answer_transcript: str,
        question_text: str,
        candidate_name: str
    ) -> AnswerAnalysis:
        """
        Analyze a candidate's video answer for key points and stance.

        Args:
            answer_transcript: Transcript of the video answer
            question_text: The question being answered
            candidate_name: Name of the candidate

        Returns:
            AnswerAnalysis with key insights
        """
        if not self.enabled:
            return AnswerAnalysis(
                key_points=[],
                stance="unknown",
                specificity_score=50.0,
                claims=[],
                potential_issues=[],
                summary="AI analysis not enabled"
            )

        prompt = f"""Analyze this candidate's answer to a question.

Question: "{question_text}"
Candidate: {candidate_name}
Answer Transcript: "{answer_transcript}"

Provide a JSON response with:
1. key_points: List of 3-5 main points made in the answer
2. stance: Overall position ("for", "against", "neutral", "complex")
3. specificity_score (0-100): How specific vs vague is the answer?
4. claims: List of factual claims that could be verified
5. potential_issues: Any problematic statements (evasiveness, contradictions, etc.)
6. summary: 1-2 sentence summary of the answer

Respond with ONLY valid JSON, no additional text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            import json
            result = json.loads(content)

            return AnswerAnalysis(**result)

        except Exception as e:
            print(f"Answer analysis error: {e}")
            return AnswerAnalysis(
                key_points=[],
                stance="unknown",
                specificity_score=50.0,
                claims=[],
                potential_issues=[f"Error analyzing answer: {str(e)}"],
                summary="Analysis failed"
            )

    def generate_suggested_questions(
        self,
        contest_type: str,
        contest_title: str,
        city_name: str,
        num_suggestions: int = 5
    ) -> List[str]:
        """
        Generate suggested questions for a contest.

        Args:
            contest_type: Type of contest
            contest_title: Title of the contest
            city_name: Name of the city
            num_suggestions: Number of questions to generate

        Returns:
            List of suggested question texts
        """
        if not self.enabled:
            return []

        prompt = f"""Generate {num_suggestions} relevant, specific questions that voters might want to ask for this local election.

City: {city_name}
Contest: {contest_title} ({contest_type})

Requirements:
- Questions should be specific to local issues
- Focus on actionable policy questions
- Avoid yes/no questions when possible
- Keep questions clear and concise
- Cover different topic areas

Provide a JSON response with a single field "questions" containing an array of question strings.

Respond with ONLY valid JSON, no additional text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            import json
            result = json.loads(content)

            return result.get("questions", [])

        except Exception as e:
            print(f"Question generation error: {e}")
            return []

    def _default_analysis(self) -> QuestionAnalysis:
        """Return default analysis when AI is disabled"""
        return QuestionAnalysis(
            quality_score=75.0,
            is_appropriate=True,
            category="General",
            subcategory=None,
            issues=[],
            suggestions=[],
            improved_version=None
        )


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
