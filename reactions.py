
import json
import time
from google import genai
from google.genai import types

SYSTEM_INSTRUCTION = """You are simulating how a specific demographic/economic \
segment of a population might plausibly react to a proposed policy, for an \
exploratory "what if" tool. This is NOT a real prediction — it's a rough, \
directionally-sensible thought experiment.

Ground every reaction in defensible economic and social reasoning tied to \
the segment's employment status and income tier (e.g. how the policy affects \
their income, costs, job security, or daily life) rather than in stereotypes \
about ethnicity. Ethnicity should only matter insofar as it correlates with \
plausible economic circumstances or historically-grounded policy exposure — \
never invoke ethnic stereotypes about character, values, or behavior.

Make the reaction feel like a real, specific person, not a survey average:
- Take a real position. Real people are rarely at 50/50 — if this segment has \
clear, direct stakes in the policy (it changes their income, costs, or job \
security in an obvious direction), the support_pct should reflect real \
conviction (e.g. in the 10-30 or 70-90 range), not a cautious 45-55. Reserve \
scores near 50 for segments that genuinely have offsetting pros and cons, not \
as a default hedge.
- Get concrete. Reference specific numbers from the policy (a dollar figure, \
a percentage, a timeline) and tie them to what this segment's week-to-week \
budget or work actually looks like, instead of vague language like "this could \
impact my finances."
- Vary the voice segment to segment. Don't reuse the same sentence openers, \
structure, or stock phrases ("As a working-class...") across segments — write \
each rationale like a different person said it: some blunt and short, some \
detailed and hedged, some frustrated, some cautiously optimistic, some \
resigned. Avoid corporate-survey phrasing ("this policy may have implications \
for...").
- Let emotion show where it's warranted (relief, anger, skepticism, cautious \
hope) rather than defaulting to flat neutrality — but keep it earned by the \
economics, not performative.

Always respond with strict JSON matching this schema, and nothing else:
{
  "support_pct": <integer 0-100, how much this segment would support the policy>,
  "sentiment_score": <float -1.0 to 1.0, overall emotional reaction, negative to positive>,
  "quote": <string, one short first-person sentence (under 25 words) in this person's own voice — how they'd actually put it, not a summary>,
  "rationale": <string, 2-3 sentences explaining the reasoning, concrete and specific to this segment>,
  "key_benefits": [<string>, <string>],
  "key_concerns": [<string>, <string>]
}"""


def _build_prompt(segment_dict, policy_text):
    return f"""Policy being evaluated:
\"\"\"{policy_text}\"\"\"

Population segment reacting to this policy:
- Employment status: {segment_dict['employment_status']}
- Income tier: {segment_dict['income_tier']}
- Ethnicity: {segment_dict['ethnicity']}
- This segment represents approximately {segment_dict['count']} people \
({segment_dict['weight']*100:.1f}% of the simulated population).

Generate this segment's plausible reaction as JSON per the schema. Make it \
specific and decisive, not a hedge-everything average."""


def get_reaction(segment_dict, policy_text, api_key, model_name, max_retries=3):
    client = genai.Client(api_key=api_key)
    prompt = _build_prompt(segment_dict, policy_text)

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    temperature=1.05,
                ),
            )
            raw_text = (response.text or "").strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                if raw_text.lower().startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()

            data = json.loads(raw_text)

            data["support_pct"] = max(0, min(100, int(data.get("support_pct", 50))))
            data["sentiment_score"] = max(-1.0, min(1.0, float(data.get("sentiment_score", 0.0))))
            data.setdefault("quote", "")
            data.setdefault("rationale", "")
            data.setdefault("key_benefits", [])
            data.setdefault("key_concerns", [])
            return data
        except Exception as e: 
            last_error = e
            print(f"[reactions.py] segment {segment_dict.get('id')} attempt {attempt+1}/{max_retries} failed: {e!r}")
            time.sleep(1.0 * (attempt + 1))

    return {
        "support_pct": 50,
        "sentiment_score": 0.0,
        "quote": "",
        "rationale": f"⚠️ Reaction generation failed after {max_retries} attempts: {last_error}",
        "key_benefits": [],
        "key_concerns": [],
        "error": True,
        "error_message": str(last_error),
    }


def run_simulation(segments, policy_text, api_key, model_name, progress_callback=None):
    """
    segments: list of Segment.to_dict() dicts
    Returns a list of merged segment + reaction dicts.

    progress_callback(done, total, latest_merged_result) is called after
    each segment completes, so callers can render live updates.
    """
    results = []
    total = len(segments)
    for i, seg in enumerate(segments):
        reaction = get_reaction(seg, policy_text, api_key, model_name)
        merged = {**seg, **reaction}
        results.append(merged)
        if progress_callback:
            progress_callback(i + 1, total, merged)
    return results
