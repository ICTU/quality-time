import React from 'react';
import { mount } from 'enzyme';
import { DatePicker } from './DatePicker';

let mockCallback;
let wrapper;

describe('<DatePicker />', () => {
    beforeEach(() => {
        mockCallback = jest.fn();
        wrapper = mount(<DatePicker onDate={mockCallback} name="report_date_string" value={"20-07-2020"} label="Report date" />);
    });

    it('calls the callback on date pick', () => {
        wrapper.find("input").simulate("change", { target: { name: "report_date_string", value: "21-07-2020" } });
        wrapper.find("input").simulate("keydown", { key: "Enter" });
        expect(mockCallback).toHaveBeenCalled();
    });
    it('does not call the callback on an invalid date', () => {
        wrapper.find("input").simulate("change", { target: { name: "report_date_string", value: "21-21-2020" } });
        wrapper.find("input").simulate("keydown", { key: "Enter" });
        expect(mockCallback).not.toHaveBeenCalled();
    });
    it('does not call the callback when the value is not a date', () => {
        wrapper.find("input").simulate("change", { target: { name: "report_date_string", value: "not a date" } });
        wrapper.find("input").simulate("keydown", { key: "Enter" });
        expect(mockCallback).not.toHaveBeenCalled();
    });
    it('calls the callback on clear', () => {
        wrapper.find("Icon").simulate("click")
        expect(mockCallback).toHaveBeenCalled();
    });
});
