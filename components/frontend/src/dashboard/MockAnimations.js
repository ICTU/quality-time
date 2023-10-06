export function mockGetAnimations() {
    const originalGetElementById = document.getElementById;
    document.getElementById = (id) => {
        const element = originalGetElementById.call(document, id);
        if (id === "dashboard" && element) {
            element.getAnimations = jest.fn().mockReturnValue([]);
        }
        return element;
    };
}
