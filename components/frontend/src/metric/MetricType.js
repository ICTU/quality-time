import React, { useContext } from 'react';
import { Header } from 'semantic-ui-react';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { set_metric_attribute } from '../api/metric';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { DataModel } from '../context/Contexts';

export function MetricType({metricType, metric_uuid, reload}) {
    const dataModel = useContext(DataModel)
    let options = [];
    Object.keys(dataModel.metrics).forEach(
        (key) => {
            const metric_type = dataModel.metrics[key];
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
            set_value={(value) => set_metric_attribute(metric_uuid, "type", value, reload)}
            value={metricType}
        />
    )
}
