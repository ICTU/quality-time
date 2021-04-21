import React from 'react';
import { shallow } from 'enzyme';
import { ReadOnlyContext, ReadOnlyOrEditable } from './ReadOnly';

function MockComponent() { return ("Hi") }
function MockComponent2() { return ("Two") }

describe("<ReadOnly />", () => {
  it('provides the read only context to components', () => {
    const wrapper = shallow(
      <ReadOnlyContext.Provider value={['mockPermission']}>
        <ReadOnlyContext.Consumer>{(permissions) => (<MockComponent permissions={permissions} />)}</ReadOnlyContext.Consumer>
      </ReadOnlyContext.Provider>);
    expect(wrapper.dive().find('MockComponent').prop("permissions")).toStrictEqual(['mockPermission']);
  });
});

describe("<ReadOnlyOrEditable />", () => {
  it('shows the read only component if no permissions are present', () => {
    const wrapper = shallow(
      <ReadOnlyContext.Provider value={[]}>
        <ReadOnlyOrEditable requiredPermissions={['mockPermission']} readOnlyComponent={<MockComponent/>} editableComponent={<MockComponent2/>} />
      </ReadOnlyContext.Provider>)
    expect(wrapper.dive().dive().name()).toBe("MockComponent");
  });
  it('shows the read only component if not all permissions are present', () => {
    const wrapper = shallow(
      <ReadOnlyContext.Provider value={['mockPermission']}>
        <ReadOnlyOrEditable 
          requiredPermissions={['mockPermission', 'mockPermission1']}
          readOnlyComponent={<MockComponent/>}
          editableComponent={<MockComponent2/>} />
      </ReadOnlyContext.Provider>)
    expect(wrapper.dive().dive().name()).toBe("MockComponent");
  });
  it('shows the editable only component', () => {
    const wrapper = shallow(
      <ReadOnlyContext.Provider value={['mockPermission']}>
        <ReadOnlyOrEditable requiredPermissions={['mockPermission']} readOnlyComponent={<MockComponent/>} editableComponent={<MockComponent2/>} />
      </ReadOnlyContext.Provider>);
    expect(wrapper.dive().dive().name()).toBe("MockComponent2");
  });
});
