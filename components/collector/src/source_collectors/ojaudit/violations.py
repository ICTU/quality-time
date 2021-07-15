"""OJAudit violations collector."""

from typing import Optional, cast
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from base_collectors import SourceCollectorException, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml_with_namespace, sha1_hash
from collector_utilities.type import Namespaces
from model import Entities, Entity, SourceMeasurement, SourceResponses


ModelFilePaths = dict[str, str]  # Model id to model file path mapping


class OJAuditViolations(XMLFileSourceCollector):
    """Collector to get violations from OJAudit."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.violation_counts: dict[str, int] = {}  # Keep track of the number of duplicated violations per key

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the violations from the OJAudit XML."""
        severities = cast(list[str], self._parameter("severities"))
        count = 0
        entities = Entities()
        for response in responses:
            tree, namespaces = await parse_source_response_xml_with_namespace(response)
            entities.extend(self.__violations(tree, namespaces, severities))
            for severity in severities:
                count += int(tree.findtext(f"./ns:{severity}-count", default="0", namespaces=namespaces))
        return SourceMeasurement(value=str(count), entities=entities)

    def __violations(self, tree: Element, namespaces: Namespaces, severities: list[str]) -> Entities:
        """Return the violations."""
        models = self.__model_file_paths(tree, namespaces)
        violation_elements = tree.findall(".//ns:violation", namespaces)
        violations = Entities()
        for element in violation_elements:
            violation = self.__violation(element, namespaces, models, severities)
            if violation is not None:
                violations.append(violation)
        # Add the duplication counts
        for violation in violations:
            violation["count"] = str(self.violation_counts[str(violation["key"])])
        return violations

    def __violation(
        self, violation: Element, namespaces: Namespaces, models: ModelFilePaths, severities: list[str]
    ) -> Optional[Entity]:
        """Return the violation as entity."""
        location = violation.find("./ns:location", namespaces)
        if not location:
            raise SourceCollectorException(f"OJAudit violation {violation} has no location element")
        severity = violation.findtext("./ns:values/ns:value", default="", namespaces=namespaces)
        if severities and severity not in severities:
            return None
        message = violation.findtext("ns:message", default="", namespaces=namespaces)
        line_number = violation.findtext(".//ns:line-number", namespaces=namespaces)
        column_offset = violation.findtext(".//ns:column-offset", namespaces=namespaces)
        model = models[location.get("model", "")]
        component = f"{model}:{line_number}:{column_offset}"
        key = sha1_hash(f"{message}:{component}")
        entity = Entity(key=key, severity=severity, message=message, component=component)
        if entity["key"] in self.violation_counts:
            self.violation_counts[entity["key"]] += 1
            return None  # Ignore duplicate violation
        self.violation_counts[entity["key"]] = 1
        return entity

    @staticmethod
    def __model_file_paths(tree: Element, namespaces: Namespaces) -> ModelFilePaths:
        """Return the model file paths."""
        models = tree.findall(".//ns:model", namespaces)
        return {
            model.get("id", ""): model.findtext("./ns:file/ns:path", default="", namespaces=namespaces)
            for model in models
        }
