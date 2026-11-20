import React from 'react'
import { act, renderHook } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from '../configureStore'
import { SET_STTS } from '../actions/sttList'
import {
  createParticipationStt,
  createProgramParticipation,
} from '../test-utils/programParticipation'
import { useReportAssignment } from './useReportAssignment'

const tanf = createProgramParticipation({
  sectionNames: ['Aggregate Data', 'Active Case Data'],
})
const ssp = createProgramParticipation({
  id: 502,
  programSlug: 'ssp',
  sectionNames: ['Closed Case Data'],
})
const stateStt = createParticipationStt({
  ssp: false,
  program_participations: [tanf, ssp],
})
const otherStt = createParticipationStt({
  id: 2,
  name: 'Alaska',
  program_participations: [
    createProgramParticipation({ sectionNames: ['Stratum Data'] }),
  ],
})
const defaultSelection = {
  selectedSttName: stateStt.name,
  fileType: 'tanf',
}

const setup = ({
  role = 'OFA Admin',
  profile = stateStt,
  regions,
  stts = [stateStt, otherStt],
  catalog,
  selection = defaultSelection,
} = {}) => {
  const store = configureStore({
    auth: {
      user: {
        id: 7,
        stt: profile,
        roles: [{ name: role, permissions: [] }],
        account_approval_status: 'Approved',
        ...(regions && { regions }),
      },
    },
    stts: catalog || { sttList: stts, loading: false, loaded: true },
  })
  const originalReports = store.getState().reports
  const hook = renderHook((props) => useReportAssignment(props), {
    initialProps: selection,
    wrapper: ({ children }) => <Provider store={store}>{children}</Provider>,
  })

  return { ...hook, store, originalReports }
}

