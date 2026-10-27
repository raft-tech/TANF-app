import {
  presentReportSections,
  programSlugToResponseCode,
} from './reportSections'
import { getAssignedSections } from '../selectors/stts'
import {
  CANONICAL_SECTION_NAMES,
  createParticipationStt,
  createProgramParticipation,
} from '../test-utils/programParticipation'

describe('presentReportSections', () => {
  it.each(['tanf', 'tribal', 'ssp'])(
    'sorts a shuffled %s assignment without using IDs or mutating API names',
    (programSlug) => {
      const participation = createProgramParticipation({
        programSlug,
        sectionNames: [
          'Stratum Data',
          'Closed Case Data',
          'Aggregate Data',
          'Active Case Data',
        ],
      })
      const sections = Object.freeze(participation.sections)
      const before = JSON.stringify(sections)
      const presented = presentReportSections(sections)
      expect(presented.map((section) => section.name)).toEqual(
        CANONICAL_SECTION_NAMES
      )
      expect(presented.map((section) => section.number)).toEqual([1, 2, 3, 4])
      expect(presented.map((section) => section.tableKind)).toEqual([
        'case',
        'case',
        'total',
        'total',
      ])
      expect(presented[0]).toEqual({
        ...sections[3],
        number: 1,
        tableKind: 'case',
      })
      expect(presented[0]).not.toBe(sections[3])
      expect(JSON.stringify(sections)).toBe(before)
    }
  )

  it('presents sparse assigned sections 1 and 3, not the first two catalog names', () => {
    const stt = createParticipationStt({
      program_participations: [
        createProgramParticipation({
          sectionNames: ['Aggregate Data', 'Active Case Data'],
        }),
      ],
    })
    expect(presentReportSections(getAssignedSections(stt, 'tanf'))).toEqual([
      {
        ...stt.program_participations[0].sections[1],
        number: 1,
        tableKind: 'case',
      },
      {
        ...stt.program_participations[0].sections[0],
        number: 3,
        tableKind: 'total',
      },
    ])
  })

  it('retains Section 3 numbering and table kind for a singleton assignment', () => {
    const { sections } = createProgramParticipation({
      sectionNames: ['Aggregate Data'],
    })
    expect(presentReportSections(sections)).toEqual([
      { ...sections[0], number: 3, tableKind: 'total' },
    ])
  })

  it('preserves an explicit empty assignment', () => {
    expect(presentReportSections([])).toEqual([])
  })

  it.each([undefined, null, {}])(
    'rejects invalid collections: %j',
    (sections) => {
      expect(() => presentReportSections(sections)).toThrow(/must be an array/)
    }
  )

  it.each([
    null,
    {},
    { name: 'Future API Section' },
    { name: 'toString' },
    { name: 'Aggregate Data ' },
  ])(
    'surfaces unsupported catalog names rather than inventing presentation: %j',
    (section) => {
      expect(() => presentReportSections([section])).toThrow(
        /Unsupported report section/
      )
    }
  )
})

describe('programSlugToResponseCode', () => {
  it.each([
    ['tanf', 'TAN'],
    ['tribal', 'TRIBAL'],
    ['ssp', 'SSP'],
    ['ssp-moe', null],
    ['fra', null],
    ['audit', null],
    ['toString', null],
    [undefined, null],
  ])('maps %s explicitly to %s', (slug, expected) => {
    expect(programSlugToResponseCode(slug)).toBe(expected)
  })
})
