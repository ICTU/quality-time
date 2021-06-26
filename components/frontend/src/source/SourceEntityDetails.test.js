import React from 'react';
import { mount } from 'enzyme';
import { EDIT_ENTITY_PERMISSION, Permissions } from '../context/Permissions';
import * as source from '../api/source';
import { SourceEntityDetails } from './SourceEntityDetails';

jest.mock("../api/source.js")

describe('<SourceEntityDetails />', () => {
    beforeEach(() => { source.set_source_entity_attribute = jest.fn(); });
    it('invokes the callback on changing the status', () => {
        const wrapper = mount(
            <Permissions.Provider value={[EDIT_ENTITY_PERMISSION]}>
                <SourceEntityDetails entity={{key: "key"}} status="unconfirmed" name="violation" />
            </Permissions.Provider>);
        wrapper.find("div.item").at(1).simulate("click");
        expect(source.set_source_entity_attribute).toHaveBeenCalled();
    });
    it('invokes the callback on changing the comment', () => {
        const wrapper = mount(
            <Permissions.Provider value={[EDIT_ENTITY_PERMISSION]}>
                <SourceEntityDetails entity={{key: "key"}} status="unconfirmed" name="violation" />
            </Permissions.Provider>);
        wrapper.find("textarea").at(0).simulate("change", {target: {value: "comment"}});
        wrapper.find("TextInput").at(0).simulate("submit");
        expect(source.set_source_entity_attribute).toHaveBeenCalled();
    });
});
