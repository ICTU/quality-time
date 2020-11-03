"""Snyk metrics collector."""

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import md5_hash
from source_model import Entity, SourceMeasurement, SourceResponses

class SnykSecurityWarnings(JSONFileSourceCollector):
    """Snyk collector for security warnings."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement: # pylint: disable=too-many-locals
        entities = []
        unique_directdependency_vulns = {}
        for response in responses:
            json = await response.json(content_type=None)
            vulnerabilities = json.get("vulnerabilities", [])
            vulnerabilities = json.get("vulnerabilities", [])
            for vulnerability in vulnerabilities:
                path = " ➜ ".join([str(dependency) for dependency in vulnerability["from"][0:]]) \
                    if isinstance(vulnerability["from"], list) else vulnerability["from"]
                directdependency = vulnerability["from"][0] if len(vulnerability["from"]) == 1 else vulnerability["from"][1] # pylint: disable=line-too-long
                directdependency_vulns = {}
                directdependency_vulns[directdependency] = []
                directdependency_vulns[directdependency].append([vulnerability["id"], path, vulnerability["severity"]])

                for key, intervulns in directdependency_vulns.items():
                    unique_directdependency_vulns.setdefault(key, []).append(intervulns[0])
        consolidatedreport = {}
        for directdependency, vulnlist in unique_directdependency_vulns.items():
            consolidatedreport[directdependency] = []
            paths = []
            consolidatedreport[directdependency].append({'vulnerabilities': vulnlist})
            consolidatedreport[directdependency].append({'numbervulns': len(vulnlist)})

            for uniquevulnlist in consolidatedreport[directdependency][0].values():
                for vulnpaths in uniquevulnlist:
                    paths.append(vulnpaths[1])
            consolidatedreport[directdependency].append({'paths': [paths]})
            consolidatedreport[directdependency].append({'examplepath': paths[1]})
            consolidatedreport[directdependency].append({'examplevuln': vulnlist[1][0]})
            consolidatedreport[directdependency].append({'severity': vulnlist[1][2]})
            entities.append(
                Entity(
                    key=md5_hash(directdependency), directdependency=directdependency,
                    numbervulns=consolidatedreport[directdependency][1].get('numbervulns'),
                    examplevuln=consolidatedreport[directdependency][4].get('examplevuln'),
                    url=f"https://snyk.io/vuln/{consolidatedreport[directdependency][4].get('examplevuln')}",
                    examplepath=consolidatedreport[directdependency][3].get('examplepath'),
                    severity=consolidatedreport[directdependency][5].get('severity'))
                        )
        return SourceMeasurement(entities=entities)
