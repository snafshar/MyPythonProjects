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
2. Click **Scaffold project** and choose the HTTP and HTTPS ports. The scaffold creates Flask services, OpenAPI, Docker and Compose files, pytest mocks, a Postman collection, a Locust workload and a GitHub Actions workflow. Repeating this action fills in missing files and keeps existing ones.
3. Click **Install project tools** to prepare the project's `.venv`, then **Check tools** to see which checks your machine can run. The full profile uses Docker Engine with Compose v2, Node.js with Newman 6 on PATH, OpenSSL with `req -addext` support, and Trivy. For Newman, use `npm install --global newman@6`.
4. Choose a profile below or run a stage's own checks. Tool output streams to **Run log**. **Cancel run** stops the active tool and records its partial log. Use **History** to open previous results, durations and evidence files. **Stop stacks** stops both Compose profiles and keeps the database volumes.
5. Record architecture and release decisions in **Stage notes and evidence**, then click **Mark reviewed**. **Record candidate** on the release stage saves the local release manifest and evidence once the checks and prerequisite reviews pass for the current project revision. **Export evidence** saves a separate Markdown report.

| Profile | Checks |
|---|---|
| **Quick checks** | OpenAPI validation, isolated pytest tests, and Bandit. Runs with the project Python environment. |
| **Run baseline** | OpenAPI, pytest, Compose configuration and image build, local gateway startup and smoke check, then the Newman collection. |
| **Run full pipeline** | Baseline, Locust, HTTPS and JWT checks, Bandit, pip-audit, Trivy, and Compose logs. |

If an earlier check in the selected run fails, checks that depend on it are recorded as **Blocked**. Independent checks still run. For example, a Docker startup failure blocks the gateway smoke test, while the Python source and dependency scans can still run.

### What runs

| Stage | Workbench action |
|---|---|
| Requirements and architecture | Saved prompts, decisions and review status |
| Flask and OpenAPI | Scaffold, contract validation, explicit query and response schemas |
| Docker and Compose | Build and run the API Gateway, calculator, string service, DB Manager and a MongoDB volume |
| Testing and CI | pytest with mock dependencies, Newman against the real gateway, and a generated GitHub Actions workflow with isolated jobs followed by integration |
| Load Test | Locust, five local simulated users for 15 seconds, per-run CSV results, and request count, throughput, median and p95 response time in the log |
| Data Security and Access Security | A local self-signed certificate with loopback hostname/IP verification, Compose file secrets, and live JWT checks for 401, 200 and 403 |
| Security Analysis | Bandit, pip-audit, and Trivy against the local gateway image |
| Continuous delivery and DevOps measurement | Local staging evidence, revision-aware review, logs and Markdown export |

The defaults are **8500** for HTTP and **8501** for HTTPS. Choose different pairs to run multiple workspaces. The workbench reads the gateway's loopback mapping from `compose.json` and `compose.secure.json`, including for projects created with the earlier workbench. If you change an existing mapping, update the OpenAPI server URL and Postman collection variable for clients that run outside the workbench. A single workspace accepts one active check run at a time.

Existing notes and logs are retained. Earlier evidence can show **Stale** after the upgrade because the project fingerprint now covers nested source files, tests, and configuration. Rerun the checks for the current revision.

The generated login service uses two locally generated test identities and short-lived JWTs. It is a teaching implementation behind the HTTPS gateway. Internal service traffic and the MongoDB volume are local Compose resources. The full course alternatives, including mTLS, database encryption, Keycloak, Docker Scout, Dependabot, Kubernetes and cloud deployment, are concepts or tooling choices to apply separately in an actual release. Production deployment, user research, architecture approval and release approval require a target environment and human decisions.

The generated GitHub Actions workflow applies when the generated project itself is published as a repository. On push or pull request it runs pytest with isolated dependencies, then starts Compose and checks the public routes with Newman. The desktop app runs its local equivalent and records local evidence.

Run logs, project state and generated local secrets are excluded by the scaffold's `.gitignore`. Evidence exported elsewhere can contain your stage notes, so review any report before sharing it.

## Terminal and CI use

Run the same workspaces and checks without a graphical display.

```sh
python3 cli.py --workspace ~/ase-lab scaffold --http-port 8510 --https-port 8511
python3 cli.py --workspace ~/ase-lab install
python3 cli.py --workspace ~/ase-lab doctor
python3 cli.py --workspace ~/ase-lab run quick
python3 cli.py --workspace ~/ase-lab run baseline
python3 cli.py --workspace ~/ase-lab status
python3 cli.py --workspace ~/ase-lab report ~/ase-evidence.md
python3 cli.py --workspace ~/ase-lab stop
```

Use `run full` for the full profile and `check <name>` for an individual check. `python3 cli.py check --help` lists the check names. A check run exits with `0` when all selected checks pass, `1` when a check fails or is blocked, and `130` on cancellation. `doctor` exits with `1` when a check for the full profile reports a missing prerequisite, so quick checks can still work when Docker is unavailable.

Run the workbench regression tests from this directory with `python3 -m unittest discover -s tests -v`.

Use `note <stage> <file>` to save notes from a UTF-8 file and `review <stage>` to apply the same review checks as the GUI. For example:

```sh
python3 cli.py --workspace ~/ase-lab note vision ./product-vision.md
python3 cli.py --workspace ~/ase-lab review vision
python3 cli.py --workspace ~/ase-lab history
```

Once the delivery stage passes review, `candidate` records the local release manifest and evidence. Run `review --help` for the stage identifiers.

### Inspect the workflow and evidence

| Command | Result |
|---|---|
| `stages` / `checks` | List valid stage and check identifiers. |
| `stage tests` | Show the stage's tools, activity, expected output and checks. |
| `plan baseline` | Preview the checks and their ordering dependencies. |
| `prompts vision` / `show-note vision` | Print a Markdown template or read a saved note. |
| `log unit` | Read the latest unit check log. |
| `history --check unit --limit 5 --json` | Export the latest five matching entries as JSON. |
| `status --json` | Export stage status keyed by identifier. |
| `readiness` | List outstanding release requirements. Exits with 1 while any remain. |
