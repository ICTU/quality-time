import React from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { Icon, Popup } from '../semantic_ui_react_wrappers';
import { DateInput } from '../fields/DateInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { TextInput } from '../fields/TextInput';
import { set_source_entity_attribute } from '../api/source';
import { capitalize } from '../utils';
import { source_entity_status_name as status_name } from './source_entity_status';
import { EDIT_ENTITY_PERMISSION } from '../context/Permissions';

function entity_status_option(status, text, content, subheader) {
    return {
        key: status, text: text, value: status, content: <Header as="h5" content={content} subheader={subheader} />
    }
}

function entity_status_options(entity_type) {
    return [
        entity_status_option('unconfirmed', status_name.unconfirmed, 'Unconfirm', `This ${entity_type} should be reviewed to decide what to do with it.`),
        entity_status_option('fixed', status_name.fixed, "Resolve as will be fixed", `This ${entity_type} will be fixed shortly and then disappear.`),
        entity_status_option('false_positive', status_name.false_positive, 'Resolve as false positive', `This ${entity_type} can be ignored because it's been incorrectly identified as ${entity_type}.`),
        entity_status_option('wont_fix', status_name.wont_fix, "Resolve as won't fix", `This ${entity_type} will not be fixed.`),
        entity_status_option('confirmed', status_name.confirmed, 'Confirm', `This ${entity_type} has been reviewed and should be dealt with.`),
    ]
}

export function SourceEntityDetails({ entity, metric_uuid, name, rationale, reload, status, status_end_date, source_uuid }) {
    return (
        <Grid stackable>
            <Grid.Row>
                <Grid.Column width={3}>
                    <SingleChoiceInput
                        requiredPermissions={[EDIT_ENTITY_PERMISSION]}
                        label={`${capitalize(name)} status`}
                        options={entity_status_options(name)}
                        set_value={(value) => set_source_entity_attribute(metric_uuid, source_uuid, entity.key, "status", value, reload)}
                        value={status}
                        sort={false}
                    />
                </Grid.Column>
                <Grid.Column width={3}>
                    <DateInput
                        requiredPermissions={[EDIT_ENTITY_PERMISSION]}
                        label={<label>{`${capitalize(name)} status end date`} <Popup on={['hover', 'focus']} content={`Consider the status of this ${name} to be 'Unconfirmed' after the selected date.`} trigger={<Icon tabIndex="0" name="help circle" />} /></label>}
                        placeholder="YYYY-MM-DD"
                        set_value={(value) => set_source_entity_attribute(metric_uuid, source_uuid, entity.key, "status_end_date", value, reload)}
                        value={status_end_date}
                    />
                </Grid.Column>
                <Grid.Column width={10}>
                    <TextInput
                        requiredPermissions={[EDIT_ENTITY_PERMISSION]}
                        label={`${capitalize(name)} status rationale`}
                        placeholder={`Rationale for the ${name} status...`}
                        rows={Math.min(5, rationale?.split("\n").length ?? 1)}
                        set_value={(value) => set_source_entity_attribute(metric_uuid, source_uuid, entity.key, "rationale", value, reload)}
                        value={rationale}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    );
}
