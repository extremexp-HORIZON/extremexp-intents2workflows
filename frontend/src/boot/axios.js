import {boot} from 'quasar/wrappers'
import axios from 'axios'

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const odinApi = axios.create({baseURL: "http://localhost:9001/"});
const intentsApi = axios.create({baseURL: "http://localhost:9002/"});
const textToIntentAPI = axios.create({baseURL: "http://localhost:9003/"});
const intentToGraphDBAPI = axios.create({baseURL: "http://localhost:9004/"});

export default boot(({app}) => {
   app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$odinApi = odinApi
  app.config.globalProperties.$intentsApi = intentsApi
  app.config.globalProperties.$textToIntentAPI = textToIntentAPI
  app.config.globalProperties.$intentToGraphDBAPI = intentToGraphDBAPI
})

export {odinApi, intentsApi, textToIntentAPI, intentToGraphDBAPI}
