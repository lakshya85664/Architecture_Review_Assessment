# Topic 17 — Existing AI Agent Architecture

## Evidence-Based Architecture Diagram

```mermaid
flowchart TD

    User[User / Goal Input]

    Brain[Brain<br/>Decision Processing]
    State[Agent State<br/>goal / plan / observations / status / step_count]
    Loop[Control Loop<br/>Observe → Decide → Act → State Update]

    Planner[Planner<br/>Structured Plan]
    Executor[Executor<br/>Validated Execution]
    Tools[Tools / Actions Registry]

    Communication[Communication Layer<br/>Message / Routing / ACK / Dead Letter]
    Persistence[Persistence Boundary<br/>Operational Traces / JSON Evidence]

    Memory[Long-Term Memory<br/>NOT EVIDENCED]
    Deployment[Deployment Boundary<br/>Local Python Execution]

    User --> Brain
    Brain <--> State
    Brain --> Loop

    Loop --> Planner
    Planner --> Executor
    Executor --> Tools

    Executor <--> Communication
    Brain --> Persistence
    Executor --> Persistence
    Communication --> Persistence

    Memory -.-> Brain
    Memory -.-> Planner

    Deployment --- Brain
    Deployment --- Planner
    Deployment --- Executor
    Deployment --- Communication