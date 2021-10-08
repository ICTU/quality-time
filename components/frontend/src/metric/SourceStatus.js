import React, { useContext } from 'react';
import { Label, Popup } from 'semantic-ui-react';
import { DataModel } from '../context/DataModel';
import { HyperLink } from '../widgets/HyperLink';
import { get_source_name } from '../utils';

export function SourceStatus({metric, measurement_source, source_uuid}) {
    const dataModel = useContext(DataModel)
    // Source may be deleted from report but still referenced in the latest measurement, be prepared:
    if (!Object.keys(metric.sources).includes(source_uuid)) { return null }
    const source = metric.sources[source_uuid];
    const source_name = get_source_name(source, dataModel);
    function source_label() {
        return (measurement_source.landing_url ? <HyperLink url={measurement_source.landing_url}>{source_name}</HyperLink> : source_name)
    }
    if (measurement_source.connection_error || measurement_source.parse_error) {
        return (
            <Popup
                flowing hoverable
                trigger={<Label color='red'>{source_label()}</Label>}>
                {measurement_source.connection_error ? 'Connection error' : 'Parse error'}
            </Popup>
        )
    } else {
        return source_label()
    }
}
