export function formatDate(date, language) {
    return formatDateTime(date, language, { day: "2-digit", month: "2-digit", year: "numeric" })
}

export function formatTime(date, language) {
    return formatDateTime(date, language, { hour: "numeric", minute: "numeric" })
}

function formatDateTime(date, language, options) {
    const format = new Intl.DateTimeFormat(language, options)
    return format.format(date)
}
