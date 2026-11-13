import {
  SET_FILE,
  CLEAR_FILE,
  SET_FILE_ERROR,
  FILE_EXT_ERROR,
  CLEAR_ERROR,
  SET_SELECTED_STT,
  SET_FILE_LIST,
  CLEAR_FILE_LIST,
  SET_FILE_SUBMITTED,
  REINITIALIZE_SUBMITTED_FILES,
  FETCH_FILE_LIST,
  FETCH_FILE_LIST_ERROR,
  SET_TANF_SUBMISSION_STATUS,
  CONFIGURE_UPLOAD_SECTIONS,
  BEGIN_FILE_VALIDATION,
  INVALIDATE_FILE_LIST,
} from '../actions/reports'

import { programIntegrityAuditLabels } from '../components/Reports/utils'
import {
  sameUploadScope,
  sameSection,
  sameHistoryScope,
} from '../utils/reportScopes'
import { programSlugToResponseCode } from '../utils/reportSections'

const getFileIndex = (files, section) =>
  files.findIndex((currentFile) => currentFile.section.includes(section))

const getFile = (files, section) =>
  files
    .slice()
    .sort((a, b) => b.id - a.id)
    .find((currentFile) => currentFile.section.includes(section))

export const fileUploadSections = [
  'Active Case Data',
  'Closed Case Data',
  'Aggregate Data',
  'Stratum Data',
]

export const getUpdatedFiles = ({
  state,
  fileName,
  section,
  id = null,
  uuid = null,
  fileType = null,
  error = null,
  file = null,
  validatedYear,
  validatedQuarter,
}) => {
  const oldFileIndex = getFileIndex(state?.submittedFiles, section)
  if (oldFileIndex === -1) return state.submittedFiles
  const updatedFiles = [...state.submittedFiles]
  updatedFiles[oldFileIndex] = {
    id,
    file,
    section,
    fileName,
    error,
    uuid,
    fileType,
    ...(validatedYear && { validatedYear }),
    ...(validatedQuarter && { validatedQuarter }),
  }

  return updatedFiles
}

export const serializeApiDataFile = (dataFile) => ({
  id: dataFile.id,
  fileName: dataFile.original_filename,
  fileType: dataFile.extension,
  quarter: dataFile.quarter,
  section: dataFile.section,
  program_type: dataFile.program_type,
  uuid: dataFile.slug,
  year: dataFile.year,
  s3_version_id: dataFile.s3_version_id,
  createdAt: dataFile.created_at,
  submittedBy: dataFile.submitted_by,
  hasError: dataFile.has_error,
  summary: dataFile.summary,
  latest_reparse_file_meta: dataFile.latest_reparse_file_meta,
})

const initialState = {
  files: [],
  submittedFiles: fileUploadSections.map((section) => ({
    section,
    fileName: null,
    error: null,
    uuid: null,
    fileType: null,
  })),
  year: '',
  stt: '',
  quarter: '',
  fileType: '',
  loading: false,
}

const configuredSlots = (scope) =>
  scope.sections.map(({ id, name, program }) => ({
    section: name,
    sectionId: id,
    program,
    fileName: null,
    error: null,
    uuid: null,
    fileType: null,
    isValidating: false,
  }))

const updateConfiguredSlot = (state, type, payload) => {
  if (!sameUploadScope(state.uploadScope, payload.uploadScope)) return state
  const identity = payload.sourceFile || payload
  const index = state.submittedFiles.findIndex((slot) =>
    sameSection(slot, {
      id: identity.sectionId,
      name: identity.section,
      program: identity.program,
    })
  )
  if (index === -1) return state
  const slot = state.submittedFiles[index]
  if (
    [
      BEGIN_FILE_VALIDATION,
      SET_FILE,
      SET_FILE_ERROR,
      FILE_EXT_ERROR,
      SET_FILE_SUBMITTED,
    ].includes(type) &&
    !identity.uuid
  )
    return state
  if (
    type !== BEGIN_FILE_VALIDATION &&
    identity.uuid !== undefined &&
    slot.uuid !== identity.uuid
  )
    return state
  let updated
  if (type === SET_FILE_SUBMITTED) {
    const { submittedFile } = payload
    if (
      !identity.uuid ||
      submittedFile?.slug !== identity.uuid ||
      submittedFile?.section !== slot.section ||
      submittedFile?.program_type !==
        programSlugToResponseCode(slot.program.slug)
    )
      return state
    updated = { ...slot, ...serializeApiDataFile(submittedFile) }
  } else if (type === CLEAR_ERROR) {
    updated = { ...slot, error: null }
  } else if (type === CLEAR_FILE) {
    updated = configuredSlots(state.uploadScope)[index]
  } else {
    const changes = { ...payload }
    delete changes.uploadScope
    const isValidating = type === BEGIN_FILE_VALIDATION
    updated = {
      ...(isValidating ? configuredSlots(state.uploadScope)[index] : slot),
      ...changes,
      id: null,
      isValidating,
      error: payload.error || null,
    }
  }
  const submittedFiles = [...state.submittedFiles]
  submittedFiles[index] = updated
  return { ...state, submittedFiles }
}

