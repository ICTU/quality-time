import React from 'react';
import { shallow } from 'enzyme';
import { ReadOnlyContext, ReadOnlyOrEditable } from './ReadOnly';

function MockComponent() { return ("Hi") }
function MockComponent2() { return ("Two") }

describe("<ReadOnly />", () => {
  it('provides the read only context to components', () => {
    const wrapper = shallow(
      <ReadOnlyContext.Provider value={false}>
        <ReadOnlyContext.Consumer>{(readOnly) => (<MockComponent readOnly={readOnly} />)}</ReadOnlyContext.Consumer>
      </ReadOnlyContext.Provider>);
    expect(wrapper.dive().find('MockComponent').prop("readOnly")).toBe(false);
  });
});

describe("<ReadOnlyOrEditable />", () => {
  it('shows the read only component', () => {
    const wrapper = shallow(
      <ReadOnlyOrEditable readOnlyComponent={<MockComponent/>} editableComponent={<MockComponent2/>} />)
    expect(wrapper.dive().name()).toBe("MockComponent");
  });
  it('shows the editable only component', () => {
    const wrapper = shallow(
      <ReadOnlyContext.Provider value={false}>
        <ReadOnlyOrEditable readOnlyComponent={<MockComponent/>} editableComponent={<MockComponent2/>} />
      </ReadOnlyContext.Provider>);
    expect(wrapper.dive().dive().name()).toBe("MockComponent2");
  });
});
