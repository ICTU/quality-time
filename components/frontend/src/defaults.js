const zIndexBase = 1 // Can't use 0 because some MUI components apparently have a zIndex of 1?
const above = 1
export const zIndexInnerTableHeader = above + zIndexBase
export const zIndexTableHeader = above + zIndexInnerTableHeader
export const zIndexSubjectTitle = above + zIndexTableHeader
