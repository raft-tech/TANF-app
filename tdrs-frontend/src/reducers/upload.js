import { SET_FILE, SET_FILE_ERROR, SET_YEAR } from '../actions/upload'

const initialState = {
  file: null,
  error: null,
  year: 2020,
}

const upload = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case SET_FILE:
      return { ...state, file: payload }
    case SET_FILE_ERROR: {
      const { error } = payload
      return { ...initialState, error }
    }
    case SET_YEAR: {
      const { year } = payload
      return { ...state, year }
    }
    default:
      return state
  }
}

export default upload
