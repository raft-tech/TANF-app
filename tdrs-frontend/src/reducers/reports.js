import {
  SET_FILE,
  SET_FILE_ERROR,
  CLEAR_ERROR,
  SET_YEAR,
} from '../actions/reports'

const getUpdatedFiles = (state, file, name, error) => {
  const oldFileIndex = state.files.findIndex(
    (currentFile) => currentFile.name === name
  )
  const updatedFiles = [...state.files]
  updatedFiles[oldFileIndex] = {
    name,
    file,
    error,
  }

  return updatedFiles
}

const initialState = {
  files: [
    {
      name: 'Active Case Data',
      file: null,
      error: null,
    },
    {
      name: 'Closed Case Data',
      file: null,
      error: null,
    },
    {
      name: 'Aggregate Data',
      file: null,
      error: null,
    },
    {
      name: 'Stratum Data',
      file: null,
      error: null,
    },
  ],
  year: 2020,
}

const reports = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case SET_FILE: {
      const { file, name } = payload
      const updatedFiles = getUpdatedFiles(state, file, name)
      return { ...state, files: updatedFiles }
    }
    case SET_FILE_ERROR: {
      const { error, name } = payload
      const updatedFiles = getUpdatedFiles(state, null, name, error)
      return { ...initialState, files: updatedFiles }
    }
    case CLEAR_ERROR: {
      const { name } = payload
      const updatedFiles = getUpdatedFiles(state, null, name, null)
      return { ...state, files: updatedFiles }
    }
    case SET_YEAR: {
      const { year } = payload
      return { ...state, year }
    }
    default:
      return state
  }
}

export default reports
