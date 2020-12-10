import axios from 'axios'

export const SET_FILE = 'SET_FILE'
export const SET_FILE_ERROR = 'SET_FILE_ERROR'
export const CLEAR_ERROR = 'CLEAR_ERROR'

export const clearError = ({ name }) => (dispatch) => {
  dispatch({ type: CLEAR_ERROR, payload: { name } })
}

// process.env.REACT_APP_ACCESS_KEY_ID and
// process.env.SECRET_ACCESS_KEY need to be defined in your .env.local file.

export const upload = ({ file, name }) => async (dispatch) => {
  try {
    const URL = 'https://s3-us-gov-west-1.amazonaws.com'

    const resp = await axios.post(URL, file, {
      headers: {
        access_key_id: process.env.REACT_APP_ACCESS_KEY_ID,
        secret_access_key: process.env.SECRET_ACCESS_KEY,
        region: 'us-gov-west-1',
        bucket: 'cg-f073b546-cf1c-4960-845f-746318ebc15e',
      },
    })

    if (resp) {
      dispatch({
        type: SET_FILE,
        payload: {
          file,
          name,
        },
      })
    } else {
      console.log('NO RESPONSE')
    }
  } catch (error) {
    dispatch({ type: SET_FILE_ERROR, payload: { error, name } })
    return false
  }

  return true
}

export const SET_YEAR = 'SET_YEAR'

export const setYear = (year) => (dispatch) => {
  dispatch({ type: SET_YEAR, payload: { year } })
}
