import React from 'react';
import ReactDOM from 'react-dom';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import { shallow } from 'enzyme';
import App from './App';

Enzyme.configure({ adapter: new Adapter() });

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<App />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders all components, while loading', () => {
  const wrapper = shallow(<App />);
  expect(wrapper.find('Menubar').exists()).toBe(true);
  expect(wrapper.find('SemanticToastContainer').exists()).toBe(true);
  expect(wrapper.find('Container').exists()).toBe(true);
  expect(wrapper.find('Container').find('Segment').exists()).toBe(true);
  expect(wrapper.find('Footer').exists()).toBe(true);
});
