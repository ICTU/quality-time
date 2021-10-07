import React from 'react';
import { mount } from 'enzyme';
import { SourceStatus } from './SourceStatus';
import { DataModel } from '../context/Contexts';

const metric = { sources: { source_uuid: { name: "Source name" } } };

describe("<SourceStatus />", () => {
    it('renders the hyperlink label if the the source has a landing url', () => {
        const wrapper = mount(<DataModel.Provider value={{}}><SourceStatus
            metric={metric} measurement_source={{ landing_url: "https://landing" }} source_uuid="source_uuid"
        /></DataModel.Provider>);
        expect(wrapper.find("HyperLink").text()).toBe("Source name");
    });
    it('renders the source label if there is no error', () => {
        const wrapper = mount(<DataModel.Provider value={{}}><SourceStatus
            metric={metric} measurement_source={{}} source_uuid="source_uuid"
        /></DataModel.Provider>);
        expect(wrapper.text()).toBe("Source name");
    });
    it('renders the source label if there is an error', () => {
        const wrapper = mount(<DataModel.Provider value={{}}><SourceStatus
            metric={metric} measurement_source={{ connection_error: "error" }} source_uuid="source_uuid"
        /></DataModel.Provider>);
        expect(wrapper.find("Popup").text()).toBe("Source name");
    });
});
