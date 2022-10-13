import React from 'react';
import { act, render } from '@testing-library/react';
import { DarkMode } from '../context/DarkMode';
import { Form } from '../semantic_ui_react_wrappers';

it('shows the form dropdown in darkmode', async () => {
    await act(async () => {
        const { container } = render(
            <DarkMode.Provider value={true}>
                <Form>
                    <Form.Dropdown options={[{ key: "Hi", value: "Hi", text: "Hi" }]} value={"Hi"} />
                </Form>
            </DarkMode.Provider>
        )
        expect(container.querySelector(".inverted")).not.toBe(null)
    })
});

it('shows the form dropdown in light mode', async () => {
    await act(async () => {
        const { container } = render(
            <DarkMode.Provider value={false}>
                <Form>
                    <Form.Dropdown options={[{ key: "Hi", value: "Hi", text: "Hi" }]} value={"Hi"} />
                </Form>
            </DarkMode.Provider>
        )
        expect(container.querySelector(".inverted")).toBe(null)
    })
});
