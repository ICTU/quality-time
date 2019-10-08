import React from 'react';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import { shallow } from 'enzyme';
import { SourceParameter } from './SourceParameter';

Enzyme.configure({ adapter: new Adapter() });

var example_report={"subjects": [{"metrics": [{"sources": [{"type": "x", "parameters": {"key": "b"}}]}]}]}

it('renders url type', () => {
  const wrapper = shallow(<SourceParameter placeholder="place-holder" readOnly={true} parameter_name="name"
                            required={false} source_uuid="source-uuid" parameter_key="key"
                            parameter_type="url" reload="reload-" parameter_value="value-" warning={true}
                            source={{"type": "x"}} report={example_report}/>);

  expect(wrapper.find('StringInput').prop('label')).toBe("name");
  expect(Array.from(wrapper.find('StringInput').prop('options'))).toStrictEqual(["b"]);
  expect(wrapper.find('StringInput').prop('placeholder')).toBe("place-holder");
  expect(wrapper.find('StringInput').prop('readOnly')).toBe(true);
  expect(wrapper.find('StringInput').prop('required')).toBe(false);
  expect(wrapper.find('StringInput').prop('value')).toBe('value-');
  expect(wrapper.find('StringInput').prop('warning')).toBe(true);
});

it('renders string type', () => {
    const wrapper = shallow(<SourceParameter parameter_type="string" source={{"type": "x"}} report={example_report}/>);
    expect(wrapper.find('StringInput').exists()).toBe(true);
});
