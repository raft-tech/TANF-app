import {
  availableStts,
  fileTypeToProgramSlug,
  getProgramParticipation,
  getAssignedSections,
} from './stts'
import {
  createParticipationStt,
  createProgramParticipation,
} from '../test-utils/programParticipation'
import { AUTH_CHECK_DATA, STT_ALPHA_DATA } from '../mirage.data'

const baseStts = [
  { id: 1, name: 'Alabama', type: 'state' },
  { id: 2, name: 'Tribe A', type: 'tribe' },
  { id: 3, name: 'Guam', type: 'territory' },
]

const makeState = ({ roleName, sttList = baseStts, regions } = {}) => ({
  auth: {
    user: {
      account_approval_status: 'Approved',
      roles: [{ name: roleName }],
      regions,
    },
  },
  stts: { sttList },
})

describe('availableStts', () => {
  it('filters tribal STTs for non-regional staff on FRA pages', () => {
    const state = makeState({ roleName: 'OFA System Admin' })
    const result = availableStts('/reports/fra')(state)

    expect(result.map((stt) => stt.type)).toEqual(['state', 'territory'])
  })

  it('keeps tribal STTs for non-regional staff on non-FRA pages', () => {
    const state = makeState({ roleName: 'OFA System Admin' })
    const result = availableStts('/data-files')(state)

    expect(result.map((stt) => stt.type)).toEqual([
      'state',
      'tribe',
      'territory',
    ])
  })

  it('filters tribal STTs for regional staff on FRA pages', () => {
    const state = makeState({
      roleName: 'OFA Regional Staff',
      regions: [{ stts: baseStts }],
    })
    const result = availableStts('/reports/fra')(state)

    expect(result.map((stt) => stt.type)).toEqual(['state', 'territory'])
  })

  it('keeps tribal STTs for regional staff on non-FRA pages', () => {
    const state = makeState({
      roleName: 'OFA Regional Staff',
      regions: [{ stts: baseStts }],
    })
    const result = availableStts('/data-files')(state)

    expect(result.map((stt) => stt.name)).toEqual([
      'Alabama',
      'Guam',
      'Tribe A',
    ])
  })

  it('returns an empty list when regional staff has no regions', () => {
    const state = makeState({
      roleName: 'OFA Regional Staff',
      regions: undefined,
    })
    const result = availableStts('/data-files')(state)

    expect(result).toEqual([])
  })

  it('returns empty list when sttList is missing for non-regional staff', () => {
    const state = {
      auth: {
        user: {
          account_approval_status: 'Approved',
          roles: [{ name: 'OFA System Admin', permissions: [] }],
        },
      },
      stts: {},
    }
    const result = availableStts('/data-files')(state)

    expect(result).toEqual([])
  })
})

const assignedStt = (participation = createProgramParticipation()) =>
  createParticipationStt({ program_participations: [participation] })

describe('fileTypeToProgramSlug', () => {
  it.each([
    ['tanf', 'state', 'tanf'],
    ['tanf', 'territory', 'tanf'],
    ['tanf', 'tribe', 'tribal'],
    ['ssp-moe', 'state', 'ssp'],
    ['ssp-moe', 'tribe', 'ssp'],
    ['fra', 'state', null],
    ['audit', 'state', null],
    ['unknown', 'state', null],
    ['tanf', undefined, null],
    ['tanf', 'unknown', null],
  ])('maps %s for %s to %s', (fileType, type, expected) => {
    expect(fileTypeToProgramSlug(fileType, type)).toBe(expected)
  })
})

