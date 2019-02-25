import React from 'react';
import { Grid } from 'semantic-ui-react';
import { SourceParameter } from './SourceParameter';


function SourceParameters(props) {
    const all_parameters = props.datamodel.sources[props.source_type].parameters;
    const parameter_keys = Object.keys(all_parameters).filter((parameter_key) =>
        all_parameters[parameter_key].metrics.includes(props.metric_type)
    );
    const parameters = parameter_keys.map((parameter_key) =>
        (
            <Grid.Column key={parameter_key} style={{paddingTop: '10px'}}>
                <SourceParameter report_uuid={props.report_uuid} source_uuid={props.source_uuid}
                    parameter_name={all_parameters[parameter_key].name}
                    parameter_key={parameter_key} reload={props.reload}
                    parameter_type={all_parameters[parameter_key].type}
                    parameter_values={all_parameters[parameter_key].values || []}
                    parameter_value={props.source.parameters[parameter_key]} />
            </Grid.Column>
        )
    );
    return (
        <>
            {parameters}
        </>
    )
}

export { SourceParameters };
