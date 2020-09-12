import React from 'react';
import { Table } from 'semantic-ui-react';
import { mount } from 'enzyme';
import { SourceEntity } from './SourceEntity';

describe('<SourceEntity />', () => {
    it('render', () => {
        const wrapper = mount(
            <Table>
                <Table.Body>
                    <SourceEntity
                        data_model={{ entities: { default: { status: { unconfirmed: { ignore_entity: false } } } } }}
                        entity_attributes={["attr"]} entity={{ key: "1" }} status="unconfirmed"
                    />
                </Table.Body>
            </Table>
        );
        expect(wrapper.find("TableRow").hasClass("status_unknown"));
    });
});