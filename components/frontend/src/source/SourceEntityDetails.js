import React from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { DateInput } from '../fields/DateInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { TextInput } from '../fields/TextInput';
import { set_source_entity_attribute } from '../api/source';
import { capitalize } from '../utils';
import { source_entity_status_name as status_name } from './source_entity_status';
import { EDIT_ENTITY_PERMISSION } from '../context/Permissions';
import { LabelWithDate } from '../widgets/LabelWithDate';

function entity_status_option(status, text, content, subheader) {
    return {
        key: status, text: text, value: status, content: <Header as="h5" content={content} subheader={subheader} />
    }
}

function entity_status_options(entity_type, report) {
    const desired_response_times = report?.desired_response_times ?? {}
    const unconfirmed_subheader = `This ${entity_type} should be reviewed to decide what to do with it.`
    const confirmed_subheader = `This ${entity_type} has been reviewed and should be dealt with within ${desired_response_times["confirmed"]} days.`
    const fixed_subheader = `Ignore this ${entity_type} for ${desired_response_times["fixed"]} days because it has been fixed or will be fixed shortly.`
    const false_positive_subheader = `Ignore this ${entity_type} for ${desired_response_times["false_positive"]} days because it's been incorrectly identified as ${entity_type}.`
    const wont_fix_subheader = `Ignore this ${entity_type} for ${desired_response_times["wont_fix"]} days because it will not be fixed.`
    return [
        entity_status_option('unconfirmed', status_name.unconfirmed, 'Unconfirm', unconfirmed_subheader),
        entity_status_option('confirmed', status_name.confirmed, "Confirm", confirmed_subheader),
        entity_status_option('fixed', status_name.fixed, "Resolve as fixed", fixed_subheader),
        entity_status_option('false_positive', status_name.false_positive, "Resolve as false positive", false_positive_subheader),
        entity_status_option('wont_fix', status_name.wont_fix, "Resolve as won't fix", wont_fix_subheader),
    ]
}

export function SourceEntityDetails({ entity, metric_uuid, name, rationale, reload, report, status, status_end_date, source_uuid }) {
    return (
        <Grid stackable>
            <Grid.Row>
                <Grid.Column width={4}>
                    <SingleChoiceInput
                        requiredPermissions={[EDIT_ENTITY_PERMISSION]}
                        label={`${capitalize(name)} status`}
                        options={entity_status_options(name, report)}
                        set_value={(value) => set_source_entity_attribute(metric_uuid, source_uuid, entity.key, "status", value, reload)}
                        value={status}
                        sort={false}
                    />
                </Grid.Column>
                <Grid.Column width={4}>
                    <DateInput
                        requiredPermissions={[EDIT_ENTITY_PERMISSION]}
                        label={
                            <LabelWithDate
                                date={status_end_date}
                                labelId={entity.key}
                                label={`${capitalize(name)} status end date`}
                                help={`Consider the status of this ${name} to be 'Unconfirmed' after the selected date.`}
                            />
                        }
                        placeholder="YYYY-MM-DD"
                        set_value={(value) => set_source_entity_attribute(metric_uuid, source_uuid, entity.key, "status_end_date", value, reload)}
                        value={status_end_date}
                    />
                </Grid.Column>
                <Grid.Column width={8}>
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
