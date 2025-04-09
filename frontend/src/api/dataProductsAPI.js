import {odinApi} from 'boot/axios';

export default {
  getDataProducts() {
    return odinApi.get('/data-products')
  },  
/*   materializeDataProduct(projectID, dataProductID) {
    return odinApi.post('/project/' + projectID + '/data-product/' + dataProductID + '/materialize')
  }, */
/*   postDataProduct(projectID, data) {
    return odinApi.post('/project/' + projectID + '/data-product', data)
  }, */
  deleteDataProduct(fileName) {
    return odinApi.delete('/data-product/' +  fileName)
  },
/*   putDataProduct(projectID, dataProductID, data) {
    return odinApi.put('/project/' + projectID + '/data-product/' +  dataProductID, data)
  }, */
/*   downloadTemporalDataProduct(projectID, dataProductUUID) {
    return odinApi.post('/project/' + projectID + '/download-temporal-data-product/' +  dataProductUUID)
  }, */
  downloadDataProduct(fileName) {
    return odinApi.get('/data-product/' +  fileName)
  },
}
