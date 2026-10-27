const SECTION_PRESENTATION = {
  'Active Case Data': { number: 1, tableKind: 'case' },
  'Closed Case Data': { number: 2, tableKind: 'case' },
  'Aggregate Data': { number: 3, tableKind: 'total' },
  'Stratum Data': { number: 4, tableKind: 'total' },
}

const RESPONSE_PROGRAM_CODES = {
  tanf: 'TAN',
  tribal: 'TRIBAL',
  ssp: 'SSP',
}

export const programSlugToResponseCode = (slug) =>
  Object.hasOwn(RESPONSE_PROGRAM_CODES, slug)
    ? RESPONSE_PROGRAM_CODES[slug]
    : null

/** Adds presentation metadata without granting sections or changing API names. */
export const presentReportSections = (sections) => {
  if (!Array.isArray(sections)) {
    throw new Error('Assigned sections must be an array.')
  }
  return sections
    .map((section) => {
      if (!section || !Object.hasOwn(SECTION_PRESENTATION, section.name)) {
        throw new Error(`Unsupported report section: ${section?.name}.`)
      }
      return { ...section, ...SECTION_PRESENTATION[section.name] }
    })
    .sort((a, b) => a.number - b.number)
}
