const PROGRAMS = {
  tanf: { id: 11, slug: 'tanf', name: 'TANF' },
  tribal: { id: 22, slug: 'tribal', name: 'Tribal TANF' },
  ssp: { id: 33, slug: 'ssp', name: 'SSP' },
}

export const CANONICAL_SECTION_NAMES = [
  'Active Case Data',
  'Closed Case Data',
  'Aggregate Data',
  'Stratum Data',
]

// Deliberately nonsequential IDs prevent fixtures from implying display numbers.
const SECTION_IDS = [101, 104, 109, 115]

export const createProgramParticipation = ({
  programSlug = 'tanf',
  sectionNames = [],
  id = 501,
  status = 'ACTIVE',
} = {}) => {
  const program = PROGRAMS[programSlug]
  if (!program) throw new Error(`Unknown fixture program: ${programSlug}`)
  return {
    id,
    program: { ...program },
    status,
    sections: sectionNames.map((name) => {
      const index = CANONICAL_SECTION_NAMES.indexOf(name)
      if (index === -1) throw new Error(`Unknown fixture section: ${name}`)
      return {
        id: program.id * 100 + SECTION_IDS[index],
        name,
        program: { ...program },
      }
    }),
  }
}

export const createParticipationStt = (overrides = {}) => ({
  id: 1,
  type: 'state',
  code: 'AL',
  name: 'Alabama',
  program_participations: [],
  ...overrides,
})
