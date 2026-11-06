import { v4 as uuidv4 } from 'uuid'

import { get, post } from '../fetch-instance'
import { logErrorToServer } from '../utils/eventLogger'
import removeFileInputErrorState from '../utils/removeFileInputErrorState'
import { quarters } from '../components/Reports/utils'
import {
  getUploadAssignmentKey,
  getHistoryQueryKey,
  sameHistoryScope,
  sameUploadScope,
  isUploadCurrent,
} from '../utils/reportScopes'

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL

export const SET_FILE = 'SET_FILE'
export const CLEAR_FILE = 'CLEAR_FILE'
export const CLEAR_FILE_LIST = 'CLEAR_FILE_LIST'
export const SET_FILE_ERROR = 'SET_FILE_ERROR'
export const FILE_EXT_ERROR = 'FILE_EXT_ERROR'
export const SET_FILE_SUBMITTED = 'SET_FILE_SUBMITTED'
export const CLEAR_ERROR = 'CLEAR_ERROR'

export const START_FILE_DOWNLOAD = 'START_FILE_DOWNLOAD'
export const FILE_DOWNLOAD_ERROR = 'FILE_DOWNLOAD_ERROR'

export const FETCH_FILE_LIST = 'FETCH_FILE_LIST'
export const SET_FILE_LIST = 'SET_FILE_LIST'
export const FETCH_FILE_LIST_ERROR = 'FETCH_FILE_LIST_ERROR'
export const DOWNLOAD_DIALOG_OPEN = 'DOWNLOAD_DIALOG_OPEN'

export const REINITIALIZE_SUBMITTED_FILES = 'REINITIALIZE_SUBMITTED_FILES'

export const SET_TANF_SUBMISSION_STATUS = 'SET_TANF_SUBMISSION_STATUS'
export const CONFIGURE_UPLOAD_SECTIONS = 'CONFIGURE_UPLOAD_SECTIONS'
export const BEGIN_FILE_VALIDATION = 'BEGIN_FILE_VALIDATION'
export const INVALIDATE_FILE_LIST = 'INVALIDATE_FILE_LIST'

/**
 * Opt-in TDR slots. null restores legacy defaults; expectedScope makes cleanup
 * conditional so an old owner cannot invalidate a newer assignment.
 */
export const configureUploadSections =
  (configuration, expectedScope) => (dispatch, getState) => {
    const current = getState().reports.uploadScope
    if (expectedScope && !sameUploadScope(current, expectedScope))
      return current
    const key = configuration ? getUploadAssignmentKey(configuration) : null
    if (configuration && current?.key === key) return current
    const uploadScope = configuration
      ? { ...configuration, key, generation: uuidv4() }
      : null
    dispatch({ type: CONFIGURE_UPLOAD_SECTIONS, payload: { uploadScope } })
    return uploadScope
  }

export const reinitializeSubmittedFiles =
  (fileType, options = {}) =>
  (dispatch, getState) => {
    dispatch({
      type: REINITIALIZE_SUBMITTED_FILES,
      payload: {
        fileType,
        ...options,
        ...(getState()?.reports?.uploadScope && { generation: uuidv4() }),
      },
    })
  }

export const clearFile =
  ({ section, ...identity }) =>
  (dispatch) => {
    dispatch({ type: CLEAR_FILE, payload: { section, ...identity } })
  }

export const clearFileList =
  ({ fileType, uploadScope }) =>
  (dispatch, getState) => {
    if (
      uploadScope &&
      !sameUploadScope(getState().reports.uploadScope, uploadScope)
    )
      return
    // Clean up any DOM error states before clearing Redux state
    removeFileInputErrorState()
    dispatch({
      type: CLEAR_FILE_LIST,
      payload: {
        fileType,
        ...(uploadScope && { uploadScope }),
        ...(getState()?.reports?.uploadScope && { generation: uuidv4() }),
      },
    })
  }

export const clearError =
  ({ section, ...identity }) =>
  (dispatch) => {
    dispatch({ type: CLEAR_ERROR, payload: { section, ...identity } })
  }

