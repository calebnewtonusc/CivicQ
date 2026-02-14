# AI-Powered Features in CivicQ

CivicQ integrates **Claude Sonnet 4.5** to provide intelligent assistance throughout the civic engagement process.

## Features

### 1. Smart Question Composer 🤖

The `SmartQuestionComposer` component provides real-time AI assistance when users write questions:

- **Quality Scoring (0-100)**: Evaluates clarity, specificity, and relevance
  - 🟢 Green (80+): Excellent question
  - 🟡 Yellow (60-79): Good but could improve
  - 🔴 Red (<60): Needs significant improvement

- **Automatic Categorization**:
  - Primary categories: Housing, Public Safety, Education, Infrastructure, Budget, Environment, Transportation, Health, Economy, Governance
  - Subcategories for more specific topics

- **Duplicate Detection**:
  - Uses semantic similarity to find existing similar questions
  - Prevents redundant submissions
  - Shows matched question if duplicate found

- **AI Suggestions**:
  - Lists specific issues with the question
  - Provides actionable improvement suggestions
  - Offers one-click improved version for low-quality questions

- **Suggested Questions**:
  - AI-generated starter questions specific to each contest
  - Based on city and contest context
  - Helps users get started

### 2. Question Analysis API

**Endpoint**: `POST /api/v1/llm/analyze-question`

```json
{
  "question_text": "What is your plan for housing?",
  "contest_id": 123
}
```

**Response**:
```json
{
  "analysis": {
    "quality_score": 65,
    "is_appropriate": true,
    "category": "Housing",
    "subcategory": "Affordable Housing",
    "issues": ["Too broad", "Lacks specificity"],
    "suggestions": [
      "Specify which aspect of housing (affordability, development, zoning)",
      "Add context about current challenges"
    ],
    "improved_version": "What specific policies will you implement to increase affordable housing units in our city over the next 4 years?"
  },
  "success": true
}
```

### 3. Duplicate Detection API

**Endpoint**: `POST /api/v1/llm/check-duplicate`

```json
{
  "question_text": "How will you address homelessness?",
  "contest_id": 123
}
```

**Response**:
```json
{
  "is_duplicate": true,
  "similarity_score": 0.92,
  "matched_question_id": 456,
  "explanation": "This question is nearly identical to question #456 which asks about homeless response strategies.",
  "success": true
}
```

### 4. Suggested Questions API

**Endpoint**: `GET /api/v1/llm/suggested-questions/{contest_id}?num_suggestions=5`

**Response**:
```json
{
  "questions": [
    "What is your plan to reduce traffic congestion on Main Street?",
    "How will you balance the city budget while maintaining essential services?",
    "What strategies will you use to improve public safety without over-policing?",
    "How do you plan to attract new businesses to our downtown area?",
    "What is your position on the proposed Green Park development?"
  ],
  "success": true
}
```

### 5. Answer Analysis (Coming Soon)

Will analyze candidate video answers to extract:
- Key points made
- Overall stance (for/against/neutral/complex)
- Specificity score
- Factual claims
- Potential issues
- Summary

## Setup

### Environment Variables

Add to `backend/.env`:

```bash
# LLM / AI Features
ANTHROPIC_API_KEY=sk-ant-api03-...
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ENABLE_AI_FEATURES=true
```

### Install Dependencies

```bash
cd backend
pip install anthropic==0.48.0
```

### Usage in Code

```python
from app.services.llm_service import get_llm_service

# Analyze a question
llm = get_llm_service()
analysis = llm.analyze_question(
    question_text="What is your housing plan?",
    contest_type="race",
    contest_title="City Council District 3",
    city_name="San Francisco"
)

print(f"Quality: {analysis.quality_score}/100")
print(f"Category: {analysis.category}")
```

## How It Works

1. **Real-time Analysis**: Questions are analyzed as users type (1.5 second debounce)
2. **Context-Aware**: Uses contest details (type, title, city) for relevant analysis
3. **Graceful Degradation**: If AI is disabled or fails, returns sensible defaults
4. **User Privacy**: Question text is sent to Claude API but not stored permanently
5. **Cost Control**: Debouncing and caching minimize API calls

## Benefits

### For Voters
- Write better, clearer questions
- Avoid duplicates
- Get inspired by AI-generated questions
- Understand if their question is appropriate

### For Candidates
- Receive higher-quality, well-formed questions
- Less confusion from vague or duplicate questions
- Better organized questions by category

### For Platform
- Improved content quality
- Reduced moderation burden
- Better user experience
- More structured data for analysis

## Limitations

- Requires valid Anthropic API key
- API calls have cost ($0.003/1k input tokens, $0.015/1k output tokens for Sonnet 4.5)
- Analysis is not perfect - human review still needed
- Rate limits apply (set in environment variables)

## Future Enhancements

- [ ] Batch analysis for efficiency
- [ ] Caching similar questions to reduce API calls
- [ ] Answer analysis implementation
- [ ] Fact-checking integration
- [ ] Multi-language support
- [ ] Custom fine-tuned models for local politics
- [ ] Question trending and topic clustering
- [ ] Automated moderation suggestions

## Cost Estimation

Assuming:
- Average question: 50 tokens input + 200 tokens output
- Analysis cost per question: ~$0.003
- 1,000 questions analyzed/month: ~$3/month
- Very affordable for most use cases

## Attribution

All AI-powered features include "AI-powered by Claude" attribution per Anthropic's usage guidelines.
