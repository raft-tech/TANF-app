/* istanbul ignore file */
import {
  createContext,
  useContext,
  useState,
  useRef,
  useEffect,
  useCallback,
  useMemo,
} from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  clearFileList,
  configureUploadSections,
  reinitializeSubmittedFiles,
  setStt,
} from '../../actions/reports'
import { openFeedbackWidget } from '../../reducers/feedbackWidget'
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import {
  accountCanSelectStt,
  accountIsRegionalStaff,
} from '../../selectors/auth'
import { resolveReportStt } from '../../selectors/stts'
import { getTdrAssignment } from '../../utils/reportSections'
import { getUploadAssignmentKey } from '../../utils/reportScopes'
import { usePollingTimer } from '../../hooks/usePollingTimer'
import { getCurrentFiscalYear, quarters } from './utils'
import {
  FRA_SUBMISSION_YEARS_FEATURE_FLAG,
  getFlagOrDefault,
  isFeatureActiveForYear,
  selectFeatureFlags,
} from '../../selectors/featureFlags'

const ReportsContext = createContext()

export const useReportsContext = () => {
  const context = useContext(ReportsContext)
  if (!context) {
    throw new Error('useReportsContext must be used within ReportsProvider')
  }
  return context
}

const getValidFileTypes = (isFra, piaEnabled = false) => {
  if (isFra) {
    return [
      'workOutcomesOfTanfExiters',
      // TODO: uncomment when we collect this data
      // 'secondarySchoolAttainment',
      // 'supplementalWorkOutcomes',
    ]
  }

  if (piaEnabled) {
    return ['tanf', 'ssp-moe', 'program-integrity-audit']
  }

  return ['tanf', 'ssp-moe']
}

// Valid quarters
const VALID_QUARTERS = Object.keys(quarters) // ['Q1', 'Q2', 'Q3', 'Q4']

/**
 * Validates URL parameters for the report pages.
 * Invalid parameters are cleared individually, valid ones are kept.
 * @param {URLSearchParams} searchParams - URL search parameters
 * @param {boolean} isFra - Whether this is for FRA reports
 * @param {Array} sttList - List of valid STTs
 */
const validateUrlParams = (
  searchParams,
  isFra,
  sttList,
  piaFeatureFlag = null
) => {
  const fiscalYear = searchParams.get('fy')
  const quarter = searchParams.get('q')
  const type = searchParams.get('type')
  const stt = searchParams.get('stt')
  const tab = searchParams.get('tab')

  const defaultType = isFra ? 'workOutcomesOfTanfExiters' : 'tanf'
  let validatedFy = ''
  let validatedQ = ''
  let validatedType = defaultType
  let validatedStt = ''
  let validatedTab = 1
  let hasInvalidParam = false

  // Validate fiscal year (must be a valid year between 2021 and current fiscal year)
  // For program-integrity-audit, only 2024 is allowed
  const year = parseInt(fiscalYear, 10)
  const currentFiscalYear = getCurrentFiscalYear()
  const minYear =
    type === 'program-integrity-audit'
      ? piaFeatureFlag?.config?.minYear || 2024
      : 2021
  const maxYear =
    type === 'program-integrity-audit'
      ? piaFeatureFlag?.config?.maxYear || 2024
      : currentFiscalYear
  if (!isNaN(year) && year >= minYear && year <= maxYear) {
    validatedFy = fiscalYear
  } else {
    hasInvalidParam = true
  }

  // Validate quarter (must be Q1, Q2, Q3, or Q4)
  if (VALID_QUARTERS.includes(quarter)) {
    validatedQ = quarter
  } else {
    hasInvalidParam = true
  }

  // Validate file type
  const validTypes = getValidFileTypes(isFra, piaFeatureFlag?.enabled || false)
  if (validTypes.includes(type)) {
    validatedType = type
  } else {
    hasInvalidParam = true
  }

  // Validate STT (must exist in the STT list if provided)
  if (sttList && sttList.length > 0) {
    if (sttList.some((s) => s?.name === stt)) {
      validatedStt = stt
    } else {
      hasInvalidParam = true
    }
  } else {
    // STT list not loaded yet, keep the value for now
    validatedStt = stt
  }

  // Validate tab (must be 1 or 2)
  if (tab === '1' || tab === '2') {
    validatedTab = parseInt(tab, 10)
  } else {
    hasInvalidParam = true
  }

  return {
    fy: validatedFy,
    q: validatedQ,
    type: validatedType,
    stt: validatedStt,
    tab: validatedTab,
    wasInvalid: hasInvalidParam,
  }
}

