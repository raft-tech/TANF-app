import { applyMiddleware, createStore } from 'redux'
import { thunk } from 'redux-thunk'
import reports from '../reducers/reports'
import { BEGIN_FILE_VALIDATION, upload } from '../actions/reports'
import { createProgramParticipation } from './programParticipation'

export const deferred = () => {
  let resolve
  let reject
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise
    reject = rejectPromise
  })
  return { promise, resolve, reject }
}

export const createReportsStore = () =>
  createStore(
    (state = {}, action) => ({
      reports: reports(state.reports, action),
      auth: { user: { id: 1, roles: [] } },
    }),
    applyMiddleware(thunk)
  )

export const uploadConfiguration = ({
  sttId = 1,
  programSlug = 'tanf',
  sectionNames = ['Aggregate Data'],
} = {}) => {
  const { program, sections } = createProgramParticipation({
    programSlug,
    sectionNames,
  })
  return { sttId, program, sections }
}

export const stageScopedFile = (
  store,
  uploadScope,
  uuid = 'file-a',
  descriptor = uploadScope.sections[0]
) => {
  const file = new File(['HEADER'], `${uuid}.txt`, { type: 'text/plain' })
  const identity = {
    uploadScope,
    section: descriptor.name,
    sectionId: descriptor.id,
    program: descriptor.program,
    uuid,
  }
  store.dispatch({
    type: BEGIN_FILE_VALIDATION,
    payload: { ...identity, file, fileName: file.name },
  })
  store.dispatch(upload({ ...identity, file, year: '2024', quarter: 'Q1' }))
  return store
    .getState()
    .reports.submittedFiles.find((slot) => slot.uuid === uuid)
}
