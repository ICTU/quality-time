import { addInvertedClassNameWhenInDarkMode } from "./dark_mode";

it('adds inverted when in dark mode', () => {
    expect(addInvertedClassNameWhenInDarkMode({ foo: "bar" }, true)).toEqual({ "className": " inverted", "foo": "bar" })
})

it('does not add inverted when in light mode', () => {
    expect(addInvertedClassNameWhenInDarkMode({ foo: "bar" }, false)).toEqual({ "className": "", "foo": "bar" })
})