import React, { useRef, useEffect } from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector, useStore } from 'react-redux'
import { v4 as uuidv4 } from 'uuid'
import fileTypeChecker from 'file-type-checker'
import { fileInput } from '@uswds/uswds/src/js/components'

import {
  clearError,
  clearFile,
  SET_FILE_ERROR,
  FILE_EXT_ERROR,
  upload,
  BEGIN_FILE_VALIDATION,
} from '../../actions/reports'
import {
  isUploadCurrent,
  sameUploadScope,
  sameSection,
} from '../../utils/reportScopes'
import createFileInputErrorState from '../../utils/createFileInputErrorState'
import {
  handlePreview,
  getTargetClassName,
  tryGetUTF8EncodedFile,
  validateHeader,
  checkPreviewDependencies,
  removeOldPreviews,
} from './utils'

const INVALID_FILE_ERROR =
  'We can’t process that file format. Please provide a plain text file.'

const INVALID_EXT_ERROR = (
  <>
    Invalid extension. Accepted file types are: .txt, .ms##, .ts##, or
    .ts###.&nbsp;
    <a
      className="usa-link"
      href="https://tdp-project-updates.app.cloud.gov/knowledge-center/file-extension-guide.html"
      target="_blank"
      aria-label="Need help? Read file extension guidance"
      rel="noreferrer"
    >
      Need help?
    </a>
  </>
)

const NULL_PROGRAM_TYPE_ERROR = (
  <>
    Could not determine the file type. Please verify the file has a valid
    header.&nbsp;
    <a
      className="usa-link"
      href="https://acf.gov/sites/default/files/documents/ofa/transmission_file_header_trailer_record.pdf"
      target="_blank"
      aria-label="Need help? Read header record guidance"
      rel="noreferrer"
    >
      Need help?
    </a>
  </>
)

const load = (
  file,
  section,
  input,
  dropTarget,
  dispatch,
  isCurrent = () => true
) => {
  const filereader = new FileReader()
  const types = ['png', 'gif', 'jpeg']

  return new Promise((resolve, reject) => {
    filereader.onerror = () => {
      filereader.abort()
      reject(new Error('Problem parsing input file.'))
    }

    filereader.onload = () => {
      if (!isCurrent()) {
        resolve({ stale: true })
        return
      }
      let error = false
      const basePayload = {
        file,
        fileName: file.name,
        fileType: file.type,
      }
      const re = /(\.txt|\.ms\d{2}|\.ts\d{2,3})$/i
      if (!re.exec(file.name)) {
        createFileInputErrorState(input, dropTarget, { preservePreview: true })

        dispatch({
          type: FILE_EXT_ERROR,
          payload: {
            error: { message: INVALID_EXT_ERROR },
            ...basePayload,
            section,
          },
        })
        error = true
      }

      const isImg = fileTypeChecker.validateFileType(filereader.result, types)

      if (!error && isImg) {
        createFileInputErrorState(input, dropTarget, { preservePreview: true })

        dispatch({
          type: SET_FILE_ERROR,
          payload: {
            error: { message: INVALID_FILE_ERROR },
            ...basePayload,
            section,
          },
        })
        error = true
      }

      resolve({ result: filereader.result, error: error })
    }
    filereader.readAsArrayBuffer(file)
  })
}

