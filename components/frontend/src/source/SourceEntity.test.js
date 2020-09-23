import React from 'react';
import { Table } from 'semantic-ui-react';
import { mount } from 'enzyme';
import { SourceEntity } from './SourceEntity';

describe('<SourceEntity />', () => {
    it('renders', () => {
        const wrapper = mount(
            <Table>
                <Table.Body>
                    <SourceEntity entity_attributes={["attr"]} entity={{ key: "1" }} status={"confirmed"} />
                </Table.Body>
            </Table>
        );
        expect(wrapper.find("TableRow").hasClass("status_unknown"))
    });
    it('renders a line through the entity if the the entity is marked as false positive', () => {
        const wrapper = mount(
            <Table>
                <Table.Body>
                    <SourceEntity entity_attributes={["attr"]} entity={{ key: "1" }} status={"false_positive"} />
                </Table.Body>
            </Table>
        );
        expect(wrapper.find("TableRow").prop("style")).toHaveProperty("textDecoration", "line-through");
    });
    it('does not render the entity if the the entity is marked as false positive and hidden', () => {
        const wrapper = mount(
            <Table>
                <Table.Body>
                    <SourceEntity entity_attributes={["attr"]} entity={{ key: "1" }} status={"false_positive"} hide_ignored_entities={true} />
                </Table.Body>
            </Table>
        );
        expect(wrapper.find("SourceEntity").isEmptyRender()).toBe(true);
    });
});