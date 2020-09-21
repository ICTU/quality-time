import React from 'react';
import ReactDOM from 'react-dom';
import { act } from 'react-dom/test-utils';
import { mount, shallow } from 'enzyme';
import { Action } from 'history';
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

  it('does not crash scrolling if there is no dashboard', () => {
    const wrapper = shallow(<App />);
    wrapper.instance().go_dashboard(new Event('click'));
  });

  it('scrolls the dashboard', () => {
    const scrollIntoView = jest.fn();
    scrollIntoView.mockImplementation(() => { return { scrollIntoView: jest.fn() } });
    Object.defineProperty(global.document, 'getElementById', { value: scrollIntoView });
    Object.defineProperty(global.window, 'scrollBy', { value: jest.fn() });
    const wrapper = shallow(<App />);
    wrapper.instance().go_dashboard(new Event('click'));
    expect(scrollIntoView).toHaveBeenCalled()
  });

  it('sets the user', () => {
    const wrapper = mount(<App />);
    wrapper.instance().set_user("admin", "email@example.org");
    expect(wrapper.state("user")).toBe("admin");
    expect(wrapper.state("email")).toBe("email@example.org");
    wrapper.instance().set_user(null);
    expect(wrapper.state("user")).toBe(null);
    expect(wrapper.state("email")).toBe(null);
  });

  it('resets the user when the session is expired', () => {
    const wrapper = mount(<App />);
    wrapper.instance().set_user("admin", "email@example.org");
    wrapper.instance().check_session({ ok: true });
    expect(wrapper.state("user")).toBe("admin");
    wrapper.instance().check_session({ ok: false, status: 401 });
    expect(wrapper.state("user")).toBe(null);
  });

  it('listens to history pop events', () => {
    const wrapper = mount(<App />);
    wrapper.instance().open_report({ preventDefault: jest.fn }, "report1");
    expect(wrapper.state("report_uuid")).toBe("report1");
    wrapper.instance().on_history({ location: {pathname: "/"}, action: Action.Pop });  // simulate user hitting "back"
    expect(wrapper.state("report_uuid")).toBe("");
  });
});
