import axios from 'axios'

export const SET_FILE = 'SET_FILE'
export const SET_FILE_ERROR = 'SET_FILE_ERROR'

export const upload = ({ file }) => async (dispatch) => {
  try {
    const URL =
      's3://AKIAR7FXZINYNGDGPPZ5:WZace4tXL97nyBsiAA8RiZsvey4h9QBzepIAEdD8@s3-us-gov-west-1.amazonaws.com/cg-f073b546-cf1c-4960-845f-746318ebc15e'
    const resp = await axios.post(URL, file, {
      access_key_id: 'AKIAR7FXZINYNGDGPPZ5',
      secret_access_key: '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',
      region: 'us-gov-west-1',
      bucket: 'cg-f073b546-cf1c-4960-845f-746318ebc15e',
    })

    if (resp) {
      dispatch({ type: SET_FILE, file: resp })
    } else {
      console.log('NO RESPONSE')
    }
  } catch (error) {
    dispatch({ type: SET_FILE_ERROR, payload: { error } })
  }
}

export const SET_YEAR = 'SET_YEAR'

export const setYear = (year) => (dispatch) => {
  dispatch({ type: SET_YEAR, payload: { year } })
}
