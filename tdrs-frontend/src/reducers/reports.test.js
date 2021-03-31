import reducer, { getUpdatedFiles } from './reports'
import {
  CLEAR_ERROR,
  SET_FILE,
  CLEAR_FILE,
  SET_FILE_ERROR,
  SET_YEAR,
} from '../actions/reports'

const initialState = {
  files: [
    {
      section: 'Active Case Data',
      fileName: null,
      error: null,
    },
    {
      section: 'Closed Case Data',
      fileName: null,
      error: null,
    },
    {
      section: 'Aggregate Data',
      fileName: null,
      error: null,
    },
    {
      section: 'Stratum Data',
      fileName: null,
      error: null,
    },
  ],
  year: 2020,
}

describe('reducers/reports', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual(initialState)
  })

  it('should handle SET_FILE', () => {
    expect(
      reducer(undefined, {
        type: SET_FILE,
        payload: {
          fileName: 'Test.txt',
          section: 'Stratum Data',
        },
      })
    ).toEqual({
      files: [
        {
          section: 'Active Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Stratum Data',
          fileName: 'Test.txt',
          error: null,
        },
      ],
      year: 2020,
    })
  })

  it('should handle CLEAR_FILE', () => {
    expect(
      reducer(undefined, {
        type: CLEAR_FILE,
        payload: {
          section: 'Stratum Data',
        },
      })
    ).toEqual({
      files: [
        {
          section: 'Active Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Stratum Data',
          fileName: null,
          error: null,
        },
      ],
      year: 2020,
    })
  })

  it('should handle SET_FILE_ERROR', () => {
    const fakeError = new Error({ message: 'something went wrong' })
    expect(
      reducer(undefined, {
        type: SET_FILE_ERROR,
        payload: {
          error: fakeError,
          section: 'Stratum Data',
        },
      })
    ).toEqual({
      files: [
        {
          section: 'Active Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Stratum Data',
          fileName: null,
          error: fakeError,
        },
      ],
      year: 2020,
    })
  })

  it('should handle CLEAR_ERROR', () => {
    const fakeError = new Error({ message: 'something went wrong' })
    expect(
      reducer(
        {
          files: [
            {
              section: 'Active Case Data',
              fileName: null,
              error: null,
            },
            {
              section: 'Closed Case Data',
              fileName: null,
              error: null,
            },
            {
              section: 'Aggregate Data',
              fileName: null,
              error: null,
            },
            {
              section: 'Stratum Data',
              fileName: null,
              error: fakeError,
            },
          ],
          year: 2020,
        },
        {
          type: CLEAR_ERROR,
          payload: {
            section: 'Stratum Data',
          },
        }
      )
    ).toEqual({
      files: [
        {
          section: 'Active Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Stratum Data',
          fileName: null,
          error: null,
        },
      ],
      year: 2020,
    })
  })

  it('should handle "SET_YEAR"', () => {
    expect(
      reducer(undefined, {
        type: SET_YEAR,
        payload: {
          year: 2021,
        },
      })
    ).toEqual({
      files: initialState.files,
      year: 2021,
    })
  })

  it('should be able to update files with a new value and return those files', () => {
    const state = initialState

    const updatedFiles = getUpdatedFiles(state, 'Test.txt', 'Active Case Data')

    expect(updatedFiles).toStrictEqual([
      {
        section: 'Active Case Data',
        fileName: 'Test.txt',
        error: null,
      },
      {
        section: 'Closed Case Data',
        fileName: null,
        error: null,
      },
      {
        section: 'Aggregate Data',
        fileName: null,
        error: null,
      },
      {
        section: 'Stratum Data',
        fileName: null,
        error: null,
      },
    ])
  })
})
