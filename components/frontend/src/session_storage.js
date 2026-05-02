const USER_KEY = "user"
const EMAIL_KEY = "email"
const SESSION_EXPIRATION_KEY = "session_expiration_datetime"

export function loadStoredSession() {
    const expirationISOString = localStorage.getItem(SESSION_EXPIRATION_KEY)
    if (!expirationISOString) {
        return null
    }
    return {
        user: localStorage.getItem(USER_KEY),
        email: localStorage.getItem(EMAIL_KEY),
        sessionExpirationDateTime: new Date(expirationISOString),
    }
}

export function storeSession(user, email, sessionExpirationDateTime) {
    localStorage.setItem(USER_KEY, user)
    localStorage.setItem(EMAIL_KEY, email)
    localStorage.setItem(SESSION_EXPIRATION_KEY, sessionExpirationDateTime.toISOString())
}

export function clearStoredSession() {
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(EMAIL_KEY)
    localStorage.removeItem(SESSION_EXPIRATION_KEY)
}
