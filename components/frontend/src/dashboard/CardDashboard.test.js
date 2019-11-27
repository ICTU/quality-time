import React from 'react';
import { mount } from 'enzyme';
import { CardDashboard } from './CardDashboard';
import { MetricSummaryCard } from './MetricSummaryCard'

describe("<CardDashboard />", () => {
    it('calls the callback on drag', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(<CardDashboard
            cards={[<MetricSummaryCard red={1} green={2} yellow={1} white={0} grey={0} />]}
            initial_layout={[]}
            save_layout={mockCallBack}
        />);
        wrapper.find("div.react-draggable").at(0).simulate("drag");
        expect(mockCallBack).toHaveBeenCalled();
    });
});
