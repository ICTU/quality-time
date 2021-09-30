import React from 'react';
import { Grid } from 'semantic-ui-react';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { SourceParameter } from './SourceParameter';

export function SourceParameters(props) {
    const all_parameters = props.datamodel.sources[props.source.type].parameters;
    const parameter_keys = Object.keys(all_parameters).filter((parameter_key) =>
        all_parameters[parameter_key].metrics.includes(props.metric_type)
    );
    const parameters = parameter_keys.map((parameter_key, index) =>
    (
        <Grid.Column key={parameter_key} style={{ paddingTop: '10px' }}>
            <SourceParameter
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                help={all_parameters[parameter_key].help}
                help_url={all_parameters[parameter_key].help_url}
                index={index}
                parameter_key={parameter_key}
                parameter_max={all_parameters[parameter_key].max_value || null}
                parameter_min={all_parameters[parameter_key].min_value || null}
                parameter_name={all_parameters[parameter_key].name}
                parameter_short_name={all_parameters[parameter_key].short_name}
                parameter_type={all_parameters[parameter_key].type}
                parameter_values={all_parameters[parameter_key].values || []}
                parameter_value={props.source.parameters && props.source.parameters[parameter_key] ?
                    props.source.parameters[parameter_key] : all_parameters[parameter_key].default_value}
                parameter_unit={all_parameters[parameter_key].unit || props.metric_unit}
                placeholder={all_parameters[parameter_key].placeholder || ""}
                required={all_parameters[parameter_key].mandatory}
                source_type_name={props.datamodel.sources[props.source.type].name}
                warning={props.changed_param_keys ? (props.changed_param_keys.indexOf(parameter_key) !== -1) : false}
                {...props}
            />
        </Grid.Column>
    )
    );
    return (<>{parameters}</>)
}
