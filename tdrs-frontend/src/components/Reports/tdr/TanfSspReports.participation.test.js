import React from 'react'
import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from '@testing-library/react'
import { Provider } from 'react-redux'
import { MemoryRouter, useLocation } from 'react-router-dom'
import configureStore, { history } from '../../../configureStore'
import createRootReducer from '../../../reducers'
import Reports from '../Reports'
import { SET_STTS } from '../../../actions/sttList'
import {
  createParticipationStt,
  createProgramParticipation,
} from '../../../test-utils/programParticipation'
import { deferred, stageScopedFile } from '../../../test-utils/reportScopes'
import { get, post } from '../../../fetch-instance'

jest.mock('../../../fetch-instance')
const mockLogger = { alert: jest.fn() }
jest.mock('../../../utils/eventLogger', () => ({
  useEventLogger: () => mockLogger,
}))
jest.mock('@uswds/uswds/src/js/components', () => ({
  ...jest.requireActual('@uswds/uswds/src/js/components'),
  fileInput: { init: jest.fn() },
}))

const participation = (programSlug, sectionNames, status) =>
  createProgramParticipation({
    programSlug,
    sectionNames,
    status,
    id: programSlug === 'ssp' ? 502 : 501,
  })
const a = createParticipationStt({
  name: 'Alabama',
  ssp: true,
  num_sections: 1,
  program_participations: [
    participation('tanf', ['Aggregate Data', 'Active Case Data']),
    participation('ssp', ['Closed Case Data']),
  ],
})
const b = createParticipationStt({
  id: 2,
  name: 'Alaska',
  ssp: true,
  num_sections: 4,
  program_participations: [
    participation('tanf', ['Aggregate Data']),
    participation('ssp', ['Closed Case Data']),
  ],
})
const row = (id, section, program_type = 'TAN', extra = {}) => ({
  id,
  section,
  program_type,
  original_filename: `history-${id}.txt`,
  extension: 'txt',
  year: 2024,
  quarter: 'Q1',
  slug: `history-${id}`,
  submitted_by: 'Tester',
  created_at: '2024-01-01T00:00:00Z',
  summary: { status: 'Accepted' },
  ...extra,
})
const Location = () => {
  const location = useLocation()
  return (
    <output data-testid="location">
      {location.search}
      {location.hash}
    </output>
  )
}
const setup = ({
  stts = [a, b],
  profile = a,
  role = 'OFA Admin',
  regions,
  url = '/?stt=Alabama&type=tanf&fy=2024&q=Q1#assigned',
  catalog,
  staleStt = 'Alaska',
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
    stts: catalog || { sttList: stts, loaded: true, loading: false },
  })
  store.dispatch({ type: 'SET_SELECTED_STT', payload: { stt: staleStt } })
  const view = render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[url]}>
        <Reports />
        <Location />
      </MemoryRouter>
    </Provider>
  )
  const stage = (uuid = 'staged-file', descriptor) => {
    let file
    act(() => {
      file = stageScopedFile(
        store,
        store.getState().reports.uploadScope,
        uuid,
        descriptor
      )
    })
    return file
  }
  return { ...view, store, stage }
}
const changeStt = (name) =>
  fireEvent.change(screen.getByTestId('stt-combobox'), {
    target: { value: name },
  })
const modalButton = (name) =>
  within(document.querySelector('#modal')).getByRole('button', { name })

