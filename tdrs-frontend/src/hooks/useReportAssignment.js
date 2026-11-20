import { useMemo } from 'react'
import { useSelector } from 'react-redux'
import { accountCanSelectStt, accountIsRegionalStaff } from '../selectors/auth'
import { resolveReportStt } from '../selectors/stts'
import { getTdrAssignment } from '../utils/reportSections'
import { getUploadAssignmentKey } from '../utils/reportScopes'

/** Selection state and upload lifecycle remain owned by the reports provider. */
export const useReportAssignment = ({
  selectedSttName,
  fileType,
  piaEnabled = false,
}) => {
  const canSelectStt = useSelector(accountCanSelectStt)
  const isRegionalStaff = useSelector(accountIsRegionalStaff)
  const user = useSelector((state) => state.auth.user)
  const sttState = useSelector((state) => state.stts)

  const sttResolution = useMemo(
    () =>
      resolveReportStt({
        user,
        canSelectStt,
        isRegionalStaff,
        catalog: sttState,
        selectedName: selectedSttName,
      }),
    [user, canSelectStt, isRegionalStaff, sttState, selectedSttName]
  )

  const tdrAssignment = useMemo(
    () => getTdrAssignment(sttResolution, fileType, piaEnabled),
    [sttResolution, fileType, piaEnabled]
  )

  const configuration = useMemo(
    () => ({
      sttId: sttResolution.stt?.id || null,
      program: tdrAssignment.program || { id: null, slug: null },
      sections: tdrAssignment.sections,
    }),
    [sttResolution.stt?.id, tdrAssignment.program, tdrAssignment.sections]
  )

  return {
    canSelectStt,
    sttList: sttState?.sttList,
    sttResolution,
    tdrAssignment,
    configuration,
    assignmentKey: getUploadAssignmentKey(configuration),
  }
}
