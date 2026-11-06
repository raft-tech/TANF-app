import { v4 as uuidv4 } from 'uuid'
import reducer, { getUpdatedFiles } from './reports'
import {
  CLEAR_ERROR,
  SET_FILE,
  CLEAR_FILE,
  FILE_EXT_ERROR,
  SET_FILE_ERROR,
  SET_SELECTED_STT,
  SET_FILE_LIST,
  SET_FILE_SUBMITTED,
  configureUploadSections,
  clearFileList,
  reinitializeSubmittedFiles,
  FETCH_FILE_LIST,
  FETCH_FILE_LIST_ERROR,
  INVALIDATE_FILE_LIST,
  SET_TANF_SUBMISSION_STATUS,
  BEGIN_FILE_VALIDATION,
} from '../actions/reports'
import {
  createReportsStore,
  uploadConfiguration,
  stageScopedFile,
} from '../test-utils/reportScopes'
import { getUploadAssignmentKey } from '../utils/reportScopes'
import { programIntegrityAuditLabels } from '../components/Reports/utils'

const initialState = {
  files: [],
  submittedFiles: [
    {
      section: 'Active Case Data',
      fileName: null,
      fileType: null,
      error: null,
      uuid: null,
    },
    {
      section: 'Closed Case Data',
      fileName: null,
      fileType: null,
      error: null,
      uuid: null,
    },
    {
      section: 'Aggregate Data',
      fileName: null,
      fileType: null,
      error: null,
      uuid: null,
    },
    {
      section: 'Stratum Data',
      fileName: null,
      fileType: null,
      error: null,
      uuid: null,
    },
  ],
  year: '',
  stt: '',
  quarter: '',
  fileType: '',
  loading: false,
}

