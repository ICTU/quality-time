"""OJAudit metric collector."""

from typing import cast, Dict, List, Optional
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from collector_utilities.type import Namespaces, Entities, Entity, Responses
from collector_utilities.functions import sha1_hash, parse_source_response_xml_with_namespace
from base_collectors import XMLFileSourceCollector, SourceMeasurement


ModelFilePaths = Dict[str, str]  # Model id to model file path mapping


class OJAuditViolations(XMLFileSourceCollector):
    """Collector to get violations from OJAudit."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.violation_counts: Dict[str, int] = dict()  # Keep track of the number of duplicated violations per key

    async def _parse_source_responses(self, responses: Responses) -> SourceMeasurement:
        severities = cast(List[str], self._parameter("severities"))
        count = 0
        entities = []
        for response in responses:
            tree, namespaces = await parse_source_response_xml_with_namespace(response)
            entities.extend(self.__violations(tree, namespaces, severities))
            for severity in severities:
                count += int(tree.findtext(f"./ns:{severity}-count", default="0", namespaces=namespaces))
        return SourceMeasurement(str(count), entities=entities)

    def __violations(self, tree: Element, namespaces: Namespaces, severities: List[str]) -> Entities:
        """Return the violations."""
        models = self.__model_file_paths(tree, namespaces)
        violation_elements = tree.findall(".//ns:violation", namespaces)
        violations = [self.__violation(element, namespaces, models, severities) for element in violation_elements]
        # Discard duplicated violations (where self.__violation() returned None) and add the duplication count
        return [{**violation, "count": str(self.violation_counts[str(violation["key"])])}
                for violation in violations if violation is not None]

    def __violation(self, violation: Element, namespaces: Namespaces, models: ModelFilePaths,
                    severities: List[str]) -> Optional[Entity]:
        """Return the violation as entity."""
        location = violation.find("./ns:location", namespaces)
        if not location:
            raise ValueError(f"OJAudit violation {violation} has no location element")
        severity = violation.findtext("./ns:values/ns:value", default="", namespaces=namespaces)
        if severities and severity not in severities:
            return None
        message = violation.findtext("ns:message", default="", namespaces=namespaces)
        line_number = violation.findtext(".//ns:line-number", namespaces=namespaces)
        column_offset = violation.findtext(".//ns:column-offset", namespaces=namespaces)
        model = models[location.get("model", "")]
        component = f"{model}:{line_number}:{column_offset}"
        key = sha1_hash(f"{message}:{component}")
        if key in self.violation_counts:
            self.violation_counts[key] += 1
            return None  # Ignore duplicate violation
        self.violation_counts[key] = 1
        return dict(key=key, severity=severity, message=message, component=component)

    @staticmethod
    def __model_file_paths(tree: Element, namespaces: Namespaces) -> ModelFilePaths:
        """Return the model file paths."""
        models = tree.findall(".//ns:model", namespaces)
        return {model.get("id", ""): model.findtext("./ns:file/ns:path", default="", namespaces=namespaces)
                for model in models}
