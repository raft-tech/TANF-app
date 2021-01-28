import axiosInstance from '../axios-instance'

export const SET_FILE = 'SET_FILE'
export const SET_FILE_ERROR = 'SET_FILE_ERROR'
export const CLEAR_ERROR = 'CLEAR_ERROR'
export const GET_FILE = 'GET_FILE'

export const getFiles = ({ file }) => async (dispatch) => {
  try {
    const URL = `${process.env.REACT_APP_BACKEND_URL}/reports/signed_url/`

    const resp = await axiosInstance.post(URL, {
      file_name: file.fileName,
      file_type: 'text/plain',
      client_method: 'get_object',
    })

    return resp
  } catch (error) {
    console.log('ERROR', error)
    return false
  }
}

export const clearError = ({ section }) => (dispatch) => {
  dispatch({ type: CLEAR_ERROR, payload: { section } })
}

export const upload = ({ file, section }) => async (dispatch) => {
  try {
    const URL = `${process.env.REACT_APP_BACKEND_URL}/reports/signed_url/`

    const resp = await axiosInstance.post(
      URL,
      {
        file_name: file.name,
        file_type: file.type,
        client_method: 'put_object',
      },
      { withCredentials: true }
    )

    if (resp) {
      const signedURL = resp.data.signed_url
      const options = {
        headers: {
          'Content-Type': file.type,
        },
      }

      await axiosInstance.put(signedURL, file, options)

      dispatch({
        type: SET_FILE,
        payload: {
          fileName: file.name,
          section,
        },
      })
    } else {
      console.log('THAT DIDN"T WORK')
    }
  } catch (error) {
    console.log('ERROR', error)
    dispatch({ type: SET_FILE_ERROR, payload: { error, section } })
    return false
  }

  return true
}

export const SET_YEAR = 'SET_YEAR'

export const setYear = (year) => (dispatch) => {
  dispatch({ type: SET_YEAR, payload: { year } })
}
