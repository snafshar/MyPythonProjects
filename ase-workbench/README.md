# ASE Workflow Workbench

A Python/Tkinter desktop app for the recurring Advanced Software Engineering workflow. The color-coded pipeline uses the course terminology from **The product vision** and **System decomposition** through **Splitting the monolith**, **Security Analysis**, and **DevOps measurement**.

## Run

From this directory, with Python 3.12+ and Tkinter installed:

```sh
python3 -m tkinter
python3 workbench.py
```

Use a desktop Python installation with Tk support. On Linux, install your distribution's Tkinter package if needed. Use a new, trusted project folder outside this source directory. The workbench executes that folder's project tests, Dockerfiles, Compose configuration, and Python dependencies.

## Run a reference lab

1. Click **Open workspace** and select a folder. Use **Insert prompts** to record the vision, sprint goal, acceptance cases, boundaries, ownership and review evidence. Notes are saved in the workspace.
2. Click **Scaffold project**. It creates Flask services, OpenAPI, Dockerfiles and Compose files, pytest mocks, a Postman collection, a Locust workload, and a GitHub Actions workflow. Existing files are kept. Use a fresh folder for an unmodified reference scaffold.
3. Click **Install project tools** to install the Python project and test dependencies into its own `.venv`. Docker Engine with Compose v2, Node.js with Newman 6 on PATH, OpenSSL with `-addext` support, and Trivy are separate local prerequisites. For Newman, use `npm install --global newman@6`.
4. Click **Run baseline** for OpenAPI validation, the Compose build, a smoke check, isolated pytest checks, and Newman integration. Select any stage to run its checks individually. **Run full local pipeline** also attempts Locust, the HTTPS and JWT scenario, dependency and image scans, and Compose logs. An unavailable tool or failed check remains visible, with its log.
5. Record architecture and release decisions in **Stage notes and evidence**, then use **Mark reviewed**. Release review checks the recorded project fingerprint and reports incomplete checks. Use **Record candidate** on the release stage to save the local release manifest and evidence. Use **Export evidence** to save a separate Markdown report. **Stop stacks** stops the reference environments without removing database volumes.

### What runs

| Stage | Workbench action |
|---|---|
| Requirements and architecture | Saved prompts, decisions and review status |
| Flask and OpenAPI | Scaffold, contract validation, explicit query and response schemas |
| Docker and Compose | Build and run the API Gateway, calculator, string service, DB Manager and a MongoDB volume |
| Testing and CI | pytest with mock dependencies, Newman against the real gateway, and a generated GitHub Actions workflow with isolated jobs followed by integration |
| Load Test | Locust, five local simulated users for 15 seconds, and CSV results in `.ase-workbench/` |
| Data Security and Access Security | A local self-signed certificate with loopback hostname/IP verification, Compose file secrets, and live JWT checks for 401, 200 and 403 |
| Security Analysis | Bandit, pip-audit, and Trivy against the local gateway image |
| Continuous delivery and DevOps measurement | Local staging evidence, revision-aware review, logs and Markdown export |

The stack uses loopback ports **8500** for HTTP and **8501** for HTTPS. Docker project names are derived from the workspace path, while those two host ports are shared, so run one workspace at a time. The app uses a foreground desktop UI and runs commands on a background thread. Command output appears as each check finishes.

The generated login service uses two locally generated test identities and short-lived JWTs. It is a teaching implementation behind the HTTPS gateway. Internal service traffic and the MongoDB volume are local Compose resources. The full course alternatives, including mTLS, database encryption, Keycloak, Docker Scout, Dependabot, Kubernetes and cloud deployment, are concepts or tooling choices to apply separately in an actual release. Production deployment, user research, architecture approval and release approval require a target environment and human decisions.

The generated GitHub Actions workflow applies when the generated project itself is published as a repository. On push or pull request it runs pytest with isolated dependencies, then starts Compose and checks the public routes with Newman. The desktop app runs its local equivalent and records local evidence.

Run logs, project state and generated local secrets are excluded by the scaffold's `.gitignore`. Evidence exported elsewhere can contain your stage notes, so review any report before sharing it.
