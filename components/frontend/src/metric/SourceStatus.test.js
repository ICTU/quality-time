import React from 'react';
import { mount } from 'enzyme';
import { SourceStatus } from './SourceStatus';

const data_model = {};

const metric = { sources: { source_uuid: { name: "Source name", landing_url: "https://landing" } } };

describe("<SourceStatus />", () => {
    it('renders the source label if there is no error', () => {
        const wrapper = mount(<SourceStatus
            datamodel={data_model} metric={metric} source={{}} source_uuid="source_uuid"
        />);
        expect(wrapper.text()).toBe("Source name");
    });
    it('renders the source label if there is an error', () => {
        const wrapper = mount(<SourceStatus
            datamodel={data_model} metric={metric} source={{ connection_error: "error" }} source_uuid="source_uuid"
        />);
        expect(wrapper.find("Popup").text()).toBe("Source name");
    });
});
