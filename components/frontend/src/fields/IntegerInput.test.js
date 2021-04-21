import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { IntegerInput } from './IntegerInput';

function integerinput_wrapper(props) {
  return mount(
    <ReadOnlyContext.Provider value={false}>
      <IntegerInput {...props} />
    </ReadOnlyContext.Provider>
  )
}

let mock_set_value;

describe("<IntegerInput />", () => {
  beforeEach(() => { mock_set_value = jest.fn(); });

  it('renders the value read only', () => {
    const wrapper = mount(<IntegerInput requiredPermissions={['testPermission']}value="42" />);
    expect(wrapper.find("FormInput").prop("value")).toStrictEqual("42");
    expect(wrapper.find("FormInput").prop("readOnly")).toBe(true);
  });
  it('renders the editable value', () => {
    const wrapper = integerinput_wrapper({value: "42"});
    expect(wrapper.find("FormInput").prop("value")).toStrictEqual("42");
    expect(wrapper.find("FormInput").prop("readOnly")).toBe(false);
  });
  it('renders values less than the minimum as error', () => {
    const wrapper = integerinput_wrapper({value: "-42", min: "0"});
    expect(wrapper.find("FormInput").prop("value")).toStrictEqual("-42");
    expect(wrapper.find("FormInput").prop("error")).toBe(true);
  });
  it('renders values less than the minimum as error', () => {
    const wrapper = integerinput_wrapper({value: "42", max: "10"});
    expect(wrapper.find("FormInput").prop("value")).toStrictEqual("42");
    expect(wrapper.find("FormInput").prop("error")).toBe(true);
  });
  it('submits the changed value', () => {
    const wrapper = integerinput_wrapper({value: "42", set_value: mock_set_value});
    wrapper.find("input").simulate("change", {target: {value: "10"}});
    wrapper.find("FormInput").simulate("submit");
    expect(mock_set_value).toHaveBeenCalled();
  });
  it('submits the changed value on blur', () => {
    const wrapper = integerinput_wrapper({value: "0", set_value: mock_set_value});
    wrapper.find("input").simulate("change", {target: {value: "42"}});
    wrapper.find("input").simulate("blur");
    expect(mock_set_value).toHaveBeenCalledTimes(1);
  });
  it('does not submit an unchanged value', () => {
    const wrapper = integerinput_wrapper({value: "42", set_value: mock_set_value});
    wrapper.find("input").simulate("change", {target: {value: "42"}});
    wrapper.find("FormInput").simulate("submit");
    expect(mock_set_value).toHaveBeenCalledTimes(0);
  });
  it('does not submit a value that is too small', () => {
    const wrapper = integerinput_wrapper({value: "0", min: "0", set_value: mock_set_value});
    wrapper.find("input").simulate("change", {target: {value: "-42"}});
    wrapper.find("FormInput").simulate("submit");
    expect(mock_set_value).toHaveBeenCalledTimes(0);
  });
  it('does not accept an invalid value', () => {
    const wrapper = integerinput_wrapper({value: "0"});
    wrapper.find("input").simulate("change", {target: {value: "abc"}});
    expect(wrapper.find("FormInput").prop("value")).toStrictEqual("0");
  });
  it('undoes the change on escape', () => {
    const wrapper = integerinput_wrapper({value: "0", set_value: mock_set_value});
    wrapper.find("input").simulate("change", {target: {value: "42"}});
    wrapper.find("input").simulate("keydown", {key: "Escape"});
    wrapper.find("FormInput").simulate("submit");
    expect(mock_set_value).toHaveBeenCalledTimes(0);
  });
});