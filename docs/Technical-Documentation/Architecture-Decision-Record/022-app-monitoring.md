# 22. Monitoring Application Health and Performance

Date: 2024-09-30

## Status

Pending

## Context
Historic feedback highlighted an ongoing desire for improved alerting and monitoring mechanisms, particularly originating in issue [#831](https://github.com/raft-tech/TANF-app/issues/831). Currently, our cloud platform has limited monitoring features leading to a  "blindness" to errors and stack traces that have occurred, ultimately impairing our ability to maintain system stability; additionally, the existing dashboards only offer live performance data lacking data over time or any archives. Without context for either performance or system logging, determination of anomalous or suboptimal system behavior is not possible.

Additionally, we have experienced critical blocking issues related to our updates to both Elasticsearch (ES) and PostgreSQL, which have compounded the need for more proactive alerting and load-testing in lower environments. Without timely notifications, we risk delays in addressing failures that could escalate into more significant problems. 


## Decision
Implementing a comprehensive monitoring and alerting ecosystem will not only help in identifying errors in real-time but also enable us to establish benchmarks based on historical data. This approach will foster a more proactive response strategy, ensuring that potential issues are mitigated before they impact our users or that system owners are aware of issues that have impacted users.

We will build out a suite of tools in accordance with industry best practices to monitor our applications including:
- Prometheus
- Loki
- Grafana
- Promtail
- Sentry

Grafana shall provide a visualization dashboard for these various tools which will collect and aggregate performance metrics, system logs, and deeper analysis for all aspects of our systems: frontend, proxies, backend, databases, and even networking. Additionally, the development team will seek to hone a proactive alerting system for out-of-threshold issues and errors for improved visibility of system issues.

## Consequences

Increased platform costs for running these tools
Time and effort maintaining and configuring these new systems
"Noisy" notifications from from out-of-tune alerting
Efforts made towards security compliance as these systems have intimate access to our systems and data
Learning curve for technical staff

## Notes
Given the prohibitive costs of self-hosting Sentry in Cloud.gov, we plan on usage of Sentry's Cloud SaaS offering which will alter the boundary diagram. The other tools in use (PLG stack and associated), will be self-hosted and maintained by the technical staff both at Raft and OFA.