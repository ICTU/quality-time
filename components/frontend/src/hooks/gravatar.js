import { useEffect, useState } from "react"

async function gravatarHash(email) {
    // Gravatar identifies users by the SHA-256 hash of their trimmed and lower-cased email address,
    // see https://docs.gravatar.com/api/avatars/hash/
    const emailBytes = new TextEncoder().encode(email.trim().toLowerCase())
    const hashBytes = await globalThis.crypto.subtle.digest("SHA-256", emailBytes)
    return Array.from(new Uint8Array(hashBytes), (byte) => byte.toString(16).padStart(2, "0")).join("")
}

export function useGravatarUrl(email) {
    // Hook to calculate the Gravatar URL for the email address. Returns null as long as the URL is not available.
    const [url, setUrl] = useState(null)
    useEffect(() => {
        // The Web Crypto API is only available in secure contexts, so when Quality-time is served over plain HTTP
        // no Gravatar URL can be calculated and the avatar falls back to a placeholder icon
        if (!globalThis.crypto?.subtle) return
        let didCancel = false
        gravatarHash(email).then((hash) => {
            if (!didCancel) {
                setUrl(`https://gravatar.com/avatar/${hash}?d=identicon`)
            }
            return null
        })
        return () => {
            didCancel = true
        }
    }, [email])
    return url
}
