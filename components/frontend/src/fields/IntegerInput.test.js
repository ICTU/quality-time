import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { IntegerInput } from './IntegerInput';

describe("<IntegerInput />", () => {
  it('renders the value read only', () => {
      const wrapper = mount(<IntegerInput value="42" />);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("42");
      expect(wrapper.find("FormInput").prop("readOnly")).toBe(true);
  });
  it('renders the editable value', () => {
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <IntegerInput value="42" />
        </ReadOnlyContext.Provider>);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("42");
      expect(wrapper.find("FormInput").prop("readOnly")).toBe(false);
  });
  it('renders values less than the minimum as error', () => {
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <IntegerInput value="-42" min="0" />
        </ReadOnlyContext.Provider>);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("-42");
      expect(wrapper.find("FormInput").prop("error")).toBe(true);
  });
  it('renders values less than the minimum as error', () => {
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <IntegerInput value="42" max="10" />
        </ReadOnlyContext.Provider>);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("42");
      expect(wrapper.find("FormInput").prop("error")).toBe(true);
  });
  it('submits the changed value', () => {
      let mock_set_value = jest.fn();
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <IntegerInput value="42" set_value={mock_set_value} />
        </ReadOnlyContext.Provider>);
      wrapper.find("input").simulate("change", {target: {value: "10"}});
      wrapper.find("FormInput").simulate("submit");
      expect(mock_set_value).toHaveBeenCalled();
  });
  it('submits the changed value on blur', () => {
    let mock_set_value = jest.fn();
    const wrapper = mount(
      <ReadOnlyContext.Provider value={false}>
        <IntegerInput value="0" set_value={mock_set_value} />
      </ReadOnlyContext.Provider>);
    wrapper.find("input").simulate("change", {target: {value: "42"}});
    wrapper.find("input").simulate("blur");
    expect(mock_set_value).toHaveBeenCalled();
});
  it('does not submit an unchanged value', () => {
      let mock_set_value = jest.fn();
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <IntegerInput value="42" set_value={mock_set_value} />
        </ReadOnlyContext.Provider>);
      wrapper.find("input").simulate("change", {target: {value: "42"}});
      wrapper.find("FormInput").simulate("submit");
      expect(mock_set_value).toHaveBeenCalledTimes(0);
  });
  it('does not submit an invalid value', () => {
    let mock_set_value = jest.fn();
    const wrapper = mount(
      <ReadOnlyContext.Provider value={false}>
        <IntegerInput value="0" min="0" set_value={mock_set_value} />
      </ReadOnlyContext.Provider>);
    wrapper.find("input").simulate("change", {target: {value: "-42"}});
    wrapper.find("FormInput").simulate("submit");
    expect(mock_set_value).toHaveBeenCalledTimes(0);
  });
});