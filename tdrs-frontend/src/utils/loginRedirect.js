const LOGIN_DESTINATION_KEY = 'loginDestination'

/** @param {string} destination */
export const saveLoginDestination = (destination) => {
  try {
    // Keep destinations separate between tabs and across the IdP round trip.
    window.sessionStorage.setItem(LOGIN_DESTINATION_KEY, destination)
  } catch {
    // Sign-in must still work when browser storage is unavailable.
  }
}

/** @returns {string} A local destination, or the usual landing page. */
export const getLoginDestination = () => {
  try {
    const destination = window.sessionStorage.getItem(LOGIN_DESTINATION_KEY)
    if (!destination?.startsWith('/') || destination.startsWith('//')) {
      return '/home'
    }

    const url = new URL(destination, window.location.origin)
    const pathname = decodeURIComponent(url.pathname).replace(/\/+$/, '')
    if (
      url.origin !== window.location.origin ||
      destination.includes('\\') ||
      !pathname ||
      pathname.toLowerCase() === '/login'
    ) {
      return '/home'
    }

    return destination
  } catch {
    return '/home'
  }
}

export const clearLoginDestination = () => {
  try {
    window.sessionStorage.removeItem(LOGIN_DESTINATION_KEY)
  } catch {
    // Sign-in must still work when browser storage is unavailable.
  }
}
