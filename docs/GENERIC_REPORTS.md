# Generic Security Warnings*

In some cases, there are security vulnerabilities not found by automated tools. Quality-time has the ability to parse security warnings from JSON files with a simple generic format.
The JSON format consists of an object with one key `vulnerabilities`. The value should be a list of, you guess it, vulnerabilities. Each vulnerability is an object with three keys: `title`, `description`, and `severity`. The severity can be `low`, `medium`, or `high`.

## Example Generic Report


```json
{
    "vulnerabilities": [
      {
        "title": "ISO27001:2013 A9 Insufficient Access Control",
        "description": "The Application does not enforce Two-Factor Authentication and therefore not satisfy security best practices.",
        "severity": "high"
      },
      {
        "title": "Threat Model Finding: Uploading Malicious of Malicious files",
        "description": "An attacker can upload malicious files with low privileges can perform direct API calls and perform unwanted mutations or see unauthorized information.",
        "severity": "medium"
      }
    ]
  }
```