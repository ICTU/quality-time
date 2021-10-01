import React, { useContext } from 'react';
import { Header } from 'semantic-ui-react';
<<<<<<< HEAD
import { DataModel } from '../context/DataModel';
=======
import { DataModel } from '../context/Contexts';
>>>>>>> b61395ea (found some last props.datamodel)
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { Logo } from './Logo';

export function SourceType({metric_type, set_source_attribute, source_type}) {
    const dataModel = useContext(DataModel)
    let options = [];
    dataModel.metrics[metric_type].sources.forEach(
        (key) => {
<<<<<<< HEAD
            const option_source_type = dataModel.sources[key];
=======
            const source_type = dataModel.sources[key];
>>>>>>> b61395ea (found some last props.datamodel)
            options.push(
                {
                    key: key,
                    text: option_source_type.name,
                    value: key,
                    content:
                        <Header as="h4">
                            <Header.Content>
                                <Logo logo={key} alt={option_source_type.name} />{option_source_type.name}<Header.Subheader>{option_source_type.description}</Header.Subheader>
                            </Header.Content>
                        </Header>
                })
        });
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
