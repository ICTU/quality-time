import { metricTypePropType } from "../sharedPropTypes"
import { slugify } from "../utils"
import { Header } from "../widgets/Header"
import { ReadTheDocsLink } from "../widgets/ReadTheDocsLink"

export function MetricTypeHeader({ metricType }) {
    const url = `https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/reference.html${slugify(metricType.name)}`
    const howToConfigure = metricType.documentation
        ? " for specific information on how to configure this metric type."
        : ""
    return (
        <Header
            header={metricType.name}
            level="h4"
            subheader={
                <>
                    {metricType.description} <ReadTheDocsLink url={url} /> {howToConfigure}
                </>
            }
        />
    )
}
MetricTypeHeader.propTypes = {
    metricType: metricTypePropType,
}