function FileUpload({
  section,
  year,
  quarter,
  fileType,
  label,
  setUploadAlertState,
  setProcessingAlertState,
  uploadScope,
  sectionDescriptor,
}) {
  // e.g. 'Aggregate Case Data' => 'aggregate-case-data'
  // The set of uploaded files in our Redux state
  const files = useSelector((state) => state.reports.submittedFiles)

  const dispatch = useDispatch()
  const store = useStore()
  const mountedRef = useRef(true)
  const validationTokenRef = useRef(null)
  const latestScopeRef = useRef(uploadScope)
  latestScopeRef.current = uploadScope

  const selectedFile = files?.find((file) =>
    uploadScope
      ? sameUploadScope(store.getState().reports.uploadScope, uploadScope) &&
        sectionDescriptor &&
        sameSection(file, sectionDescriptor)
      : file.section.includes(section)
  )

  const hasFile = Boolean(selectedFile?.uuid)
  const hasPreview = Boolean(selectedFile?.file)

  // Sanitize section name for use as CSS selector ID
  // Remove parentheses, hyphens, and other special characters
  const formattedSectionName = (selectedFile?.section || section)
    .toLowerCase()
    .replace(/[()]/g, '') // Remove parentheses
    .replace(/\s+/g, '_') // Replace spaces with underscores

  const targetClassName = getTargetClassName(formattedSectionName)

  const fileName = selectedFile?.fileName || 'report.txt'
  const hasUploadedFile = Boolean(fileName)

  const ariaDescription = hasUploadedFile
    ? `Selected File ${selectedFile?.fileName}. To change the selected file, click this button.`
    : `Drag file here or choose from folder.`

  useEffect(() => {
    // Reserving a UUID happens before USWDS finishes its own FileReader.
    // Do not replace/remove that in-flight preview during scoped validation.
    if (selectedFile?.isValidating) return
    let active = true
    let timer
    const trySettingPreview = () => {
      if (!active) return
      const previewState = handlePreview(fileName, targetClassName)
      if (!previewState) {
        timer = setTimeout(trySettingPreview, 100)
      }
    }
    if (hasPreview || hasFile) {
      trySettingPreview()
    } else {
      // When the file upload modal is cancelled we need to remove our hiding logic
      const deps = checkPreviewDependencies(targetClassName)
      if (deps.rendered) removeOldPreviews(deps.dropTarget, deps.instructions)
    }
    return () => {
      active = false
      clearTimeout(timer)
    }
  }, [
    hasPreview,
    hasFile,
    fileName,
    targetClassName,
    selectedFile?.isValidating,
  ])

  const inputRef = useRef(null)
  const previousFiscalPeriodRef = useRef(null)
  const validateAndUploadFileRef = useRef(null)

  const validateAndUploadFile = async (event, isRevalidation = false) => {
    if (
      uploadScope &&
      (!selectedFile ||
        !sameUploadScope(store.getState().reports.uploadScope, uploadScope))
    )
      return
    setUploadAlertState({
      active: false,
      type: null,
      message: null,
    })
    if (setProcessingAlertState) {
      setProcessingAlertState({
        active: false,
        type: null,
        message: null,
      })
    }

    const { name: section } = event.target
    const file = event.target.files[0]

    if (!file) return

    const basePayload = {
      file,
      fileName: file.name,
      fileType: file.type,
    }
    const identity = uploadScope
      ? {
          uploadScope,
          sectionId: sectionDescriptor.id,
          program: sectionDescriptor.program,
          uuid: uuidv4(),
        }
      : {}
    validationTokenRef.current = identity.uuid
    const isCurrent = () =>
      !uploadScope ||
      (mountedRef.current &&
        sameUploadScope(latestScopeRef.current, uploadScope) &&
        validationTokenRef.current === identity.uuid &&
        isUploadCurrent(store.getState().reports, uploadScope, [
          { ...identity, section },
        ]))
    const validationDispatch = (action) => {
      if (isCurrent())
        dispatch({ ...action, payload: { ...action.payload, ...identity } })
    }

    if (uploadScope) {
      dispatch({
        type: BEGIN_FILE_VALIDATION,
        payload: { ...basePayload, ...identity, section },
      })
    } else if (!isRevalidation) {
      // Clear existing errors and the current file if the user is replacing it.
      dispatch(clearError({ section }))
      dispatch(clearFile({ section }))
    }

    const input = inputRef.current
    const dropTarget = inputRef.current.parentNode

    const { result, error } = await load(
      file,
      section,
      input,
      dropTarget,
      validationDispatch,
      isCurrent
    ).catch((readError) => {
      if (!uploadScope) throw readError
      validationDispatch({
        type: SET_FILE_ERROR,
        payload: { ...basePayload, section, error: readError },
      })
      return { error: true }
    })
    if (!isCurrent()) return
    let hasValidationError = error

    const dispatchProgramTypeError = (
      programTypeResult,
      selectedProgramType,
      input,
      dropTarget,
      section,
      basePayload
    ) => {
      let formattedFileProgramType = programTypeResult.progType
      let formattedSelectedProgramType = selectedProgramType
      if (formattedFileProgramType === 'TAN') {
        formattedFileProgramType = 'TANF'
      }
      if (formattedSelectedProgramType === 'TAN') {
        formattedSelectedProgramType = 'TANF'
      }
      if (formattedSelectedProgramType === 'PRO') {
        formattedSelectedProgramType = 'TANF Program Integrity Audit'
      }

      const programTypeError = `File may correspond to ${formattedFileProgramType} instead of ${formattedSelectedProgramType}. Please verify the file type.`
      // Handle specific program type cases
      createFileInputErrorState(input, dropTarget, { preservePreview: true })
      hasValidationError = true
      validationDispatch({
        type: SET_FILE_ERROR,
        payload: {
          error: {
            message: formattedFileProgramType
              ? programTypeError
              : NULL_PROGRAM_TYPE_ERROR,
          },
          ...basePayload,
          section,
        },
      })
    }

    const dispatchCalendarFiscalError = (
      calendarFiscalResult,
      input,
      dropTarget,
      section,
      basePayload
    ) => {
      // Handle fiscal year and quarter mismatch
      let error_period
      var link = (
        <a
          className="usa-link"
          target="_blank"
          rel="noopener noreferrer"
          href="https://tdp-project-updates.app.cloud.gov/knowledge-center/uploading-data.html#reporting-period"
        >
          Need help?
        </a>
      )
      switch (calendarFiscalResult.fileFiscalQuarter) {
        case '1':
          error_period = 'Oct 1 - Dec 31, '
          break
        case '2':
          error_period = 'Jan 1 - Mar 31, '
          break
        case '3':
          error_period = 'Apr 1 - Jun 30, '
          break
        case '4':
          error_period = 'Jul 1 - Sep 30, '
          break
        default:
          error_period = ''
      }
      createFileInputErrorState(input, dropTarget, { preservePreview: true })
      hasValidationError = true
      validationDispatch({
        type: SET_FILE_ERROR,
        payload: {
          error: {
            message:
              `File contains data from ` +
              error_period +
              `which belongs to Fiscal Year ` +
              calendarFiscalResult.fileFiscalYear +
              `, Quarter ` +
              calendarFiscalResult.fileFiscalQuarter +
              `. Adjust your search parameters or upload a different file.`,
            link: link,
          },
          ...basePayload,
          section,
        },
      })
    }

    if (!error) {
      // Get the correctly encoded file
      const { encodedFile, header } = await tryGetUTF8EncodedFile(result, file)
      if (!isCurrent()) return
      const selectedProgramType = fileType.slice(0, 3).toUpperCase()
      const { isValid, calendarFiscalResult, programTypeResult } =
        await validateHeader(header, year, quarter, selectedProgramType)
      if (!isCurrent()) return
      if (isValid) {
        dropTarget.classList.remove('has-invalid-file')
        dispatch(
          upload({ file: encodedFile, section, year, quarter, ...identity })
        )
      } else if (!programTypeResult.isValid) {
        dispatchProgramTypeError(
          programTypeResult,
          selectedProgramType,
          input,
          dropTarget,
          section,
          {
            file: encodedFile,
            fileName: encodedFile.name,
            fileType: encodedFile.type,
          }
        )
      } else if (!calendarFiscalResult.isValid) {
        dispatchCalendarFiscalError(
          calendarFiscalResult,
          input,
          dropTarget,
          section,
          {
            file: encodedFile,
            fileName: encodedFile.name,
            fileType: encodedFile.type,
          }
        )
      }
    }
    if (inputRef.current && !hasValidationError) {
      inputRef.current.value = null
    }
  }

  validateAndUploadFileRef.current = validateAndUploadFile

  useEffect(() => {
    const previousFiscalPeriod = previousFiscalPeriodRef.current
    const fiscalPeriodChanged =
      previousFiscalPeriod &&
      (previousFiscalPeriod.year !== year ||
        previousFiscalPeriod.quarter !== quarter)

    previousFiscalPeriodRef.current = { year, quarter }

    if (
      (previousFiscalPeriod === null || fiscalPeriodChanged) &&
      selectedFile?.file
    ) {
      validateAndUploadFileRef.current(
        {
          target: { name: section, files: [selectedFile.file] },
        },
        true
      )
    }
  }, [year, quarter, section, selectedFile?.file])

  // Initialize USWDS file input component
  useEffect(() => {
    mountedRef.current = true
    if (inputRef.current) {
      fileInput.init(inputRef.current.parentNode)
    }
    return () => {
      mountedRef.current = false
    }
  }, [])

  return (
    <div
      className={`usa-form-group ${selectedFile?.error ? 'usa-form-group--error' : ''}`}
    >
      <label className="usa-label text-bold" htmlFor={formattedSectionName}>
        {label}
      </label>
      <div>
        {selectedFile?.error && (
          <div
            className="usa-error-message"
            id={`${formattedSectionName}-error-alert`}
            role="alert"
          >
            {selectedFile.error.message} {selectedFile.error.link}
          </div>
        )}
      </div>
      <div
        id={`${formattedSectionName}-file`}
        aria-hidden
        className="display-none"
      >
        {ariaDescription}
      </div>
      <input
        ref={inputRef}
        onChange={validateAndUploadFile}
        id={formattedSectionName}
        className="usa-file-input"
        type="file"
        disabled={Boolean(uploadScope && !selectedFile)}
        name={section}
        aria-describedby={`${formattedSectionName}-file`}
        aria-hidden="false"
        data-errormessage={INVALID_FILE_ERROR}
      />
    </div>
  )
}

FileUpload.propTypes = {
  section: PropTypes.string.isRequired,
  uploadScope: PropTypes.object,
  sectionDescriptor: PropTypes.object,
}

export default FileUpload
