import { useEffect, useRef, useState } from 'react'

/**
 * Custom hook to manage form submission state and prevent multiple submissions
 * @param {string} scopeKey - Optional generation isolating submitting state
 * @returns {Object} Form submission utilities
 */
export const useFormSubmission = (scopeKey) => {
  const [submission, setSubmission] = useState({ scopeKey, active: false })
  const currentScopeRef = useRef(scopeKey)
  const requestRef = useRef(null)
  const mountedRef = useRef(true)
  if (currentScopeRef.current !== scopeKey) {
    currentScopeRef.current = scopeKey
    requestRef.current = null
  }
  const isSubmitting = submission.scopeKey === scopeKey && submission.active
  const setIsSubmitting = (active) => setSubmission({ scopeKey, active })
  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
    }
  }, [])

  /**
   * Execute a submission with proper state management
   * @param {Function} submitFn - The function to execute for submission
   * @param {Object} options - Additional options
   * @param {Function} options.onSuccess - Optional callback for success
   * @param {Function} options.onError - Optional callback for error
   * @returns {Promise} The result of the submission function
   */
  const executeSubmission = async (submitFn, options = {}) => {
    // Prevent multiple submissions
    if (isSubmitting || requestRef.current) {
      return
    }

    // Set submitting state to true
    setIsSubmitting(true)
    const request = {}
    requestRef.current = request
    const isCurrent = () =>
      mountedRef.current &&
      requestRef.current === request &&
      (options.isCurrent?.() ?? true)

    try {
      // Execute the submission function
      const result = await submitFn()

      // Call success callback if provided
      if (isCurrent() && options.onSuccess) {
        options.onSuccess(result)
      }
      return result
    } catch (error) {
      // Call error callback if provided
      if (isCurrent() && options.onError) {
        options.onError(error)
      }
      // Re-throw the error for further handling
      throw error
    } finally {
      // Reset submitting state
      if (mountedRef.current && requestRef.current === request) {
        requestRef.current = null
        setIsSubmitting(false)
      }
    }
  }

  return {
    isSubmitting,
    executeSubmission,
    onSubmitStart: () => setIsSubmitting(true),
    onSubmitComplete: () => setIsSubmitting(false),
  }
}
