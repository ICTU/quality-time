// Note that the API-server also has these constants, in src/model/report.py.
export const defaultDesiredResponseTimes = {
    debt_target_met: 60,
    near_target_met: 21,
    target_not_met: 7,
    unknown: 3,
    confirmed: 180,
    false_positive: 180,
    wont_fix: 180,
    fixed: 7,
}
