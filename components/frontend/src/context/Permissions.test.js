import React from 'react';
import { render, screen } from '@testing-library/react';
import { Permissions, ReadOnlyOrEditable } from './Permissions';

function MockComponent1() { return ("One") }
function MockComponent2() { return ("Two") }

it('shows the read only component if no permissions are present', () => {
    render(
        <Permissions.Provider value={[]}>
            <ReadOnlyOrEditable
                requiredPermissions={['mockPermission']}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />}
            />
        </Permissions.Provider>)
    expect(screen.queryAllByText("One").length).toBe(1)
    expect(screen.queryAllByText("Two").length).toBe(0)
});

it('shows the read only component if not all permissions are present', () => {
    render(
        <Permissions.Provider value={['mockPermission']}>
            <ReadOnlyOrEditable
                requiredPermissions={['mockPermission', 'mockPermission1']}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />} />
        </Permissions.Provider>)
    expect(screen.queryAllByText("One").length).toBe(1)
    expect(screen.queryAllByText("Two").length).toBe(0)
});

it('shows the editable only component', () => {
    render(
        <Permissions.Provider value={['mockPermission']}>
            <ReadOnlyOrEditable
                requiredPermissions={['mockPermission']}
                readOnlyComponent={<MockComponent1 />}
                editableComponent={<MockComponent2 />}
            />
        </Permissions.Provider>);
    expect(screen.queryAllByText("One").length).toBe(0)
    expect(screen.queryAllByText("Two").length).toBe(1)
});
