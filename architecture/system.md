# System Architecture: Real-Time Exception Resolution Workbench

## Overview
The **Exception Resolution Workbench** is a high-performance modular monolith built for AP/Procurement operations. It marries **deterministic exception detection** (for zero-hallucination mathematical verification) with **evidence-grounded AI employees** and a strict **human-in-command governance loop**.

```mermaid
flowchart TB
    subgraph Client ["Frontend Client (HTML5 / Tailwind CSS / Vanilla JS)"]
        UI_Queue["Live Exception Queue\n(Status / Severity / Type)"]
        UI_Detail["Evidence Inspection\n(Expected vs Actual, Discrepancies)"]
        UI_AI["AI Employee Console\n(Explain, Suggest, Confidence Gauge)"]
        UI_Human["Human Governance Modal\n(Approve, Reject, Escalate)"]
    end

    subgraph API ["FastAPI Modular Monolith (Backend)"]
        R_Exc["/api/exceptions\n(Query & Filters)"]
        R_Res["/api/exceptions/{id}/resolve\n(Auto / Human Review)"]
        R_AI["/api/exceptions/{id}/explain & suggest"]
        R_Audit["/api/exceptions/{id}/audit\n(Chronological Timeline)"]
    end

    subgraph Services ["Core Business Logic & Reasoning"]
        Engine["Deterministic Exception Engine\n(Math, Tolerance, Severities)"]
        Confidence["Composite Confidence Engine\n(30% Ev, 30% Rule, 20% Class, 20% AI)"]
        Safety["Deterministic Safety Gates\n(Completeness, Non-Null, Type Validity)"]
        AI_Svc["AI Employee Service"]
    end

    subgraph LLM_Tier ["Dual LLM Provider & Resilience"]
        Groq["Primary: Groq llama-3.3-70b-versatile\n(<1s Latency)"]
        NVIDIA["Failover: NVIDIA NIM nemotron-3.5-30b"]
        Offline["Offline: Grounded Deterministic Fallback"]
    end

    subgraph Storage ["Persistence Layer (SQLite + WAL)"]
        DB[(app.db)]
    end

    UI_Queue --> R_Exc
    UI_Detail --> R_Exc
    UI_AI --> R_AI
    UI_Human --> R_Res

    R_Exc --> Engine --> Storage
    R_Res --> Confidence --> Safety --> Storage
    R_AI --> AI_Svc --> Groq
    Groq -. Failover / Rate Limit .-> NVIDIA
    NVIDIA -. Failover .-> Offline
    R_Audit --> Storage
```

## Key Architectural Decisions

1. **Deterministic-First Discrepancy Math**: Discrepancies (e.g. 25% price variance, short shipment of 80 units, 17 days past due) are calculated with 100% determinism.
2. **Dual-Tier Resilient AI Pipeline**: Groq (`llama-3.3-70b-versatile`) delivers sub-second inference. If rate limits (HTTP 429) or connection issues occur, requests transparently fail over to NVIDIA NIM (`nemotron-3.5-lightning-30b-a3b`), and finally to offline deterministic rule synthesis.
3. **Composite Confidence Scoring Formula**:
   $$	ext{Confidence} = 0.30 	imes 	ext{evidence\_score} + 0.30 	imes 	ext{rule\_certainty} + 0.20 	imes 	ext{classification\_score} + 0.20 	imes 	ext{ai\_score}$$
4. **Deterministic Safety Gates**:
   - Evidence completeness score $\ge 0.70$
   - All mandatory fields non-null
   - Resolvable exception type
5. **Human-in-Command Autonomous Thresholds**:
   - $\ge 0.90 ightarrow 	ext{AUTO\_RESOLVE}$
   - $0.70 	ext{--} 0.89 ightarrow 	ext{PENDING\_HUMAN}$ (Human Review Gate)
   - $< 0.70 ightarrow 	ext{ESCALATE}$
