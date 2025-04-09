import {odinApi} from 'boot/axios';

export default {
  postWorkflow(intentID, data) {
    return odinApi.post('/intent/' + intentID + '/workflow', data)
  },
  /* putWorkflow(projectID, intentID, workflowID, data) {
    return odinApi.put('/project/' + projectID + '/intent/' + intentID + '/workflow/' + workflowID, data)
  }, */
  deleteWorkflow(intentName, workflowName) {
    return odinApi.delete('/intent/' + intentName + '/workflow/' + workflowName)
  },
/*   downloadWorkflowSchema(projectID, intentID, workflowID) {
    return odinApi.get('/project/' + projectID + '/intent/' + intentID + '/workflow/' + workflowID + '/schema', {responseType: 'blob'})
  }, */
}
