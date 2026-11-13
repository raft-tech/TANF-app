import React from 'react'
import { render, fireEvent, act, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from '../../configureStore'
import FileUpload from './FileUpload'
import * as reportsActions from '../../actions/reports'
import * as utils from './utils'
import fileTypeChecker from 'file-type-checker'
import {
  createReportsStore,
  uploadConfiguration,
  deferred,
} from '../../test-utils/reportScopes'
import createFileInputErrorState from '../../utils/createFileInputErrorState'

// Mock dependencies
jest.mock('file-type-checker')
jest.mock('../../utils/createFileInputErrorState')
jest.mock('./utils', () => ({
  handlePreview: jest.fn(),
  getTargetClassName: jest.fn((name) => `.target-${name}`),
  tryGetUTF8EncodedFile: jest.fn(),
  validateHeader: jest.fn(),
  checkPreviewDependencies: jest.fn(),
  removeOldPreviews: jest.fn(),
}))

jest.mock('@uswds/uswds/src/js/components', () => ({
  fileInput: {
    init: jest.fn(),
  },
}))

const initialState = {
  reports: {
    submittedFiles: [
      {
        section: 'Active Case Data',
        fileName: null,
        error: null,
        uuid: null,
        name: null,
      },
    ],
  },
}

const mockStore = (initial = initialState) => configureStore(initial)

const makeTestFile = (name, contents = 'test content', type = 'text/plain') =>
  new File([contents], name, { type })

describe('FileUpload', () => {
  let mockSetUploadAlertState
  let mockDispatch

  beforeEach(() => {
    mockSetUploadAlertState = jest.fn()
    jest.clearAllMocks()

    // Mock FileReader
    global.FileReader = jest.fn(() => ({
      readAsArrayBuffer: jest.fn(function () {
        this.onload()
      }),
      result: new ArrayBuffer(8),
      onerror: jest.fn(),
      abort: jest.fn(),
    }))

    // Default mock implementations
    fileTypeChecker.validateFileType.mockReturnValue(false)
    utils.handlePreview.mockReturnValue(true)
    utils.checkPreviewDependencies.mockReturnValue({
      rendered: true,
      dropTarget: document.createElement('div'),
      instructions: document.createElement('div'),
    })
    utils.tryGetUTF8EncodedFile.mockResolvedValue({
      encodedFile: makeTestFile('test.txt'),
      header: 'HEADER20241A06   TAN1ED',
    })
    utils.validateHeader.mockResolvedValue({
      isValid: true,
      calendarFiscalResult: { isValid: true },
      programTypeResult: { isValid: true },
    })
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  const renderComponent = (
    storeState = initialState,
    props = {
      section: 'Active Case Data',
      year: '2024',
      quarter: 'Q1',
      fileType: 'tanf',
      label: 'Active Case Data',
      setUploadAlertState: mockSetUploadAlertState,
    }
  ) => {
    const store = mockStore(storeState)
    mockDispatch = jest.spyOn(store, 'dispatch')

    return {
      ...render(
        <Provider store={store}>
          <FileUpload {...props} />
        </Provider>
      ),
      store,
    }
  }

  describe('Scoped validation', () => {
    const setup = () => {
      const store = createReportsStore()
      const scope = store.dispatch(
        reportsActions.configureUploadSections(uploadConfiguration())
      )
      const props = {
        section: 'Aggregate Data',
        label: 'Section 3',
        year: '2024',
        quarter: 'Q1',
        fileType: 'tanf',
        uploadScope: scope,
        sectionDescriptor: scope.sections[0],
        setUploadAlertState: mockSetUploadAlertState,
      }
      const view = (overrides = {}) => (
        <Provider store={store}>
          <FileUpload {...props} {...overrides} />
        </Provider>
      )
      return { store, scope, view, ...render(view()) }
    }

    beforeEach(() => {
      utils.tryGetUTF8EncodedFile.mockImplementation(async (result, file) => ({
        encodedFile: file,
        header: 'HEADER',
      }))
    })

    it.each(['selection', 'stt', 'assignment', 'replacement', 'unmount'])(
      'ignores an old FileReader extension error after %s',
      async (transition) => {
        const readers = []
        global.FileReader.mockImplementation(() => {
          const reader = {
            readAsArrayBuffer: jest.fn(),
            result: new ArrayBuffer(8),
          }
          readers.push(reader)
          return reader
        })
        const hook = setup()
        const input = hook.container.querySelector('input')
        fireEvent.change(input, {
          target: { files: [makeTestFile('old.pdf')] },
        })
        if (['selection', 'stt', 'assignment'].includes(transition)) {
          let scope
          act(() => {
            scope = hook.store.dispatch(
              reportsActions.configureUploadSections(
                uploadConfiguration({
                  programSlug: transition === 'selection' ? 'ssp' : 'tanf',
                  sttId: transition === 'stt' ? 2 : 1,
                  ...(transition === 'assignment' && { sectionNames: [] }),
                })
              )
            )
          })
          hook.rerender(
            hook.view({
              fileType: transition === 'selection' ? 'ssp-moe' : 'tanf',
              uploadScope: scope,
              sectionDescriptor: scope.sections[0],
            })
          )
        } else if (transition === 'replacement') {
          fireEvent.change(input, {
            target: { files: [makeTestFile('new.txt')] },
          })
          await act(async () => {
            readers[1].onload()
          })
        } else hook.unmount()
        const before = hook.store.getState().reports
        mockSetUploadAlertState.mockClear()
        await act(async () => {
          readers[0].onload()
        })
        expect(hook.store.getState().reports).toBe(before)
        expect(createFileInputErrorState).not.toHaveBeenCalled()
        expect(mockSetUploadAlertState).not.toHaveBeenCalled()
      }
    )

    it('does not replace or remove the USWDS preview before its reader finishes', async () => {
      const readers = []
      global.FileReader.mockImplementation(() => {
        const reader = {
          readAsArrayBuffer: jest.fn(),
          result: new ArrayBuffer(8),
        }
        readers.push(reader)
        return reader
      })
      const hook = setup()
      utils.handlePreview.mockClear()
      utils.removeOldPreviews.mockClear()
      fireEvent.change(hook.container.querySelector('input'), {
        target: { files: [makeTestFile('pending.txt')] },
      })
      expect(utils.handlePreview).not.toHaveBeenCalled()
      expect(utils.removeOldPreviews).not.toHaveBeenCalled()
      await act(async () => readers[0].onload())
      expect(utils.handlePreview).toHaveBeenCalledTimes(1)
    })

    it('retains and revalidates a staged file across fiscal corrections without accepting the old validation', async () => {
      const oldValidation = deferred()
      utils.validateHeader.mockReturnValueOnce(oldValidation.promise)
      const hook = setup()
      const file = makeTestFile('retained.txt')
      fireEvent.change(hook.container.querySelector('input'), {
        target: { files: [file] },
      })
      await waitFor(() => expect(utils.validateHeader).toHaveBeenCalledTimes(1))
      hook.rerender(hook.view({ quarter: 'Q2' }))
      await waitFor(() =>
        expect(
          hook.store.getState().reports.submittedFiles[0].validatedQuarter
        ).toBe('Q2')
      )
      const current = hook.store.getState().reports
      await act(async () => {
        oldValidation.resolve({
          isValid: false,
          programTypeResult: { isValid: false, progType: 'SSP' },
        })
      })
      expect(hook.store.getState().reports).toBe(current)
      expect(current.uploadScope).toBe(hook.scope)
      expect(current.submittedFiles[0].file).toBe(file)
      expect(current.submittedFiles[0].error).toBeNull()
    })
  })

  describe('Rendering', () => {
    it('does not render error message when no error', () => {
      const { queryByRole } = renderComponent()

      expect(queryByRole('alert')).not.toBeInTheDocument()
    })

    it('renders error message when error exists', () => {
      const stateWithError = {
        reports: {
          submittedFiles: [
            {
              section: 'Active Case Data',
              fileName: null,
              error: { message: 'Invalid file type' },
              uuid: null,
              name: null,
            },
          ],
        },
      }

      const { getByRole } = renderComponent(stateWithError)

      const alert = getByRole('alert')
      expect(alert).toHaveTextContent('Invalid file type')
    })

    it('renders error message with link when provided', () => {
      const stateWithError = {
        reports: {
          submittedFiles: [
            {
              section: 'Active Case Data',
              fileName: null,
              error: {
                message: 'Invalid file',
                link: (
                  <a className="usa-link" href="/help">
                    Need help?
                  </a>
                ),
              },
              uuid: null,
              name: null,
            },
          ],
        },
      }

      const { getByRole, getByText } = renderComponent(stateWithError)

      expect(getByRole('alert')).toBeInTheDocument()
      expect(getByText('Need help?')).toBeInTheDocument()
    })

    it('initializes USWDS file input on mount', () => {
      const { fileInput } = require('@uswds/uswds/src/js/components')
      renderComponent()

      expect(fileInput.init).toHaveBeenCalled()
    })
  })

  describe('File Selection', () => {
    it('clears alert state when file is selected', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockSetUploadAlertState).toHaveBeenCalledWith({
          active: false,
          type: null,
          message: null,
        })
      })
    })
  })

  describe('File Validation - Extension', () => {
    it('accepts .txt files', async () => {
      const { container, store } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // The upload action is a thunk, so we check if dispatch was called with a function
        const uploadCalls = mockDispatch.mock.calls.filter(
          (call) => typeof call[0] === 'function'
        )
        expect(uploadCalls.length).toBeGreaterThan(0)
        expect(store.getState().reports.submittedFiles[0]).toEqual(
          expect.objectContaining({
            validatedYear: '2024',
            validatedQuarter: 'Q1',
          })
        )
      })
    })

    it('accepts .ms## files', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.ms01')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // The upload action is a thunk, so we check if dispatch was called with a function
        const uploadCalls = mockDispatch.mock.calls.filter(
          (call) => typeof call[0] === 'function'
        )
        expect(uploadCalls.length).toBeGreaterThan(0)
      })
    })

    it('accepts .ts## files', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.ts06')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // The upload action is a thunk, so we check if dispatch was called with a function
        const uploadCalls = mockDispatch.mock.calls.filter(
          (call) => typeof call[0] === 'function'
        )
        expect(uploadCalls.length).toBeGreaterThan(0)
      })
    })

    it('accepts .ts### files', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.ts123')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // The upload action is a thunk, so we check if dispatch was called with a function
        const uploadCalls = mockDispatch.mock.calls.filter(
          (call) => typeof call[0] === 'function'
        )
        expect(uploadCalls.length).toBeGreaterThan(0)
      })
    })

    it('rejects files with invalid extensions', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.pdf')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalledWith(
          expect.objectContaining({
            type: reportsActions.FILE_EXT_ERROR,
          })
        )
      })
    })

    it('rejects image files (png)', async () => {
      // Reset the mock and set it to return true for this specific test
      fileTypeChecker.validateFileType.mockReset()
      fileTypeChecker.validateFileType.mockReturnValue(true)

      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt') // Has valid extension but is actually an image

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        const errorCalls = mockDispatch.mock.calls.filter(
          (call) => call[0].type === reportsActions.SET_FILE_ERROR
        )
        expect(errorCalls.length).toBeGreaterThan(0)
        // Verify the error was dispatched (message is INVALID_FILE_ERROR constant)
        expect(errorCalls[0][0].payload.section).toBe('Active Case Data')
      })

      // Reset back to false for other tests
      fileTypeChecker.validateFileType.mockReturnValue(false)
    })
  })

  describe('File Validation - Header', () => {
    it('uploads file when header validation passes', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: true,
        calendarFiscalResult: { isValid: true },
        programTypeResult: { isValid: true },
      })

      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // The upload action is a thunk, so we check if dispatch was called with a function
        const uploadCalls = mockDispatch.mock.calls.filter(
          (call) => typeof call[0] === 'function'
        )
        expect(uploadCalls.length).toBeGreaterThan(0)
      })
    })

    it('shows program type error when program type validation fails', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: false,
        calendarFiscalResult: { isValid: true },
        programTypeResult: { isValid: false, progType: 'SSP' },
      })

      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalledWith(
          expect.objectContaining({
            type: reportsActions.SET_FILE_ERROR,
            payload: expect.objectContaining({
              error: expect.objectContaining({
                message: expect.stringContaining(
                  'File may correspond to SSP instead of TAN'
                ),
              }),
            }),
          })
        )
      })
    })

    it('shows null program type error when program type cannot be determined', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: false,
        calendarFiscalResult: { isValid: true },
        programTypeResult: { isValid: false, progType: null },
      })

      const { container, getByText } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // Check that the error message text is displayed
        expect(
          getByText(/Could not determine the file type/i)
        ).toBeInTheDocument()

        // Check that the help link is present
        const helpLink = container.querySelector(
          'a[aria-label="Need help? Read header record guidance"]'
        )
        expect(helpLink).toBeInTheDocument()
        expect(helpLink).toHaveAttribute(
          'href',
          'https://acf.gov/sites/default/files/documents/ofa/transmission_file_header_trailer_record.pdf'
        )

        // Verify the action was dispatched with the correct type
        expect(mockDispatch).toHaveBeenCalledWith(
          expect.objectContaining({
            type: reportsActions.SET_FILE_ERROR,
            payload: expect.objectContaining({
              section: 'Active Case Data',
            }),
          })
        )
      })
    })

    it('shows calendar/fiscal year error when validation fails', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: false,
        calendarFiscalResult: {
          isValid: false,
          fileFiscalYear: '2023',
          fileFiscalQuarter: '1',
        },
        programTypeResult: { isValid: true },
      })

      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalledWith(
          expect.objectContaining({
            type: reportsActions.SET_FILE_ERROR,
            payload: expect.objectContaining({
              error: expect.objectContaining({
                message: expect.stringContaining('Oct 1 - Dec 31'),
              }),
            }),
          })
        )
      })
    })

    it('revalidates and clears a fiscal period error when the quarter changes', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: false,
        calendarFiscalResult: {
          isValid: false,
          fileFiscalYear: '2024',
          fileFiscalQuarter: '2',
        },
        programTypeResult: { isValid: true },
      })

      const props = {
        section: 'Active Case Data',
        year: '2024',
        quarter: 'Q1',
        fileType: 'tanf',
        label: 'Active Case Data',
        setUploadAlertState: mockSetUploadAlertState,
      }
      const { container, getByRole, queryByRole, rerender, store } =
        renderComponent(initialState, props)
      const input = container.querySelector('input[type="file"]')

      fireEvent.change(input, {
        target: { files: [makeTestFile('test.txt')] },
      })

      await waitFor(() => {
        expect(getByRole('alert')).toHaveTextContent('Fiscal Year 2024')
      })

      const dropTarget = input.parentNode
      dropTarget.classList.add('has-invalid-file')
      const removeErrorStateSpy = jest.spyOn(dropTarget.classList, 'remove')

      utils.validateHeader.mockResolvedValue({
        isValid: true,
        calendarFiscalResult: { isValid: true },
        programTypeResult: { isValid: true },
      })

      rerender(
        <Provider store={store}>
          <FileUpload {...props} quarter="Q2" />
        </Provider>
      )

      await waitFor(() => {
        expect(utils.validateHeader).toHaveBeenLastCalledWith(
          'HEADER20241A06   TAN1ED',
          '2024',
          'Q2',
          'TAN'
        )
        expect(queryByRole('alert')).not.toBeInTheDocument()
        expect(removeErrorStateSpy).toHaveBeenCalledWith('has-invalid-file')
        expect(dropTarget).not.toHaveClass('has-invalid-file')
      })
    })

    it('handles default case for unknown quarter', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: false,
        calendarFiscalResult: {
          isValid: false,
          fileFiscalYear: '2023',
          fileFiscalQuarter: '5', // Invalid quarter
        },
        programTypeResult: { isValid: true },
      })

      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalledWith(
          expect.objectContaining({
            type: reportsActions.SET_FILE_ERROR,
            payload: expect.objectContaining({
              error: expect.objectContaining({
                message: expect.stringContaining('Fiscal Year 2023'),
              }),
            }),
          })
        )
      })
    })
  })
})
