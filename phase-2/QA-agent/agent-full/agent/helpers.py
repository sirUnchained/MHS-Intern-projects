# Safe call for structured output
def safe_structured_invoke(structured_llm, messages, fallback, retries=1):
    """
    This function will call structured llm and if it fails the program will not crash.
    You'll see just a warning.
    """
    for attempt in range(retries + 1):
        try:
            return structured_llm.invoke(messages)
        except Exception as e:
            if attempt == retries:
                print(f"[WARNING] structured_output failed, using fallback: {e}")
                return fallback
