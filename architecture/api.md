# API Reference & Endpoints

## REST API Summary

| Method | Endpoint | Description | Auth / Role |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/exceptions` | List exceptions with status, severity, and type filters | Operations Reviewer |
| `GET` | `/api/exceptions/{id}` | Get full exception detail with structured evidence & latest resolution | Operations Reviewer |
| `POST` | `/api/exceptions/{id}/explain` | Request AI root-cause explanation grounded in verified evidence | AI Employee |
| `POST` | `/api/exceptions/{id}/suggest` | Request AI resolution recommendation & composite confidence breakdown | AI Employee |
| `POST` | `/api/exceptions/{id}/resolve` | Trigger autonomous resolution policy (subject to safety gates & $\ge 0.90$) | Operations Lead / System |
| `POST` | `/api/exceptions/{id}/review` | Submit human reviewer authoritative decision (`APPROVE`, `REJECT`, `ESCALATE`) | Human Reviewer |
| `GET` | `/api/exceptions/{id}/audit` | Retrieve complete chronological immutable audit trail | Compliance / Operations |
| `POST` | `/api/seed/reset` | Reset mock database back to initial 12 seed exceptions | Demo / Testing |
