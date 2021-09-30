import React from 'react';
import { Header } from 'semantic-ui-react';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { set_metric_attribute } from '../api/metric';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';

export function MetricType(props) {
    let options = [];
    Object.keys(props.datamodel.metrics).forEach(
        (key) => {
            const metric_type = props.datamodel.metrics[key];
            options.push({
                key: key, text: metric_type.name, value: key,
                content: <Header as="h4" content={metric_type.name} subheader={metric_type.description} />
            })
        });
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Metric type"
            options={options}
            set_value={(value) => set_metric_attribute(props.metric_uuid, "type", value, props.reload)}
            value={props.metric_type}
        />
    )
}
