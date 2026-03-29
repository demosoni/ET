import os
from backend.services import get_weather, get_soil, get_market_data
from groq import Groq

client = Groq(api_key="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")

# ===== STRUCTURED MEMORY =====
farmer_memory = {
    "location": None,
    "crop": None,
    "history": []
}

# ================= MEMORY =================
def update_memory(q):
    if hasattr(q, "location") and q.location:
        farmer_memory["location"] = q.location

    if hasattr(q, "crop") and q.crop:
        farmer_memory["crop"] = q.crop

    farmer_memory["history"].append(q.query)
    farmer_memory["history"] = farmer_memory["history"][-6:]


# ================= FOLLOW-UP (LLM DRIVEN, NO HARDCODING) =================
def generate_followup(query, memory):
    prompt = f"""
You are an expert Indian agricultural assistant.

GOAL:
- Understand the farmer's intent
- Check if any IMPORTANT info is missing
- Ask ONLY ONE smart follow-up question IF needed
- If nothing missing → return EXACTLY: NO_FOLLOWUP

STRICT RULES:
- NEVER repeat a question already answered
- Use memory like a human
- Respond in SAME language as user
- Do NOT give advice here

MEMORY:
Location: {memory["location"]}
Crop: {memory["crop"]}
History: {memory["history"]}

CURRENT QUERY:
{query}

OUTPUT:
- One question OR NO_FOLLOWUP
"""

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content.strip()
    except:
        return "NO_FOLLOWUP"


# ================= MAIN AGENT =================
def run_agents(q):
    try:
        # update structured memory
        update_memory(q)

        # ===== STEP 1: FOLLOW-UP =====
        followup = generate_followup(q.query, farmer_memory)

        # Only ask follow-up if critical info missing
        if followup != "NO_FOLLOWUP":
            if not farmer_memory["location"] or not farmer_memory["crop"]:
                return followup

        # ===== STEP 2: DATA FETCH =====
        soil = get_soil(q.location)
        weather = get_weather(q.location)
        market = get_market_data()

        # ===== STEP 3: CORE REASONING =====
        prompt = f"""
You are a real Indian agricultural expert speaking to a farmer.

CRITICAL BEHAVIOR:
- Talk like a human, not a bot
- DO NOT repeat questions already answered
- Use memory properly
- Continue conversation naturally

LANGUAGE:
- Detect language of user
- Respond STRICTLY in same language
- If Hinglish → reply in Hinglish

MEMORY:
Location: {farmer_memory["location"]}
Crop: {farmer_memory["crop"]}
Past Conversation: {farmer_memory["history"]}

LIVE DATA:
Soil: {soil}
Weather: {weather}
Market: {market}

USER QUERY:
{q.query}

TASK:
1. Understand exact farmer need
2. If enough info → give clear advice
3. If still something missing → ask ONLY one NEW question

RESPONSE STYLE:
- Conversational (like real expert)
- Practical field advice
- No rigid formatting

CONTENT MUST INCLUDE (naturally):
- What to do (decision)
- Why (reason)
- Fertilizer (if relevant)
- Risk (pest/weather)
- Improvement idea
- Govt schemes (if useful)
- Confidence (low/medium/high)

IMPORTANT:
- Do NOT sound like template
- Do NOT repeat same question
- Do NOT ignore memory
"""

        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        return res.choices[0].message.content

    except Exception:
        try:
            fallback_prompt = f"""
The system faced an issue.

User query: {q.query}

Respond:
- Politely
- In SAME language
- Ask user to retry
- Keep it simple
"""
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": fallback_prompt}]
            )
            return res.choices[0].message.content
        except:
            return "⚠️ Please try again."