export const ReportsProvider = ({ isFra = false, children }) => {
  const dispatch = useDispatch()
  const canSelectStt = useSelector(accountCanSelectStt)
  const isRegionalStaff = useSelector(accountIsRegionalStaff)
  const user = useSelector((state) => state.auth.user)
  const catalog = useSelector((state) => state.stts)
  const uploadScope = useSelector((state) => state.reports.uploadScope)
  const historyScope = useSelector((state) => state.reports.historyScope)
  const sttList = useSelector((state) => state?.stts?.sttList)
  const featureFlags = useSelector(selectFeatureFlags)
  const piaFeatureFlag = getFlagOrDefault(
    'program-integrity-audit',
    featureFlags
  )

  // Search params
  const [searchParams] = useSearchParams()
  const { hash } = useLocation()
  const navigate = useNavigate()
  const [hasValidatedParams, setHasValidatedParams] = useState(false)

  // Get validated params (without STT validation since it will never be loaded since we have to wait for fetchSTTs to
  // run.
  const validatedParams = useMemo(
    () => validateUrlParams(searchParams, isFra, [], piaFeatureFlag),
    [searchParams, isFra, piaFeatureFlag]
  )

  // Form state
  const [yearInputValue, setYearInputValue] = useState(validatedParams.fy)
  const [quarterInputValue, setQuarterInputValue] = useState(validatedParams.q)
  const [fileTypeInputValue, setFileTypeInputValue] = useState(
    validatedParams.type
  )
  const [sttInputValue, setSttInputValue] = useState(validatedParams.stt)
  const isFraSubmissionYearActive = isFeatureActiveForYear(
    FRA_SUBMISSION_YEARS_FEATURE_FLAG,
    yearInputValue,
    featureFlags
  )

  const sttResolution = useMemo(
    () =>
      resolveReportStt({
        user,
        canSelectStt,
        isRegionalStaff,
        catalog,
        selectedName: sttInputValue,
      }),
    [user, canSelectStt, isRegionalStaff, catalog, sttInputValue]
  )
  const tdrAssignment = useMemo(
    () =>
      getTdrAssignment(
        sttResolution,
        fileTypeInputValue,
        piaFeatureFlag.enabled
      ),
    [sttResolution, fileTypeInputValue, piaFeatureFlag.enabled]
  )
  const isTdr = !isFra && fileTypeInputValue !== 'program-integrity-audit'
  const configuration = useMemo(
    () => ({
      sttId: sttResolution.stt?.id || null,
      program: tdrAssignment.program || { id: null, slug: null },
      sections: tdrAssignment.sections,
    }),
    [sttResolution.stt?.id, tdrAssignment.program, tdrAssignment.sections]
  )
  const assignmentKey = getUploadAssignmentKey(configuration)
  const uploadScopeReady = isTdr && uploadScope?.key === assignmentKey
  const ownedScopeRef = useRef(null)
  useEffect(() => {
    if (isFra) return
    if (isTdr) {
      ownedScopeRef.current = dispatch(configureUploadSections(configuration))
    } else if (ownedScopeRef.current) {
      dispatch(configureUploadSections(null, ownedScopeRef.current))
      ownedScopeRef.current = null
      dispatch(reinitializeSubmittedFiles('program-integrity-audit'))
    }
  }, [dispatch, isFra, isTdr, configuration])
  // Clear/reset advances generations; cleanup must own the latest one.
  if (
    uploadScopeReady ||
    (uploadScope && uploadScope.key === ownedScopeRef.current?.key)
  )
    ownedScopeRef.current = uploadScope
  useEffect(
    () => () => {
      if (ownedScopeRef.current)
        dispatch(configureUploadSections(null, ownedScopeRef.current))
    },
    [dispatch]
  )

  useEffect(() => {
    if (isFra || sttResolution.state !== 'ready') return
    if (sttResolution.unauthorized) {
      setSttInputValue('')
      setYearInputValue('')
      setQuarterInputValue('')
    } else if (canSelectStt && sttInputValue && !sttResolution.stt) {
      setSttInputValue('')
    } else if (
      sttResolution.stt &&
      !sttResolution.provisional &&
      tdrAssignment.state === 'ready' &&
      !tdrAssignment.options.some(({ value }) => value === fileTypeInputValue)
    ) {
      setFileTypeInputValue(tdrAssignment.options[0]?.value || '')
    }
  }, [
    isFra,
    sttResolution,
    canSelectStt,
    sttInputValue,
    tdrAssignment,
    fileTypeInputValue,
  ])

  // Re-validate when STT list becomes available (only validates STT param) since it might not be available yet
  useEffect(() => {
    if (isFra && sttList && sttList.length > 0 && !hasValidatedParams) {
      // Check if the STT from URL is valid
      const sttParam = searchParams.get('stt')
      if (sttParam && !sttList.some((s) => s?.name === sttParam)) {
        // Invalid STT in URL clear it
        setSttInputValue('')
      }
      setHasValidatedParams(true)
    }
  }, [
    sttList,
    isFra,
    hasValidatedParams,
    searchParams,
    setSttInputValue,
    setHasValidatedParams,
  ])

  const [pendingChange, setPendingChange] = useState({
    type: null,
    value: null,
  })

  useEffect(() => {
    const newParams = new URLSearchParams()
    if (yearInputValue) {
      newParams.set('fy', yearInputValue)
    }
    if (quarterInputValue) {
      newParams.set('q', quarterInputValue)
    }
    if (fileTypeInputValue) {
      newParams.set('type', fileTypeInputValue)
    }
    if (sttInputValue) {
      newParams.set('stt', sttInputValue)
    }
    // Query updates must retain the fragment restored after sign-in.
    navigate({ search: `?${newParams}`, hash })
  }, [
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    sttInputValue,
    navigate,
    hash,
  ])

  // Touched state for validation
  const [yearTouched, setYearTouched] = useState(false)
  const [quarterTouched, setQuarterTouched] = useState(false)
  const [fileTypeTouched, setFileTypeTouched] = useState(false)
  const [sttTouched, setSttTouched] = useState(false)

  // FRA-specific upload state
  const [fraSelectedFile, setFraSelectedFile] = useState(null)
  const [fraUploadError, setFraUploadError] = useState(null)

  // Modal state
  const [errorModalVisible, setErrorModalVisible] = useState(false)
  const [modalTriggerSource, setModalTriggerSource] = useState(null) // 'cancel' or 'input-change'
  const [reprocessedModalVisible, setReprocessedModalVisible] = useState(false)
  const [reprocessedDate, setReprocessedDate] = useState('')

  // Alert state — the `timestamp` field ensures React always sees a new object
  // even when the same message is set consecutively, so the useEffect that
  // focuses the alert re-fires and the screen reader announces it again.
  const [uploadAlert, setUploadAlert] = useState({
    active: false,
    type: null,
    message: null,
  })
  const setUploadAlertState = (alert) =>
    setUploadAlert({ ...alert, timestamp: Date.now() })

  // Processing alert state (separate from uploadAlert for accessibility)
  const [processingAlert, setProcessingAlertState] = useState({
    active: false,
    type: null,
    message: null,
  })
  useEffect(() => {
    if (!isTdr) return
    setUploadAlert({ active: false, type: null, message: null })
    setProcessingAlertState({ active: false, type: null, message: null })
  }, [assignmentKey, isTdr])

  // Refs
  const headerRef = useRef(null)
  const uploadAlertRef = useRef(null)
  const processingAlertRef = useRef(null)

  // Redux selectors
  const files = useSelector((state) => state.reports.submittedFiles)
  const uploadedFiles = useMemo(
    () => files?.filter((file) => file.fileName && !file.id) || [],
    [files]
  )
  const submittedFiles = useMemo(
    () => files?.filter((file) => file.fileName && file.id) || [],
    [files]
  )

  // FRA-specific derived state
  const fraHasUploadedFile = !!fraSelectedFile && !fraSelectedFile.id
  const hasUnsubmittedFile = isFra
    ? fraHasUploadedFile
    : uploadedFiles.length > 0

  const { startPolling, isPolling, stopAllTimers } = usePollingTimer()
  // Tables still consume file IDs; scoped timers use request-token:file-ID.
  const visiblePolling = useMemo(() => {
    if (!isTdr) return isPolling
    const prefix = `${historyScope?.requestId}:`
    return Object.fromEntries(
      Object.entries(isPolling).flatMap(([key, active]) =>
        key.startsWith(prefix)
          ? [[key.slice(prefix.length), active]]
          : key.includes(':')
            ? []
            : [[key, active]]
      )
    )
  }, [isTdr, historyScope, isPolling])

  // Actions
  const handleClearAll = () => {
    // Clear everything including STT, year, quarter
    if (isFra) {
      setFraSelectedFile(null)
      setFraUploadError(null)
      setYearInputValue('')
      setQuarterInputValue('')
      setSttInputValue('')
    } else {
      dispatch(clearFileList({ fileType: fileTypeInputValue }))
      setYearInputValue('')
      setQuarterInputValue('')
    }
  }

  const handleClearFilesOnly = () => {
    // Clear only file inputs/previews, keep STT, year, quarter
    if (isFra) {
      setFraSelectedFile(null)
      setFraUploadError(null)
    } else {
      dispatch(clearFileList({ fileType: fileTypeInputValue }))
    }
    if (pendingChange.type)
      applySelection(pendingChange.type, pendingChange.value)
    setPendingChange({ type: null, value: null, sttObject: null })
  }

  const cancelPendingChange = () => {
    setPendingChange({ type: null, value: null })
  }

  const handleOpenFeedbackWidget = useCallback(
    (files = null) => {
      dispatch(
        openFeedbackWidget({
          dataType: fileTypeInputValue,
          dataFiles: files || submittedFiles,
          widgetId: `${fileTypeInputValue}-report-submission-feedback`,
        })
      )
    },
    [dispatch, fileTypeInputValue, submittedFiles]
  )

  const resetPiaYear = (type) => {
    // Reset year if it's invalid for the new file type
    // Program Integrity Audit starts at 2024, TANF/SSP/FRA start at 2021
    const currentFiscalYear = getCurrentFiscalYear()
    const minYear =
      type === 'program-integrity-audit'
        ? piaFeatureFlag?.config?.minYear || 2024
        : 2021
    const maxYear =
      type === 'program-integrity-audit'
        ? piaFeatureFlag?.config?.maxYear || 2024
        : currentFiscalYear

    if (yearInputValue && parseInt(yearInputValue) < minYear) {
      setYearInputValue('')
    } else if (
      type === 'program-integrity-audit' &&
      parseInt(yearInputValue) > maxYear
    ) {
      setYearInputValue(`${maxYear}`)
    }
  }

  const applySelection = (type, value) => {
    setUploadAlertState({ active: false, type: null, message: null })
    setProcessingAlertState({ active: false, type: null, message: null })
    if (type === 'fileType') {
      setFileTypeInputValue(value)
      resetPiaYear(value)
      dispatch(clearFileList({ fileType: value }))
      if (isFra || !isTdr) dispatch(reinitializeSubmittedFiles(value))
    } else {
      setSttInputValue(value)
      dispatch(setStt(value))
      dispatch(clearFileList({ fileType: fileTypeInputValue }))
    }
    setFraSelectedFile(null)
  }

  const selectFileType = (value) => {
    setFileTypeTouched(true)
    handleFieldSelection('fileType')

    if (hasUnsubmittedFile) {
      setModalTriggerSource('input-change')
      setPendingChange({ type: 'fileType', value })
      setErrorModalVisible(true)
    } else {
      applySelection('fileType', value)
    }
  }

  const selectYear = ({ target: { value } }) => {
    setYearTouched(true)
    handleFieldSelection('year')
    setYearInputValue(value)
    setUploadAlertState({ active: false, type: null, message: null })
    setProcessingAlertState({ active: false, type: null, message: null })
    if (!hasUnsubmittedFile) {
      dispatch(clearFileList({ fileType: fileTypeInputValue }))
      setFraSelectedFile(null)
    }
  }

  const selectQuarter = ({ target: { value } }) => {
    setQuarterTouched(true)
    handleFieldSelection('quarter')
    setQuarterInputValue(value)
    setUploadAlertState({ active: false, type: null, message: null })
    setProcessingAlertState({ active: false, type: null, message: null })
    if (!hasUnsubmittedFile) {
      dispatch(clearFileList({ fileType: fileTypeInputValue }))
      setFraSelectedFile(null)
    }
  }

  const selectStt = (value, sttObject = null) => {
    setSttTouched(true)
    handleFieldSelection('stt')

    if (hasUnsubmittedFile) {
      setModalTriggerSource('input-change')
      setPendingChange({ type: 'stt', value, sttObject })
      setErrorModalVisible(true)
    } else {
      applySelection('stt', value)
    }
  }

  const handleYearBlur = () => {
    setYearTouched(true)
  }

  const handleQuarterBlur = () => {
    setQuarterTouched(true)
  }

  // Helper to check if order is broken and mark all fields as touched
  const handleFieldSelection = (fieldName) => {
    // Define the correct order with field values
    const fieldOrder = [
      {
        name: 'stt',
        isTouched: () => sttTouched,
        hasValue: () => !canSelectStt || !!sttInputValue,
        isRequired: () => canSelectStt,
      },
      {
        name: 'fileType',
        isTouched: () => fileTypeTouched,
        hasValue: () => !!fileTypeInputValue,
        isRequired: () => true,
      },
      {
        name: 'year',
        isTouched: () => yearTouched,
        hasValue: () => !!yearInputValue,
        isRequired: () => true,
      },
      {
        name: 'quarter',
        isTouched: () => quarterTouched,
        hasValue: () => !!quarterInputValue,
        isRequired: () => true,
      },
    ]

    // Find the index of the current field
    const currentFieldIndex = fieldOrder.findIndex((f) => f.name === fieldName)

    // Check if any required previous fields are empty (regardless of touched state)
    // A field with a value is considered valid even if not explicitly touched
    let orderBroken = false
    for (let i = 0; i < currentFieldIndex; i++) {
      const field = fieldOrder[i]
      if (field.isRequired() && !field.hasValue()) {
        orderBroken = true
        break
      }
    }

    // If order is broken, mark all fields as touched
    if (orderBroken) {
      if (canSelectStt) setSttTouched(true)
      setFileTypeTouched(true)
      setYearTouched(true)
      setQuarterTouched(true)
    }
  }

  // Validation helpers with sequential order enforcement
  // Order: STT (if applicable) -> File Type -> Fiscal Year -> Fiscal Quarter

  const getSttError = () => {
    // Only show error if user can select STT and hasn't selected one
    if (!canSelectStt) return false
    return sttTouched && !sttInputValue
  }

  const getFileTypeError = () => {
    // Show error if:
    // 1. Field was touched and is empty, OR
    // 2. Previous required field (STT) is not filled AND this field was touched
    if (canSelectStt && !sttInputValue) {
      return fileTypeTouched && !fileTypeInputValue
    }
    return fileTypeTouched && !fileTypeInputValue
  }

  const getYearError = () => {
    // Only show error if the field is empty
    if (yearInputValue) return false

    // Show error if field was touched OR any previous required field is invalid
    if (!yearTouched) return false

    return true
  }

  const getQuarterError = () => {
    // Only show error if the field is empty
    if (quarterInputValue) return false

    // Show error if field was touched OR any previous required field is invalid
    if (!quarterTouched) return false

    return true
  }

  const value = {
    effectiveStt: sttResolution.stt,
    sttResolution,
    tdrAssignment,
    uploadScope,
    uploadScopeReady,
    // State
    sttInputValue,
    fileTypeInputValue,
    yearInputValue,
    quarterInputValue,
    errorModalVisible,
    setErrorModalVisible,
    modalTriggerSource,
    setModalTriggerSource,
    reprocessedModalVisible,
    setReprocessedModalVisible,
    reprocessedDate,
    setReprocessedDate,
    uploadAlert,
    setUploadAlertState,
    processingAlert,
    setProcessingAlertState,
    headerRef,
    processingAlertRef,
    uploadAlertRef,

    // FRA-specific state
    fraSelectedFile,
    setFraSelectedFile,
    fraUploadError,
    setFraUploadError,
    isFraSubmissionYearActive,

    // Derived state
    uploadedFiles,
    fraHasUploadedFile,

    // Validation state
    yearTouched,
    quarterTouched,
    fileTypeTouched,
    sttTouched,
    getYearError,
    getQuarterError,
    getFileTypeError,
    getSttError,

    // Actions
    handleClearAll,
    handleClearFilesOnly,
    cancelPendingChange,
    handleOpenFeedbackWidget,
    selectFileType,
    selectYear,
    selectQuarter,
    selectStt,
    handleYearBlur,
    handleQuarterBlur,

    // polling
    startPolling,
    isPolling: visiblePolling,
    stopAllTimers,

    // Program audit
    piaFeatureFlag,
  }

  // Scroll to and focus alert when it becomes active
  useEffect(() => {
    if (uploadAlert.active && uploadAlertRef && uploadAlertRef.current) {
      uploadAlertRef.current.scrollIntoView({ behavior: 'smooth' })
      uploadAlertRef.current.focus({ preventScroll: true })
    }
  }, [uploadAlert, uploadAlertRef])

  // Scroll to processing alert when it becomes active (uses aria-live="polite" for sequential reading)
  useEffect(() => {
    if (
      processingAlert.active &&
      processingAlertRef &&
      processingAlertRef.current
    ) {
      processingAlertRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
    }
  }, [processingAlert, processingAlertRef])

  return (
    <ReportsContext.Provider value={value}>{children}</ReportsContext.Provider>
  )
}
