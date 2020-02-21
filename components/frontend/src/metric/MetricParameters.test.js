import React from 'react';
import { mount } from 'enzyme';
import { MetricParameters } from './MetricParameters';

const data_model = {
    metrics: {
        violations: { unit: "violation", direction: "<", name: "Violations" }
    }
};

const report = { summary_by_tag: { } }

describe("<MetricParameters />", () => {
    it('renders the default metric name', () => {
        const wrapper = mount(<MetricParameters
            datamodel={data_model} report={report}
            metric={{type: "violations", tags: [], accept_debt: false}}
            metric_uuid="metric_uuid"
        />);
        expect(wrapper.find("HeaderContent").text()).toBe("Violations");
    });
});
