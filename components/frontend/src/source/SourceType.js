import React, { useContext } from 'react';
import { Header } from '../semantic_ui_react_wrappers';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { Logo } from './Logo';

function sourceTypeOption(key, sourceType) {
    return {
        key: key,
        text: sourceType.name,
        value: key,
        content:
            <Header as="h4">
                <Header.Content>
                    <Logo logo={key} alt={sourceType.name} />{sourceType.name}<Header.Subheader>{sourceType.description}</Header.Subheader>
                </Header.Content>
            </Header>
    }
}

export function sourceTypeOptions(dataModel, metricType) {
    // Return menu options for all sources that support the metric type
    return dataModel.metrics[metricType].sources.map((key) => sourceTypeOption(key, dataModel.sources[key]));
}

export function SourceType({metric_type, set_source_attribute, source_type}) {
    const dataModel = useContext(DataModel);
    const options = sourceTypeOptions(dataModel, metric_type)
    const sourceTypes = options.map(option => option.key)
    if (!sourceTypes.includes(source_type)) {
        options.push(sourceTypeOption(source_type, dataModel.sources[source_type]))
    }
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Source type"
            options={options}
            set_value={(value) => set_source_attribute("type", value)}
            value={source_type}
        />
    )
}
