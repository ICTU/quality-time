import React from 'react';
import ReactDOM from 'react-dom';
import { act } from 'react-dom/test-utils';
import { shallow } from 'enzyme';
import App from './App';

let container;

beforeAll(() => {
  global.EventSource = jest.fn(() => ({
    addEventListener: jest.fn(),
    close: jest.fn()
  }))
});

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
});

afterEach(() => {
  document.body.removeChild(container);
  container = null;
});

it('is loading datamodel and reports', async () => {
  await act(async () => { ReactDOM.render(<App />, container) });
  expect(container.querySelectorAll("div.loading").length).toBe(1);
});


describe("<App/>", () => {
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
    expect(wrapper.find('Container').find('Reports').exists()).toBe(false);
    expect(wrapper.find('Container').find('Report').exists()).toBe(false);
    expect(wrapper.find('Footer').exists()).toBe(true);
  });

  it('renders Reports', () => {
    const wrapper = shallow(<App />);
    wrapper.setState({ loading: false, report_uuid: '' });
    expect(wrapper.find('Container').find('Reports').exists()).toBe(true);
    expect(wrapper.find('Container').find('Report').exists()).toBe(false);
    expect(wrapper.find('Container').find('Segment').exists()).toBe(false);
  });

  it('renders Report', () => {
    const wrapper = shallow(<App />);
    wrapper.setState({ loading: false, report_uuid: 'id' });
    expect(wrapper.find('Container').find('Reports').exists()).toBe(false);
    expect(wrapper.find('Container').find('Report').exists()).toBe(true);
    expect(wrapper.find('Container').find('Segment').exists()).toBe(false);
  });

  it('sets the dashboard to visible on go home', () => {
    const wrapper = shallow(<App />);
    wrapper.instance().open_report(new Event('click'), "report_uuid");
    wrapper.instance().go_home();
    expect(wrapper.state('dashboard_visible')).toBe(true);
  });

  it('does not crash scrolling if there is no dashboard', () => {
    const wrapper = shallow(<App />);
    wrapper.instance().go_dashboard(new Event('click'));
    expect(wrapper.state('dashboard_visible')).toBe(true);
  });
  it('scrolls the dashboard', () => {
    const spy = jest.fn();
    Object.defineProperty(global.document, 'getElementById', { value: spy });
    const wrapper = shallow(<App />);
    wrapper.instance().go_dashboard(new Event('click'));
    expect(wrapper.state('dashboard_visible')).toBe(true);
    expect(spy).toHaveBeenCalled()
  });
});
