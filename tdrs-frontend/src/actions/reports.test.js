import { get, post } from '../fetch-instance'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { v4 as uuidv4 } from 'uuid'

import {
  START_FILE_DOWNLOAD,
  SET_FILE,
  SET_FILE_LIST,
  FILE_DOWNLOAD_ERROR,
  DOWNLOAD_DIALOG_OPEN,
  SET_FILE_ERROR,
  SET_SELECTED_STT,
  setStt,
  upload,
  download,
  getAvailableFileList,
  submit,
  getTanfSubmissionStatus,
  SET_FILE_SUBMITTED,
  configureUploadSections,
  INVALIDATE_FILE_LIST,
} from './reports'
import {
  createReportsStore,
  deferred,
  uploadConfiguration,
  stageScopedFile,
} from '../test-utils/reportScopes'

jest.mock('../fetch-instance')

describe('actions/reports', () => {
  const mockStore = configureStore([thunk])

  it('should dispatch SET_FILE', async () => {
    const store = mockStore()

    await store.dispatch(
      upload({
        file: { name: 'HELLO', type: 'text/plain' },
        section: 'Active Case Data',
      })
    )

    const actions = store.getActions()

    const { uuid } = actions[0].payload

    expect(actions[0].type).toBe(SET_FILE)
    expect(actions[0].payload).toStrictEqual({
      file: { name: 'HELLO', type: 'text/plain' },
      fileName: 'HELLO',
      fileType: 'text/plain',
      section: 'Active Case Data',
      uuid,
    })
  })

  it('should dispatch SET_FILE_ERROR when there is an error with the post', async () => {
    const store = mockStore()

    await store.dispatch(
      upload({ boop: 'asdasd', section: 'Active Case Data' })
    )

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_FILE_ERROR)
    expect(actions[0].payload).toHaveProperty('error')
  })

  it('should dispatch OPEN_FILE_DIALOG when a file has been successfully downloaded', async () => {
    window.URL.createObjectURL = jest.fn(() => null)
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: 'Some text',
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(
      download({
        id: 1,
        section: 'Active Case Data',
        fileName: 'test.txt',
      })
    )
    const actions = store.getActions()

    expect(actions[0].type).toBe(START_FILE_DOWNLOAD)
    try {
      expect(actions[1].type).toBe(DOWNLOAD_DIALOG_OPEN)
    } catch (err) {
      throw actions[1].payload.error
    }
  })

  it('should dispatch SET_FILE_LIST', async () => {
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: [
          {
            fileName: 'test.txt',
            section: 'Active Case Data',
            uuid: uuidv4(),
          },
          {
            fileName: 'testb.txt',
            section: 'Closed Case Data',
            uuid: uuidv4(),
          },
        ],
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(
      getAvailableFileList({
        stt: { id: 10 },
        year: 2020,
      })
    )
    const actions = store.getActions()
    try {
      expect(actions[1].type).toBe(SET_FILE_LIST)
    } catch (err) {
      throw actions[1].payload.error
    }
  })

  it('should dispatch SET_FILE_SUBMITTED', async () => {
    const uuid = uuidv4()
    post.mockImplementationOnce(() =>
      Promise.resolve({
        data: {
          extension: 'txt',
          id: 1,
          original_filename: 'Test.txt',
          quarter: 'Q1',
          section: 'Stratum Data',
          slug: uuid,
          year: 2021,
        },
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(
      submit({
        formattedSections: '4',
        logger: { alert: jest.fn() },
        quarter: 'Q1',
        setUploadAlertState: jest.fn(),
        setProcessingAlertState: jest.fn(),
        stt: { id: 10 },
        uploadedFiles: [
          {
            file: { name: 'Test.txt', type: 'text/plain' },
            fileName: 'Test.txt',
            section: 'Stratum Data',
            uuid,
          },
        ],
        user: { id: 1 },
        year: 2021,
      })
    )
    const actions = store.getActions()

    try {
      expect(post).toHaveBeenCalledTimes(1)
      expect(actions[0].type).toBe(SET_FILE_SUBMITTED)
    } catch (err) {
      throw actions[0].payload.error
    }
  })

  it.each([
    [
      {
        non_field_errors: ['Something went wrong'],
      },
      null,
    ],
    [
      {
        detail: 'Something went wrong',
      },
      null,
    ],
    [{ file: 'Something went wrong' }, null],
    [{}, 'Error: null'],
  ])(
    'should set local alert state on submission failure',
    async (data, msg) => {
      const uuid = uuidv4()
      post.mockImplementationOnce(() =>
        Promise.resolve({
          data,
          ok: false,
          status: 400,
          error: new Error('Error'),
        })
      )
      const store = mockStore()

      const setUploadAlertState = jest.fn()

      await store.dispatch(
        submit({
          formattedSections: '4',
          logger: { alert: jest.fn() },
          quarter: 'Q1',
          setUploadAlertState: setUploadAlertState,
          stt: { id: 10 },
          uploadedFiles: [
            {
              file: { name: 'Test.txt', type: 'text/plain' },
              fileName: 'Test.txt',
              section: 'Stratum Data',
              uuid,
            },
          ],
          user: { id: 1 },
          year: 2021,
        })
      )

      expect(post).toHaveBeenCalledTimes(1)
      expect(setUploadAlertState).toHaveBeenCalledWith({
        active: true,
        message: msg || 'Error: Something went wrong',
        type: 'error',
      })
    }
  )

  it('should dispatch FILE_DOWNLOAD_ERROR if no year is provided to download', async () => {
    const store = mockStore()

    await store.dispatch(
      download({
        section: 'Active Case Data',
      })
    )
    const actions = store.getActions()
    expect(actions[0].type).toBe(FILE_DOWNLOAD_ERROR)
  })

  it('should dispatch SET_SELECTED_STT', async () => {
    const store = mockStore()

    await store.dispatch(setStt('florida'))

    const actions = store.getActions()
    expect(actions[0].type).toBe(SET_SELECTED_STT)
    expect(actions[0].payload).toStrictEqual({
      stt: 'florida',
    })
  })

  it('should dispatch SET_SELECTED_STT with empty stt', async () => {
    const store = mockStore()

    await store.dispatch(setStt(''))

    const actions = store.getActions()
    expect(actions[0].type).toBe(SET_SELECTED_STT)
    expect(actions[0].payload).toStrictEqual({
      stt: '',
    })
  })

  it('returns submission status when fetch succeeds', async () => {
    const responseData = { id: 123, status: 'accepted' }
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: responseData,
        ok: true,
        error: null,
      })
    )

    const result = await getTanfSubmissionStatus(123)

    expect(result).toEqual({ data: responseData, ok: true })
  })

  it('throws when submission status fetch fails', async () => {
    const error = new Error('Request failed')
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: null,
        ok: false,
        error,
      })
    )

    await expect(getTanfSubmissionStatus(123)).rejects.toThrow('Request failed')
  })
})

