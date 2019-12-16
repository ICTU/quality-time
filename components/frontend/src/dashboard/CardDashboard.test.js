import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext} from '../context/ReadOnly';
import { CardDashboard } from './CardDashboard';
import { MetricSummaryCard } from './MetricSummaryCard';

describe("<CardDashboard />", () => {
    it('returns null without cards', () => {
        const wrapper = mount(<CardDashboard cards={[]} />);
        expect(wrapper.instance()).toBe(null);
    });
});

describe("<CardDashboard />", () => {
    var mockCallBack, wrapper;
    beforeEach(() => {
        mockCallBack = jest.fn();
        wrapper = mount(
            <ReadOnlyContext.Provider value={false}>
                <CardDashboard
                    cards={[<MetricSummaryCard red={1} green={2} yellow={1} white={0} grey={0} />]}
                    initial_layout={[]}
                    save_layout={mockCallBack}
                />
            </ReadOnlyContext.Provider>
        );
    });
    it('calls the callback on drag', () => {
        wrapper.find("div.react-draggable").at(0).simulate("drag");
        expect(mockCallBack).toHaveBeenCalled();
    });
    it('calls the callback on click', () => {
        wrapper.find("div.react-draggable").at(0).simulate("click");
        expect(mockCallBack).toHaveBeenCalled();
    });
});