export const getAvailableFileList =
  (
    { quarter = 'Q1', stt, year, file_type, section },
    onSuccess = () => null,
    options = {}
  ) =>
  async (dispatch, getState) => {
    const historyScope = options.scoped
      ? {
          key: getHistoryQueryKey({ quarter, stt, year, file_type }),
          requestId: options.requestId || uuidv4(),
        }
      : undefined
    const isCurrent = () =>
      !historyScope ||
      (sameHistoryScope(getState().reports.historyScope, historyScope) &&
        (options.isCurrent?.() ?? true))
    if (
      options.scoped &&
      (!historyScope.key || options.isCurrent?.() === false)
    )
      return
    const scopePayload = historyScope ? { historyScope } : {}
    dispatch({
      type: FETCH_FILE_LIST,
      ...(historyScope && { payload: scopePayload }),
    })
    let url = `${BACKEND_URL}/data_files/?year=${year}&stt=${stt.id}&file_type=${file_type}`
    if (quarter) {
      url += `&quarter=${quarter}`
    }
    let response
    try {
      response = await get(url)
    } catch (error) {
      if (!historyScope) throw error
      response = { ok: false, error }
    }
    if (!isCurrent()) return
    const { data, ok, error } = response

    if (!ok) {
      dispatch({
        type: FETCH_FILE_LIST_ERROR,
        payload: {
          error,
          year,
          quarter,
          file_type,
          section,
          ...scopePayload,
        },
      })
      return
    }

    dispatch({
      type: SET_FILE_LIST,
      payload: {
        data,
        ...scopePayload,
      },
    })
    if (!isCurrent()) return
    if (historyScope) onSuccess(historyScope)
    else onSuccess()
  }

export const download =
  ({
    id,
    quarter = 'Q1',
    program_type,
    section,
    year,
    s3_version_id,
    fileName,
  }) =>
  async (dispatch) => {
    try {
      if (!id) throw new Error('No id was provided to download action.')
      dispatch({ type: START_FILE_DOWNLOAD })
      const { data, ok, error } = await get(
        `${BACKEND_URL}/data_files/${id}/download/`,
        { responseType: 'blob' }
      )

      if (!ok) throw error

      // Create a link and associate it with the blob returned from the file
      // download - this allows us to trigger the file download dialog without
      // having to change the route or reload the page.
      const url = window.URL.createObjectURL(new Blob([data]))
      const link = document.createElement('a')

      link.href = url
      const fileNameParts = fileName.split('.')
      const baseName = fileNameParts.slice(0, -1).join('.')
      link.setAttribute(
        'download',
        `${baseName} (${year}-${quarter}-${program_type}-${section}).txt`
      )

      document.body.appendChild(link)

      // Click the link to actually prompt the file download
      link.click()

      // Cleanup afterwards to prevent unwanted side effects
      document.body.removeChild(link)
      dispatch({ type: DOWNLOAD_DIALOG_OPEN })
    } catch (error) {
      dispatch({
        type: FILE_DOWNLOAD_ERROR,
        payload: { error, year, quarter, section, s3_version_id },
      })
      return false
    }
  }

// Main Redux action to add files to the state
export const upload =
  ({ file, section, year, quarter, uploadScope, sectionId, program, uuid }) =>
  async (dispatch) => {
    try {
      dispatch({
        type: SET_FILE,
        payload: {
          file: file,
          fileName: file.name,
          fileType: file.type,
          section,
          uuid: uuid || uuidv4(),
          ...(uploadScope && { uploadScope, sectionId, program }),
          ...(year && { validatedYear: year }),
          ...(quarter && { validatedQuarter: quarter }),
        },
      })
    } catch (error) {
      logErrorToServer(SET_FILE_ERROR)
      dispatch({
        type: SET_FILE_ERROR,
        payload: {
          error,
          section,
          ...(uploadScope && { uploadScope, sectionId, program, uuid }),
        },
      })
      return false
    }

    return true
  }

// For now because we consider Program Audit to be the section and program type in the backend, that is what is
// returned to the frontend for the submittedFile's section. However, the frontend maps the Program Audit file's
// section to be the quarter labels. Thus, we need this function to map the backend to the frontend.
const map_section = (fileType, submittedFile) => {
  if (fileType === 'program-integrity-audit') {
    return {
      ...submittedFile,
      section: quarters[submittedFile.quarter],
    }
  }
  return submittedFile
}

