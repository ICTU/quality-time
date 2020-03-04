import React from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { TextInput } from '../fields/TextInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { set_source_entity_attribute } from '../api/source';
import { capitalize } from '../utils';
import { source_entity_status_name as status_name } from './source_entity_status';

function entity_status_option(status, text, content, subheader) {
  return {
    key: status, text: text, value: status, content: <Header as="h5" content={content} subheader={subheader} />
  }
}

function entity_status_options(entity_type) {
  return [
    entity_status_option('unconfirmed', status_name.unconfirmed, 'Unconfirm', `This ${entity_type} should be reviewed to decide what to do with it.`),
    entity_status_option('confirmed', status_name.confirmed, 'Confirm', `This ${entity_type} has been reviewed and should be dealt with.`),
    entity_status_option('fixed', 'Fixed', status_name.fixed, `This ${entity_type} has been fixed and will disappear shortly.`),
    entity_status_option('false_positive', status_name.false_positive, 'Resolve as false positive', `This ${entity_type} can be ignored because it's been incorrectly identified as ${entity_type}.`),
    entity_status_option('wont_fix', status_name.wont_fix, "Resolve as won't fix", `This ${entity_type} will not be fixed.`)
  ]
}

export function SourceEntityDetails(props) {
  return (
    <Grid stackable>
      <Grid.Row columns={4}>
        <Grid.Column width={4}>
          <SingleChoiceInput
            label={`${capitalize(props.name)} status`}
            options={entity_status_options(props.name)}
            set_value={(value) => set_source_entity_attribute(props.metric_uuid, props.source_uuid, props.entity.key, "status", value, props.reload)}
            value={props.status}
          />
        </Grid.Column>
        <Grid.Column width={12}>
          <TextInput
            label="Rationale"
            placeholder={`Rationale for ${props.name} status...`}
            set_value={(value) => set_source_entity_attribute(props.metric_uuid, props.source_uuid, props.entity.key, "rationale", value, props.reload)}
            value={props.rationale}
          />
        </Grid.Column>
      </Grid.Row>
    </Grid>
  );
}
