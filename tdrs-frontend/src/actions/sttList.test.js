import { get } from '../fetch-instance'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import {
  createParticipationStt,
  createProgramParticipation,
} from '../test-utils/programParticipation'
import sttListReducer from '../reducers/sttList'

import {
  fetchSttList,
  FETCH_STTS,
  SET_STTS,
  SET_STTS_ERROR,
  CLEAR_STTS,
} from './sttList'

jest.mock('../fetch-instance')

describe('actions/stts.js', () => {
  const mockStore = configureStore([thunk])

  it('retains nested participation metadata through fetch and reducer storage', async () => {
    const data = [
      createParticipationStt({
        program_participations: [
          createProgramParticipation({
            sectionNames: ['Aggregate Data', 'Active Case Data'],
          }),
          createProgramParticipation({
            id: 502,
            programSlug: 'ssp',
            sectionNames: [],
          }),
        ],
      }),
      createParticipationStt({
        id: 58,
        type: 'tribe',
        program_participations: [
          createProgramParticipation({
            id: 503,
            programSlug: 'tribal',
            sectionNames: ['Closed Case Data'],
          }),
        ],
      }),
    ]
    get.mockResolvedValueOnce({ data, ok: true })
    const store = mockStore()

    await store.dispatch(fetchSttList())

    expect(get).toHaveBeenLastCalledWith(
      `${process.env.REACT_APP_BACKEND_URL}/stts/alpha`
    )
    expect(store.getActions()).toEqual([
      { type: FETCH_STTS },
      { type: SET_STTS, payload: { data } },
    ])
    const state = store.getActions().reduce(sttListReducer, undefined)
    expect(state).toEqual({ sttList: data, loading: false, loaded: true })
    expect(
      state.sttList[0].program_participations[0].sections.map((s) => s.name)
    ).toEqual(['Aggregate Data', 'Active Case Data'])
    expect(state.sttList[0].program_participations[1].sections).toEqual([])
    expect(state.sttList[1].program_participations[0].program.slug).toBe(
      'tribal'
    )
  })

  it('fetches a list of stts, when the user is authenticated', async () => {
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: [{ id: 1, type: 'state', code: 'AL', name: 'Alabama' }],
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchSttList())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(SET_STTS)
    expect(actions[1].payload.data).toStrictEqual([
      { id: 1, type: 'state', code: 'AL', name: 'Alabama' },
    ])
  })

  it('fetches a list of stts and puts "Federal Government" as the first option if it exists, when the user is authenticated', async () => {
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: [
          { id: 1, type: 'state', code: 'AL', name: 'Alabama' },
          {
            id: 57,
            type: 'territory',
            code: 'US',
            name: 'Federal Government',
          },
        ],
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchSttList())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(SET_STTS)
    expect(actions[1].payload.data).toStrictEqual([
      {
        id: 57,
        type: 'territory',
        code: 'US',
        name: 'Federal Government',
      },
      { id: 1, type: 'state', code: 'AL', name: 'Alabama' },
    ])
  })

  it('clears the stt state, if user is not authenticated', async () => {
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: null,
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchSttList())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(CLEAR_STTS)
  })

  it('dispatches an error to the store if the API errors', async () => {
    const mockError = new Error('something went wrong')
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: null,
        ok: false,
        status: 500,
        error: mockError,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchSttList())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(SET_STTS_ERROR)
    expect(actions[1].payload).toStrictEqual({
      error: mockError,
    })
  })
})
