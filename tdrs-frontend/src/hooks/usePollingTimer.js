import { useCallback, useEffect, useRef, useState } from 'react'

const WAIT_TIME = 2000
const MAX_TRIES = 30

export const usePollingTimer = () => {
  const timers = useRef({})
  const generations = useRef({})
  const [pollState, setPollState] = useState({})

  // settimeout uses state from the time it was scheduled, not the time it executes
  // so we MUST use the state setter callback
  const setPollStateForRequest = (requestId, changes = {}) =>
    setPollState((prevState) => ({
      ...prevState,
      [`${requestId}`]: {
        ...prevState[requestId],
        ...changes,
      },
    }))

  const addTimer = (requestId, timer) => {
    timers.current[requestId] = timer
  }

  const stopTimer = (requestId, deleteRef = true) => {
    clearTimeout(timers.current[requestId])

    if (deleteRef) {
      delete timers.current[requestId]
    }
  }

  const reset = (requestId) => {
    setPollStateForRequest(requestId, {
      isDonePolling: false,
      isPerformingRequest: false,
    })
  }

  const start = (requestId) => {
    setPollStateForRequest(requestId, {
      isDonePolling: false,
      isPerformingRequest: true,
    })
  }

  const finish = (requestId, then = () => null) => {
    setPollStateForRequest(requestId, {
      isDonePolling: true,
      isPerformingRequest: false,
    })
    stopTimer(requestId)
    then()
  }

  const poll = async (
    requestId,
    tryNumber = 1,
    request,
    test,
    onSuccess,
    onError,
    onTimeout,
    wait_time = WAIT_TIME,
    max_tries = MAX_TRIES,
    isCurrent = () => true
  ) => {
    if (!isCurrent()) return
    if (tryNumber > max_tries) {
      finish(requestId, () => onTimeout(onError))
      return
    }

    const retry = () => {
      if (!isCurrent()) return
      setPollStateForRequest(requestId, {
        isPerformingRequest: false,
        isDonePolling: false,
      })
      poll(
        requestId,
        tryNumber + 1,
        request,
        test,
        onSuccess,
        onError,
        onTimeout,
        wait_time,
        max_tries,
        isCurrent
      )
    }

    const fetchAndTest = async () => {
      if (!isCurrent()) return
      let response = null

      start(requestId)

      try {
        response = await request()
      } catch (networkError) {
        if (!isCurrent()) return
        retry(requestId, tryNumber)
        return
      }
      if (!isCurrent()) return

      if (!response.ok) {
        const statusCode = response.status
        const shouldStopPolling =
          statusCode === 400 || statusCode === 401 || statusCode === 403

        if (!shouldStopPolling) {
          retry(requestId, tryNumber)
          return
        } else {
          finish(requestId, () =>
            onError(response.error || new Error(`HTTP ${statusCode}`))
          )
          return
        }
      }

      let result = test(response)

      if (result) {
        finish(requestId, () => onSuccess(response))
        return
      } else {
        retry()
        return
      }
    }

    let timeout = setTimeout(fetchAndTest, tryNumber === 1 ? 0 : wait_time)
    addTimer(requestId, timeout)
  }

  /**
   * Start polling the provided request function with give intervals and result steps.
   * @param {Number} requestId - the id to track for multiple independent timers
   * @param {Function} request - an axios request to poll
   * @param {Function} test - takes the axios response and returns a boolean indicating whether to continue polling
   * @param {Function} onSuccess - called when `test` returns true
   * @param {Function} onError - called when `request` throws an exception
   * @param {Function} onTimeout - called when the number of tries exceeds `max_tries`
   * @param {Number} wait_time - the time to wait in ms
   * @param {Number} max_tries - the number of requests to try before calling `onTimeout`
   * @param {Object} options - Optional isCurrent guard for requests and callbacks
   * @returns {Function} Cancel this polling generation, including in-flight callbacks
   */
  const startPolling = (
    requestId,
    request,
    test,
    onSuccess,
    onError,
    onTimeout,
    wait_time = WAIT_TIME,
    max_tries = MAX_TRIES,
    options = {}
  ) => {
    if (requestId in timers.current) stopTimer(requestId)
    const generation = {}
    generations.current[requestId] = generation
    // A cleared timeout cannot cancel its already-running request.
    const isCurrent = () => {
      if (generations.current[requestId] !== generation) return false
      if (options.isCurrent?.() === false) {
        delete generations.current[requestId]
        finish(requestId)
        return false
      }
      return true
    }
    reset(requestId)
    poll(
      requestId,
      1,
      request,
      test,
      onSuccess,
      onError,
      onTimeout,
      wait_time,
      max_tries,
      isCurrent
    )
    return () => {
      if (generations.current[requestId] === generation) {
        delete generations.current[requestId]
        finish(requestId)
      }
    }
  }

  const stopAllTimers = useCallback(() => {
    generations.current = {}
    const timer = timers.current
    if (timer && Object.keys(timer).length !== 0) {
      Object.keys(timers.current).forEach((requestId) =>
        stopTimer(requestId, false)
      )
      setPollState({})
    }
  }, [timers])

  const isPolling = {}
  Object.keys(pollState).forEach((t) => {
    isPolling[t] =
      !pollState[t].isDonePolling || pollState[t].isPerformingRequest
  })

  useEffect(() => {
    const onUnmount = () => stopAllTimers()
    return onUnmount
  }, [timers, stopAllTimers])

  return { startPolling, isPolling, stopAllTimers }
}
