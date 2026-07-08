# MSAI — QA Engineering Assignment

QA submission for the MSAI Online Event Registration Platform. Covers test strategy, test cases, root cause analysis, API testing, and a Selenium automation project.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.44-green.svg)
![pytest](https://img.shields.io/badge/pytest-9.0+-yellow.svg)
[![Python application](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/python-app.yml/badge.svg)](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/python-app.yml)
[![API Tests (Newman)](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/api-tests.yml/badge.svg)](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/api-tests.yml)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

---

## Quick Start

### Run Selenium Tests
```bash
cd automation/
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest
```

### Run API Tests (Newman)
```bash
npm install -g newman
cd api-testing/postman
node mock-server.js &
sleep 2
newman run collection.json -e environment.json
```

---

## What's Included

- **QA Strategy** — Risk-based strategy for launch day. Covers test types, feature priorities, and release criteria.
- **Test Cases** — 15 test cases across 5 modules with a 5-test critical path selection.
- **Root Cause Analysis** — How I'd investigate 3 production bug scenarios step by step.
- **API Testing** — Written approach for all 6 endpoints with positive, negative, and edge cases.
- **Automation** — Selenium POM framework in Python using pytest, runs in CI on Chrome and Firefox.
- **AI Usage** — What AI tools I used, how they helped, and how I verified their output.

---

## Repository Structure

| Part | Deliverable | Path |
|------|-------------|------|
| Part 1 — QA Strategy | Risk-based test strategy for first production launch | [qa-strategy/README.md](qa-strategy/README.md) |
| Part 2 — Test Case Design | 15 test cases across 5 modules with prioritization | [test-cases/README.md](test-cases/README.md) |
| Part 3 — Root Cause Analysis | How I'd investigate 3 production scenarios | [rca/README.md](rca/README.md) |
| Part 4 — API Testing Approach | Written approach for all 6 endpoints | [api-testing/api-testing-approach.md](api-testing/api-testing-approach.md) |
| Part 5 — Automation (Selenium + pytest) | Page Object Model framework with CI | [automation/README.md](automation/README.md) |
| Part 6 — AI Usage | AI tools, contributions, and validation | [ai-usage/README.md](ai-usage/README.md) |

### Folder Layout

```
ms-qa-assignment/
├── .github/workflows/
│   ├── python-app.yml           # Selenium CI
│   └── api-tests.yml            # Newman CI
├── qa-strategy/
│   └── README.md                # Part 1
├── test-cases/
│   └── README.md                # Part 2
├── rca/
│   └── README.md                # Part 3 + sample bug report
├── api-testing/
│   ├── api-testing-approach.md  # Part 4
│   └── postman/                 # Supporting: Postman + Newman suite
│       ├── collection.json
│       ├── environment.json
│       ├── mock-server.js
│       └── README.md
├── ai-usage/
│   └── README.md                # Part 6
├── automation/
│   ├── pages/
│   │   ├── base_page.py
│   │   ├── cart_page.py
│   │   ├── inventory_page.py
│   │   └── login_page.py
│   ├── tests/
│   │   └── test_saucedemo_workflow.py
│   ├── conftest.py
│   ├── pytest.ini
│   └── requirements.txt
└── README.md
```

---

## Tech Stack

| Tool | What I Used It For |
|------|--------------------|
| Python | Main automation language |
| Selenium WebDriver | Browser automation |
| pytest | Test runner |
| Selenium Manager (built-in) | Auto driver management |
| Postman + Newman | API testing |
| Node.js | Mock server for API tests |
| GitHub Actions | CI pipelines |

---

## CI Pipelines

Two GitHub Actions workflows run on push/PR to `main`:

1. **`python-app.yml`** — Installs Chrome/Firefox, runs Selenium tests in headless mode.
2. **`api-tests.yml`** — Starts mock server, runs Newman collection, uploads HTML report.

---

## Assumptions

- Payment is **simulated** — no real gateway. I tested flow correctness, not PCI compliance.
- Single deployment environment (staging -> prod). No blue-green or canary setup.
- No existing load testing infrastructure or performance baselines.
- Email service is third-party (SendGrid/SES). I can test send calls but not inbox delivery at scale.
- Web-only for launch. No native mobile apps.
- I'm the only QA engineer. Scope is bounded by what one person can do in the timeline.

---

## AI Tools Used

| Tool | Models | What I Used It For |
|------|--------|--------------------|
| [opencode](https://opencode.ai) | big-pickle (online) | Code generation, debugging, file ops, architecture suggestions |
| [ollama](https://ollama.ai) | gemma4-12b, qwen3.5 (local) | Code review, test case drafting, documentation review |

I used AI as a coding assistant — it helped with boilerplate, code structure suggestions, and reviewing drafts. But everything was manually reviewed, tested, and often rewritten. Nothing went in without being verified. Details in [ai-usage/README.md](ai-usage/README.md).

---

## Troubleshooting

**Selenium issues** — See [automation/README.md](automation/README.md).

**Newman connection refused** — Make sure mock server is running: `node mock-server.js` before running Newman.
