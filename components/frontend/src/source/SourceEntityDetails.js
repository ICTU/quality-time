import React from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { TextInput } from '../fields/TextInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { set_source_entity_attribute } from '../api/source';
import { entity_status } from './source_entity_status';
import { capitalize } from '../utils';

function entity_status_option(status, key, entity_name) {
  // Replace the possible '${entity_type}' expression in the description with the entity name
  const description = status.description.replace(/\${(.*?)}/g, entity_name);
  return {
    key: key, text: status.name, value: key, content: <Header as="h5" content={status.action} subheader={description} />
  }
}

function entity_status_options(statuses, entity_name) {
  return Object.keys(statuses).map(key => entity_status_option(statuses[key], key, entity_name))
}

export function SourceEntityDetails(props) {
  const statuses = entity_status(props.data_model);
  return (
    <Grid stackable>
      <Grid.Row columns={4}>
        <Grid.Column width={4}>
          <SingleChoiceInput
            label={`${capitalize(props.name)} status`}
            options={entity_status_options(statuses, props.name)}
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
