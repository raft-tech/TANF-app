import {
  availableStts,
  canSubmitSsp,
  canViewSsp,
  findProgramParticipation,
} from './stts'

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

describe('SSP program participation helpers', () => {
  const sttWithSspStatus = (status) => ({
    program_participations: [
      {
        program: { slug: 'ssp' },
        status,
      },
    ],
  })

  it('finds a participation by program slug', () => {
    const stt = {
      program_participations: [
        { program: { slug: 'tanf' }, status: 'ACTIVE' },
        { program: { slug: 'ssp' }, status: 'FORMER' },
      ],
    }

    expect(findProgramParticipation(stt, 'ssp')).toEqual({
      program: { slug: 'ssp' },
      status: 'FORMER',
    })
  })

  it.each([
    ['ACTIVE', true, true],
    ['FORMER', true, false],
    ['NEVER', false, false],
    ['UNKNOWN', false, false],
  ])(
    'derives SSP capabilities for %s status',
    (status, expectedCanView, expectedCanSubmit) => {
      const stt = sttWithSspStatus(status)

      expect(canViewSsp(stt)).toBe(expectedCanView)
      expect(canSubmitSsp(stt)).toBe(expectedCanSubmit)
    }
  )

  it.each([
    ['missing participation array', {}],
    ['empty participation array', { program_participations: [] }],
    [
      'another program only',
      {
        program_participations: [
          { program: { slug: 'tanf' }, status: 'ACTIVE' },
        ],
      },
    ],
    ['malformed participation', { program_participations: [{ status: 'ACTIVE' }] }],
  ])('fails closed for %s', (_label, stt) => {
    expect(canViewSsp(stt)).toBe(false)
    expect(canSubmitSsp(stt)).toBe(false)
  })
})
