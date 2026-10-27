import { useEffect, useRef } from 'react'
import { useDispatch, useSelector, useStore } from 'react-redux'
import {
  submit,
  SET_TANF_SUBMISSION_STATUS,
  getTanfSubmissionStatus,
  getAvailableFileList,
} from '../actions/reports'
import { useEventLogger } from '../utils/eventLogger'
import { useFormSubmission } from './useFormSubmission'
import { POLLING_TIMEOUT_MESSAGE } from '../components/Reports/constants'
import { useReportsContext } from '../components/Reports/ReportsContext'
import {
  getHistoryQueryKey,
  sameHistoryScope,
  sameUploadScope,
  isUploadCurrent,
} from '../utils/reportScopes'

/**
 * Custom hook that encapsulates shared file upload form logic
 * Used by both QuarterFileUploadForm and SectionFileUploadForm
 *
 * @param {Object} config - Configuration object
 * @param {Object} config.stt - STT object with id
 * @param {Function} config.transformFiles - Function to transform uploaded files before submission
 * @param {Function} config.formatSections - Function to format section names for display
 * @param {Function} config.getSubmitPayload - Function to generate submit action payload
 * @param {Object} config.uploadScope - Optional configured TDR assignment/generation
 * @returns {Object} Form state and handlers
 */