describe('reducers/reports', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual(initialState)
  })

  it('should handle SET_FILE_LIST', () => {
    const uuid = uuidv4()
    expect(
      reducer(undefined, {
        type: SET_FILE_LIST,
        payload: {
          data: [
            {
              id: 1,
              extension: 'txt',
              original_filename: 'test.txt',
              section: 'Active Case Data',
              quarter: 'Q1',
              slug: uuid,
              year: 2021,
              submitted_by: 'test@test.com',
              program_type: 'TAN',
              s3_version_id: 'v123',
              created_at: '2021-01-01T00:00:00Z',
              has_error: false,
              summary: null,
              latest_reparse_file_meta: null,
            },
          ],
        },
      })
    ).toEqual({
      submittedFiles: initialState.submittedFiles,
      files: [
        {
          fileName: 'test.txt',
          fileType: 'txt',
          id: 1,
          section: 'Active Case Data',
          quarter: 'Q1',
          program_type: 'TAN',
          year: 2021,
          submittedBy: 'test@test.com',
          uuid,
          s3_version_id: 'v123',
          createdAt: '2021-01-01T00:00:00Z',
          hasError: false,
          summary: null,
          latest_reparse_file_meta: null,
        },
      ],
      quarter: '',
      stt: '',
      year: '',
      fileType: '',
      loading: false,
    })
  })

  it('should handle SET_FILE', () => {
    const uuid = uuidv4()
    expect(
      reducer(undefined, {
        type: SET_FILE,
        payload: {
          file: {},
          fileName: 'Test.txt',
          fileType: 'text/plain',
          section: 'Stratum Data',
          uuid,
        },
      })
    ).toEqual({
      files: initialState.files,
      submittedFiles: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          file: {},
          fileName: 'Test.txt',
          fileType: 'text/plain',
          id: null,
          error: null,
          uuid,
        },
      ],
      stt: '',
      year: '',
      quarter: '',
      fileType: '',
      loading: false,
    })
  })

  it('should handle SET_FILE_SUBMITTED', () => {
    const uuid = uuidv4()
    expect(
      reducer(undefined, {
        type: SET_FILE_SUBMITTED,
        payload: {
          submittedFile: {
            extension: 'txt',
            id: 1,
            original_filename: 'Test.txt',
            quarter: 'Q1',
            section: 'Stratum Data',
            slug: uuid,
            year: 2021,
            s3_version_id: 'v456',
            created_at: '2021-02-01T00:00:00Z',
            submitted_by: 'user@test.com',
            has_error: false,
            summary: null,
            latest_reparse_file_meta: null,
          },
        },
      })
    ).toEqual({
      files: initialState.files,
      submittedFiles: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          fileName: 'Test.txt',
          fileType: 'txt',
          id: 1,
          quarter: 'Q1',
          year: 2021,
          uuid,
          s3_version_id: 'v456',
          createdAt: '2021-02-01T00:00:00Z',
          submittedBy: 'user@test.com',
          hasError: false,
          summary: null,
          latest_reparse_file_meta: null,
        },
      ],
      stt: '',
      year: '',
      quarter: '',
      fileType: '',
      loading: false,
    })
  })

  it('should handle CLEAR_FILE', () => {
    expect(
      reducer(undefined, {
        type: CLEAR_FILE,
        payload: {
          section: 'Stratum Data',
        },
      })
    ).toEqual({
      files: initialState.files,
      submittedFiles: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          file: null,
          fileName: undefined,
          fileType: null,
          id: null,
          error: null,
          uuid: null,
        },
      ],
      stt: '',
      year: '',
      quarter: '',
      fileType: '',
      loading: false,
    })
  })

  it('should handle FILE_EXT_ERROR', () => {
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })

    expect(
      reducer(undefined, {
        type: FILE_EXT_ERROR,
        payload: {
          error: { message: 'Test invalid ext.' },
          file,
          fileName: file.name,
          fileType: file.type,
          section: 'Active Case Data',
        },
      })
    ).toEqual({
      ...initialState,
      submittedFiles: [
        {
          id: null,
          file,
          section: 'Active Case Data',
          fileName: 'test.pdf',
          error: { message: 'Test invalid ext.' },
          uuid: null,
          fileType: 'application/pdf',
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          error: null,
          uuid: null,
          fileType: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          error: null,
          uuid: null,
          fileType: null,
        },
        {
          section: 'Stratum Data',
          fileName: null,
          error: null,
          uuid: null,
          fileType: null,
        },
      ],
    })
  })

  it('should handle SET_FILE_ERROR', () => {
    const fakeError = new Error({ message: 'something went wrong' })
    expect(
      reducer(undefined, {
        type: SET_FILE_ERROR,
        payload: {
          error: fakeError,
          section: 'Stratum Data',
        },
      })
    ).toEqual({
      files: initialState.files,
      submittedFiles: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          file: null,
          fileName: undefined,
          fileType: null,
          id: null,
          error: fakeError,
          uuid: null,
        },
      ],
      stt: '',
      year: '',
      quarter: '',
      fileType: '',
      loading: false,
    })
  })

  it('should handle CLEAR_ERROR', () => {
    const fakeError = new Error({ message: 'something went wrong' })
    expect(
      reducer(
        {
          submittedFiles: [
            {
              section: 'Active Case Data',
              fileName: null,
              fileType: null,
              error: null,
              uuid: null,
            },
            {
              section: 'Closed Case Data',
              fileName: null,
              fileType: null,
              error: null,
              uuid: null,
            },
            {
              section: 'Aggregate Data',
              fileName: null,
              fileType: null,
              error: null,
              uuid: null,
            },
            {
              section: 'Stratum Data',
              fileName: null,
              fileType: null,
              error: fakeError,
              uuid: null,
            },
          ],
          stt: '',
          quarter: '',
          year: '2020',
          loading: false,
        },
        {
          type: CLEAR_ERROR,
          payload: {
            section: 'Stratum Data',
          },
        }
      )
    ).toEqual({
      submittedFiles: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          file: null,
          fileName: null,
          fileType: null,
          id: null,
          error: null,
          uuid: null,
        },
      ],
      stt: '',
      quarter: '',
      year: '2020',
      loading: false,
    })
  })

  it('should handle "SET_SELECTED_STT"', () => {
    expect(
      reducer(undefined, {
        type: SET_SELECTED_STT,
        payload: {
          stt: 'florida',
        },
      })
    ).toEqual({
      files: initialState.files,
      submittedFiles: initialState.submittedFiles,
      year: '',
      stt: 'florida',
      quarter: '',
      fileType: '',
      loading: false,
    })
  })

  it('should be able to update files with a new value and return those files', () => {
    const uuid = uuidv4()

    const updatedFiles = getUpdatedFiles({
      state: initialState,
      id: 10,
      file: {},
      fileName: 'Test.txt',
      section: 'Active Case Data',
      fileType: 'text/plain',
      uuid,
    })

    expect(updatedFiles).toStrictEqual([
      {
        file: {},
        section: 'Active Case Data',
        fileName: 'Test.txt',
        fileType: 'text/plain',
        error: null,
        id: 10,
        uuid,
      },
      {
        section: 'Closed Case Data',
        fileName: null,
        fileType: null,
        error: null,
        uuid: null,
      },
      {
        section: 'Aggregate Data',
        fileName: null,
        fileType: null,
        error: null,
        uuid: null,
      },
      {
        section: 'Stratum Data',
        fileName: null,
        fileType: null,
        error: null,
        uuid: null,
      },
    ])
  })
})

