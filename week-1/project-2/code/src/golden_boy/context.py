import contextvars

# Holds the current conversation thread_id for the running agent call
current_thread_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_thread_id", default="unknown"
)
