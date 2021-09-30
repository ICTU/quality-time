import React from 'react';
import { mount } from 'enzyme';
import { Permissions } from '../context/Permissions';
import { Input } from './Input';

function input_wrapper(props) {
    return mount(
        <Permissions.Provider value={false}>
            <Input {...props} />
        </Permissions.Provider>
    )
}
let mock_set_value;

describe("<Input />", () => {
    beforeEach(() => { mock_set_value = jest.fn(); });

    it('renders the value read only', () => {
        const wrapper = mount(<Input requiredPermissions={['test']} value="Hello" />);
        expect(wrapper.find("FormInput").prop("value")).toStrictEqual("Hello");
        expect(wrapper.find("FormInput").prop("readOnly")).toBe(true);
    });
    it('renders the editable value', () => {
        const wrapper = input_wrapper({ value: "Hello" });
        expect(wrapper.find("FormInput").prop("value")).toStrictEqual("Hello");
        expect(wrapper.find("FormInput").prop("readOnly")).toBe(false);
    });
    it('renders in error state if a value is missing and required', () => {
        const wrapper = input_wrapper({ value: "", required: true });
        expect(wrapper.find("FormInput").prop("error")).toBe(true);
    });
    it('renders in error state if the warning props is true', () => {
        const wrapper = input_wrapper({ value: "Hello", warning: true });
        expect(wrapper.find("FormInput").prop("error")).toBe(true);
    });
    it('submits the value when changed', () => {
        const wrapper = input_wrapper({ value: "Hello", set_value: mock_set_value });
        wrapper.find("input").simulate("change", { target: { value: "Ciao" } });
        wrapper.find("input").simulate("keydown", { key: "Enter" });
        expect(mock_set_value).toHaveBeenCalled();
    });
    it('submits the value when blurred', () => {
        const wrapper = input_wrapper({ value: "Hello", set_value: mock_set_value });
        wrapper.find("input").simulate("change", { target: { value: "Ciao" } });
        wrapper.find("input").simulate("blur");
        expect(mock_set_value).toHaveBeenCalled();
    });
    it('does not submit the value when it is unchanged', () => {
        const wrapper = input_wrapper({ value: "Hello", set_value: mock_set_value });
        wrapper.find("input").simulate("keydown", { key: "Enter" });
        expect(mock_set_value).toHaveBeenCalledTimes(0);
    });
    it('renders the initial value on escape and does not submit', () => {
        const wrapper = input_wrapper({ value: "Hello", set_value: mock_set_value });
        wrapper.find("input").simulate("change", { target: { value: "Ciao" } });
        wrapper.find("input").simulate("keydown", { key: "Escape" });
        expect(wrapper.find("FormInput").prop("value")).toStrictEqual("Hello");
        expect(mock_set_value).toHaveBeenCalledTimes(0);
    })
})