# Generic Security Warnings*

In some cases, there are security vulnerabilities not found by automated tools. Quality Time has the ability to parse JSON files into reports for generic security warnings.

## Example Generic Report

generic.json
```
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