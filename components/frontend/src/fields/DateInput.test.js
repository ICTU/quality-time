import React from 'react';
import { mount } from 'enzyme';
import { Permissions } from '../context/Permissions';
import { DateInput } from './DateInput';

function input_wrapper(props) {
    return mount(
        <Permissions.Provider value={false}>
            <DateInput {...props} />
        </Permissions.Provider>
    )
}
let mock_set_value;

describe("<DateInput />", () => {
    beforeEach(() => { mock_set_value = jest.fn(); });

    it('renders the value read only', () => {
        const wrapper = mount(<DateInput requiredPermissions={['test']} value="2019-09-30" />);
        expect(wrapper.find("FormInput").prop("value")).toStrictEqual("2019-09-30");
    });
    it('renders the editable value', () => {
        const wrapper = input_wrapper({ value: "2019-09-30" })
        expect(wrapper.find('EditableDateInput').prop("value")).toStrictEqual("2019-09-30");
    });
    it('renders in error state if a value is missing and required', () => {
        const wrapper = input_wrapper({ value: "", required: true });
        expect(wrapper.find("DateInput").at(1).prop("error")).toBe(true);
    });
    it('submits the value when changed', () => {
        const wrapper = input_wrapper({ value: "2019-09-30", set_value: mock_set_value })
        wrapper.find("input").simulate("change", { target: { value: "2020-01-02" } });
        wrapper.find("input").simulate("keydown", { key: "Enter" });
        expect(mock_set_value).toHaveBeenCalled();
    });
    it('does not submit the value when the value is not changed', () => {
        const wrapper = input_wrapper({ value: "2020-01-02", set_value: mock_set_value })
        wrapper.find("input").simulate("change", { target: { value: "2020-01-02" } });
        wrapper.find("input").simulate("keydown", { key: "Enter" });
        expect(mock_set_value).not.toHaveBeenCalled();
    });
});