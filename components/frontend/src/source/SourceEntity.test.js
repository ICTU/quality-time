import React from 'react';
import { Table } from 'semantic-ui-react';
import { mount } from 'enzyme';
import { SourceEntity } from './SourceEntity';

const data_model = { sources: {} };

function source_entity(status = "confirmed", hide_ignored_entities = false) {
    return (
        mount(
            <Table>
                <Table.Body>
                    <SourceEntity
                        data_model={data_model} entity_attributes={["attr"]} entity={{ key: "1" }}
                        status={status} hide_ignored_entities={hide_ignored_entities} />
                </Table.Body>
            </Table>
        )
    )
}

describe('<SourceEntity />', () => {
    it('renders', () => {
        const wrapper = source_entity();
        expect(wrapper.find("TableRow").hasClass("status_unknown"))
    });
    it('renders a line through the entity if the the entity is marked as false positive', () => {
        const wrapper = source_entity("false_positive");
        expect(wrapper.find("TableRow").prop("style")).toHaveProperty("textDecoration", "line-through");
    });
    it('does not render the entity if the the entity is marked as false positive and hidden', () => {
        const wrapper = source_entity("false_positive", true);
        expect(wrapper.find("SourceEntity").isEmptyRender()).toBe(true);
    });
});