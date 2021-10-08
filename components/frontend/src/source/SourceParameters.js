import React, { useContext } from 'react';
import { Grid } from 'semantic-ui-react';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { SourceParameter } from './SourceParameter';

export function SourceParameters({report, source_uuid, source, metric_type, metric_unit, changed_param_keys, reload}) {
    const dataModel = useContext(DataModel)
    const all_parameters = dataModel.sources[source.type].parameters;
    const parameter_keys = Object.keys(all_parameters).filter((parameter_key) =>
        all_parameters[parameter_key].metrics.includes(metric_type)
    );
    const parameters = parameter_keys.map((parameter_key, index) =>
    (
        <Grid.Column key={parameter_key} style={{ paddingTop: '10px' }}>
            <SourceParameter
                report={report}
                source={source}
                source_uuid={source_uuid}
                source_type_name={dataModel.sources[source.type].name}
                parameter_key={parameter_key}
                parameter_type={all_parameters[parameter_key].type}
                parameter_name={all_parameters[parameter_key].name}
                parameter_short_name={all_parameters[parameter_key].short_name}
                parameter_unit={all_parameters[parameter_key].unit || metric_unit}
                parameter_min={all_parameters[parameter_key].min_value || null}
                parameter_max={all_parameters[parameter_key].max_value || null}
                parameter_value={source.parameters && source.parameters[parameter_key] ?
                    source.parameters[parameter_key] : all_parameters[parameter_key].default_value}
                parameter_values={all_parameters[parameter_key].values || []}
                help_url={all_parameters[parameter_key].help_url}
                help={all_parameters[parameter_key].help}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                placeholder={all_parameters[parameter_key].placeholder || ""}
                required={all_parameters[parameter_key].mandatory}
                warning={changed_param_keys ? (changed_param_keys.indexOf(parameter_key) !== -1) : false}
                reload={reload}
                index={index}
            />
        </Grid.Column>
    )
    );
    return (<>{parameters}</>)
}
