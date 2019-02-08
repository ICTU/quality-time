import React from 'react';
import { Table } from 'semantic-ui-react';
import { SourceParameter } from './SourceParameter';


function SourceParameters(props) {
    const all_parameters = props.datamodel.sources[props.source_type].parameters;
    const parameter_keys = Object.keys(all_parameters).filter((parameter_key) =>
        all_parameters[parameter_key].metrics.includes(props.metric_type)
    );
    const parameters = parameter_keys.map((parameter_key) =>
        (
            <Table.Row key={parameter_key}>
                <Table.Cell>
                    {all_parameters[parameter_key].name}
                </Table.Cell>
                <Table.Cell>
                    <SourceParameter source_uuid={props.source_uuid} parameter_key={parameter_key}
                        parameter_value={props.source.parameters[parameter_key]} />
                </Table.Cell>
            </Table.Row>
        )
    );
    return (
        <Table columns={2} basic='very' size='small'>
            <Table.Body>
                {parameters}
            </Table.Body>
        </Table>
    )
}

export { SourceParameters };
