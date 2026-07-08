# MSAI — QA Engineering Assignment

A complete QA engineering submission for the MSAI Online Event Registration Platform, covering strategy, test design, root cause analysis, API testing, and end-to-end automation.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.44-green.svg)
![pytest](https://img.shields.io/badge/pytest-9.0+-yellow.svg)
[![Python application](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/python-app.yml/badge.svg)](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/python-app.yml)
[![API Tests (Newman)](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/api-tests.yml/badge.svg)](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/api-tests.yml)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

---

## Quick Start

### 1. Run Selenium Tests
```bash
cd automation/
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest
```

### 2. Run API Tests (Newman)
```bash
npm install -g newman
cd api-testing/postman
node mock-server.js &
sleep 2
newman run collection.json -e environment.json
```

---

## What's Included

The repository contains the following core components:

* **QA Strategy**: A detailed risk-based strategy for launch day, specifying test types, prioritized features, and launch criteria.
* **Test Case Design**: 15 structured test cases covering five event modules, with a 5-test critical path selection.
* **Root Cause Analysis (RCA)**: Step-by-step diagnostic procedures for three production bug scenarios, including logs and systems to inspect.
* **API Testing**: A comprehensive written approach covering validation logic and positive/negative test cases for six API endpoints.
* **Automation Suite**: A Selenium POM framework written in Python with pytest, running in continuous integration across Chrome and Firefox.
* **Postman Collection**: A runnable 21-request suite testing contract validation and data chaining against an local Node.js mock server.

---

## Repository Structure

| Part | Deliverable | Path |
|------|-------------|------|
| Part 1 — QA Strategy | Risk-based test strategy for a first production launch | [qa-strategy/README.md](qa-strategy/README.md) |
| Part 2 — Test Case Design | 15 structured test cases across 5 modules with prioritization | [test-cases/README.md](test-cases/README.md) |
| Part 3 — Root Cause Analysis | Investigation approach for 3 production scenarios | [rca/README.md](rca/README.md) |
| Part 4 — API Testing Approach | Written approach for all 6 endpoints | [api-testing/api-testing-approach.md](api-testing/api-testing-approach.md) |
| Part 5 — Automation (Selenium + pytest) | Page Object Model framework with CI | [automation/README.md](automation/README.md) |
| Bonus — Postman Collection + Newman CI | 21-request API test suite with mock server | [api-testing/postman/README.md](api-testing/postman/README.md) |

### Detailed Folder Structure

```
ms-qa-assignment/
├── .github/workflows/
│   ├── python-app.yml           # Selenium automation CI
│   └── api-tests.yml            # Newman API tests CI
├── qa-strategy/
│   └── README.md                # Part 1 — QA Strategy
├── test-cases/
│   └── README.md                # Part 2 — Test Case Design
├── rca/
│   └── README.md                # Part 3 — Root Cause Analysis
├── api-testing/
│   ├── api-testing-approach.md  # Part 4 — API Testing Approach (written)
│   └── postman/                 # Bonus — Postman/Newman suite
│       ├── collection.json      # 21-request Postman collection
│       ├── environment.json     # Environment variables
│       ├── mock-server.js       # Standalone Node.js mock server
│       └── README.md            # Postman suite documentation
├── automation/
│   ├── pages/                   # Page Object classes
│   │   ├── base_page.py         # Core element interactions & explicit waits
│   │   ├── cart_page.py         # Cart page actions
│   │   ├── inventory_page.py    # Products listing page actions
│   │   └── login_page.py        # Login page actions
│   ├── tests/                   # Test files
│   │   └── test_saucedemo_workflow.py
│   ├── conftest.py              # Pytest fixtures and browser setup
│   ├── pytest.ini               # Pytest configuration
│   └── requirements.txt         # Python dependencies (pinned)
└── README.md                    # This file
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Selenium WebDriver | Browser automation and interaction |
| pytest | Test runner and assertion framework |
| Selenium Manager (built-in) | Automatic browser driver management |
| Postman + Newman | API test design and CLI execution |
| Node.js | Local mock server execution |
| GitHub Actions | Continuous Integration pipelines |

---

## CI Pipelines

Two independent GitHub Actions workflows run on push/PR to `main`:

1. **`python-app.yml`** — Selenium automation: installs Chrome/Firefox, installs dependencies, and runs `pytest` in headless mode.
2. **`api-tests.yml`** — API tests: installs Newman, starts the mock server, runs the collection, and uploads the HTML report as an artifact.

---

## Assumptions

* **Payment is simulated**: No real payment gateway integration is tested.
* **Endpoints are undocumented**: API contracts for endpoints (except login) were inferred from application behavior.
* **Single deployment environment**: No canary or blue-green infrastructure assumed.
* **Web-only platform**: Native mobile app support is out of scope for launch.
* **Sole QA engineer**: Bounded by single-engineer throughput.

---

## AI Tools Used

| Tool | Models | Usage |
|------|--------|-------|
| [opencode](https://opencode.ai) / Antigravity | big-pickle (online) | Code generation, debugging, architecture suggestions, file operations |
| [ollama](https://ollama.ai) (offline/local) | `batiai/gemma4-12b:q3`, `qwen3.5:latest` | Local code review, test case generation, documentation drafting |

### AI Workflow

* **Orchestration**: The `opencode` terminal-based agent orchestrated the directory management, file creation, and execution of test commands.
* **Online Assistance**: The `big-pickle` model handled online queries and verified standard Selenium syntax patterns.
* **Local Refinement**: Local `Ollama` models were used for code reviews, drafting initial documentation outlines, and validating test coverages to keep code development secure and isolated.
* **Manual Verification**: All outputs, suggestions, and scripts generated by AI tools were manually reviewed, revised, and validated by running the test suite locally.

### Example: Rejecting an AI-Generated Click Strategy

During development of the SauceDemo automation, an AI model suggested using Selenium's standard `.click()` method for the burger menu and logout link. Initial tests passed locally but failed intermittently in CI with `ElementClickInterceptedException` — React was collapsing the sidebar menu before the click registered.

Instead of accepting the suggestion as-is, I:

1. **Investigated the root cause**: A classic React re-render race — the click target was being replaced in the DOM between WebDriver locating it and executing the click.
2. **Iterated on a fix**:
   - `.click()` with `WebDriverWait` — still flaky
   - `.click()` wrapped in try/except with retries — improved but not reliable
   - Final solution: `JavaScript click()` via `executeScript` inside a `click_until_visible` retry loop — stable across all CI runs
3. **Generalized the pattern**: Added `js_click()` and `click_until_*` retry methods to `BasePage`, making the hybrid JS-click pattern reusable across all page objects.

The AI's original suggestion was correct for simple static pages, but I rejected it because it didn't account for React's asynchronous DOM replacement. The evidence of this iteration is visible in the `test_debug*.py` scripts in the `debug-scripts/` directory, which trace the progression from standard click to JS click.

---

## Troubleshooting

### 1. Automation Framework Issues
Please refer to the troubleshooting section in [automation/README.md](automation/README.md).

### 2. Newman Mock Server Connection Refused
* **Issue:** `connect ECONNREFUSED 127.0.0.1:3000` when running Newman.
* **Solution:** Verify that the mock server is running before executing Newman (`node mock-server.js`).
