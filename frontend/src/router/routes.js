const routes = [
  {
    path: '/',
    redirect: to => {
      // the function receives the target route as the argument and we return a redirect path/location here.
      return {path: '/data-products', name: 'data-products'}
    },
  },

  // Page that appears when no project has been selected yet
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {path: 'data-products', name: 'data-products', component: () => import('pages/DataProducts.vue')},
      {path: 'intents', name: 'intents', component: () => import('pages/Intents.vue')},
      // Steps to create an intent
      {path: 'intent-definition', name: 'intent-definition', component: () => import('pages/CreateIntent.vue')},
      {path: 'abstract-planner', name: 'abstract-planner', component: () => import('pages/CreateIntent.vue')},
      {path: 'logical-planner', name: 'logical-planner', component: () => import('pages/CreateIntent.vue')},
      {path: 'workflow-planner', name: 'workflow-planner', component: () => import('pages/CreateIntent.vue')},
      {path: 'intent-workflows', name: 'intent-workflows', component: () => import('pages/CreateIntent.vue')},
    ]
  },

  // When the specified route is not found, redirect to the 404 page
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