describe('useReportAssignment', () => {
  it('switches exact sparse assignments without configuring or clearing upload state', () => {
    const { result, rerender, store, originalReports } = setup()
    expect(result.current.canSelectStt).toBe(true)
    expect(result.current.sttResolution.stt).toBe(stateStt)
    expect(
      result.current.configuration.sections.map(({ number }) => number)
    ).toEqual([1, 3])
    const tanfKey = result.current.assignmentKey

    rerender({ ...defaultSelection, fileType: 'ssp-moe' })

    expect(
      result.current.tdrAssignment.options.map(({ value }) => value)
    ).toEqual(['tanf', 'ssp-moe'])
    expect(result.current.configuration.program.slug).toBe('ssp')
    expect(
      result.current.configuration.sections.map(({ name }) => name)
    ).toEqual(['Closed Case Data'])
    expect(result.current.assignmentKey).not.toBe(tanfKey)
    expect(store.getState().reports).toBe(originalReports)
  })

  it('keeps derived references stable across unrelated renders and fiscal changes', () => {
    const { result, rerender } = setup()
    const before = result.current

    rerender({
      ...defaultSelection,
      year: '2025',
      quarter: 'Q2',
      modalOpen: true,
    })

    expect(result.current.sttResolution).toBe(before.sttResolution)
    expect(result.current.tdrAssignment).toBe(before.tdrAssignment)
    expect(result.current.configuration).toBe(before.configuration)
    expect(result.current.assignmentKey).toBe(before.assignmentKey)
  })

  it('uses the active administrative selection and clears assignments when it is cleared', () => {
    const { result, rerender } = setup()
    rerender({ ...defaultSelection, selectedSttName: otherStt.name })
    expect(result.current.configuration.sttId).toBe(otherStt.id)
    expect(
      result.current.configuration.sections.map(({ number }) => number)
    ).toEqual([4])

    rerender({ ...defaultSelection, selectedSttName: '' })
    expect(result.current.sttResolution.stt).toBeNull()
    expect(result.current.tdrAssignment.options).toEqual([])
    expect(result.current.configuration.sections).toEqual([])
  })

  it('waits for metadata arrival before deriving an SSP deep-link assignment', () => {
    const { result, store } = setup({
      catalog: { sttList: [], loading: true, loaded: false },
      selection: { ...defaultSelection, fileType: 'ssp-moe' },
    })
    expect(result.current.sttResolution.state).toBe('loading')
    expect(result.current.configuration.sections).toEqual([])

    act(() => store.dispatch({ type: SET_STTS, payload: { data: [stateStt] } }))

    expect(result.current.sttList).toEqual([stateStt])
    expect(result.current.sttResolution.state).toBe('ready')
    expect(result.current.configuration.program.slug).toBe('ssp')
    expect(
      result.current.configuration.sections.map(({ number }) => number)
    ).toEqual([2])
  })

  it('uses completed catalog metadata rather than falling back to stale profile assignments', () => {
    const { result, store } = setup({ role: 'Data Analyst' })
    expect(result.current.canSelectStt).toBe(false)
    const emptyStt = {
      ...stateStt,
      program_participations: [
        createProgramParticipation({ sectionNames: [] }),
      ],
    }
    act(() => store.dispatch({ type: SET_STTS, payload: { data: [emptyStt] } }))

    expect(result.current.sttResolution.stt).toBe(emptyStt)
    expect(result.current.configuration.sections).toEqual([])
    expect(
      result.current.tdrAssignment.options.map(({ value }) => value)
    ).toEqual(['tanf'])

    act(() => store.dispatch({ type: SET_STTS, payload: { data: [] } }))
    expect(result.current.sttResolution.stt).toBeNull()
    expect(result.current.tdrAssignment.options).toEqual([])
  })

  it('blocks foreign profile URLs and uses only permitted regional metadata', () => {
    const profileHook = setup({
      role: 'Data Analyst',
      selection: { ...defaultSelection, selectedSttName: otherStt.name },
    })
    expect(profileHook.result.current.sttResolution.unauthorized).toBe(true)
    expect(profileHook.result.current.configuration.sections).toEqual([])
    profileHook.unmount()

    const { result, rerender } = setup({
      role: 'OFA Regional Staff',
      regions: [{ stts: [stateStt] }],
      stts: [{ ...stateStt, program_participations: [] }, otherStt],
    })
    expect(result.current.sttResolution.stt).toBe(stateStt)
    expect(result.current.configuration.sections).toHaveLength(2)
    rerender({ ...defaultSelection, selectedSttName: otherStt.name })
    expect(result.current.sttResolution.stt).toBeNull()
    expect(result.current.configuration.sections).toEqual([])
  })

  it.each(['state', 'tribe'])(
    'retains separate PIA feature/type gating for a %s without participation',
    (type) => {
      const stt = createParticipationStt({ type, program_participations: [] })
      const { result, rerender } = setup({ stts: [stt] })
      expect(result.current.tdrAssignment.options).toEqual([])

      rerender({ ...defaultSelection, piaEnabled: true })
      const expectedOptions =
        type === 'tribe'
          ? []
          : [
              {
                label: 'Program Integrity Audit',
                value: 'program-integrity-audit',
              },
            ]
      expect(result.current.tdrAssignment.options).toEqual(expectedOptions)
      expect(result.current.configuration.sections).toEqual([])
    }
  )

  it('keeps status outside assignment identity and surfaces malformed assignments', () => {
    const { result, store } = setup()
    const key = result.current.assignmentKey
    const changedStatus = {
      ...stateStt,
      program_participations: stateStt.program_participations.map((record) => ({
        ...record,
        status: 'unfamiliar',
      })),
    }
    act(() =>
      store.dispatch({ type: SET_STTS, payload: { data: [changedStatus] } })
    )
    expect(result.current.assignmentKey).toBe(key)

    const malformed = {
      ...stateStt,
      program_participations: [{ ...tanf, sections: null }],
    }
    act(() =>
      store.dispatch({ type: SET_STTS, payload: { data: [malformed] } })
    )
    expect(result.current.tdrAssignment.state).toBe('error')
    expect(result.current.configuration.sections).toEqual([])
    expect(result.current.tdrAssignment.error).toMatch(/Assigned sections/)
  })
})
