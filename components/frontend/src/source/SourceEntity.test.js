import React from 'react';
import { Table } from 'semantic-ui-react';
import { mount } from 'enzyme';
import { SourceEntity } from './SourceEntity';

describe('<SourceEntity />', () => {
    it('render', () => {
        const wrapper = mount(
            <Table>
                <Table.Body>
                    <SourceEntity entity_attributes={["attr"]} entity={{ key: "1" }} status={"confirmed"} />
                </Table.Body>
            </Table>
        );
        expect(wrapper.find("TableRow").hasClass("status_unknown"))
    });
});