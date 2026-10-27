import React from 'react'
import { act, renderHook, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { useFileUploadForm } from './useFileUploadForm'
import { configureUploadSections, clearFileList } from '../actions/reports'
import { get, post } from '../fetch-instance'
import {
  createReportsStore,
  uploadConfiguration,
  stageScopedFile,
  deferred,
} from '../test-utils/reportScopes'

jest.mock('../fetch-instance')
const mockLogger = { alert: jest.fn() }
jest.mock('../utils/eventLogger', () => ({ useEventLogger: () => mockLogger }))
let mockContext
jest.mock('../components/Reports/ReportsContext', () => ({
  useReportsContext: () => mockContext,
}))

describe('opt-in scoped upload form', () => {
  const setup = () => {
    const store = createReportsStore()
    const scope = store.dispatch(configureUploadSections(uploadConfiguration()))
    const file = stageScopedFile(store, scope)
    mockContext = {
      yearInputValue: '2024',
      quarterInputValue: 'Q1',
      fileTypeInputValue: 'tanf',
      uploadedFiles: [file],
      setUploadAlertState: jest.fn(),
      setProcessingAlertState: jest.fn(),
      handleOpenFeedbackWidget: jest.fn(),
      handleClearFilesOnly: jest.fn(() =>
        store.dispatch(clearFileList({ fileType: 'tanf' }))
      ),
      startPolling: jest.fn(),
    }
    const hook = renderHook(
      ({ scope }) =>
        useFileUploadForm({
          stt: { id: scope.sttId },
          uploadScope: scope,
          formatSections: () => '3',
          getSubmitPayload: (payload) => ({ ...payload, ssp: false }),
        }),
      {
        initialProps: { scope },
        wrapper: ({ children }) => (
          <Provider store={store}>{children}</Provider>
        ),
      }
    )
    const response = {
      ok: true,
      data: {
        id: 42,
        slug: file.uuid,
        section: file.section,
        original_filename: file.fileName,
        program_type: 'TAN',
        extension: 'txt',
      },
    }
    return { ...hook, store, scope, file, response }
  }
  beforeEach(() => {
    jest.clearAllMocks()
    get.mockResolvedValue({ ok: true, data: [] })
  })

  it('does not submit a scoped file while its validation is still pending', async () => {
    const hook = setup()
    mockContext.uploadedFiles = [{ ...hook.file, isValidating: true }]
    hook.rerender({ scope: hook.scope })
    await act(async () => {
      await hook.result.current.onSubmit({ preventDefault: jest.fn() })
    })
    expect(post).not.toHaveBeenCalled()
    expect(mockContext.setUploadAlertState).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'error' })
    )
  })

  it.each(['selection', 'replacement', 'period', 'unmount'])(
    'does not clear, refresh, announce, poll, or open feedback for a stale %s completion',
    async (transition) => {
      const pending = deferred()
      post.mockReturnValueOnce(pending.promise)
      const hook = setup()
      let submitted
      act(() => {
        submitted = hook.result.current.onSubmit({ preventDefault: jest.fn() })
      })
      if (transition === 'selection') {
        let scope
        act(() => {
          scope = hook.store.dispatch(
            configureUploadSections(uploadConfiguration({ sttId: 2 }))
          )
        })
        mockContext.uploadedFiles = []
        hook.rerender({ scope })
      } else if (transition === 'replacement') {
        act(() => {
          mockContext.uploadedFiles = [
            stageScopedFile(hook.store, hook.scope, 'replacement'),
          ]
        })
        hook.rerender({ scope: hook.scope })
      } else if (transition === 'period') {
        mockContext.quarterInputValue = 'Q2'
        hook.rerender({ scope: hook.scope })
      } else hook.unmount()
      await act(async () => {
        pending.resolve(hook.response)
        await submitted
      })
      expect(mockContext.handleClearFilesOnly).not.toHaveBeenCalled()
      expect(mockContext.handleOpenFeedbackWidget).not.toHaveBeenCalled()
      expect(mockContext.setUploadAlertState).not.toHaveBeenCalled()
      expect(mockContext.setProcessingAlertState).not.toHaveBeenCalled()
      expect(mockContext.startPolling).not.toHaveBeenCalled()
      expect(get).not.toHaveBeenCalled()
      expect(mockLogger.alert).toHaveBeenCalledTimes(1)
    }
  )

  it('clears successful current uploads and guards the history refresh/poll after navigation', async () => {
    const history = deferred()
    get.mockReturnValueOnce(history.promise)
    const hook = setup()
    post.mockResolvedValueOnce(hook.response)
    await act(async () => {
      await hook.result.current.onSubmit({ preventDefault: jest.fn() })
    })
    expect(mockContext.handleClearFilesOnly).toHaveBeenCalledTimes(1)
    expect(mockContext.handleOpenFeedbackWidget).toHaveBeenCalledWith([
      hook.response.data,
    ])
    expect(hook.store.getState().reports.submittedFiles[0].uuid).toBeNull()
    expect(get).toHaveBeenCalledTimes(1)
    let nextScope
    act(() => {
      nextScope = hook.store.dispatch(
        configureUploadSections(uploadConfiguration({ sttId: 2 }))
      )
    })
    hook.rerender({ scope: nextScope })
    await act(async () => {
      history.resolve({ ok: true, data: [hook.response.data] })
    })
    expect(mockContext.startPolling).not.toHaveBeenCalled()
    expect(hook.store.getState().reports.files).toEqual([])
  })

  it('prevents old polling errors/timeouts from alerting a newer selection', async () => {
    const hook = setup()
    post.mockResolvedValueOnce(hook.response)
    await act(async () => {
      await hook.result.current.onSubmit({ preventDefault: jest.fn() })
    })
    await waitFor(() =>
      expect(mockContext.startPolling).toHaveBeenCalledTimes(1)
    )
    const poll = mockContext.startPolling.mock.calls[0]
    mockContext.setProcessingAlertState.mockClear()
    mockContext.quarterInputValue = 'Q2'
    hook.rerender({ scope: hook.store.getState().reports.uploadScope })
    expect(poll[8].isCurrent()).toBe(false)
    act(() => {
      poll[4](new Error('old error'))
      poll[5](poll[4])
    })
    expect(mockContext.setProcessingAlertState).not.toHaveBeenCalled()
  })
})
