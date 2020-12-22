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
    const URL = `${process.env.REACT_APP_BACKEND_URL}/reports/signed_url/`

    const resp = await axios.post(URL, {
      file_name: file.name,
      file_type: file.type,
    })

    if (resp) {
      const signedURL = resp.data.signed_url
      const options = {
        headers: {
          'Content-Type': file.type,
        },
      }

      const result = await axios.post(signedURL, file, options)

      console.log('RESULT', result)
      // dispatch({
      //   type: SET_FILE,
      //   payload: {
      //     file,
      //     name,
      //   },
      // })
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
