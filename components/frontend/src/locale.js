import "dayjs/locale/en-gb"
import "dayjs/locale/nl"

import dayjs from "dayjs"
import localeData from "dayjs/plugin/localeData"
import updateLocale from "dayjs/plugin/updateLocale"
import { string } from "prop-types"

export function adapterLocale(language) {
    // Quick and dirty solution while we wait for a more generic solution to finding the user's locale
    // Our issue: https://github.com/ICTU/quality-time/issues/10710
    // Upstream issue: https://github.com/iamkun/dayjs/issues/732
    let locale = "en-GB"
    if (language === "nl-NL") {
        // Use the Dutch locale, but keep the language English
        locale = "nl" // dayjs doesn't have nl-NL
        dayjs.extend(updateLocale)
        dayjs.extend(localeData)
        dayjs.updateLocale("nl", {
            months: dayjs.months(),
            monthsShort: dayjs.monthsShort(),
            weekdays: dayjs.weekdays(),
            weekdaysShort: dayjs.weekdaysShort(),
            weekdaysMin: dayjs.weekdaysMin(),
        })
    }
    return locale
}
adapterLocale.propTypes = {
    language: string,
}
