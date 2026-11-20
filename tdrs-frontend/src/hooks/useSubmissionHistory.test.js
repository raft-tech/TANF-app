import React from 'react'
import { render, renderHook, act, waitFor } from '@testing-library/react'
import configureMockStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import { thunk } from 'redux-thunk'

import { useSubmissionHistory } from './useSubmissionHistory'
import { SET_TANF_SUBMISSION_STATUS } from '../actions/reports'
import { get } from '../fetch-instance'
import { createReportsStore, deferred } from '../test-utils/reportScopes'

jest.mock('../fetch-instance')

const mockContext = {
  isPolling: {},
  startPolling: jest.fn(),
}

jest.mock('../components/Reports/ReportsContext', () => ({
  useReportsContext: () => mockContext,
}))

const mockStore = configureMockStore([thunk])

const renderWithStore = (store, filterValues) => {
  const TestComponent = () => {
    useSubmissionHistory(filterValues)
    return null
  }

  const renderResult = render(
    <Provider store={store}>
      <TestComponent />
    </Provider>
  )

  return { ...renderResult, TestComponent }
}

describe('useSubmissionHistory', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockContext.isPolling = {}
    get.mockResolvedValue({ ok: true, data: [] })
  })

  it('restarts polling for pending files when history loads', async () => {
    const pendingFile = { id: 1, summary: { status: 'Pending' } }
    const completedFile = { id: 2, summary: { status: 'Approved' } }
    const store = mockStore({
      reports: {
        files: [pendingFile, completedFile],
        loading: false,
      },
    })

    renderWithStore(store, {
      quarter: 'Q1',
      stt: { id: 1 },
      year: '2021',
      file_type: 'test',
    })

    await waitFor(() => {
      expect(mockContext.startPolling).toHaveBeenCalledWith(
        `${pendingFile.id}`,
        expect.any(Function),
        expect.any(Function),
        expect.any(Function),
        expect.any(Function),
        expect.any(Function)
      )
    })
  })

  it('does not restart polling when already polling a file', async () => {
    const pendingFile = { id: 3, summary: { status: 'Pending' } }
    mockContext.isPolling = { 3: true }
    const store = mockStore({
      reports: {
        files: [pendingFile],
        loading: false,
      },
    })

    renderWithStore(store, {
      quarter: 'Q1',
      stt: { id: 1 },
      year: '2021',
      file_type: 'test',
    })

    await waitFor(() => {
      expect(mockContext.startPolling).not.toHaveBeenCalled()
    })
  })

  it('does not restart polling when isPolling changes without new files', async () => {
    const pendingFile = { id: 4, summary: { status: 'Pending' } }
    const store = mockStore({
      reports: {
        files: [pendingFile],
        loading: false,
      },
    })

    const renderResult = renderWithStore(store, {
      quarter: 'Q1',
      stt: { id: 1 },
      year: '2021',
      file_type: 'test',
    })

    await waitFor(() => {
      expect(mockContext.startPolling).toHaveBeenCalledTimes(1)
    })

    mockContext.isPolling = { 4: true }
    renderResult.rerender(
      <Provider store={store}>
        <renderResult.TestComponent />
      </Provider>
    )

    await waitFor(() => {
      expect(mockContext.startPolling).toHaveBeenCalledTimes(1)
    })
  })

  it('does not fetch file list on first render when polling has not started', async () => {
    mockContext.isPolling = { 1: false }
    const store = mockStore({
      reports: {
        files: [],
        loading: false,
      },
    })

    renderWithStore(store, {
      quarter: 'Q1',
      stt: { id: 1 },
      year: '2021',
      file_type: 'test',
    })

    await waitFor(() => {
      expect(store.getActions()).toEqual([])
      expect(mockContext.startPolling).not.toHaveBeenCalled()
    })
  })

  it('uses polling callbacks to determine completion and dispatch status updates', async () => {
    const pendingFile = { id: 9, summary: { status: 'Pending' } }
    const store = mockStore({
      reports: {
        files: [pendingFile],
        loading: false,
      },
    })

    renderWithStore(store, {
      quarter: 'Q1',
      stt: { id: 1 },
      year: '2021',
      file_type: 'test',
    })

    await waitFor(() => {
      expect(mockContext.startPolling).toHaveBeenCalledTimes(1)
    })

    const [, fetchStatusAction, shouldStopPolling, handleSuccess] =
      mockContext.startPolling.mock.calls[0]

    expect(typeof fetchStatusAction()).toBe('object')
    expect(
      shouldStopPolling({ data: { summary: { status: 'Pending' } } })
    ).toBe(false)
    expect(
      shouldStopPolling({ data: { summary: { status: 'Accepted' } } })
    ).toBe(true)
    expect(shouldStopPolling({ data: {} })).toBeUndefined()

    const response = {
      data: { id: pendingFile.id, summary: { status: 'Accepted' } },
    }
    handleSuccess(response)

    expect(store.getActions()).toContainEqual({
      type: SET_TANF_SUBMISSION_STATUS,
      payload: {
        datafile_id: pendingFile.id,
        datafile: response.data,
      },
    })
  })
})

