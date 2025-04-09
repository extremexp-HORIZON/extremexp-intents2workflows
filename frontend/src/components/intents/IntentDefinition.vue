<template>
    <q-page>
        <q-form class="row text-center justify-center" @submit.prevent="handleSubmit" @reset="resetForm">            
            <div class="col-12">
                <h4> Intent Definition </h4>
            </div>
            <div class="col-6" style="padding-top: 10px; padding-bottom: 10px;">
                <q-input label="Intent name" outlined v-model="intentName" class="q-mb-sm"
                    :rules="[ val => val && val.length > 0 || 'Insert a name']"/>

                <q-select label="Data product" outlined v-model="selectedDataProdutName" :options="dataProductsStore.dataProducts.map(dp => dp.name)" class="q-mb-sm"
                    :rules="[ val => val && val.length > 0 || 'Select a dataset']"/>

                <h6>
                  You can either select the problem manually or infer it based on the intent description
                </h6>
                  
                <q-select label="Problem" outlined v-model="problem" :options=Object.keys(intentsStore.problems) class="q-mb-sm"
                    :rules="[ val => val && val.length > 0 || 'Select a problem']"/>

                <q-input label="Insert analytical intent description" outlined v-model="intentDescription" type="textarea" rows="7" class="q-mb-sm"/>
                
                <div style="text-align: right;">
                  <q-btn @click="predictIntentType()" label="Infer intent" color="pink" class="q-mb-sm" style="font-size: 10px;"/>
                </div>

                <q-select v-if="selectedDataProdutName && problem ==='Classification'" label="Target variable" outlined v-model="target" :options="attributes" class="q-mb-sm"
                    :rules="[ val => val && val.length > 0 || 'Select a target variable']"/>
                
            </div>
            <div class="col-12">
                <q-btn label="Suggest parameters" color="primary" type="submit"/>
                <q-btn label="Reset" type="reset" class="q-ml-sm"/>
                
            </div>
        </q-form>
    </q-page>
</template>

<script setup>
import {onMounted, computed, watch} from 'vue'
import {useIntentsStore} from 'stores/intentsStore.js'
import {useDataProductsStore} from 'stores/dataProductsStore.js'
import {useRoute, useRouter} from "vue-router";
import {useQuasar} from 'quasar'
import {intentsApi} from 'boot/axios';

const router = useRouter()
const route = useRoute()
const $q = useQuasar()

const intentsStore = useIntentsStore()
const dataProductsStore = useDataProductsStore()

const intentName = computed({
  get: () => intentsStore.intentName,
  set: (value) => intentsStore.intentName = value
})
const intentDescription = computed({
  get: () => intentsStore.intentDescription,
  set: (value) => intentsStore.intentDescription = value
})
const selectedDataProdutName = computed({
  get: () => intentsStore.selectedDataProdutName,
  set: (value) => intentsStore.selectedDataProdutName = value
})
const problem = computed({
  get: () => intentsStore.selectedProblem,
  set: (value) => intentsStore.selectedProblem = value
})
const target = computed({
  get: () => intentsStore.target,
  set: (value) => intentsStore.target = value
})

const handleSubmit = async() => { // TODO: Remove this and make the code query over the Jena graph, not in graphDB
  $q.loading.show({message: 'Suggesting parameters...'})
  await intentsStore.getAllInfo()
  await intentsStore.predictParameters()
  router.push({ path: route.path.substring(0, route.path.lastIndexOf("/")) + "/abstract-planner" })
  $q.loading.hide()
}

const predictIntentType = async() => {
  $q.loading.show({message: 'Predicting intent type...'})

  let data = {
    'text': intentDescription.value,
  }
  await intentsStore.predictIntentType(data)

  $q.loading.hide()
}

const resetForm = () => {
  intentName.value = null
  intentDescription.value = null
  selectedDataProdutName.value = null
  problem.value = null
  target.value = null
}

let attributes = [];

const getAttributes = async() => {
  const selectedDataProduct = dataProductsStore.dataProducts.find(dp => dp.name === selectedDataProdutName.value);
  if (selectedDataProduct) {
    let data = {
      'path': selectedDataProduct.path,
    }
    const response = await intentsApi.post('/attributes',data)
    console.log(response.data)
    attributes = response.data//selectedDataProduct.attributes.map(att => att)
  }
  else {
    attributes = []
  }
}

onMounted(async() => {
  await dataProductsStore.getDataProducts()
  intentsStore.getProblems()
  getAttributes()
})


// Watch for changes to selectedDataProdutName and refetch attributes if needed
watch(() => selectedDataProdutName.value, () => {
  getAttributes();  // Re-fetch when the selected data product changes
});

</script>
