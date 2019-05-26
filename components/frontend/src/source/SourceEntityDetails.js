import React from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { TextInput } from '../fields/TextInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';

export function SourceEntityDetails(props) {
  const options = [
    {
      key: 'unconfirmed', text: 'Unconfirmed', value: 'unconfirmed',
      content:
        <Header
          as="h5"
          content="Unconfirm"
          subheader={`This ${props.name} should be reviewed to decide what to do with it.`}
        />
    },
    {
      key: 'confirmed', text: 'Confirmed', value: 'confirmed',
      content:
        <Header
          as="h5"
          content="Confirm"
          subheader={`This ${props.name} has been reviewed and should be dealt with.`}
        />
    },
    {
      key: 'fixed', text: 'Fixed', value: 'fixed',
      content:
        <Header
          as="h5"
          content="Resolve as fixed"
          subheader={`This ${props.name} has been fixed and will disappear shortly.`}
        />
    },
    {
      key: 'false_positive', text: 'False positive', value: 'false_positive',
      content:
        <Header
          as="h5"
          content="Resolve as false positive"
          subheader={`This ${props.name} can be ignored because it's been incorrectly identified as ${props.name}.`}
        />
    },
    {
      key: 'wont_fix', text: "Won't fix", value: "wont_fix",
      content:
        <Header
          as="h5"
          content="Resolve as won't fix"
          subheader={`This ${props.name} will not be fixed.`}
        />
    }
  ];
  return (<Grid stackable>
    <Grid.Row columns={4}>
      <Grid.Column width={4}>
        <SingleChoiceInput
          label={`${props.name[0].toUpperCase()}${props.name.slice(1)} status`}
          options={options}
          readOnly={props.readOnly}
          set_value={(value) => props.set_entity_attribute(props.source_uuid, props.entity.key, "status", value)}
          value={props.status}
        />
      </Grid.Column>
      <Grid.Column width={12}>
        <TextInput
          label="Rationale"
          placeholder={`Rationale for ${props.name} status...`}
          readOnly={props.readOnly}
          set_value={(value) => props.set_entity_attribute(props.source_uuid, props.entity.key, "rationale", value)}
          value={props.rationale}
        />
      </Grid.Column>
    </Grid.Row>
  </Grid>);
}
