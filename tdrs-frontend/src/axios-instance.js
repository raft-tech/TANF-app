import axios from 'axios'
import tough from 'tough-cookie'
import axiosCookieJarSupport from 'axios-cookiejar-support'
axiosCookieJarSupport(axios)

// Need a custom instance of axios so we can set the csrf keys on auth_check
// Work around for csrf cookie issue we encountered in production.
// It may still be possible to do this with a cookie, and something on the
// frontend (most likely) is misconfigured. the configuration has alluded
// us thus far, and this implementation is functionally equivalent to
// using cookies.
export default axios.create({
  jar:new tough.CookieJar(),
  withCredentials:true
})
