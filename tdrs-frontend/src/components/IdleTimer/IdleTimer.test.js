import React from 'react'
import { shallow } from 'enzyme'
import { render } from '@testing-library/react'

import { act } from 'react-dom/test-utils'
import IdleTimer from './IdleTimer'

describe('IdleTimer', () => {
  it('should have a modal with an id of "myModal"', () => {
    const wrapper = shallow(<IdleTimer />)

    const modal = wrapper.find('#myModal')

    expect(modal).toExist()
  })

  it('should start with a className of display-none', () => {
    const wrapper = shallow(<IdleTimer />)

    const modal = wrapper.find('#myModal')

    expect(modal.hasClass('display-none')).toBeTruthy()
  })

  it('should change to a className of display-block after 2 seconds', () => {
    jest.useFakeTimers()
    const { container } = render(<IdleTimer />)

    const modal = container.querySelector('#myModal')

    act(() => {
      jest.runAllTimers()
    })

    expect(modal.classList.contains('display-block')).toBeTruthy()
  })
})
