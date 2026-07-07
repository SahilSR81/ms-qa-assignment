# MSAI QA Automation

A clean, production-grade Selenium automation framework built for the MeetStream AI QA Engineering Internship assignment.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.45+-green.svg)
![pytest](https://img.shields.io/badge/pytest-9.1+-yellow.svg)
![CI](https://github.com/sahilsr81/ms-qa-assignment/actions/workflows/python-app.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| Selenium WebDriver | Browser automation and interaction |
| pytest | Test runner and assertion framework |
| Selenium Manager (built-in) | Automatic management of browser drivers |
| GitHub Actions | Continuous Integration (CI) |

## Folder Structure

```
ms-qa-assignment/
├── .github/
│   └── workflows/
│       └── python-app.yml       # CI configuration
├── automation/
│   ├── pages/                   # Page Object classes
│   │   ├── __init__.py
│   │   ├── base_page.py         # Core element interactions & explicit waits
│   │   ├── cart_page.py         # Cart interactions
│   │   ├── inventory_page.py    # Products listing interactions
│   │   └── login_page.py        # Login interactions
│   ├── tests/                   # Test files
│   │   ├── __init__.py
│   │   └── test_saucedemo_workflow.py
│   ├── conftest.py              # Pytest fixtures and browser setup
│   ├── pytest.ini               # Pytest configuration
│   └── requirements.txt         # Python dependencies
└── README.md                    # Project documentation
```

## Setup Instructions

Run the following commands to get the environment ready:

```bash
# Clone the repository (if applicable) and navigate to the project directory
cd automation/

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## How to Run Tests

By default, tests are configured to run in **headless** mode.

**Run tests normally (headless mode):**
```bash
cd automation/
pytest
```

**Run tests in UI mode (visible browser):**
```bash
cd automation/
pytest --headless=False
```

## Design Decisions

### Strict Page Object Model (POM)
The framework strictly adheres to the Page Object Model design pattern. All locators and WebDriver interactions are encapsulated within the `pages/` directory. Test files (`tests/`) contain zero locators (`By.ID`, `By.CLASS_NAME`, etc.). This separation of concerns ensures that the test logic remains clean, readable, and focused on business flows, while UI changes only require updates in a single page class.

### No-Sleep Policy (Explicit Waits Only)
The framework enforces a strict zero `time.sleep()` policy. Hardcoded sleeps lead to flaky tests and unnecessarily increase execution time. Instead, the `BasePage` class implements robust `WebDriverWait` strategies combined with Expected Conditions (e.g., `visibility_of_element_located`, `element_to_be_clickable`). The framework actively polls the DOM and proceeds exactly when the element is ready, ensuring fast and reliable test execution.

## Troubleshooting

1. **Chromedriver Mismatch Error:**
   * **Issue:** `SessionNotCreatedException: This version of ChromeDriver only supports Chrome version X`.
   * **Solution:** The framework uses `webdriver-manager` to avoid this, but if it occurs, clear the webdriver-manager cache: `rm -rf ~/.wdm` and re-run. Ensure your local Google Chrome browser is up to date.

2. **Headless CI Failures:**
   * **Issue:** Tests pass locally but fail in GitHub Actions with element not found or timeout exceptions.
   * **Solution:** Headless browsers often run with a smaller default window size. Ensure `driver.maximize_window()` is called in `conftest.py`, or pass explicit window size arguments (`--window-size=1920,1080`).

3. **Stale Element Reference Exception:**
   * **Issue:** `StaleElementReferenceException: stale element reference: element is not attached to the page document`.
   * **Solution:** This happens when the DOM refreshes after an element is located but before it is interacted with. The `BasePage` methods re-locate elements dynamically using explicit waits on every action to prevent this.

## Results

*(Placeholder for a pytest output screenshot)*
![pytest output screenshot](placeholder_results.png)
