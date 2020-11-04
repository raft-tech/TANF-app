import React from 'react'
import { shallow } from 'enzyme'

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

  // it('should change to a className of display-block', (done) => {
  //   const wrapper = shallow(<IdleTimer />)

  //   const modal = wrapper.find('#myModal')

  //   setTimeout(() => {
  //     console.log('timed out')
  //     expect(modal.hasClass('display-block')).toBeTruthy()
  //     wrapper.unmount()
  //     done()
  //   }, 5000)
  // })

  // it('should setDisplay to true when page is idle for five seconds', (done) => {
  // Cache original functionality
  // const realUseState = React.useState

  // Stub the initial state
  // const stubInitialState = true

  // Mock useState before rendering your component
  // jest
  //   .spyOn(React, 'useState')
  //   .mockImplementationOnce(() => realUseState(stubInitialState))

  // const wrapper = shallow(<IdleTimer />)

  // React.useState(true)

  // setTimeout(() => {
  // expect(React.useState).toHaveBeenCalledTimes(1)
  //   wrapper.unmount()
  //   done()
  // }, 3000)
  // })
})
