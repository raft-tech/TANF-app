import { SET_FILE } from '../actions/upload'

const initialState = {
  file: null,
}

const upload = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case SET_FILE: {
      return { ...state, file: payload }
    }
    default:
      return state
  }
}

export default upload
