import React, { useContext } from 'react';
import { Header } from '../semantic_ui_react_wrappers';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { set_metric_attribute } from '../api/metric';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';

export function metricTypeOption(key, metricType) {
    return {
        key: key, text: metricType.name, value: key,
        content: <Header as="h4" content={metricType.name} subheader={metricType.description} />
    }
}

export function metricTypeOptions(dataModel, subjectType) {
    // Return menu options for all metric that support the subject type
    return dataModel.subjects[subjectType].metrics.map((key) => metricTypeOption(key, dataModel.metrics[key]));
}

export function MetricType({subjectType, metricType, metric_uuid, reload}) {
    const dataModel = useContext(DataModel);
    const options = metricTypeOptions(dataModel, subjectType)
    const metricTypes = options.map(option => option.key)
    if (!metricTypes.includes(metricType)) {
        options.push(metricTypeOption(metricType, dataModel.metrics[metricType]))
    }
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
