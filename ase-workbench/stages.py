"""Slide-aligned workflow metadata for the desktop workbench."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    title: str
    color: str
    tools: str
    action: str
    output: str
    checks: tuple[str, ...] = ()


STAGES = {
    "vision": Stage("The product vision", "#2563eb", "Theory 2 · Personas, scenarios, prototypes, roadmap",
                   "Identify a user, their problem, the value of solving it, and how to validate it.",
                   "Product vision, scenario and prototype feedback"),
    "stories": Stage("Features, Scenarios, and Stories · Sprint planning", "#2563eb",
                     "Theory 3–4 · Scrum, product backlog, sprint backlog; Lab 4 · User stories",
                     "Split and prioritize stories. Record dependencies, a sprint goal and observable acceptance criteria.",
                     "Prioritized stories and a sprint plan"),
    "architecture": Stage("System decomposition", "#7c3aed",
                          "Theory 5, 7, 9 · Bounded contexts, Structure 101, SchemaSpy, Hibernate",
                          "Assign service and data ownership. Choose boundaries, communication and failure behavior.",
                          "Component responsibilities, dependency list and data ownership"),
    "service": Stage("Coding with AI · Flask", "#0891b2",
                      "Labs 1–3 · Python, venv, pip, Flask, Git; VS Code, Roo Code and GitHub Copilot are examples",
                      "Scaffold the reference service, then implement project rules in Python. Record any AI assistance.",
                      "Flask services and requirements.txt"),
    "contract": Stage("REST and OpenAPI", "#0891b2",
                       "Lab 5 · OpenAPI, Swagger Editor; Swagger Hub and Flask-RESTX are examples",
                       "Review paths, query parameters, response schemas, status codes and security requirements.",
                       "openapi.json and its validation result", ("contract",)),
    "docker": Stage("Docker · Docker Volumes", "#c2410c",
                     "Theory 6; Lab 6 · Docker Engine, Dockerfile, image tags and named volumes",
                     "Validate the Compose model, then build the images used by the services.",
                     "Validated configuration and locally built images", ("compose_config", "docker_build")),
    "split": Stage("Splitting the monolith · Microservices and Docker Compose", "#7c3aed",
                    "Theory 9; Lab 7 · Flask, requests, Docker Compose, MongoDB; Redis is the lab bonus",
                    "Extract calc and string, establish the API Gateway and DB Manager, then wire the HTTP and storage paths.",
                    "Running local stack and a verified gateway route", ("compose_up", "smoke")),
    "smells": Stage("Architectural smells and refactoring", "#7c3aed",
                     "Theory 8; Lab 7 · MicroFreshener, API Gateway, DB Manager, timeouts",
                     "Review No API Gateway, Shared Persistence, Wobbly Service Interaction and Endpoint-based Service Interaction.",
                     "Architecture review and refactoring decisions"),
    "tests": Stage("Test in isolation · Integration test", "#15803d",
                   "Theory 10; Lab 8 · pytest, mocks, Postman, Docker Compose",
                   "Run isolated Python tests, then verify real requests through the gateway with the Postman collection.",
                   "Unit and integration results", ("unit", "newman")),
    "load": Stage("Load Test", "#15803d", "Lab 8 · Locust, HttpUser, locustfile.py",
                  "Run the bounded loopback workload. Compare failures, throughput and latency after each change.",
                  "Locust CSV metrics", ("load",)),
    "ci": Stage("DevOps with GitHub Actions", "#4338ca",
                "Theory 12; Lab 9 · GitHub Actions, Node.js, Newman, Docker Compose",
                "Generate a workflow for the project repository. Rehearse the same unit and integration checks locally.",
                "Workflow YAML and local rehearsal results", ("unit", "newman")),
    "data": Stage("Data Security", "#be123c",
                  "Theory 13-I; Lab 10 · OpenSSL, HTTPS, Compose secrets, input sanitization",
                  "Create development-only HTTPS material, start the secure profile, and check certificate trust.",
                  "Local HTTPS configuration and trust evidence", ("cert", "secure_up", "tls")),
    "analysis": Stage("Security Analysis", "#be123c",
                      "Lab 11 · Bandit, pip-audit, Trivy; Docker Scout and Dependabot are also covered",
                      "Scan Python source, dependencies and local images. Review findings, fix the owning layer, and rerun checks.",
                      "Source, dependency and image scan results", ("bandit", "audit", "trivy")),
    "access": Stage("Access Security", "#be123c",
                    "Theory 13-II; Lab 12 · OAuth 2.0, JWT, PyJWT, Keycloak, Postman",
                    "Check the lab JWT profile with missing, invalid, authorized and insufficient-scope requests.",
                    "Authorization evidence from the local gateway", ("access",)),
    "delivery": Stage("Continuous delivery and deployment", "#a16207",
                      "Theory 11–12 · GitHub Actions, Kubernetes, Puppet, Chef and Ansible",
                      "Review acceptance and security evidence. Record the release and rollback decision for a specific revision.",
                      "Release review and versioned evidence report"),
    "measure": Stage("DevOps measurement", "#a16207",
                     "Theory 12–13 · Compose logs locally; CloudWatch, New Relic, Prometheus, Grafana, Jaeger and Zipkin in theory",
                     "Collect logs and link observations to a defect, a design change or the next backlog item.",
                     "Runtime evidence and next-iteration notes", ("logs",)),
}

NOTE_TEMPLATES = {
    "vision": ("Persona", "Current problem", "User outcome", "Prototype or feedback evidence"),
    "stories": ("Sprint goal", "As a ... I want ... so that ...", "Priority and dependencies",
                "Given ... when ... then ...", "Failure and boundary examples"),
    "architecture": ("Bounded contexts", "Service responsibilities", "Data ownership",
                     "Dependencies and timeouts", "Alternatives and trade-offs"),
    "smells": ("Observed smell", "Affected property", "Refactoring selected", "Verification evidence"),
    "delivery": ("Release version or Git SHA", "Staging and acceptance evidence", "Release decision",
                 "Rollback trigger", "Rollback procedure and data compatibility"),
    "measure": ("Observed metric or incident", "Operating conditions", "Likely owning service",
                "Backlog item or follow-up test"),
}
