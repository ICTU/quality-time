import React from 'react';
import { mount } from 'enzyme';
import { MetricParameters } from './MetricParameters';

const data_model = {
    metrics: {
        violations: {
            unit: "violation", direction: "<", tags: ["tag"], name: "Violations"
        }
    }
};

describe("<MetricParameters />", () => {
    it('renders the default metric name', () => {
        const wrapper = mount(<MetricParameters
            datamodel={data_model}
            metric={{type: "violations", tags: [], accept_debt: false}}
            metric_uuid="metric_uuid"
        />);
        expect(wrapper.find("HeaderContent").text()).toBe("Violations");
    });
});
