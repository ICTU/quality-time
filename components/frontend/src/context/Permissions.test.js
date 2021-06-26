import React from 'react';
import { shallow } from 'enzyme';
import { Permissions, ReadOnlyOrEditable } from './Permissions';

function MockComponent() { return ("Hi") }
function MockComponent2() { return ("Two") }

describe("<Permissions />", () => {
  it('provides the permissions context to components', () => {
    const wrapper = shallow(
      <Permissions.Provider value={['mockPermission']}>
        <Permissions.Consumer>{(permissions) => (<MockComponent permissions={permissions} />)}</Permissions.Consumer>
      </Permissions.Provider>);
    expect(wrapper.dive().find('MockComponent').prop("permissions")).toStrictEqual(['mockPermission']);
  });
});

describe("<ReadOnlyOrEditable />", () => {
  it('shows the read only component if no permissions are present', () => {
    const wrapper = shallow(
      <Permissions.Provider value={[]}>
        <ReadOnlyOrEditable requiredPermissions={['mockPermission']} readOnlyComponent={<MockComponent/>} editableComponent={<MockComponent2/>} />
      </Permissions.Provider>)
    expect(wrapper.dive().dive().name()).toBe("MockComponent");
  });
  it('shows the read only component if not all permissions are present', () => {
    const wrapper = shallow(
      <Permissions.Provider value={['mockPermission']}>
        <ReadOnlyOrEditable 
          requiredPermissions={['mockPermission', 'mockPermission1']}
          readOnlyComponent={<MockComponent/>}
          editableComponent={<MockComponent2/>} />
      </Permissions.Provider>)
    expect(wrapper.dive().dive().name()).toBe("MockComponent");
  });
  it('shows the editable only component', () => {
    const wrapper = shallow(
      <Permissions.Provider value={['mockPermission']}>
        <ReadOnlyOrEditable requiredPermissions={['mockPermission']} readOnlyComponent={<MockComponent/>} editableComponent={<MockComponent2/>} />
      </Permissions.Provider>);
    expect(wrapper.dive().dive().name()).toBe("MockComponent2");
  });
});
