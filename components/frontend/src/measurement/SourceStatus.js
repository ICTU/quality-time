import React, { useContext } from 'react';
import { Label, Popup } from '../semantic_ui_react_wrappers';
import { DataModel } from '../context/DataModel';
import { HyperLink } from '../widgets/HyperLink';
import { get_metric_name, get_source_name } from '../utils';

export function SourceStatus({ metric, measurement_source }) {
    const dataModel = useContext(DataModel)
    // Source may be deleted from report but still referenced in the latest measurement, be prepared:
    if (!Object.keys(metric.sources).includes(measurement_source.source_uuid)) { return null }
    const source = metric.sources[measurement_source.source_uuid];
    const source_name = get_source_name(source, dataModel);
    const configError = !dataModel.metrics[metric.type].sources.includes(source.type)
    function source_label(error) {
        return (measurement_source.landing_url ? <HyperLink error={error} url={measurement_source.landing_url}>{source_name}</HyperLink> : source_name)
    }
    if (configError || measurement_source.connection_error || measurement_source.parse_error) {
        let content;
        let header;
        if (configError) {
            content = `${source_name} cannot be used to measure ${get_metric_name(metric, dataModel)}.`
            header = 'Configuration error'
        } else if (measurement_source.connection_error) {
            content = 'Quality-time could not retrieve data from the source.'
            header = 'Connection error'
        } else {
            content = 'Quality-time could not parse the data received from the source.'
            header = 'Parse error'
        }
        return (
            <Popup content={content} flowing header={header} hoverable trigger={<Label color='red'>{source_label(true)}</Label>} />
        )
    } else {
        return source_label()
    }
}
