# MSAI — QA Engineering Assignment

A complete QA engineering submission for the MSAI Online Event Registration Platform, covering strategy, test design, root cause analysis, API testing, and end-to-end automation.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.44-green.svg)
![pytest](https://img.shields.io/badge/pytest-9.0+-yellow.svg)
[![Python application](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/python-app.yml/badge.svg)](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/python-app.yml)
[![API Tests (Newman)](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/api-tests.yml/badge.svg)](https://github.com/SahilSR81/ms-qa-assignment/actions/workflows/api-tests.yml)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

## Quick Start

To execute the test suites immediately:

### 1. Run UI Automation Tests (Selenium + pytest)
```bash
cd automation/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

### 2. Run API Contract Tests (Postman + Newman)
```bash
cd api-testing/postman/
npm install -g newman
node mock-server.js &
sleep 2
newman run collection.json -e environment.json
```

---

## What's Included

The submission is structured into the following key components:

*   **QA Strategy & Design**: A comprehensive risk-based test strategy for the initial launch and 15 detailed test cases spanning authentication, payments, and notifications.
*   **Root Cause Analysis (RCA)**: Step-by-step investigation procedures for three critical production failure scenarios.
*   **API Validation**: Pinned-down contract validation for the platform's backend endpoints, backed by a Node.js mock server and Newman test suite.
*   **E2E Automation**: A complete Selenium Python framework implementing the Page Object Model (POM) to automate user flows on SauceDemo.

---

## Repository Structure

| Part | Deliverable | Path |
|------|-------------|------|
| Part 1 — QA Strategy | Risk-based test strategy for a first production launch | [qa-strategy/README.md](qa-strategy/README.md) |
| Part 2 — Test Case Design | 15 structured test cases across 5 modules with prioritization | [test-cases/README.md](test-cases/README.md) |
| Part 3 — Root Cause Analysis | Investigation approach for 3 production scenarios | [rca/README.md](rca/README.md) |
| Part 4 — API Testing Approach | Written approach for all 6 endpoints | [api-testing/api-testing-approach.md](api-testing/api-testing-approach.md) |
| Part 5 — Automation (Selenium + pytest) | Page Object Model framework with CI | [automation/](automation/) |
| Bonus — Postman Collection + Newman CI | 21-request API test suite with mock server | [api-testing/postman/](api-testing/postman/) |

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
│   ├── README.md                # Part 3 — Root Cause Analysis
│   └── sample-bug-report.md     # Jira-style bug report for Scenario 1
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
│   │   ├── cart_page.py         # Cart interactions
│   │   ├── inventory_page.py    # Products listing interactions
│   │   └── login_page.py        # Login interactions
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
| Selenium Manager (built-in) | Automatic management of browser drivers — no webdriver-manager dependency |
| Postman + Newman | API test design (GUI) and CI-ready CLI execution |
| Node.js | Lightweight mock server for API tests |
| GitHub Actions | Continuous Integration — two pipelines (automation + API tests) |

---

## Setup Instructions

### Automation (Selenium + pytest)

Please see the dedicated [automation/README.md](automation/README.md) for full setup and execution instructions.

### API Testing (Postman + Newman)

```bash
# Install Newman (one-time)
npm install -g newman newman-reporter-htmlextra

# Navigate to the postman directory
cd api-testing/postman

# Start mock server + run tests
node mock-server.js &
sleep 2
newman run collection.json -e environment.json
```

---

## How to Run Tests

### API Tests

```bash
cd api-testing/postman/
newman run collection.json -e environment.json --reporters cli,htmlextra --reporter-htmlextra-export report.html
```

---

## CI Pipelines

Two independent GitHub Actions workflows run on push/PR to `main`:

1. **`python-app.yml`** — Selenium automation: installs Chrome, installs pinned Python dependencies, runs `pytest` in headless mode.
2. **`api-tests.yml`** — API tests: installs Node.js + Newman, starts the mock server, runs the full 21-request Postman collection, uploads the HTML report as a build artifact.

---

## Assumptions

- **Payment is simulated**: No real payment gateway or money movement. Testing validates flow correctness, not PCI compliance.
- **Endpoints are undocumented** (except `POST /api/login`): API contracts for the other 5 endpoints were inferred from reasonable assumptions, documented in the Postman collection description.
- **Single deployment environment**: No blue-green or canary infrastructure assumed.
- **Web-only platform**: No native mobile app support at launch.
- **Selenium Manager**: The project uses Selenium 4.44's built-in driver management — no `webdriver-manager` package dependency.
- **Sole QA engineer**: All testing scope is bounded by one person's throughput.

---

#### AI Tools Used

| Tool | Models | Usage |
|------|--------|-------|
| [opencode](https://opencode.ai) / Antigravity | big-pickle (online) | Code generation, debugging, architecture suggestions, file operations |
| [ollama](https://ollama.ai) (offline/local) | `batiai/gemma4-12b:q3`, `qwen3.5:latest` | Local code review, test case generation, documentation drafting |

**Workflow Details:**
- **Opencode** orchestrated the project using a terminal-based agent.
- **Big-pickle** handled online queries via eza for free access.
- **Ollama** models ran locally for sensitive work and iterative refinement.
- All AI outputs were manually reviewed, tested, and often modified. For example, when an AI tool initially suggested static `time.sleep()` calls for page navigation, this was rejected in favor of explicit `WebDriverWait` polling to ensure the CI pipeline runs stably.

---

## Troubleshooting

1. **Automation Framework Issues:**
   * Please refer to the troubleshooting section in [automation/README.md](automation/README.md).

2. **Newman Mock Server Connection Refused:**
   * **Issue:** `connect ECONNREFUSED 127.0.0.1:3000` when running Newman.
   * **Solution:** Ensure the mock server (`node mock-server.js`) is running before executing Newman. The server binds to port 3000 by default.
