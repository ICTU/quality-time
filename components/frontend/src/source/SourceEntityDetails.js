import React from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { TextInput } from '../fields/TextInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { set_source_entity_attribute } from '../api/source';
import { capitalize } from '../utils';
import { source_entity_statuses } from './source_entity_status';

function entity_status_options(entity_type) {
  return Object.entries(source_entity_statuses(entity_type)).map(([key, status]) => (
    {
      key: key, text: status.name, value: key,
      content: <Header as="h5" content={status.action} subheader={status.description} />
    }
  ));
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
