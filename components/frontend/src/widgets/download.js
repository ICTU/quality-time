export function triggerDownload(blob, filename) {
    const url = globalThis.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = filename
    a.click()
}

export function localTimestamp() {
    const now = new Date()
    const localNow = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
    return localNow.toISOString().split(".")[0]
}
