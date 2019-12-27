import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import * as source_api from '../api/source';
import { Source } from './Source';

jest.mock("../api/source.js");

const datamodel = {
    metrics: { metric_type: { sources: ["source_type"] } },
    sources: { source_type: { name: "Source type", parameters: {} } }
};
const source = { type: "source_type" };
const report = { report_uuid: "report_uuid" };

function source_wrapper() {
    return mount(
        <ReadOnlyContext.Provider value={false}>
            <Source datamodel={datamodel} metric_type="metric_type" report={report} source={source} />
        </ReadOnlyContext.Provider>
    )
}

describe('<Source />', () => {
    beforeEach(() => { source.set_source_entity_attribute = jest.fn(); });
    it('invokes the callback on clicking copy', () => {
        const wrapper = source_wrapper();
        wrapper.find("CopyButton").at(0).simulate("click");
        expect(source_api.copy_source).toHaveBeenCalled();
    });
    it('invokes the callback on clicking delete', () => {
        const wrapper = source_wrapper();
        wrapper.find("DeleteButton").at(0).simulate("click");
        expect(source_api.delete_source).toHaveBeenCalled();
    });
});