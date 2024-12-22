import { Header } from "../semantic_ui_react_wrappers"
import { metricTypePropType } from "../sharedPropTypes"
import { slugify } from "../utils"
import { ReadTheDocsLink } from "../widgets/ReadTheDocsLink"

export function MetricTypeHeader({ metricType }) {
    const url = `https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/reference.html${slugify(metricType.name)}`
    const howToConfigure = metricType.documentation
        ? " for specific information on how to configure this metric type."
        : ""
    return (
        <Header>
            <Header.Content>
                {metricType.name}
                <Header.Subheader>
                    {metricType.description} <ReadTheDocsLink url={url} />
                    {howToConfigure}
                </Header.Subheader>
            </Header.Content>
        </Header>
    )
}
MetricTypeHeader.propTypes = {
    metricType: metricTypePropType,
}
