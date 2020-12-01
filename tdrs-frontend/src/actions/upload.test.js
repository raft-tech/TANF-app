import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'

import { upload, SET_FILE } from './upload'

describe('actions/upload.js', () => {
  const mockStore = configureStore([thunk])

  it('should dispatch SET_FILE', async () => {
    const store = mockStore()

    await store.dispatch(upload({ file: 'HELLO' }))

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_FILE)
    expect(actions[0].payload).toStrictEqual('HELLO')
  })
})
