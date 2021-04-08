import React from 'react';
import { Table } from 'semantic-ui-react';
import { mount } from 'enzyme';
import { SourceEntity } from './SourceEntity';
import { ReadOnlyContext } from '../context/ReadOnly';

describe('<SourceEntity />', () => {
    it('render', () => {
        const wrapper = mount(
            <ReadOnlyContext.Provider value={[]}>
                <Table>
                    <Table.Body>
                        <SourceEntity entity_attributes={["attr"]} entity={{key:"1"}} />
                    </Table.Body>
                </Table>
            </ReadOnlyContext.Provider>);
        expect(wrapper.find("TableRow").hasClass("status_unknown"))
    });
});