import React from 'react';
import { mount } from 'enzyme';
import { MetricParameters } from './MetricParameters';

describe("<MetricParameters />", () => {
    it('renders', () => {
        const wrapper = mount(<MetricParameters
            datamodel={{ metrics: { violations: { unit: "violation", direction: "<", tags: ["tag"] } } }}
            metric={{type: "violations", tags: [], accept_debt: false}}
            metric_uuid="metric_uuid"
        />);
    });
});
