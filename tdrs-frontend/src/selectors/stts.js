import { selectUser, accountIsRegionalStaff } from './auth'

export const findProgramParticipation = (stt, programSlug) => {
  if (!Array.isArray(stt?.program_participations)) {
    return null
  }

  return (
    stt.program_participations.find(
      (participation) => participation?.program?.slug === programSlug
    ) || null
  )
}

export const canViewSsp = (stt) => {
  const status = findProgramParticipation(stt, 'ssp')?.status
  return status === 'ACTIVE' || status === 'FORMER'
}

export const canSubmitSsp = (stt) => {
  return findProgramParticipation(stt, 'ssp')?.status === 'ACTIVE'
}

export const availableStts = (path) => {
  return (state) => {
    const filterTribes = (stts = []) => {
      if (path.includes('fra')) {
        return stts.filter((stt) => stt.type !== 'tribe')
      }
      return stts
    }

    if (accountIsRegionalStaff(state)) {
      const regionalStts =
        selectUser(state)
          .regions?.map((region) => region.stts)
          .flat() || []
      return filterTribes(regionalStts).sort((a, b) =>
        a.name.localeCompare(b.name)
      )
    }

    return filterTribes(state?.stts?.sttList || [])
  }
}