describe('scoped useSubmissionHistory', () => {
  const filters = {
    stt: { id: 1 },
    file_type: 'tanf',
    year: '2024',
    quarter: 'Q1',
  }
  const setup = (initialFilters = filters, enabled = true) => {
    const store = createReportsStore()
    const renders = []
    const hook = renderHook(
      ({ filterValues, enabled }) => {
        const history = useSubmissionHistory(filterValues, {
          scoped: true,
          enabled,
        })
        renders.push({ filterValues, ...history })
        return history
      },
      {
        initialProps: { filterValues: initialFilters, enabled },
        wrapper: ({ children }) => (
          <Provider store={store}>{children}</Provider>
        ),
      }
    )
    return { ...hook, store, renders }
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockContext.isPolling = { 99: false }
    get.mockResolvedValue({ ok: true, data: [] })
  })

  it('fetches on first mount/remount despite stale completed polling flags', async () => {
    const first = setup()
    await waitFor(() => expect(first.result.current.loading).toBe(false))
    expect(get).toHaveBeenCalledTimes(1)
    first.unmount()
    const second = setup()
    await waitFor(() => expect(second.result.current.loading).toBe(false))
    expect(get).toHaveBeenCalledTimes(2)
  })

  it('uses primitive query identity instead of nested metadata or object references', async () => {
    const hook = setup()
    await waitFor(() => expect(hook.result.current.loading).toBe(false))
    hook.rerender({
      filterValues: { ...filters, stt: { id: 1, program_participations: [] } },
      enabled: true,
    })
    expect(get).toHaveBeenCalledTimes(1)
  })

  it('hides old rows on the selection render and never restarts polling for a late result', async () => {
    const old = deferred()
    const newer = deferred()
    get.mockReturnValueOnce(old.promise).mockReturnValueOnce(newer.promise)
    const hook = setup()
    hook.rerender({
      filterValues: { ...filters, stt: { id: 2 } },
      enabled: true,
    })
    await act(async () => {
      newer.resolve({
        ok: true,
        data: [
          { id: 2, section: 'Aggregate Data', summary: { status: 'Accepted' } },
        ],
      })
    })
    await act(async () => {
      old.resolve({
        ok: true,
        data: [
          { id: 1, section: 'Aggregate Data', summary: { status: 'Pending' } },
        ],
      })
    })
    expect(hook.result.current.files.map((file) => file.id)).toEqual([2])
    expect(mockContext.startPolling).not.toHaveBeenCalled()

    const third = deferred()
    get.mockReturnValueOnce(third.promise)
    hook.rerender({ filterValues: { ...filters, year: '2025' }, enabled: true })
    const firstNewPeriodRender = hook.renders.find(
      (entry) => entry.filterValues.year === '2025'
    )
    expect(firstNewPeriodRender.files).toEqual([])
    await act(async () => {
      third.resolve({ ok: true, data: [] })
    })
  })

  it('guards old poll callbacks after clearing selection and cancels its timer', async () => {
    const cancel = jest.fn()
    mockContext.startPolling.mockReturnValue(cancel)
    get.mockResolvedValueOnce({
      ok: true,
      data: [
        { id: 7, section: 'Aggregate Data', summary: { status: 'Pending' } },
      ],
    })
    const hook = setup()
    await waitFor(() =>
      expect(mockContext.startPolling).toHaveBeenCalledTimes(1)
    )
    const args = mockContext.startPolling.mock.calls[0]
    expect(args[0]).toContain(':7')
    expect(args[8].isCurrent()).toBe(true)
    hook.rerender({ filterValues: { ...filters, stt: null }, enabled: true })
    expect(args[8].isCurrent()).toBe(false)
    act(() => args[3]({ data: { id: 7, summary: { status: 'Accepted' } } }))
    expect(hook.result.current.files).toEqual([])
    expect(cancel).toHaveBeenCalledTimes(1)
    expect(get).toHaveBeenCalledTimes(1)
  })

  it('does not fetch an explicitly disabled or unresolved history query', () => {
    const hook = setup(filters, false)
    expect(hook.result.current.files).toEqual([])
    expect(get).not.toHaveBeenCalled()
    hook.rerender({ filterValues: { ...filters, stt: null }, enabled: true })
    expect(get).not.toHaveBeenCalled()
  })
})
