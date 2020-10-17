# *Quality-time* notifier

## Overview

The notifier is responsible for notifying users about significant events, such as metrics turning red. It wakes up periodically and asks the server for all reports. For each report, the notifier determines whether whether notification destinations have been configured, and whether events happened that need to be notified.
