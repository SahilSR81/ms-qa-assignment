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

```bash
cd automation/

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

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

### Automation

```bash
cd automation/

# Run tests in headless mode (default)
pytest

# Run tests with visible browser
pytest --headless=False
```

### API Tests

```bash
cd api-testing/postman/
newman run collection.json -e environment.json --reporters cli,htmlextra --reporter-htmlextra-export report.html
```

## Design Decisions

### Strict Page Object Model (POM)
The framework strictly adheres to the Page Object Model design pattern. All locators and WebDriver interactions are encapsulated within the `pages/` directory. Test files (`tests/`) contain zero locators (`By.ID`, `By.CLASS_NAME`, etc.). This separation of concerns ensures that the test logic remains clean, readable, and focused on business flows, while UI changes only require updates in a single page class.

### No-Sleep Policy (Explicit Waits Only)
The framework enforces a strict zero `time.sleep()` policy. Hardcoded sleeps lead to flaky tests and unnecessarily increase execution time. Instead, the `BasePage` class implements robust `WebDriverWait` strategies combined with Expected Conditions (e.g., `visibility_of_element_located`, `element_to_be_clickable`). The framework actively polls the DOM and proceeds exactly when the element is ready, ensuring fast and reliable test execution.

### Pinned Dependencies
`requirements.txt` uses exact version pins (`==`) for pytest and selenium. This prevents CI/local divergence caused by upstream releases — a common source of "works on my machine" failures.

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
  - **Debugging Headless CI Flakiness**: The AI helped diagnose intermittent `TimeoutException` and `StaleElementReferenceException` errors occurring only in the GitHub Actions headless environment. It identified that DOM re-renders and React state changes were swallowing standard Selenium clicks.
  - **Framework Design**: Assisted in designing the resilient `click_until_url` helper in the `BasePage` class, and migrating brittle `time.sleep()` calls to dynamic `WebDriverWait` polling methods (e.g., `wait_for_cart_badge_count`, `wait_for_staleness`).
  - **Documentation**: Aided in generating structural templates for the QA strategy, Test Cases, and RCA documentation.
  - **Validation**: All AI-suggested code was manually reviewed, executed locally both headed and headless, and verified against the CI pipeline to ensure zero flakiness.

## Troubleshooting

1. **Chromedriver Version Mismatch:**
   * **Issue:** `SessionNotCreatedException: This version of ChromeDriver only supports Chrome version X`.
   * **Solution:** Selenium 4.10+ includes Selenium Manager, which automatically downloads the correct ChromeDriver for your installed Chrome version. Ensure your Selenium version is `>=4.10` (this project pins `4.44.0`). If issues persist, verify Chrome is up-to-date: `google-chrome --version`.

2. **Headless CI Failures:**
   * **Issue:** Tests pass locally but fail in GitHub Actions with element-not-found or timeout exceptions.
   * **Solution:** Headless browsers often run with a smaller default window size. The `conftest.py` already sets `--window-size=1920,1080` and calls `driver.maximize_window()`. If still failing, check the CI logs for screenshot artifacts.

3. **Stale Element Reference Exception:**
   * **Issue:** `StaleElementReferenceException: stale element reference: element is not attached to the page document`.
   * **Solution:** The `BasePage` methods re-locate elements dynamically using explicit waits on every action to prevent this. If a new page object method encounters this, ensure it uses `self.wait.until(EC.*)` rather than storing element references.

4. **Newman Mock Server Connection Refused:**
   * **Issue:** `connect ECONNREFUSED 127.0.0.1:3000` when running Newman.
   * **Solution:** Ensure the mock server (`node mock-server.js`) is running before executing Newman. The server binds to port 3000 by default.
