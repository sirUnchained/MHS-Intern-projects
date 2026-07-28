# Safe call for structured output
def safe_structured_invoke(structured_llm, messages, fallback, retries=1):
    for attempt in range(retries + 1):
        try:
            return structured_llm.invoke(messages)
        except Exception as e:
            if attempt == retries:
                print(f"[WARNING] structured_output failed, using fallback: {e}")
                return fallback
