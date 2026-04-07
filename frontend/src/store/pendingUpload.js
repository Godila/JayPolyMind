/**
 * Temporarily store files and requirements to be uploaded
 * Used to immediately navigate after clicking Start Engine on home page, API call is made on Process page
 */
import { reactive } from 'vue'

const state = reactive({
  files: [],
  simulationRequirement: '',
  enableResearch: false,
  isPending: false
})

export function setPendingUpload(files, requirement, enableResearch = false) {
  state.files = files
  state.simulationRequirement = requirement
  state.enableResearch = enableResearch
  state.isPending = true
}

export function getPendingUpload() {
  return {
    files: state.files,
    simulationRequirement: state.simulationRequirement,
    enableResearch: state.enableResearch,
    isPending: state.isPending
  }
}

export function clearPendingUpload() {
  state.files = []
  state.simulationRequirement = ''
  state.enableResearch = false
  state.isPending = false
}

export default state
