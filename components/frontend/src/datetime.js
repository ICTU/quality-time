import { useLanguageURLSearchQuery } from "./app_ui_settings"

export function formatDate(date) {
    return formatDateTime(date, { day: "2-digit", month: "2-digit", year: "numeric" })
}

export function formatTime(date) {
    return formatDateTime(date, { hour: "numeric", minute: "numeric" })
}

function formatDateTime(date, options) {
    const format = new Intl.DateTimeFormat(useLanguageURLSearchQuery().value, options)
    return format.format(date)
}