export const submit =
  (
    {
      formattedSections,
      logger,
      quarter,
      setUploadAlertState,
      setProcessingAlertState,
      stt,
      uploadedFiles,
      user,
      year,
      ssp,
      fileType,
      uploadScope,
      isCurrent: isContextCurrent = () => true,
    },
    onComplete = () => null
  ) =>
  async (dispatch, getState) => {
    const isCurrent = () =>
      !uploadScope ||
      (isContextCurrent() &&
        isUploadCurrent(getState().reports, uploadScope, uploadedFiles))
    if (!isCurrent()) return
    const submissionRequests = uploadedFiles.map((file) => {
      const formData = new FormData()
      const dataFile = {
        file: file.file,
        original_filename: file.fileName,
        slug: file.uuid,
        user: user.id,
        section: file.section,
        year,
        stt,
        quarter: quarter ? quarter : file.quarter,
        ssp,
        is_program_audit: file.is_program_audit ? file.is_program_audit : false,
      }
      for (const [key, value] of Object.entries(dataFile)) {
        formData.append(key, value)
      }
      const request = post(
        `${process.env.REACT_APP_BACKEND_URL}/data_files/`,
        formData
      )
      return uploadScope
        ? Promise.resolve(request).catch((error) => ({ ok: false, error }))
        : request
    })

    return Promise.all(submissionRequests)
      .then((responses) => {
        // Successful server writes still need their audit event after navigation
        // or a sibling request failure, even when local UI updates are stale.
        if (uploadScope) {
          const successes = responses.filter((response) => response.ok)
          if (successes.length)
            logger.alert(
              `Submitted ${successes.length} data file(s): ${successes.map(({ data }) => `${data.original_filename} (${data.extension})`).join(', ')}`,
              {
                files: successes.map(({ data }) => data.id),
                activity: 'upload',
              }
            )
        }
        // Check if any responses have errors
        const failedResponse = responses.find((r) => !r.ok)
        if (failedResponse) {
          const err = new Error(failedResponse.error?.message || 'Error')
          err.response = { data: failedResponse.data }
          throw err
        }

        const current = isCurrent()
        if (current)
          setProcessingAlertState({
            active: true,
            type: 'success',
            message: `Successfully uploaded section(s): ${formattedSections} on ${new Date().toDateString()}`,
          })

        if (current) removeFileInputErrorState()

        const submittedFileObjects = []
        const submittedFileNames = responses.reduce(
          (result, response, index) => {
            const submittedFile = map_section(fileType, response?.data)

            if (current)
              dispatch({
                type: SET_FILE_SUBMITTED,
                payload: {
                  submittedFile,
                  ...(uploadScope && {
                    uploadScope,
                    sourceFile: uploadedFiles[index],
                  }),
                },
              })

            submittedFileObjects.push(submittedFile)
            result.push(
              `${submittedFile?.original_filename} (${submittedFile?.extension})`
            )
            return result
          },
          []
        )

        // Create LogEntries in Django for each created ReportFile
        const fileIds = responses.map((response) => response?.data?.id)
        if (!uploadScope)
          logger.alert(
            `Submitted ${
              submittedFileNames.length
            } data file(s): ${submittedFileNames.join(', ')}`,
            {
              files: fileIds,
              activity: 'upload',
            }
          )

        if (isCurrent()) {
          if (uploadScope) onComplete(fileIds, submittedFileObjects)
          else onComplete(fileIds)
        }

        // Return the submitted file objects for feedback widget
        return submittedFileObjects
      })
      .catch((error) => {
        const error_response = error.response?.data
        const msg = error_response?.non_field_errors
          ? error_response.non_field_errors[0]
          : error_response?.detail
            ? error_response.detail
            : error_response?.file
              ? error_response.file
              : null
        if (isCurrent())
          setUploadAlertState({
            active: true,
            type: 'error',
            message: ''.concat(error.message, ': ', msg),
          })
      })
  }

export const SET_SELECTED_STT = 'SET_SELECTED_STT'

export const setStt = (stt) => (dispatch) => {
  dispatch({ type: SET_SELECTED_STT, payload: { stt } })
}

export const getTanfSubmissionStatus = async (datafile_id) => {
  const { data, ok, error } = await get(
    `${BACKEND_URL}/data_files/${datafile_id}/`
  )
  if (!ok) {
    throw error
  }
  return { data, ok: true }
}