describe('configured report state', () => {
  it('starts replacement validation without retaining a submitted ID or fiscal validation', () => {
    const store = createReportsStore()
    const scope = store.dispatch(configureUploadSections(uploadConfiguration()))
    const sourceFile = stageScopedFile(store, scope)
    store.dispatch({
      type: SET_FILE_SUBMITTED,
      payload: {
        uploadScope: scope,
        sourceFile,
        submittedFile: {
          id: 42,
          slug: sourceFile.uuid,
          section: sourceFile.section,
          program_type: 'TAN',
        },
      },
    })
    store.dispatch({
      type: BEGIN_FILE_VALIDATION,
      payload: {
        uploadScope: scope,
        section: sourceFile.section,
        sectionId: sourceFile.sectionId,
        program: sourceFile.program,
        uuid: 'replacement',
      },
    })
    const replacement = store.getState().reports.submittedFiles[0]
    expect(replacement.id).toBeNull()
    expect(replacement.isValidating).toBe(true)
    expect(replacement.validatedYear).toBeUndefined()
    expect(replacement.validatedQuarter).toBeUndefined()
  })

  it('initializes exactly sparse descriptors and keeps empty assignments empty across resets', () => {
    const store = createReportsStore()
    const configuration = uploadConfiguration({
      sectionNames: ['Aggregate Data', 'Active Case Data'],
    })
    const scope = store.dispatch(configureUploadSections(configuration))
    expect(
      store.getState().reports.submittedFiles.map((slot) => slot.section)
    ).toEqual(['Aggregate Data', 'Active Case Data'])
    stageScopedFile(store, scope)
    store.dispatch(clearFileList({ fileType: 'tanf', uploadScope: scope }))
    expect(store.getState().reports.uploadScope.generation).not.toBe(
      scope.generation
    )
    expect(store.getState().reports.submittedFiles).toHaveLength(2)
    expect(
      store.getState().reports.submittedFiles.every((file) => !file.uuid)
    ).toBe(true)

    store.dispatch(
      configureUploadSections(uploadConfiguration({ sectionNames: [] }))
    )
    store.dispatch(clearFileList({ fileType: 'tanf' }))
    store.dispatch(reinitializeSubmittedFiles('tanf'))
    store.dispatch({
      type: SET_FILE_ERROR,
      payload: { section: 'Active Case Data' },
    })
    store.dispatch({
      type: CLEAR_ERROR,
      payload: { section: 'Active Case Data' },
    })
    expect(store.getState().reports.submittedFiles).toEqual([])
  })

  it('normalizes assignment identity without fiscal periods, status, or API ordering', () => {
    const configuration = uploadConfiguration({
      sectionNames: ['Aggregate Data', 'Active Case Data'],
    })
    expect(getUploadAssignmentKey(configuration)).toBe(
      getUploadAssignmentKey({
        ...configuration,
        year: '2025',
        quarter: 'Q2',
        status: 'NEVER',
        sections: [...configuration.sections].reverse(),
      })
    )
    const store = createReportsStore()
    const scope = store.dispatch(configureUploadSections(configuration))
    stageScopedFile(store, scope)
    expect(
      store.dispatch(
        configureUploadSections({
          ...configuration,
          sections: [...configuration.sections].reverse(),
        })
      )
    ).toBe(scope)
    expect(store.getState().reports.submittedFiles[0].uuid).toBe('file-a')
  })

  it.each(['ssp', 'tanf'])(
    'rejects stale updates, unscoped writes, and wrong section/program identity for %s',
    (programSlug) => {
      const store = createReportsStore()
      const oldScope = store.dispatch(
        configureUploadSections(uploadConfiguration())
      )
      const oldFile = stageScopedFile(store, oldScope)
      const scope = store.dispatch(
        configureUploadSections(uploadConfiguration({ sttId: 2, programSlug }))
      )
      const file = stageScopedFile(store, scope, 'file-b')
      const before = store.getState().reports
      for (const type of [
        SET_FILE,
        SET_FILE_ERROR,
        FILE_EXT_ERROR,
        CLEAR_ERROR,
        CLEAR_FILE,
      ]) {
        store.dispatch({ type, payload: { ...oldFile, uploadScope: oldScope } })
        store.dispatch({
          type,
          payload: { ...file, uploadScope: scope, sectionId: -1 },
        })
        store.dispatch({
          type,
          payload: {
            ...file,
            uploadScope: scope,
            program: { id: -1, slug: 'tanf' },
          },
        })
        store.dispatch({ type, payload: { section: file.section } })
      }
      store.dispatch(clearFileList({ fileType: 'tanf', uploadScope: oldScope }))
      store.dispatch(
        reinitializeSubmittedFiles('tanf', { uploadScope: oldScope })
      )
      expect(store.getState().reports).toBe(before)
      expect(Object.hasOwn(before.submittedFiles, '-1')).toBe(false)
    }
  )

  it('never replaces a newer UUID with a same-name submitted file', () => {
    const store = createReportsStore()
    const scope = store.dispatch(configureUploadSections(uploadConfiguration()))
    const sourceFile = stageScopedFile(store, scope)
    const replacement = stageScopedFile(store, scope, 'replacement')
    store.dispatch({
      type: SET_FILE_SUBMITTED,
      payload: {
        uploadScope: scope,
        sourceFile,
        submittedFile: {
          id: 99,
          slug: sourceFile.uuid,
          section: sourceFile.section,
          program_type: 'TAN',
        },
      },
    })
    expect(store.getState().reports.submittedFiles[0]).toBe(replacement)
  })

  it('clears scoped errors without losing the staged file or mutating its array', () => {
    const store = createReportsStore()
    const scope = store.dispatch(configureUploadSections(uploadConfiguration()))
    const file = stageScopedFile(store, scope)
    store.dispatch({
      type: SET_FILE_ERROR,
      payload: { ...file, uploadScope: scope, error: { message: 'invalid' } },
    })
    const before = Object.freeze(store.getState().reports.submittedFiles)
    store.dispatch({
      type: CLEAR_ERROR,
      payload: { ...file, uploadScope: scope },
    })
    expect(before[0].error).toEqual({ message: 'invalid' })
    expect(store.getState().reports.submittedFiles[0]).toEqual({
      ...before[0],
      error: null,
    })
  })

  it('keeps PIA defaults when the configured path is explicitly left', () => {
    const store = createReportsStore()
    const oldScope = store.dispatch(
      configureUploadSections(uploadConfiguration({ sectionNames: [] }))
    )
    store.dispatch(configureUploadSections(null))
    store.dispatch(reinitializeSubmittedFiles('program-integrity-audit'))
    expect(
      store.getState().reports.submittedFiles.map((file) => file.section)
    ).toEqual(programIntegrityAuditLabels)
    store.dispatch(clearFileList({ fileType: 'program-integrity-audit' }))
    expect(
      store.getState().reports.submittedFiles.map((file) => file.section)
    ).toEqual(programIntegrityAuditLabels)
    const before = store.getState().reports
    store.dispatch(
      reinitializeSubmittedFiles('tanf', { uploadScope: oldScope })
    )
    expect(store.getState().reports).toBe(before)
  })

  it('does not let an old unmount invalidate a newer upload assignment', () => {
    const store = createReportsStore()
    const oldScope = store.dispatch(
      configureUploadSections(uploadConfiguration())
    )
    const current = store.dispatch(
      configureUploadSections(uploadConfiguration({ sttId: 2 }))
    )
    store.dispatch(configureUploadSections(null, oldScope))
    expect(store.getState().reports.uploadScope).toBe(current)
    store.dispatch(configureUploadSections(null, current))
    expect(store.getState().reports.uploadScope).toBeNull()
  })

  it('rejects stale history results/errors/status callbacks and invalidates cleared queries', () => {
    const old = { key: 'query-a', requestId: '1' }
    const current = { key: 'query-b', requestId: '2' }
    let state = reducer(undefined, {
      type: FETCH_FILE_LIST,
      payload: { historyScope: old },
    })
    state = reducer(state, {
      type: FETCH_FILE_LIST,
      payload: { historyScope: current },
    })
    for (const type of [
      SET_FILE_LIST,
      FETCH_FILE_LIST_ERROR,
      SET_TANF_SUBMISSION_STATUS,
    ]) {
      expect(
        reducer(state, { type, payload: { historyScope: old, data: [] } })
      ).toBe(state)
      expect(reducer(state, { type, payload: { data: [] } })).toBe(state)
    }
    const cleared = reducer(state, {
      type: INVALIDATE_FILE_LIST,
      payload: { historyScope: current },
    })
    expect(cleared.files).toEqual([])
    expect(cleared.loading).toBe(false)
    expect(
      reducer(cleared, {
        type: SET_FILE_LIST,
        payload: { historyScope: current, data: [{ id: 1 }] },
      })
    ).toBe(cleared)
  })
})
