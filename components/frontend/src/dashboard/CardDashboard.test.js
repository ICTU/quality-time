import React from 'react';
import { act } from 'react-dom/test-utils';
import { mount } from 'enzyme';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { CardDashboard } from './CardDashboard';
import { MetricSummaryCard } from './MetricSummaryCard';

describe("<CardDashboard />", () => {
    it('returns null without cards', () => {
        const wrapper = mount(<CardDashboard cards={[]} />);
        expect(wrapper.instance()).toBe(null);
    });
});

describe("<CardDashboard />", () => {
    let mockCallback, wrapper;
    beforeEach(async () => {
        mockCallback = jest.fn();
        await act(async () => {
            wrapper = mount(
                <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                    <CardDashboard
                        cards={[<MetricSummaryCard red={1} green={2} yellow={1} white={0} grey={0} />]}
                        initial_layout={[{ h: 6, w: 4, x: 0, y: 0 }]}
                        save_layout={mockCallback}
                    />
                </Permissions.Provider>
            );
            wrapper.find("ReactGridLayout").at(0).prop("onDragStart")({}, {}, {}, {}, { clientX: 0, clientY: 0 });
            wrapper.setProps({})  // rerender
        });
    });
    it('saves the layout after drag', async () => {
        await act(async () => {
            wrapper.find("ReactGridLayout").at(0).prop("onLayoutChange")([{h: 6, w: 4, x: 200, y: 200}]);
        });
        expect(mockCallback).toHaveBeenCalled();
    });
    it('does not save the layout after click', async () => {
        await act(async () => {
            wrapper.find("div.react-draggable").at(0).simulate("click");
        });
        expect(mockCallback).not.toHaveBeenCalled();
    });
});