describe('scoped report requests', () => {
  const filters = {
    stt: { id: 1 },
    year: '2024',
    quarter: 'Q1',
    file_type: 'tanf',
  }
  const responseFor = (file) => ({
    ok: true,
    data: {
      id: 42,
      slug: file.uuid,
      original_filename: file.fileName,
      extension: 'txt',
      section: file.section,
      program_type: 'TAN',
    },
  })
  const payloadFor = (scope, file) => ({
    uploadScope: scope,
    uploadedFiles: [file],
    formattedSections: '3',
    logger: { alert: jest.fn() },
    setUploadAlertState: jest.fn(),
    setProcessingAlertState: jest.fn(),
    user: { id: 1 },
    stt: scope.sttId,
    year: '2024',
    quarter: 'Q1',
    ssp: false,
    fileType: 'tanf',
  })

  it.each([false, true])(
    'rejects old history results/errors before callbacks (same query: %s)',
    async (sameQuery) => {
      const store = createReportsStore()
      const old = deferred()
      const newer = deferred()
      const onOldSuccess = jest.fn()
      const onNewSuccess = jest.fn()
      get.mockReturnValueOnce(old.promise).mockReturnValueOnce(newer.promise)
      const first = store.dispatch(
        getAvailableFileList(filters, onOldSuccess, { scoped: true })
      )
      const second = store.dispatch(
        getAvailableFileList(
          sameQuery ? filters : { ...filters, file_type: 'ssp-moe' },
          onNewSuccess,
          { scoped: true }
        )
      )
      newer.resolve({
        ok: true,
        data: [{ id: 2, section: 'Closed Case Data' }],
      })
      await second
      const current = store.getState().reports
      old.resolve({ ok: true, data: [{ id: 1, section: 'Active Case Data' }] })
      await first
      expect(store.getState().reports).toBe(current)
      expect(current.files.map((file) => file.id)).toEqual([2])
      expect(onOldSuccess).not.toHaveBeenCalled()
      expect(onNewSuccess).toHaveBeenCalledTimes(1)
    }
  )

  it.each(['error-response', 'network-error'])(
    'does not end a newer query when an old %s arrives',
    async (errorType) => {
      const store = createReportsStore()
      const old = deferred()
      const newer = deferred()
      get.mockReturnValueOnce(old.promise).mockReturnValueOnce(newer.promise)
      const first = store.dispatch(
        getAvailableFileList(filters, undefined, { scoped: true })
      )
      const second = store.dispatch(
        getAvailableFileList({ ...filters, year: '2025' }, undefined, {
          scoped: true,
        })
      )
      if (errorType === 'network-error') old.reject(new Error('offline'))
      else old.resolve({ ok: false, error: new Error('bad request') })
      await first
      expect(store.getState().reports.loading).toBe(true)
      newer.resolve({ ok: true, data: [] })
      await second
      expect(store.getState().reports.loading).toBe(false)
    }
  )

  it('does not restore a cleared history selection or run its completion callback', async () => {
    const store = createReportsStore()
    const pending = deferred()
    const onSuccess = jest.fn()
    get.mockReturnValueOnce(pending.promise)
    const request = store.dispatch(
      getAvailableFileList(filters, onSuccess, { scoped: true })
    )
    const historyScope = store.getState().reports.historyScope
    store.dispatch({ type: INVALIDATE_FILE_LIST, payload: { historyScope } })
    pending.resolve({ ok: true, data: [{ id: 1 }] })
    await request
    expect(onSuccess).not.toHaveBeenCalled()
    expect(store.getState().reports.files).toEqual([])
  })

  it.each(['selection', 'replacement', 'unmounted'])(
    'retains successful server outcomes/audits but suppresses stale %s UI effects',
    async (transition) => {
      const store = createReportsStore()
      const scope = store.dispatch(
        configureUploadSections(uploadConfiguration())
      )
      const file = stageScopedFile(store, scope)
      const payload = payloadFor(scope, file)
      let mounted = true
      payload.isCurrent = () => mounted
      const pending = deferred()
      post.mockReturnValueOnce(pending.promise)
      const onComplete = jest.fn()
      const request = store.dispatch(submit(payload, onComplete))
      if (transition === 'selection')
        store.dispatch(
          configureUploadSections(uploadConfiguration({ sttId: 2 }))
        )
      else if (transition === 'replacement')
        stageScopedFile(store, scope, 'replacement')
      else mounted = false
      const current = store.getState().reports
      const response = responseFor(file)
      pending.resolve(response)
      await expect(request).resolves.toEqual([response.data])
      expect(store.getState().reports).toBe(current)
      expect(payload.logger.alert).toHaveBeenCalledWith(expect.any(String), {
        files: [42],
        activity: 'upload',
      })
      expect(payload.setProcessingAlertState).not.toHaveBeenCalled()
      expect(payload.setUploadAlertState).not.toHaveBeenCalled()
      expect(onComplete).not.toHaveBeenCalled()
    }
  )

  it('ignores stale POST errors after switching programs', async () => {
    const store = createReportsStore()
    const scope = store.dispatch(configureUploadSections(uploadConfiguration()))
    const payload = payloadFor(scope, stageScopedFile(store, scope))
    const pending = deferred()
    post.mockReturnValueOnce(pending.promise)
    const request = store.dispatch(submit(payload))
    store.dispatch(
      configureUploadSections(uploadConfiguration({ programSlug: 'ssp' }))
    )
    pending.reject(new Error('offline'))
    await request
    expect(payload.setUploadAlertState).not.toHaveBeenCalled()
  })

  it('preserves the scalar multipart contract and updates only the captured UUID', async () => {
    const store = createReportsStore()
    const scope = store.dispatch(configureUploadSections(uploadConfiguration()))
    const file = stageScopedFile(store, scope)
    const payload = payloadFor(scope, file)
    const response = responseFor(file)
    const onComplete = jest.fn()
    post.mockResolvedValueOnce(response)
    await store.dispatch(submit(payload, onComplete))
    const formData = post.mock.calls[0][1]
    expect(formData.get('section')).toBe('Aggregate Data')
    expect(formData.get('ssp')).toBe('false')
    expect([...formData.keys()]).not.toEqual(
      expect.arrayContaining(['uploadScope', 'sectionId', 'program'])
    )
    expect(store.getState().reports.submittedFiles[0]).toMatchObject({
      id: 42,
      uuid: file.uuid,
      sectionId: file.sectionId,
      program: file.program,
    })
    expect(onComplete).toHaveBeenCalledWith([42], [response.data])
    expect(payload.logger.alert).toHaveBeenCalledTimes(1)
  })

  it('audits successful writes even when another scoped upload fails', async () => {
    const store = createReportsStore()
    const scope = store.dispatch(
      configureUploadSections(
        uploadConfiguration({
          sectionNames: ['Aggregate Data', 'Active Case Data'],
        })
      )
    )
    const first = stageScopedFile(store, scope)
    const second = stageScopedFile(store, scope, 'file-b', scope.sections[1])
    const payload = {
      ...payloadFor(scope, first),
      uploadedFiles: [first, second],
    }
    post
      .mockResolvedValueOnce(responseFor(first))
      .mockRejectedValueOnce(new Error('offline'))
    const onComplete = jest.fn()
    await store.dispatch(submit(payload, onComplete))
    expect(payload.logger.alert).toHaveBeenCalledWith(expect.any(String), {
      files: [42],
      activity: 'upload',
    })
    expect(payload.setUploadAlertState).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'error' })
    )
    expect(onComplete).not.toHaveBeenCalled()
  })
})
