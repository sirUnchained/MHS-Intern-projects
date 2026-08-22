**QA‑Agent** was my fourth project during the MHS internship. The goal was to build an intelligent agent that understands user questions and either answers them directly or intelligently escalates to a human support team when necessary.

The project is organized into three components:

- **agent‑core** – The brain of the system. Developed entirely with LangGraph and LangChain, this folder contains the full conversational graph and tool orchestration, following the architecture below.

- **agent‑full** – A lightweight backend (built with FastAPI) wrapped around the core agent, paired with a simple, clean frontend that brings the agent to life for end users.

- **Presentation.ipynb** – A notebook that walks through the design and development process of the agent's core, originally created for a university presentation.

> *If you're looking for a deeper technical dive, the diagram below (the same one used in the main README) maps the exact decision flow that powers every conversation.*

```mermaid
flowchart RL
    USER_INPUT(User Input) --> QUESTION_CLASSIFIER{"Can the main agent answer?"}

    QUESTION_CLASSIFIER -->|No| DEPARTMENT_CLASSIFIER_AND_TICKET_DATA_EXTRACTOR[Department Classifier and extract data for ticket]
    DEPARTMENT_CLASSIFIER_AND_TICKET_DATA_EXTRACTOR --> CLASSIFIED_DEPARTMENT(Create Ticket for department)
    QUESTION_CLASSIFIER -->|Yes| AGENT["Agent"]

    subgraph Agent_pipeline [Agent pipeline]
        AGENT --> TOOLS["Other tools"]
        TOOLS --> |if tool limit is not reached| AGENT
        AGENT --> |if tool limit is reached| TOOLS_LIMIT
        TOOLS_LIMIT["no more tool use"] --> AGENT
    end

    AGENT --> VALIDATE_AGENT_RESPONSE{Is Agent Response Ok?}
    VALIDATE_AGENT_RESPONSE -->|No| DEPARTMENT_CLASSIFIER_AND_TICKET_DATA_EXTRACTOR
    VALIDATE_AGENT_RESPONSE -->|Yes| IS_DATA_WORTH_TO_SAVE 

    subgraph DATABASE_PIPELINE [database pipeline]
        IS_DATA_WORTH_TO_SAVE{"Extracting chat and check if it is worth to save?"} --> |Yes| SAVE_TO_DATABASE["Save data to database"]
    end

    SAVE_TO_DATABASE --> DONE_FROM_AGENT("done from agent")
    IS_DATA_WORTH_TO_SAVE --> |no| DONE_FROM_AGENT("done from agent")
```

This structure keeps the focus on the technical achievement while making the text welcoming and mistake‑free. You can place it in your README as a project overview, or use it wherever you need to introduce the work.
