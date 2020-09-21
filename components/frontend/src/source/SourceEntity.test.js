import React from 'react';
import { Table } from 'semantic-ui-react';
import { mount } from 'enzyme';
import { SourceEntity } from './SourceEntity';

describe('<SourceEntity />', () => {
    it('renders', () => {
        const wrapper = mount(
            <Table>
                <Table.Body>
                    <SourceEntity
                        data_model={{ entities: { statuses: { unconfirmed: { default: true, ignore_entity: false } } } }}
                        entity_attributes={["attr"]} entity={{ key: "1" }} status="unconfirmed"
                    />
                </Table.Body>
            </Table>
        );
        expect(wrapper.find("TableRow").hasClass("status_unknown"));
    });

    it('does not render if hidden', () => {
        const wrapper = mount(
            <Table>
                <Table.Body>
                    <SourceEntity
                        data_model={{ entities: { statuses: { fixed: { default: true, ignore_entity: true } } } }}
                        entity_attributes={["attr"]} entity={{ key: "1" }} status="fixed" hide_ignored_entities={true}
                    />
                </Table.Body>
            </Table>
        );
        expect(wrapper.find("TableRow").length).toBe(0);
    });
});