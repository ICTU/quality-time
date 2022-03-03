import React, { useContext } from 'react';
import { Label, Popup } from '../semantic_ui_react_wrappers';
import { DataModel } from '../context/DataModel';
import { HyperLink } from '../widgets/HyperLink';
import { get_source_name } from '../utils';

export function SourceStatus({metric, measurement_source }) {
    const dataModel = useContext(DataModel)
    // Source may be deleted from report but still referenced in the latest measurement, be prepared:
    if (!Object.keys(metric.sources).includes(measurement_source.source_uuid)) { return null }
    const source = metric.sources[measurement_source.source_uuid];
    const source_name = get_source_name(source, dataModel);
    function source_label(error) {
        return (measurement_source.landing_url ? <HyperLink error={error} url={measurement_source.landing_url}>{source_name}</HyperLink> : source_name)
    }
    if (measurement_source.connection_error || measurement_source.parse_error) {
        return (
            <Popup
                flowing hoverable
                trigger={<Label color='red'>{source_label(true)}</Label>}>
                {measurement_source.connection_error ? 'Connection error' : 'Parse error'}
            </Popup>
        )
    } else {
        return source_label()
    }
}
