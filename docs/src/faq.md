# Frequently asked questions

## What is the difference between violations and warnings?

*Quality-time* has a metric called "Violations" and a metric called "Security warnings". What is the difference?

The metric "Violations" is used to measure the number of violations of programming rules. When measuring violations, there is always some set of rules checked by the source and the metric counts the number of violations of the rules. For example, SonarQube checks source code against rules grouped in quality profile and Axe checks software for violations of WCAG guidelines.

The metric "Security warnings" is used to measure the number of potential security vulnerabilities in software. These can be insecure constructs used in the source code or known vulnerabilities in third party dependencies. For example, SonarQube checks source code for SQL-injection vulnerabilities and the OWASP Dependency-Check reports dependencies with known security vulnerabilities.

There can be overlap between the two metrics in the sense that violations can be security risks, and that security warnings can be discovered by checking source code against rules. The difference between the metrics is that "Violations" always reports violations of programming rules, which are not necessarily security risks, and "Security warnings" always reports security risks, which are not necessarily rule violations.