const reports = (state = initialState, action) => {
  const { type, payload = {} } = action
  if (
    [CLEAR_FILE_LIST, REINITIALIZE_SUBMITTED_FILES].includes(type) &&
    payload.uploadScope &&
    !sameUploadScope(state.uploadScope, payload.uploadScope)
  )
    return state
  if (
    (state.uploadScope || payload.uploadScope) &&
    [
      BEGIN_FILE_VALIDATION,
      SET_FILE,
      SET_FILE_ERROR,
      FILE_EXT_ERROR,
      CLEAR_FILE,
      CLEAR_ERROR,
      SET_FILE_SUBMITTED,
    ].includes(type)
  )
    return updateConfiguredSlot(state, type, payload)
  if (
    [SET_FILE_LIST, FETCH_FILE_LIST_ERROR, SET_TANF_SUBMISSION_STATUS].includes(
      type
    ) &&
    (state.historyScope || payload.historyScope) &&
    !sameHistoryScope(state.historyScope, payload.historyScope)
  )
    return state
  switch (type) {
    case CONFIGURE_UPLOAD_SECTIONS: {
      const { uploadScope } = payload
      return {
        ...state,
        uploadScope,
        submittedFiles: uploadScope
          ? configuredSlots(uploadScope)
          : initialState.submittedFiles,
      }
    }
    case INVALIDATE_FILE_LIST: {
      if (!sameHistoryScope(state.historyScope, payload.historyScope))
        return state
      return { ...state, historyScope: null, files: [], loading: false }
    }
    case FETCH_FILE_LIST: {
      return {
        ...state,
        loading: true,
        ...(payload.historyScope
          ? { historyScope: payload.historyScope, files: [] }
          : state.historyScope
            ? { historyScope: null }
            : {}),
      }
    }
    case REINITIALIZE_SUBMITTED_FILES: {
      if (state.uploadScope) {
        return {
          ...state,
          uploadScope: {
            ...state.uploadScope,
            generation:
              payload.generation || `${state.uploadScope.generation}:reset`,
          },
          submittedFiles: configuredSlots(state.uploadScope),
        }
      }
      const { fileType } = payload
      const sections =
        fileType === 'program-integrity-audit'
          ? programIntegrityAuditLabels
          : fileUploadSections

      return {
        ...state,
        submittedFiles: sections.map((section) => ({
          section,
          fileName: null,
          error: null,
          uuid: null,
          fileType: null,
        })),
      }
    }
    case SET_FILE: {
      const {
        file,
        fileName,
        section,
        uuid,
        fileType,
        validatedYear,
        validatedQuarter,
      } = payload
      const updatedFiles = getUpdatedFiles({
        state,
        fileName,
        section,
        uuid,
        fileType,
        file,
        validatedYear,
        validatedQuarter,
      })
      return { ...state, submittedFiles: updatedFiles }
    }
    case SET_FILE_LIST: {
      const { data } = payload
      return {
        ...state,
        files: data.map((f) => serializeApiDataFile(f)),
        loading: false,
      }
    }
    case FETCH_FILE_LIST_ERROR: {
      return {
        ...state,
        loading: false,
      }
    }
    case SET_FILE_SUBMITTED: {
      const { submittedFile } = payload
      return {
        ...state,
        submittedFiles: state.submittedFiles.map((file) =>
          // Match by uuid (slug) or section to handle transformed files because submitting PIA files changes
          // their section from `Quarter X (Month Y to Month Z)` to `Program Audit` for the backend.
          submittedFile?.slug === file.uuid ||
          submittedFile?.section.includes(file.section)
            ? serializeApiDataFile(submittedFile)
            : file
        ),
      }
    }
    case CLEAR_FILE: {
      const { section } = payload
      const updatedFiles = getUpdatedFiles({ state, section })
      return { ...state, submittedFiles: updatedFiles }
    }
    case CLEAR_FILE_LIST: {
      if (state.uploadScope) {
        return {
          ...state,
          files: [],
          uploadScope: {
            ...state.uploadScope,
            generation:
              payload.generation || `${state.uploadScope.generation}:reset`,
          },
          submittedFiles: configuredSlots(state.uploadScope),
        }
      }
      const { fileType } = payload
      return {
        ...state,
        files: initialState.files,
        submittedFiles:
          fileType !== 'program-integrity-audit'
            ? initialState.submittedFiles
            : programIntegrityAuditLabels.map((section) => ({
                section,
                fileName: null,
                error: null,
                uuid: null,
                fileType: null,
              })),
      }
    }
    case SET_FILE_ERROR: {
      const { error, file, fileName, fileType, section } = payload
      const updatedFiles = getUpdatedFiles({
        state,
        error,
        file,
        fileName,
        fileType,
        section,
      })
      return { ...state, submittedFiles: updatedFiles }
    }
    case FILE_EXT_ERROR: {
      const { error, file, fileName, fileType, section } = payload
      const updatedFiles = getUpdatedFiles({
        state,
        error,
        file,
        fileName,
        fileType,
        section,
      })
      return { ...state, submittedFiles: updatedFiles }
    }
    case CLEAR_ERROR: {
      const { section } = payload
      const file = getFile(state.submittedFiles, section)
      if (!file) return state
      const updatedFiles = getUpdatedFiles({
        state,
        fileName: file.fileName,
        section,
        uuid: file.uuid,
        id: file.id,
        fileType: file.fileType,
      })
      return { ...state, submittedFiles: updatedFiles }
    }
    case SET_SELECTED_STT: {
      const { stt } = payload
      return { ...state, stt }
    }
    case SET_TANF_SUBMISSION_STATUS: {
      const { datafile_id, datafile } = payload
      const files = state.files.map((f) =>
        f.id === datafile_id ? serializeApiDataFile(datafile) : f
      )

      return { ...state, files }
    }
    default:
      return state
  }
}

export default reports
