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

  it('goes home', () => {
    const wrapper = mount(<App />);
    wrapper.instance().open_report({ preventDefault: jest.fn }, "report1");
    expect(wrapper.state("report_uuid")).toBe("report1");
    wrapper.instance().go_home();
    expect(wrapper.state("report_uuid")).toBe("");
  })

  it('sets the user', () => {
    const wrapper = mount(<App />);
    wrapper.instance().set_user("admin", "email@example.org", new Date(Date.parse("3000-02-23T22:00:50.945872+00:00")));
    expect(wrapper.state("user")).toBe("admin");
    expect(localStorage.getItem("user")).toBe("admin");
    expect(wrapper.state("email")).toBe("email@example.org");
    expect(localStorage.getItem("email")).toBe("email@example.org");
    expect(localStorage.getItem("session_expiration_datetime")).toBe("3000-02-23T22:00:50.945Z");
    wrapper.instance().set_user(null);
    expect(wrapper.state("user")).toBe(null);
    expect(localStorage.getItem("user")).toBe(null);
    expect(wrapper.state("email")).toBe(null);
    expect(localStorage.getItem("email")).toBe(null);
    expect(localStorage.getItem("session_expiration_datetime")).toBe(null);
  });

  it('resets the user when the session is expired on mount', () => {
    localStorage.setItem("session_expiration_datetime", "2000-02-23T22:00:50.945Z")
    localStorage.setItem("user", "admin")
    localStorage.setItem("email", "admin@example.org")
    const wrapper = mount(<App />);
    expect(wrapper.state("user")).toBe(null);
    expect(localStorage.getItem("user")).toBe(null);
    expect(wrapper.state("email")).toBe(null);
    expect(localStorage.getItem("email")).toBe(null);
    expect(localStorage.getItem("session_expiration_datetime")).toBe(null);
  });

  it('does not reset the user when the session is not expired on mount', () => {
    localStorage.setItem("session_expiration_datetime", "3000-02-23T22:00:50.945Z")
    localStorage.setItem("user", "admin")
    localStorage.setItem("email", "admin@example.org")
    const wrapper = mount(<App />);
    expect(wrapper.state("user")).toBe("admin");
    expect(localStorage.getItem("user")).toBe("admin");
    expect(wrapper.state("email")).toBe("admin@example.org");
    expect(localStorage.getItem("email")).toBe("admin@example.org");
    expect(localStorage.getItem("session_expiration_datetime")).toBe("3000-02-23T22:00:50.945Z");
  });

  it('resets the user when the session is expired', () => {
    const wrapper = mount(<App />);
    wrapper.instance().set_user("admin", "email@example.org", new Date(Date.parse("3000-02-23T22:00:50.945872+00:00")));
    wrapper.instance().check_session({ ok: true });
    expect(wrapper.state("user")).toBe("admin");
    wrapper.instance().check_session({ ok: false, status: 401 });
    expect(wrapper.state("user")).toBe(null);
  });

  it('listens to history pop events', () => {
    const wrapper = mount(<App />);
    wrapper.instance().open_report({ preventDefault: jest.fn }, "report1");
    expect(wrapper.state("report_uuid")).toBe("report1");
    wrapper.instance().on_history({ location: { pathname: "/" }, action: Action.Pop });  // simulate user hitting "back"
    expect(wrapper.state("report_uuid")).toBe("");
  });

  it('handles a date change', () => {
    const wrapper = mount(<App />);
    wrapper.instance().handleDateChange({}, {name: "report_date_string", value: "13-03-2020"})
    expect(wrapper.state("report_date_string")).toBe("13-03-2020");
  });

  it('handles a date change to today', () => {
    const wrapper = mount(<App />);
    const today = new Date();
    const today_string = String(today.getDate()).padStart(2, '0') + '-' + String(today.getMonth() + 1).padStart(2, '0') + '-' + today.getFullYear();
    wrapper.instance().handleDateChange({}, {name: "report_date_string", value: today_string})
    expect(wrapper.state("report_date_string")).toBe("");
  })
});
