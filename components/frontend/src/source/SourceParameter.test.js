import React from 'react';
import Enzyme, { shallow } from 'enzyme';
import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import { SourceParameter } from './SourceParameter';

Enzyme.configure({ adapter: new Adapter() });

const example_report={"subjects": [{"metrics": [{"sources": [{"type": "x", "parameters": {"key": "b"}}]}]}]}

it('renders url type', () => {
  const wrapper = shallow(<SourceParameter placeholder="place-holder" readOnly={true} parameter_name="name"
                            required={false} source_uuid="source-uuid" parameter_key="key"
                            parameter_type="url" reload="reload-" parameter_value="value-" warning={true}
                            source={{"type": "x"}} report={example_report}/>);

  expect(wrapper.find('StringInput').prop('label')).toBe("name");
  expect(Array.from(wrapper.find('StringInput').prop('options'))).toStrictEqual(["b"]);
  expect(wrapper.find('StringInput').prop('placeholder')).toBe("place-holder");
  expect(wrapper.find('StringInput').prop('required')).toBe(false);
  expect(wrapper.find('StringInput').prop('set_value').toString().includes('set_source_parameter')).toBe(true);
  expect(wrapper.find('StringInput').prop('value')).toBe('value-');
  expect(wrapper.find('StringInput').prop('warning')).toBe(true);
});

it('renders string type', () => {
    const example_report_local={"subjects": [{"metrics": [{"sources": [{"type": "x", "parameters": {"key": ["a", "b"]}}]}]}]}
    const wrapper = shallow(<SourceParameter parameter_type="string" help_url="help-"
                              parameter_name="name" parameter_key="key" source={{"type": "x"}}
                              report={example_report_local}/>);
    expect(wrapper.find('StringInput').prop('label').type).toEqual('label');
    expect(wrapper.find('StringInput').prop('label').props.children[0]).toEqual('name');
    expect(Array.from(wrapper.find('StringInput').prop('options'))).toStrictEqual(["a", "b"]);
});

it('renders password type', () => {
  const wrapper = shallow(<SourceParameter parameter_type="password"/>);
  expect(wrapper.find('PasswordInput').exists()).toBe(true);
});

it('renders integer type', () => {
  const wrapper = shallow(<SourceParameter parameter_type="integer" parameter_max="10" parameter_min="1" parameter_unit="mg"/>);
  expect(wrapper.find('IntegerInput').exists()).toBe(true);
  expect(wrapper.find('IntegerInput').prop('max')).toBe("10");
  expect(wrapper.find('IntegerInput').prop('min')).toBe("1");
  expect(wrapper.find('IntegerInput').prop('unit')).toBe('mg');
});

it('renders multiple choice type', () => {
  const wrapper = shallow(<SourceParameter parameter_type="multiple_choice_with_addition" source={{"type": "x"}} report={example_report}/>);
  expect(wrapper.find('MultipleChoiceInput').exists()).toBe(true);
});

it('renders date type', () => {
  const wrapper = shallow(<SourceParameter parameter_type="date"/>);
  expect(wrapper.find('DateInput').exists()).toBe(true);
});

it('renders multiple choice type', () => {
  const wrapper = shallow(<SourceParameter parameter_type="multiple_choice" source={{"type": "x"}} report={example_report}/>);
  expect(wrapper.find('MultipleChoiceInput').exists()).toBe(true);
});
it('renders null, if unknown', () => {
  const wrapper = shallow(<SourceParameter parameter_type="UNKNOWN type" source={{"type": "x"}} report={example_report}/>);
  expect(wrapper).toEqual({});
});
