import { useEffect, useRef } from 'react'
import { useDispatch, useSelector, useStore } from 'react-redux'
import { v4 as uuidv4 } from 'uuid'
import {
  getAvailableFileList,
  getTanfSubmissionStatus,
  SET_TANF_SUBMISSION_STATUS,
  INVALIDATE_FILE_LIST,
} from '../actions/reports'
import { getHistoryQueryKey, sameHistoryScope } from '../utils/reportScopes'
import { useReportsContext } from '../components/Reports/ReportsContext'

const EMPTY_FILES = []

/**
 * Custom hook that encapsulates shared submission history logic
 * Used by both QuarterSubmissionHistory and SectionSubmissionHistory
 *
 * @param {Object} filterValues - Filter values for fetching files
 * @param {Object} options - Opt into scoped requests; enabled=false clears the query
 * @returns {Object} Files and fetch state
 */
export const useSubmissionHistory = (
  filterValues,
  { scoped = false, enabled = true } = {}
) => {
  const dispatch = useDispatch()
  const store = useStore()
  const reports = useSelector((state) => state.reports)
  const desiredKey = scoped && enabled ? getHistoryQueryKey(filterValues) : null
  const filtersRef = useRef(filterValues)
  filtersRef.current = filterValues
  const queryRef = useRef(null)
  if (queryRef.current?.key !== desiredKey) {
    if (queryRef.current) queryRef.current.active = false
    queryRef.current = { key: desiredKey, active: true }
  }
  const files =
    !scoped || (desiredKey && reports.historyScope?.key === desiredKey)
      ? reports.files
      : EMPTY_FILES
  const loading =
    scoped && reports.historyScope?.key !== desiredKey
      ? Boolean(desiredKey)
      : reports.loading
  const prevFilterValuesRef = useRef()
  const { isPolling, startPolling } = useReportsContext()
  const isPollingRef = useRef(isPolling)
  const startPollingRef = useRef(startPolling)

  useEffect(() => {
    isPollingRef.current = isPolling
  }, [isPolling])

  useEffect(() => {
    startPollingRef.current = startPolling
  }, [startPolling])

  useEffect(() => {
    // Serialize filterValues for comparison
    if (scoped) return
    const currentFilters = JSON.stringify(filterValues)
    const prevFilters = prevFilterValuesRef.current

    // Fetch if this is the first render or if filterValues have changed
    if (!prevFilters && Object.keys(isPolling).some((k) => !isPolling[k])) {
      return
    } else if (!prevFilters || currentFilters !== prevFilters) {
      dispatch(getAvailableFileList(filterValues))
      prevFilterValuesRef.current = currentFilters
    }
  }, [dispatch, filterValues, isPolling, scoped])

  useEffect(() => {
    if (!scoped || !desiredKey) return
    const query = queryRef.current
    query.active = true
    const historyScope = { key: desiredKey, requestId: uuidv4() }
    dispatch(
      getAvailableFileList(filtersRef.current, undefined, {
        scoped: true,
        requestId: historyScope.requestId,
        isCurrent: () => query.active,
      })
    )
    return () => {
      query.active = false
      dispatch({ type: INVALIDATE_FILE_LIST, payload: { historyScope } })
    }
  }, [dispatch, desiredKey, scoped])

  // Restart polling for any pending files when history is loaded (e.g., after navigation)
  useEffect(() => {
    if (scoped) return
    files
      ?.filter((file) => file?.summary?.status === 'Pending')
      ?.forEach((file) => {
        if (isPollingRef.current?.[file.id]) return

        startPollingRef.current(
          `${file.id}`,
          () => getTanfSubmissionStatus(file.id),
          (response) => {
            const status = response?.data?.summary?.status
            return status && status !== 'Pending'
          },
          (response) => {
            dispatch({
              type: SET_TANF_SUBMISSION_STATUS,
              payload: {
                datafile_id: file.id,
                datafile: response?.data,
              },
            })
          },
          () => {
            // Silent failure to avoid noisy alerts on navigation-driven polling
          },
          () => {
            // Timed out; leave status as-is and let user refresh manually
          }
        )
      })
  }, [dispatch, files, scoped])

  useEffect(() => {
    if (!scoped || !desiredKey || !files?.length) return
    const query = queryRef.current
    const historyScope = reports.historyScope
    const isCurrent = () =>
      query.active &&
      sameHistoryScope(store.getState().reports.historyScope, historyScope)
    const cancellations = files
      .filter((file) => file?.summary?.status === 'Pending')
      .map((file) =>
        startPollingRef.current(
          `${historyScope.requestId}:${file.id}`,
          () => getTanfSubmissionStatus(file.id),
          (response) =>
            Boolean(
              response?.data?.summary?.status &&
              response.data.summary.status !== 'Pending'
            ),
          (response) => {
            if (isCurrent())
              dispatch({
                type: SET_TANF_SUBMISSION_STATUS,
                payload: {
                  datafile_id: file.id,
                  datafile: response.data,
                  historyScope,
                },
              })
          },
          () => {},
          () => {},
          undefined,
          undefined,
          { isCurrent }
        )
      )
    return () => cancellations.forEach((cancel) => cancel?.())
  }, [dispatch, desiredKey, files, reports.historyScope, scoped, store])

  return {
    files,
    loading,
  }
}