export const useFileUploadForm = ({
  stt,
  transformFiles,
  formatSections,
  getSubmitPayload,
  uploadScope,
}) => {
  const dispatch = useDispatch()
  const store = useStore()
  const logger = useEventLogger()

  const {
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    uploadAlert,
    setUploadAlertState,
    processingAlert,
    setProcessingAlertState,
    uploadAlertRef,
    processingAlertRef,
    uploadedFiles,
    setErrorModalVisible,
    setModalTriggerSource,
    handleClearFilesOnly,
    handleClearAll,
    handleOpenFeedbackWidget,
    startPolling,
  } = useReportsContext()

  const user = useSelector((state) => state.auth.user)
  const { isSubmitting, executeSubmission } = useFormSubmission(
    uploadScope?.generation
  )
  const selectionRef = useRef()
  const mountedRef = useRef(true)
  const pollingCancellations = useRef([])
  const historyKey = getHistoryQueryKey({
    stt,
    year: yearInputValue,
    quarter: quarterInputValue,
    file_type: fileTypeInputValue,
  })
  const queryGenerationRef = useRef()
  if (queryGenerationRef.current?.key !== historyKey)
    queryGenerationRef.current = { key: historyKey }
  const queryGeneration = queryGenerationRef.current
  selectionRef.current = { uploadScope, historyKey }
  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
    }
  }, [])
  useEffect(
    () => () => {
      pollingCancellations.current.forEach((cancel) => cancel?.())
      pollingCancellations.current = []
    },
    [historyKey]
  )
  const isCurrentUpload = () =>
    !uploadScope ||
    (mountedRef.current &&
      sameUploadScope(selectionRef.current.uploadScope, uploadScope) &&
      isUploadCurrent(store.getState().reports, uploadScope, uploadedFiles))
  const isCurrentQuery = () =>
    mountedRef.current && queryGenerationRef.current === queryGeneration
  const isCurrentSubmission = () =>
    isCurrentUpload() && (!uploadScope || isCurrentQuery())

  // Format sections for display in success message
  const formattedSections = formatSections(uploadedFiles)

  const onFileUploadSuccess = (fileIds, submittedFiles) => {
    if (!isCurrentSubmission()) return
    const pollSubmissionStatus = (historyScope) =>
      fileIds.forEach((fileId) => {
        const isCurrent = () =>
          !uploadScope ||
          (isCurrentQuery() &&
            sameHistoryScope(
              store.getState().reports.historyScope,
              historyScope
            ))
        if (!isCurrent()) return
        const cancel = startPolling(
          uploadScope ? `${historyScope.requestId}:${fileId}` : `${fileId}`,
          () => getTanfSubmissionStatus(fileId),
          (response) => {
            if (!isCurrent()) return
            let summary = response?.data?.summary
            return summary && summary.status && summary.status !== 'Pending'
          },
          (response) => {
            if (!isCurrent()) return
            dispatch({
              type: SET_TANF_SUBMISSION_STATUS,
              payload: {
                datafile_id: fileId,
                datafile: response?.data,
                ...(uploadScope && { historyScope }),
              },
            })
          },
          (error) => {
            if (!isCurrent()) return
            setProcessingAlertState({
              active: true,
              type: error.type ? error.type : 'error',
              message: error.message,
            })
          },
          (onError) => {
            if (!isCurrent()) return
            onError({
              message: POLLING_TIMEOUT_MESSAGE,
              type: 'warning',
            })
          },
          ...(uploadScope ? [undefined, undefined, { isCurrent }] : [])
        )
        if (uploadScope && cancel) pollingCancellations.current.push(cancel)
      })

    dispatch(
      getAvailableFileList(
        {
          quarter: quarterInputValue,
          year: yearInputValue,
          stt: stt,
          file_type: fileTypeInputValue,
        },
        pollSubmissionStatus,
        uploadScope ? { scoped: true, isCurrent: isCurrentQuery } : undefined
      )
    )

    // Clear the local upload panel after a successful submission; history and
    // polling continue via Redux state updates.
    if (uploadScope) handleOpenFeedbackWidget(submittedFiles)
    handleClearFilesOnly()
  }

  // Handle form submission
  const onSubmit = async (event) => {
    event.preventDefault()
    if (!isCurrentUpload()) return

    const validationErrorCount = uploadedFiles.filter(
      (file) =>
        file.error ||
        (uploadScope && file.isValidating) ||
        (file.validatedYear && file.validatedYear !== yearInputValue) ||
        (fileTypeInputValue !== 'program-integrity-audit' &&
          quarterInputValue &&
          file.validatedQuarter &&
          file.validatedQuarter !== quarterInputValue)
    ).length

    if (uploadedFiles.length === 0) {
      setUploadAlertState({
        active: true,
        type: 'error',
        message:
          'No data files have been selected. Select at least one file before submitting.',
      })
      return
    }

    if (validationErrorCount > 0) {
      setUploadAlertState({
        active: true,
        type: 'error',
        message:
          validationErrorCount === 1
            ? 'There is 1 error that must be resolved before submitting'
            : `There are ${validationErrorCount} errors that must be resolved before submitting`,
      })
      return
    }

    try {
      // Transform files if needed (e.g., for Program Audit)
      const filesToSubmit = transformFiles
        ? transformFiles(uploadedFiles)
        : uploadedFiles

      // Get submit payload with all necessary parameters
      const payload = getSubmitPayload({
        quarter: quarterInputValue,
        year: yearInputValue,
        formattedSections,
        logger,
        setUploadAlertState,
        setProcessingAlertState,
        stt: stt?.id,
        uploadedFiles: filesToSubmit,
        user,
        fileType: fileTypeInputValue,
      })

      const submittedFiles = await executeSubmission(() =>
        dispatch(
          submit(
            {
              ...payload,
              ...(uploadScope && {
                uploadScope,
                isCurrent: isCurrentSubmission,
              }),
            },
            onFileUploadSuccess
          )
        )
      )
      if (!uploadScope) handleOpenFeedbackWidget(submittedFiles)
    } catch (error) {
      console.error('Error during form submission:', error)
      if (!isCurrentSubmission()) return
      setUploadAlertState({
        active: true,
        type: 'error',
        message: 'An error occurred during submission. Please try again.',
      })
    }
  }

  // Handle cancel button click
  const handleCancel = () => {
    if (uploadedFiles.length > 0) {
      setModalTriggerSource('cancel')
      setErrorModalVisible(true)
    } else {
      handleClearAll()
    }
  }

  return {
    // Form state
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    uploadAlert,
    processingAlert,
    uploadedFiles,
    isSubmitting,
    uploadAlertRef,
    processingAlertRef,
    formattedSections,

    // Form handlers
    onSubmit,
    handleCancel,

    // Context setters (for FileUpload components)
    setUploadAlertState,
    setProcessingAlertState,
  }
}
