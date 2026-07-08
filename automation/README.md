# Automation (Selenium + pytest)

This folder contains the complete Page Object Model (POM) automation framework for testing the SauceDemo user flow.

## Tech Stack
| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Selenium WebDriver | Browser automation and interaction |
| pytest | Test runner and assertion framework |
| Selenium Manager (built-in) | Automatic management of browser drivers — no webdriver-manager dependency |
| GitHub Actions | Continuous Integration (runs `pytest` in headless mode) |

## Setup Instructions

```bash
cd automation/

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## How to Run Tests

```bash
cd automation/

# Run tests in headless mode (default)
pytest

# Run tests with visible browser
pytest --headless=False
```

## Design Decisions

### Strict Page Object Model (POM)
The framework strictly adheres to the Page Object Model design pattern. All locators and WebDriver interactions are encapsulated within the `pages/` directory. Test files (`tests/`) contain zero locators (`By.ID`, `By.CLASS_NAME`, etc.). This separation of concerns ensures that the test logic remains clean, readable, and focused on business flows, while UI changes only require updates in a single page class.

### No-Sleep Policy (Explicit Waits Only)
The framework enforces a strict zero `time.sleep()` policy. Hardcoded sleeps lead to flaky tests and unnecessarily increase execution time. Instead, the `BasePage` class implements robust `WebDriverWait` strategies combined with Expected Conditions (e.g., `visibility_of_element_located`, `element_to_be_clickable`). The framework actively polls the DOM and proceeds exactly when the element is ready, ensuring fast and reliable test execution.

### Pinned Dependencies
`requirements.txt` uses exact version pins (`==`) for pytest and selenium. This prevents CI/local divergence caused by upstream releases — a common source of "works on my machine" failures.

## Follow-Up Question: Headless CI Flakiness

**Question**: *Imagine this automation passes consistently on your local machine but fails intermittently in CI. List five possible reasons and explain how you would investigate each one.*

1. **Headless viewport/rendering differences vs local headed runs**: Headless browsers often run with a smaller default window size (e.g., 800x600). This can cause elements to be hidden behind sticky footers or menus, making them un-clickable via standard WebDriver methods.
   * **Investigation**: Review the failure screenshot captured by the `conftest.py` hook. If the element is visibly off-screen or covered, enforce `--window-size=1920,1080` in the headless Chrome options.

2. **CI runner resource contention**: The GitHub Actions runner shares CPU/memory with other VMs. Under heavy load, pages might load significantly slower than on a powerful local dev machine, causing fixed 10s explicit waits to occasionally timeout.
   * **Investigation**: Check the CI run duration for the step that failed. If the step took unusually long, bump the `WebDriverWait` timeout or check runner resource usage metrics.

3. **React re-render races swallowing clicks**: In a timing-sensitive client-side rendered app, the WebDriver might click a button just as React is destroying and replacing the DOM node. The event listener never fires on the old node. Headless runs execute JavaScript faster, changing the timing and surfacing this race condition in CI.
   * **Investigation**: If the failure screenshot shows the test is still on the *previous* page despite a `.click()` passing successfully in the logs, a swallowed click is the culprit. We mitigate this using our custom `click_until_url` retry helper.

4. **Browser/driver version drift**: The `browser-actions/setup-chrome@v2` step in our CI workflow installs the latest Chrome release. If Chrome releases a new major version that introduces new default behaviors or breaks existing APIs before Selenium Manager's driver catches up, tests can randomly start failing.
   * **Investigation**: Check the exact Chrome and ChromeDriver versions printed in the CI logs of a failed run vs a passed run. If they diverged, pin the Chrome version in the CI setup action.

5. **External site latency/uptime**: This suite drives a real, live external site (`saucedemo.com`). Unlike an isolated local mock server, we have zero control over the site's latency, DNS resolution, or periodic downtime. Intermittent 502s or slow initial page loads can easily cause timeouts.
   * **Investigation**: Check if the failure screenshot shows a browser default error page (e.g., `ERR_CONNECTION_TIMED_OUT`) or a 5xx error page from the hosting provider, confirming the issue is external infrastructure, not the test code.

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
