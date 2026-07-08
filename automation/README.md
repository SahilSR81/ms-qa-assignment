# Automation (Selenium + pytest)

Page Object Model framework for testing the SauceDemo user flow.

## Tech Stack

| Tool | What I Used It For |
|------|--------------------|
| Python | Main language |
| Selenium WebDriver | Browser automation |
| pytest | Test runner and assertions |
| Selenium Manager (built-in) | Auto driver management (no webdriver-manager needed) |
| GitHub Actions | CI (headless pytest) |

## Setup

```bash
cd automation/

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## How to Run

```bash
cd automation/

# Headless (default)
pytest

# With visible browser
pytest --headless=False
```

## Design Choices

### Page Object Model (POM)
All locators and WebDriver interactions are in `pages/`. Test files (`tests/`) have zero locators (`By.ID`, `By.CLASS_NAME`, etc.). If the UI changes, I only update the page class, not the tests.

### No Hardcoded Sleeps
Zero `time.sleep()` in the framework. Instead, `BasePage` uses explicit `WebDriverWait` with Expected Conditions (`visibility_of_element_located`, `element_to_be_clickable`). The framework waits for elements to be ready rather than guessing with fixed delays. Faster and more reliable.

### Pinned Dependencies
`requirements.txt` uses exact version pins (`==`). This prevents CI and local machines from getting different versions — a common cause of "works on my machine" failures.

## Follow-Up Question: Tests Pass Locally but Fail Intermittently in CI

**Question:** *Imagine this automation passes consistently on your local machine but fails intermittently in CI. List five possible reasons and how you'd investigate each.*

1. **Headless viewport vs headed**: Headless browsers often start with a smaller window size (800x600). Elements can be off-screen or covered by sticky footers.
   * **Check**: Look at failure screenshots (captured by `conftest.py`). If element is off-screen, force `--window-size=1920,1080` in headless Chrome options.

2. **CI runner resource contention**: GitHub Actions runners share CPU/memory. Pages can load much slower than on a local dev machine.
   * **Check**: Look at CI run duration for the failing step. If it took unusually long, increase `WebDriverWait` timeout or check runner resource usage.

3. **React re-render race (swallowed clicks)**: WebDriver might click a button right when React is destroying and replacing the DOM node. The click lands on the old node and the event never fires. Headless runs execute JS faster, changing the timing and surfacing this race.
   * **Check**: If the failure screenshot shows the test is still on the *previous* page despite `.click()` succeeding in logs, a swallowed click is the cause. I handle this with a custom `click_until_url` retry helper.

4. **Browser/driver version drift**: CI installs the latest Chrome. If a new Chrome version changes behavior or breaks APIs before Selenium Manager catches up, tests can randomly fail.
   * **Check**: Compare Chrome and ChromeDriver versions from CI logs of a failed run vs a passed run. If they differ, pin the Chrome version in the CI setup action.

5. **External site latency/uptime**: This suite tests a real site (`saucedemo.com`), not a local mock. Zero control over its latency, DNS, or downtime.
   * **Check**: Does the failure screenshot show a browser error page (`ERR_CONNECTION_TIMED_OUT`) or a 5xx from the hosting provider? If yes, it's external infrastructure, not the test code.

## Troubleshooting

### ChromeDriver Version Mismatch
- **Issue:** `SessionNotCreatedException: This version of ChromeDriver only supports Chrome version X`.
- **Fix:** Selenium 4.10+ includes Selenium Manager which auto-downloads the right driver. Make sure you're on `>=4.10` (this project uses 4.44.0). If issues persist, update Chrome: `google-chrome --version`.

### Headless CI Failures
- **Issue:** Tests pass locally but fail in CI with element-not-found or timeout.
- **Fix:** `conftest.py` already sets `--window-size=1920,1080` and calls `driver.maximize_window()`. If still failing, check CI logs for screenshot artifacts.

### Stale Element Reference
- **Issue:** `StaleElementReferenceException: element is not attached to the page document`.
- **Fix:** `BasePage` methods re-locate elements dynamically using explicit waits on every action. If you write a new page method that hits this, use `self.wait.until(EC.*)` instead of storing element references.
