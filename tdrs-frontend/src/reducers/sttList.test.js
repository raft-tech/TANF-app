import reducer from './sttList'
import {
  createParticipationStt,
  createProgramParticipation,
} from '../test-utils/programParticipation'
import {
  FETCH_STTS,
  SET_STTS,
  SET_STTS_ERROR,
  CLEAR_STTS,
} from '../actions/sttList'

describe('reducers/stts', () => {
  it('stores exact nested assignments, including empty and absent participations', () => {
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
      createParticipationStt({ id: 2 }),
    ]
    const before = JSON.stringify(data)
    const state = reducer(undefined, { type: SET_STTS, payload: { data } })
    expect(state).toEqual({ sttList: data, loading: false, loaded: true })
    expect(JSON.stringify(state.sttList)).toBe(before)
    expect(state.sttList[0].program_participations[0].sections).toHaveLength(2)
    expect(state.sttList[0].program_participations[1].sections).toEqual([])
    expect(state.sttList[1].program_participations).toEqual([])
  })

  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      sttList: [],
      loading: false,
      loaded: false,
    })
  })

  it('should handle FETCH_STTS', () => {
    expect(
      reducer(undefined, {
        type: FETCH_STTS,
      })
    ).toEqual({
      sttList: [],
      loading: true,
      loaded: false,
    })
  })

  it('should handle SET_STTS', () => {
    expect(
      reducer(
        {
          sttList: [],
          loading: true,
        },
        {
          type: SET_STTS,
          payload: {
            data: [{ id: 1, type: 'state', code: 'AL', name: 'Alabama' }],
          },
        }
      )
    ).toEqual({
      sttList: [{ id: 1, type: 'state', code: 'AL', name: 'Alabama' }],
      loading: false,
      loaded: true,
    })
  })

  it('should handle CLEAR_STTS', () => {
    expect(
      reducer(
        {
          sttList: [{ value: 'alabama', label: 'Alabama' }],
          loading: false,
        },
        {
          type: CLEAR_STTS,
        }
      )
    ).toEqual({
      sttList: [],
      loading: false,
      loaded: false,
    })
  })

  it('should handle SET_STTS_ERROR when user logged out', () => {
    expect(
      reducer(undefined, {
        type: SET_STTS_ERROR,
        payload: { error: 'something went wrong' },
      })
    ).toEqual({
      sttList: [],
      loading: false,
      loaded: false,
      error: 'something went wrong',
    })
  })
})
