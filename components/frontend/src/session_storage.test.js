import { clearStoredSession, loadStoredSession, storeSession } from "./session_storage"

beforeEach(() => localStorage.clear())

it("returns null when no session is stored", () => {
    expect(loadStoredSession()).toBeNull()
})

it("returns null when the expiration datetime is not stored", () => {
    localStorage.setItem("user", "admin")
    localStorage.setItem("email", "admin@example.org")
    expect(loadStoredSession()).toBeNull()
})

it("loads a stored session", () => {
    const expiry = new Date("2099-01-01T12:00:00Z")
    localStorage.setItem("user", "admin")
    localStorage.setItem("email", "admin@example.org")
    localStorage.setItem("session_expiration_datetime", expiry.toISOString())
    const session = loadStoredSession()
    expect(session.user).toBe("admin")
    expect(session.email).toBe("admin@example.org")
    expect(session.sessionExpirationDateTime).toEqual(expiry)
})

it("stores a session", () => {
    const expiry = new Date("2099-01-01T12:00:00Z")
    storeSession("admin", "admin@example.org", expiry)
    expect(localStorage.getItem("user")).toBe("admin")
    expect(localStorage.getItem("email")).toBe("admin@example.org")
    expect(localStorage.getItem("session_expiration_datetime")).toBe(expiry.toISOString())
})

it("clears a stored session", () => {
    localStorage.setItem("user", "admin")
    localStorage.setItem("email", "admin@example.org")
    localStorage.setItem("session_expiration_datetime", new Date().toISOString())
    clearStoredSession()
    expect(localStorage.getItem("user")).toBeNull()
    expect(localStorage.getItem("email")).toBeNull()
    expect(localStorage.getItem("session_expiration_datetime")).toBeNull()
})
