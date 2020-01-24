import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { SingleChoiceInput } from './SingleChoiceInput';

function input_wrapper(props) {
  return mount(
    <ReadOnlyContext.Provider value={false}>
      <SingleChoiceInput {...props} />
    </ReadOnlyContext.Provider>
  )
}
let mock_set_value;

describe("<SingleChoiceInput />", () => {
  beforeEach(() => { mock_set_value = jest.fn(); });

  it('renders the value read only', () => {
    const wrapper = mount(<SingleChoiceInput value="hello" options={[{text: "hello", value: "hello"}]} />);
    expect(wrapper.find("FormInput").prop("value")).toStrictEqual("hello");
  });
  it('renders the editable value', () => {
    const wrapper = input_wrapper({value: "hello", options: [{text: "hello", value: "hello"}]});
    expect(wrapper.find('FormDropdown').prop("value")).toStrictEqual("hello");
  });
  it('invokes the callback on a change', () => {
    const wrapper = input_wrapper(
      {value: "hello", options: [{text: "hello", value: "hello"}, {text: "hi", value: "hi"}], set_value: mock_set_value});
    wrapper.find("FormDropdown").at(0).simulate("click");
    wrapper.find("DropdownItem").at(1).simulate("click");
    expect(mock_set_value).toHaveBeenCalled();
  });
  it('does not invoke the callback when the value is not changed', () => {
    const wrapper = input_wrapper(
      {value: "hello", options: [{text: "hello", value: "hello"}, {text: "hi", value: "hi"}], set_value: mock_set_value});
    wrapper.find("FormDropdown").at(0).simulate("click");
    wrapper.find("DropdownItem").at(0).simulate("click");
    expect(mock_set_value).not.toHaveBeenCalled();
  });
});
