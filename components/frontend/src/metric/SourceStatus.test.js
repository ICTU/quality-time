import React from 'react';
import { mount } from 'enzyme';
import { SourceStatus } from './SourceStatus';

describe("<SourceStatus />", () => {
    it('renders the hyperlink label if the the source has a landing url', () => {
        const wrapper = mount(<SourceStatus
            datamodel={{}} metric={{ sources: { source_uuid: { name: "Source name", landing_url: "https://landing" } } }}
            source={{}} source_uuid="source_uuid"
        />);
        expect(wrapper.text()).toBe("Source name");
    });
    it('renders the source label if there is no error', () => {
        const wrapper = mount(<SourceStatus
            datamodel={{}} metric={{ sources: { source_uuid: { name: "Source name" } } }}
            source={{}} source_uuid="source_uuid"
        />);
        expect(wrapper.text()).toBe("Source name");
    });
    it('renders the source label if there is an error', () => {
        const wrapper = mount(<SourceStatus
            datamodel={{}} metric={{ sources: { source_uuid: { name: "Source name" } } }}
            source={{ connection_error: "error" }} source_uuid="source_uuid"
        />);
        expect(wrapper.find("Popup").text()).toBe("Source name");
    });
});
