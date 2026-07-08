# MSAI — QA Engineering Assignment

A complete QA engineering submission for the MSAI Online Event Registration Platform, covering strategy, test design, root cause analysis, API testing, and end-to-end automation.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.44+-green.svg)
![pytest](https://img.shields.io/badge/pytest-9.0+-yellow.svg)
![Automation CI](https://github.com/sahilsr81/ms-qa-assignment/actions/workflows/python-app.yml/badge.svg)
![API Tests CI](https://github.com/sahilsr81/ms-qa-assignment/actions/workflows/api-tests.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

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

## How to Run Tests

### API Tests

```bash
cd api-testing/postman/
newman run collection.json -e environment.json --reporters cli,htmlextra --reporter-htmlextra-export report.html
```

## CI Pipelines

Two independent GitHub Actions workflows run on push/PR to `main`:

1. **`python-app.yml`** — Selenium automation: installs Chrome, installs pinned Python dependencies, runs `pytest` in headless mode.
2. **`api-tests.yml`** — API tests: installs Node.js + Newman, starts the mock server, runs the full 21-request Postman collection, uploads the HTML report as a build artifact.

## Assumptions

- **Payment is simulated**: No real payment gateway or money movement. Testing validates flow correctness, not PCI compliance.
- **Endpoints are undocumented** (except `POST /api/login`): API contracts for the other 5 endpoints were inferred from reasonable assumptions, documented in the Postman collection description.
- **Single deployment environment**: No blue-green or canary infrastructure assumed.
- **Web-only platform**: No native mobile app support at launch.
- **Selenium Manager**: The project uses Selenium 4.44's built-in driver management — no `webdriver-manager` package dependency.
- **Sole QA engineer**: All testing scope is bounded by one person's throughput.

## AI Tools Used

- **DeepMind Agentic Assistant (Antigravity)**: Used as a pair-programming partner throughout the assignment.
  - **Debugging Headless CI Flakiness**: The AI helped diagnose intermittent `TimeoutException` errors.
  - **Framework Design (Modified AI Suggestion)**: Early on, the AI suggested using `time.sleep()` after clicking buttons to wait for page transitions (a common pattern in generic Selenium tutorials). I explicitly rejected this approach because hardcoded sleeps either waste execution time or cause flakiness depending on CI runner speed. I directed the AI to replace all static sleeps with explicit `WebDriverWait` polling (e.g., `wait_for_staleness`), which is the robust pattern that ships in the final `BasePage` class today. <!-- SAHIL: Verify this accurately reflects your process before submission -->
  - **Documentation**: Aided in generating structural templates for the QA strategy, Test Cases, and RCA documentation.
  - **Validation**: All AI-suggested code was manually reviewed and verified.

## Troubleshooting

1. **Automation Framework Issues:**
   * Please refer to the troubleshooting section in [automation/README.md](automation/README.md).

2. **Newman Mock Server Connection Refused:**
   * **Issue:** `connect ECONNREFUSED 127.0.0.1:3000` when running Newman.
   * **Solution:** Ensure the mock server (`node mock-server.js`) is running before executing Newman. The server binds to port 3000 by default.