describe('participation and assigned sections', () => {
  it('uses exact sparse assignments independently for TANF and SSP', () => {
    const tanf = createProgramParticipation({
      sectionNames: ['Aggregate Data', 'Active Case Data'],
    })
    const ssp = createProgramParticipation({
      id: 502,
      programSlug: 'ssp',
      sectionNames: ['Closed Case Data'],
    })
    const stt = createParticipationStt({
      ssp: false,
      num_sections: 4,
      filenames: { 'Stratum Data': 'not-an-assignment.txt' },
      program_participations: [ssp, tanf],
    })
    expect(getProgramParticipation(stt, 'tanf')).toBe(tanf)
    expect(getProgramParticipation(stt, 'ssp')).toBe(ssp)
    expect(getAssignedSections(stt, 'tanf')).toEqual(tanf.sections)
    expect(getAssignedSections(stt, 'ssp-moe')).toEqual(ssp.sections)
    expect(getAssignedSections(stt, 'fra')).toEqual([])
  })

  it('uses Tribal TANF for tribes, not the state TANF participation', () => {
    const tribal = createProgramParticipation({
      programSlug: 'tribal',
      sectionNames: ['Aggregate Data'],
    })
    const stt = createParticipationStt({
      type: 'tribe',
      program_participations: [createProgramParticipation(), tribal],
    })
    expect(getAssignedSections(stt, 'tanf')).toEqual(tribal.sections)
    expect(getAssignedSections({ ...stt, type: 'territory' }, 'tanf')).toEqual(
      []
    )
  })

  it.each(['ACTIVE', 'FORMER', 'NEVER', 'unrecognized', null, undefined])(
    'ignores status %s, including an omitted status',
    (status) => {
      const participation = createProgramParticipation({
        programSlug: 'ssp',
        sectionNames: ['Closed Case Data'],
      })
      if (status === undefined) delete participation.status
      else participation.status = status
      expect(getProgramParticipation(assignedStt(participation), 'ssp')).toBe(
        participation
      )
      expect(
        getAssignedSections(assignedStt(participation), 'ssp-moe')
      ).toEqual(participation.sections)
    }
  )

  it.each([
    undefined,
    null,
    {},
    createParticipationStt({ ssp: true, num_sections: 4 }),
    createParticipationStt({ program_participations: undefined }),
    assignedStt(),
    assignedStt(createProgramParticipation({ programSlug: 'tribal' })),
  ])(
    'preserves missing/empty assignments without legacy fallbacks: %j',
    (stt) => {
      expect(getAssignedSections(stt, 'tanf')).toEqual([])
      expect(getAssignedSections(stt, 'ssp-moe')).toEqual([])
    }
  )

  it('retains an empty participation record as distinct from an absent one', () => {
    const stt = assignedStt()
    expect(getProgramParticipation(stt, 'tanf')).toBe(
      stt.program_participations[0]
    )
    expect(getProgramParticipation(stt, 'ssp')).toBeNull()
  })

  it.each([null, {}, 'invalid', [null], [[]], [{}], [{ id: 1, program: {} }]])(
    'rejects malformed participation metadata: %j',
    (program_participations) => {
      expect(() =>
        getAssignedSections(
          createParticipationStt({ program_participations }),
          'tanf'
        )
      ).toThrow(/participation/i)
    }
  )

  it('rejects ambiguous participation records instead of taking the first', () => {
    const stt = createParticipationStt({
      program_participations: [
        createProgramParticipation(),
        createProgramParticipation({ id: 999 }),
      ],
    })
    expect(() => getAssignedSections(stt, 'tanf')).toThrow(
      /Multiple participations/
    )
  })

  it.each([undefined, null, {}, 'invalid', [null], [[]], [{}]])(
    'rejects malformed assigned section collections/entries: %j',
    (sections) => {
      const participation = { ...createProgramParticipation(), sections }
      expect(() =>
        getAssignedSections(assignedStt(participation), 'tanf')
      ).toThrow(/section/i)
    }
  )

  it.each([
    { id: 0 },
    { id: '1201' },
    { name: '' },
    { name: ' ' },
    { program: null },
    { program: { id: 11, name: 'TANF' } },
    { program: { id: 99, slug: 'tanf', name: 'TANF' } },
    { program: { id: 11, slug: 'ssp', name: 'TANF' } },
    { program: { id: 11, slug: 'tanf', name: 'SSP' } },
  ])('rejects malformed or cross-program section metadata: %j', (override) => {
    const participation = createProgramParticipation({
      sectionNames: ['Active Case Data'],
    })
    participation.sections[0] = { ...participation.sections[0], ...override }
    expect(() =>
      getAssignedSections(assignedStt(participation), 'tanf')
    ).toThrow(/section/i)
  })

  it('deduplicates canonical IDs without mutating or sharing API objects', () => {
    const participation = createProgramParticipation({
      sectionNames: ['Aggregate Data', 'Active Case Data', 'Aggregate Data'],
    })
    const before = JSON.stringify(participation)
    Object.freeze(participation.sections)
    const sections = getAssignedSections(assignedStt(participation), 'tanf')
    expect(sections).toEqual(participation.sections.slice(0, 2))
    expect(sections[0]).not.toBe(participation.sections[0])
    expect(sections[0].program).not.toBe(participation.sections[0].program)
    expect(JSON.stringify(participation)).toBe(before)
  })

  it('does not hardcode program IDs or infer membership from catalog names', () => {
    const participation = createProgramParticipation({
      sectionNames: ['Aggregate Data'],
    })
    participation.program.id = 987
    participation.sections[0] = {
      id: 765,
      name: 'Future API Section',
      program: { ...participation.program },
    }
    expect(getAssignedSections(assignedStt(participation), 'tanf')).toEqual(
      participation.sections
    )
  })

  it('rejects conflicting metadata for a duplicated canonical ID', () => {
    const participation = createProgramParticipation({
      sectionNames: ['Aggregate Data'],
    })
    participation.sections.push({
      ...participation.sections[0],
      name: 'Active Case Data',
    })
    expect(() =>
      getAssignedSections(assignedStt(participation), 'tanf')
    ).toThrow(/Conflicting names/)
  })
})

describe('availableStts compatibility and Mirage metadata', () => {
  const stateStt = createParticipationStt()
  const tribe = createParticipationStt({
    id: 58,
    type: 'tribe',
    name: 'Test Tribe',
  })
  const state = {
    auth: {
      user: {
        account_approval_status: 'Approved',
        roles: [{ name: 'OFA Regional Staff' }],
        regions: [{ stts: [tribe, stateStt] }],
      },
    },
    stts: { sttList: [createParticipationStt({ id: 999 })] },
  }

  it('preserves regional sorting, region boundaries, and FRA tribe exclusion', () => {
    expect(availableStts('/data-files')(state)).toEqual([stateStt, tribe])
    expect(availableStts('/fra-data-files')(state)).toEqual([stateStt])
  })

  it('preserves the global catalog behavior for nonregional users', () => {
    const nonregional = { ...state, auth: { user: { roles: [] } } }
    expect(availableStts('/data-files')(nonregional)).toEqual(
      state.stts.sttList
    )
    expect(availableStts('/data-files')({ auth: { user: null } })).toEqual([])
  })

  it('keeps Mirage profile and catalog participation metadata consistent', () => {
    const profileStt = AUTH_CHECK_DATA.user.stt
    const catalogStt = STT_ALPHA_DATA.find((stt) => stt.id === profileStt.id)
    expect(profileStt.program_participations).toEqual(
      catalogStt.program_participations
    )
    expect(
      getAssignedSections(profileStt, 'ssp-moe').map((s) => s.name)
    ).toEqual(['Closed Case Data'])
    STT_ALPHA_DATA.forEach((stt) => {
      expect(getAssignedSections(stt, 'tanf')).toHaveLength(4)
    })
  })
})
