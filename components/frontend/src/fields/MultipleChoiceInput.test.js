import React from 'react';
import { mount } from 'enzyme';
import { Permissions } from '../context/Permissions';
import { MultipleChoiceInput } from './MultipleChoiceInput';

function input_wrapper(props) {
  return mount(
    <Permissions.Provider value={false}>
      <MultipleChoiceInput {...props} />
    </Permissions.Provider>
  )
}
let mock_set_value;

describe("<MultipleChoiceInput />", () => {
  beforeEach(() => { mock_set_value = jest.fn(); });

  it('renders the value read only', () => {
    const wrapper = mount(<MultipleChoiceInput requiredPermissions={["testPermission"]} value={["hello", "world"]} options={["hello", "again"]} />);
    expect(wrapper.find("FormInput").prop("value")).toStrictEqual("hello, world");
  });
  it('renders the editable value', () => {
    const wrapper = input_wrapper({ value: ["hello"], options: ["hello", "again"] });
    expect(wrapper.find('FormDropdown').prop("value")).toStrictEqual(["hello"]);
  });
  it('renders a missing editable value', () => {
    const wrapper = input_wrapper({ options: ["hello", "again"] });
    expect(wrapper.find('FormDropdown').prop("value")).toStrictEqual([]);
  });
  it('invokes the callback with correct parameters on adding a new choice', () => {
    const nativeEvent = { nativeEvent: { stopImmediatePropagation: () => {/*Dummy implementation*/} } }
    const wrapper = input_wrapper({ allowAdditions: true, value: ["hello"], options: ["hello", "hi", "ho"], set_value: mock_set_value });
    wrapper.find("input").simulate("change", {target: {value: "ciao"}});
    wrapper.find("DropdownItem").simulate("click", nativeEvent);
    expect(mock_set_value).toHaveBeenCalledWith(["hello", "ciao"]);
  });
  it('invokes the callback with correct parameters on adding an existing choice', () => {
    const nativeEvent = { nativeEvent: { stopImmediatePropagation: () => {/*Dummy implementation*/} } }
    const wrapper = input_wrapper({ allowAdditions: true, value: ["hello"], options: ["hello", "hi", "ho"], set_value: mock_set_value });
    wrapper.find("DropdownItem").at(0).simulate("click", nativeEvent);
    expect(mock_set_value).toHaveBeenCalledWith(["hello", "hi"]);
  });
});