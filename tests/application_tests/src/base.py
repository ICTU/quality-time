"""Configuration for the application tests.

The application tests run against both a Docker Compose deployment and a Kubernetes deployment. The hostnames
differ between the two, so they are read from environment variables, defaulting to the Docker Compose service names.
"""

import os

# URL the test process uses to reach the proxy (for API requests)
WWW_URL = os.environ.get("WWW_URL", "http://www:8080")

# URL the Selenium browser uses to reach the proxy; defaults to WWW_URL because in Docker both reach www the same way
WWW_BROWSER_URL = os.environ.get("WWW_BROWSER_URL", WWW_URL)

# URL the test process uses to reach the Selenium server
SELENIUM_URL = os.environ.get("SELENIUM_URL", "http://selenium:4444")