describe('participation-driven TDR integration', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    get.mockResolvedValue({ ok: true, data: [] })
    window.HTMLElement.prototype.scrollIntoView = jest.fn()
  })

  it('renders shuffled sparse assignments in both areas, matching scalar rows and table kinds exactly', async () => {
    get.mockResolvedValue({
      ok: true,
      data: [
        row(1, 'Active Case Data'),
        row(3, 'Aggregate Data'),
        row(2, 'Closed Case Data', 'SSP'),
        row(4, 'Aggregate Data', 'SSP'),
        row(5, 'prefix Aggregate Data'),
      ],
    })
    const { container } = setup()
    expect(
      [...container.querySelectorAll('input[type=file]')].map(
        (input) => input.name
      )
    ).toEqual(['Active Case Data', 'Aggregate Data'])
    await screen.findByText('history-3.txt')
    const tables = screen.getAllByRole('table', { name: /^Section/ })
    expect(
      tables.map((table) => table.querySelector('caption').textContent)
    ).toEqual(['Section 1 - Active Case Data', 'Section 3 - Aggregate Data'])
    expect(
      within(tables[0]).getByText('Cases Without Errors')
    ).toBeInTheDocument()
    expect(within(tables[1]).getByText('Total Errors')).toBeInTheDocument()
    for (const id of [2, 4, 5])
      expect(screen.queryByText(`history-${id}.txt`)).not.toBeInTheDocument()
    fireEvent.click(screen.getByLabelText('SSP-MOE'))
    expect(
      screen.getByLabelText('Section 2 - SSP-MOE - Closed Case Data')
    ).toBeEnabled()
    expect(screen.getAllByRole('table', { name: /^Section/ })).toHaveLength(1)
    expect(screen.queryByText('history-1.txt')).not.toBeInTheDocument()
    await screen.findByText('history-2.txt')
    expect(screen.queryByText('history-3.txt')).not.toBeInTheDocument()
  })

  it('uses Tribal TANF participation, exact program labels, and TRIBAL scalar history codes', async () => {
    const tribe = createParticipationStt({
      id: 3,
      type: 'tribe',
      name: 'Test Tribe',
      program_participations: [participation('tribal', ['Stratum Data'])],
    })
    get.mockResolvedValue({
      ok: true,
      data: [row(1, 'Stratum Data', 'TRIBAL'), row(2, 'Stratum Data')],
    })
    setup({
      stts: [tribe],
      profile: tribe,
      role: 'Data Analyst',
      url: '/?type=tanf&fy=2024&q=Q1',
    })
    expect(
      screen.getByLabelText('Section 4 - Tribal TANF - Stratum Data')
    ).toBeEnabled()
    await screen.findByText('history-1.txt')
    expect(screen.queryByText('history-2.txt')).not.toBeInTheDocument()
  })

  it.each([
    ['missing metadata', undefined],
    ['missing participation', []],
    ['empty sections', [participation('tanf', [])]],
    ['malformed sections', [{ ...participation('tanf', []), sections: null }]],
    [
      'unsupported name',
      [
        {
          ...participation('tanf', ['Aggregate Data']),
          sections: [
            {
              ...participation('tanf', ['Aggregate Data']).sections[0],
              name: 'Unknown API Name',
            },
          ],
        },
      ],
    ],
  ])(
    'fails closed for %s, without default sections or history requests',
    (label, records) => {
      const stt = { ...a, program_participations: records }
      const { container, store } = setup({ stts: [stt] })
      expect(container.querySelectorAll('input[type=file]')).toHaveLength(0)
      expect(screen.queryAllByRole('table', { name: /^Section/ })).toHaveLength(
        0
      )
      expect(
        screen.queryByRole('button', { name: 'Submit Data Files' })
      ).not.toBeInTheDocument()
      expect(store.getState().reports.submittedFiles).toEqual([])
      expect(
        get.mock.calls.filter(([url]) => url.includes('/data_files/'))
      ).toHaveLength(0)
      expect(
        screen.getByText(
          /No report sections are assigned|Report section configuration/
        )
      ).toBeInTheDocument()
    }
  )

  it('keeps a valid SSP deep link and hash while waiting for catalog metadata', async () => {
    const { store } = setup({
      catalog: { sttList: [], loading: true, loaded: false },
      url: '/?stt=Alabama&type=ssp-moe&fy=2024&q=Q1#assigned',
    })
    expect(
      screen.getByText('Loading report assignments...')
    ).toBeInTheDocument()
    expect(screen.getByTestId('location')).toHaveTextContent('type=ssp-moe')
    expect(
      get.mock.calls.filter(([url]) => url.includes('/data_files/'))
    ).toHaveLength(0)
    act(() => store.dispatch({ type: SET_STTS, payload: { data: [a] } }))
    expect(
      screen.getByLabelText('Section 2 - SSP-MOE - Closed Case Data')
    ).toBeEnabled()
    expect(screen.getByTestId('location')).toHaveTextContent('#assigned')
  })

  it('never replaces a completed empty catalog assignment with older profile assignments', () => {
    const empty = { ...a, program_participations: [participation('tanf', [])] }
    const { store, container } = setup({
      stts: [empty],
      profile: a,
      role: 'Data Analyst',
    })
    expect(container.querySelectorAll('input[type=file]')).toHaveLength(0)
    expect(store.getState().reports.submittedFiles).toEqual([])
    expect(
      get.mock.calls.filter(([url]) => url.includes('/data_files/'))
    ).toHaveLength(0)
  })

  it('does not normalize a profile SSP deep link using incomplete catalog readiness', () => {
    const { store } = setup({
      role: 'Data Analyst',
      profile: { ...a, program_participations: [a.program_participations[0]] },
      catalog: { sttList: [], loading: true, loaded: false },
      url: '/?type=ssp-moe&fy=2024&q=Q1#assigned',
    })
    expect(screen.getByTestId('location')).toHaveTextContent('type=ssp-moe')
    expect(
      screen.getByText('Loading report assignments...')
    ).toBeInTheDocument()
    act(() => store.dispatch({ type: SET_STTS, payload: { data: [a] } }))
    expect(
      screen.getByLabelText('Section 2 - SSP-MOE - Closed Case Data')
    ).toBeEnabled()
  })

  it('honors the controlled URL over stale Redux STT and clears usable content with selection', () => {
    const { store } = setup({
      url: '/?stt=Alaska&type=tanf&fy=2024&q=Q1',
      staleStt: 'Alabama',
    })
    expect(store.getState().reports.uploadScope.sttId).toBe(2)
    expect(
      screen.getByLabelText('Section 3 - TANF - Aggregate Data')
    ).toBeEnabled()
    expect(
      screen.queryByLabelText('Section 1 - TANF - Active Case Data')
    ).not.toBeInTheDocument()
    changeStt('')
    expect(
      screen.queryByRole('button', { name: 'Submit Data Files' })
    ).not.toBeInTheDocument()
    expect(store.getState().reports.submittedFiles).toEqual([])
  })

  it.each(['Data Analyst', 'OFA Regional Staff'])(
    'blocks foreign URL STTs for %s',
    (role) => {
      const { container } = setup({
        role,
        regions: [{ stts: [a] }],
        url: '/?stt=Alaska&type=tanf&fy=2024&q=Q1',
      })
      expect(container.querySelectorAll('input[type=file]')).toHaveLength(0)
      expect(screen.queryAllByRole('table', { name: /^Section/ })).toHaveLength(
        0
      )
      expect(
        get.mock.calls.filter(([url]) => url.includes('/data_files/'))
      ).toHaveLength(0)
    }
  )

  it('resolves regional metadata only from permitted regions, retaining nondownloadable history', async () => {
    get.mockResolvedValue({ ok: true, data: [row(3, 'Aggregate Data')] })
    setup({
      role: 'OFA Regional Staff',
      regions: [{ stts: [b] }],
      url: '/?stt=Alaska&type=tanf&fy=2024&q=Q1',
      stts: [{ ...b, program_participations: [] }],
    })
    await screen.findByText('history-3.txt')
    expect(
      screen.queryByRole('button', { name: 'history-3.txt' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Submit Data Files' })
    ).not.toBeInTheDocument()
    expect(screen.getAllByRole('table', { name: /^Section/ })).toHaveLength(1)
  })

  it.each(['ACTIVE', 'FORMER', 'NEVER', 'unknown', null, undefined])(
    'ignores status %s at render, scope, and submit boundaries',
    async (status) => {
      const { store, stage } = setup()
      const scope = store.getState().reports.uploadScope
      const file = stage()
      const changed = {
        ...a,
        program_participations: a.program_participations.map((record) => ({
          ...record,
          status,
        })),
      }
      act(() =>
        store.dispatch({ type: SET_STTS, payload: { data: [changed, b] } })
      )
      expect(store.getState().reports.uploadScope).toBe(scope)
      expect(
        store
          .getState()
          .reports.submittedFiles.find((slot) => slot.uuid === file.uuid)
      ).toBeTruthy()
      post.mockResolvedValue({
        ok: true,
        data: row(9, file.section, 'TAN', { slug: file.uuid }),
      })
      fireEvent.click(screen.getByRole('button', { name: 'Submit Data Files' }))
      await waitFor(() => expect(post).toHaveBeenCalledTimes(1))
      expect(post.mock.calls[0][1].get('section')).toBe('Active Case Data')
    }
  )

  it.each(['stt', 'program'])(
    'uses the same discard path for confirmed %s changes, while Cancel retains files',
    (field) => {
      const { store, stage } = setup()
      const file = stage()
      const scope = store.getState().reports.uploadScope
      const change = () =>
        field === 'stt'
          ? changeStt('Alaska')
          : fireEvent.click(screen.getByLabelText('SSP-MOE'))
      change()
      fireEvent.click(modalButton('Cancel'))
      expect(store.getState().reports.uploadScope).toBe(scope)
      expect(
        store
          .getState()
          .reports.submittedFiles.some((slot) => slot.uuid === file.uuid)
      ).toBe(true)
      change()
      fireEvent.click(modalButton('OK'))
      expect(store.getState().reports.uploadScope.key).not.toBe(scope.key)
      expect(
        store.getState().reports.submittedFiles.every((slot) => !slot.uuid)
      ).toBe(true)
      expect(screen.getByTestId('location')).toHaveTextContent('#assigned')
    }
  )

  it('submits sparse canonical numbers and scalar names, preserving the SSP discriminator', async () => {
    const { store, stage } = setup()
    stage('one')
    const scope = store.getState().reports.uploadScope
    stage('three', scope.sections[1])
    post.mockImplementation((url, data) =>
      Promise.resolve({
        ok: true,
        data: row(
          data.get('section') === 'Aggregate Data' ? 3 : 1,
          data.get('section'),
          'TAN',
          { slug: data.get('slug') }
        ),
      })
    )
    fireEvent.click(screen.getByRole('button', { name: 'Submit Data Files' }))
    await screen.findByText(/Successfully uploaded section\(s\): 1, and 3/)
    expect(post).toHaveBeenCalledTimes(2)
    post.mock.calls.forEach(([, data]) => {
      expect(data.get('ssp')).toBe('false')
      expect(data.has('sectionId')).toBe(false)
      expect(data.has('program')).toBe(false)
    })
    expect(
      store.getState().reports.submittedFiles.every((file) => !file.uuid)
    ).toBe(true)
  })

  it('rejects an entire batch containing a hidden stale Redux file rather than filtering it out', () => {
    const { store, stage } = setup()
    stage()
    const root = createRootReducer(history)
    store.replaceReducer((state, action) =>
      action.type === 'TEST_HIDDEN_STALE_FILE'
        ? {
            ...state,
            reports: {
              ...state.reports,
              submittedFiles: [
                ...state.reports.submittedFiles,
                {
                  section: 'Closed Case Data',
                  fileName: 'hidden.txt',
                  uuid: 'hidden',
                  sectionId: 999,
                  program: { id: 33, slug: 'ssp' },
                },
              ],
            },
          }
        : root(state, action)
    )
    act(() => store.dispatch({ type: 'TEST_HIDDEN_STALE_FILE' }))
    fireEvent.click(screen.getByRole('button', { name: 'Submit Data Files' }))
    expect(
      screen.getByText(/A staged file is no longer assigned/)
    ).toBeInTheDocument()
    expect(post).not.toHaveBeenCalled()
  })

  it.each(['stt', 'program', 'replacement', 'assignment'])(
    'suppresses a late POST and local side effects after %s changes, but audits the server write',
    async (change) => {
      const pending = deferred()
      post.mockReturnValueOnce(pending.promise)
      const { store, stage } = setup()
      const file = stage()
      fireEvent.click(screen.getByRole('button', { name: 'Submit Data Files' }))
      if (change === 'stt' || change === 'program') {
        if (change === 'stt') changeStt('Alaska')
        else fireEvent.click(screen.getByLabelText('SSP-MOE'))
        fireEvent.click(modalButton('OK'))
      } else if (change === 'assignment') {
        act(() =>
          store.dispatch({
            type: SET_STTS,
            payload: {
              data: [
                {
                  ...a,
                  program_participations: [
                    participation('tanf', ['Aggregate Data']),
                  ],
                },
                b,
              ],
            },
          })
        )
      }
      const replacement = stage('replacement')
      const getCount = get.mock.calls.length
      await act(async () =>
        pending.resolve({
          ok: true,
          data: row(99, file.section, 'TAN', { slug: file.uuid }),
        })
      )
      expect(
        store
          .getState()
          .reports.submittedFiles.some((slot) => slot.uuid === replacement.uuid)
      ).toBe(true)
      expect(
        screen.queryByText(/Successfully uploaded/)
      ).not.toBeInTheDocument()
      expect(store.getState().feedbackWidget.isOpen).not.toBe(true)
      expect(get).toHaveBeenCalledTimes(getCount)
      expect(mockLogger.alert).toHaveBeenCalledTimes(1)
    }
  )

  it('hides late history responses on STT change and does not restart old polling', async () => {
    const old = deferred()
    get.mockReturnValueOnce(old.promise)
    setup()
    changeStt('Alaska')
    await act(async () =>
      old.resolve({
        ok: true,
        data: [
          row(1, 'Aggregate Data', 'TAN', { summary: { status: 'Pending' } }),
        ],
      })
    )
    expect(screen.queryByText('history-1.txt')).not.toBeInTheDocument()
    expect(get.mock.calls.every(([url]) => url.includes('/data_files/?'))).toBe(
      true
    )
  })

  it('blocks an old FileReader after metadata removes its assigned section', async () => {
    const originalReader = global.FileReader
    const readers = []
    global.FileReader = jest.fn(() => {
      const reader = {
        readAsArrayBuffer: jest.fn(),
        result: new ArrayBuffer(8),
      }
      readers.push(reader)
      return reader
    })
    try {
      const { store } = setup()
      fireEvent.change(
        screen.getByLabelText('Section 1 - TANF - Active Case Data'),
        { target: { files: [new File(['old'], 'old.pdf')] } }
      )
      act(() =>
        store.dispatch({
          type: SET_STTS,
          payload: {
            data: [
              {
                ...a,
                program_participations: [
                  participation('tanf', ['Aggregate Data']),
                ],
              },
            ],
          },
        })
      )
      const current = store.getState().reports
      await act(async () => readers[0].onload())
      expect(store.getState().reports.submittedFiles).toBe(
        current.submittedFiles
      )
      expect(current.submittedFiles.map((file) => file.section)).toEqual([
        'Aggregate Data',
      ])
      expect(current.submittedFiles[0].uuid).toBeNull()
      expect(screen.queryByText(/Invalid extension/)).not.toBeInTheDocument()
    } finally {
      global.FileReader = originalReader
    }
  })

  it('invalidates an in-flight history poll, including its late failure and retry', async () => {
    jest.useFakeTimers()
    const pendingPoll = deferred()
    get.mockImplementation((url) => {
      if (url.includes('/data_files/1/')) return pendingPoll.promise
      return Promise.resolve({
        ok: true,
        data: url.includes('stt=1&')
          ? [
              row(1, 'Aggregate Data', 'TAN', {
                summary: { status: 'Pending' },
              }),
            ]
          : [],
      })
    })
    const view = setup()
    await act(async () => {})
    await act(async () => jest.advanceTimersByTime(0))
    expect(
      get.mock.calls.filter(([url]) => url.includes('/data_files/1/'))
    ).toHaveLength(1)
    changeStt('Alaska')
    await act(async () => pendingPoll.reject(new Error('Old poll failed')))
    await act(async () => jest.advanceTimersByTime(10000))
    expect(
      get.mock.calls.filter(([url]) => url.includes('/data_files/1/'))
    ).toHaveLength(1)
    expect(screen.queryByText('history-1.txt')).not.toBeInTheDocument()
    expect(screen.queryByText(/Old poll failed/)).not.toBeInTheDocument()
    view.unmount()
    jest.useRealTimers()
  })

  it('submits an assigned SSP section with the unchanged scalar discriminator and audits it', async () => {
    const { stage, store } = setup({
      url: '/?stt=Alabama&type=ssp-moe&fy=2024&q=Q1',
    })
    const file = stage('ssp-file')
    post.mockResolvedValue({
      ok: true,
      data: row(2, 'Closed Case Data', 'SSP', { slug: file.uuid }),
    })
    fireEvent.click(screen.getByRole('button', { name: 'Submit Data Files' }))
    await screen.findByText(/Successfully uploaded section\(s\): 2/)
    const data = post.mock.calls[0][1]
    expect(data.get('ssp')).toBe('true')
    expect(data.get('section')).toBe('Closed Case Data')
    expect(data.get('stt')).toBe('1')
    expect(mockLogger.alert).toHaveBeenCalledTimes(1)
    expect(store.getState().feedbackWidget.dataFiles[0].program_type).toBe(
      'SSP'
    )
  })

  it.each([
    ['legacy false with a record', { ...a, ssp: false }],
    [
      'legacy true without a record',
      { ...a, program_participations: [a.program_participations[0]] },
    ],
  ])('keeps the temporary SSP conjunction: %s', (label, stt) => {
    setup({ stts: [stt], url: '/?stt=Alabama&type=ssp-moe&fy=2024&q=Q1' })
    expect(screen.queryByLabelText('SSP-MOE')).not.toBeInTheDocument()
    expect(screen.getByLabelText('TANF')).toBeChecked()
    expect(screen.queryByLabelText(/Section.*SSP-MOE/)).not.toBeInTheDocument()
  })
})
