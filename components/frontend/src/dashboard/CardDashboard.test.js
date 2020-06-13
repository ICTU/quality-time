import React from 'react';
import { act } from 'react-dom/test-utils';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { CardDashboard } from './CardDashboard';
import { MetricSummaryCard } from './MetricSummaryCard';

describe("<CardDashboard />", () => {
    it('returns null without cards', () => {
        const wrapper = mount(<CardDashboard cards={[]} />);
        expect(wrapper.instance()).toBe(null);
    });
});

describe("<CardDashboard />", () => {
    it('saves the layout after drag', async () => {
        let wrapper;
        let mockCallBack = jest.fn();
        await act(async () => {
            wrapper = mount(
                <ReadOnlyContext.Provider value={false}>
                    <CardDashboard
                        cards={[<MetricSummaryCard red={1} green={2} yellow={1} white={0} grey={0} />]}
                        initial_layout={[{ h: 6, w: 4, x: 0, y: 0 }]}
                        save_layout={mockCallBack}
                    />
                </ReadOnlyContext.Provider>
            );
            wrapper.find("ReactGridLayout").at(0).prop("onDragStart")({}, {}, {}, {}, { clientX: 0, clientY: 0 });
            wrapper.setProps({})  // rerender
        });
        await act(async () => {
            wrapper.find("ReactGridLayout").at(0).prop("onLayoutChange")([{h: 6, w: 4, x: 200, y: 200}]);
        });
        expect(mockCallBack).toHaveBeenCalled();
    });
    it('does not save the layout after click', async () => {
        let wrapper;
        let mockCallBack = jest.fn();
        await act(async () => {
            wrapper = mount(
                <ReadOnlyContext.Provider value={false}>
                    <CardDashboard
                        cards={[<MetricSummaryCard red={1} green={2} yellow={1} white={0} grey={0} />]}
                        initial_layout={[{ h: 6, w: 4, x: 0, y: 0 }]}
                        save_layout={mockCallBack}
                    />
                </ReadOnlyContext.Provider>
            );
            wrapper.find("ReactGridLayout").at(0).prop("onDragStart")({}, {}, {}, {}, { clientX: 100, clientY: 100 });
            wrapper.setProps({})  // rerender
        });
        await act(async () => {
            wrapper.find("div.react-draggable").at(0).simulate("click");
        });
        expect(mockCallBack).not.toHaveBeenCalled();
    });
});
