export const SET_FILE = 'SET_FILE'

export const upload = ({ file }) => async (dispatch) => {
  dispatch({ type: SET_FILE, payload: file })
}
