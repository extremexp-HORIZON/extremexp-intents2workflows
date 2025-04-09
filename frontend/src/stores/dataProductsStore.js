import { defineStore } from 'pinia';
import { useNotify } from 'src/use/useNotify.js';
import dataProductAPI from "src/api/dataProductsAPI";
import download from 'downloadjs';

const notify = useNotify();

export const useDataProductsStore = defineStore('dataProducts', {
  state: () => ({
    dataProducts: [],
    selectedDataProductPath: "",
  }),

  actions: {

    // ------------ CRUD operations
    async getDataProducts() {
      try {
        const response = await dataProductAPI.getDataProducts();
        this.dataProducts = response.data === "" ? [] : response.data.files;
      } catch (error) {
        notify.negative("Error retrieving data products");
        console.error("Error:", error);
      }
    },
    
/*     async postDataProduct(projectID, data) {
      try {
        await dataProductAPI.postDataProduct(projectID, data);
        notify.positive("Data product stored successfully");
        this.getDataProducts();
      } catch (error) {
        notify.negative("Error storing the data product");
        console.error("Error:", error);
      }
    },
    
    async putDataProduct(dataProductID, projectID, data) {
      try {
        await dataProductAPI.putDataProduct(projectID, dataProductID, data);
        notify.positive(`Data product successfully edited`);
        this.getDataProducts(projectID);
      } catch (error) {
        notify.negative("Error editing the data product");
        console.error("Error:", error);
      }
    }, */
    
    async deleteDataProduct(fileName) {
      try {
        await dataProductAPI.deleteDataProduct(fileName);
        notify.positive(`Data product deleted successfully`);
        this.getDataProducts();
      } catch (error) {
        notify.negative("Error deleting the data product.");
        console.error("Error:", error);
      }
    },

    // ------------ Download/materialize operations
/*     async materializeDataProduct(projectID, dataProductID) { // To be ingested by the intent API
      try {
        const response = await dataProductAPI.materializeDataProduct(projectID, dataProductID);
        this.selectedDataProductPath = response.data;
      } catch (error) {
        notify.negative("Error materializing the data");
        console.error("Error:", error);
      }
    },

    async downloadTemporalDataProduct(projectID, dataProductUUID) { // The user downloads it from the frontend
      try {
        const response = await dataProductAPI.downloadTemporalDataProduct(projectID, dataProductUUID);
        const content = response.headers['content-type'];
        download(response.data, "result.csv", content);
      } catch (error) {
        notify.negative("Error downloading the data");
        console.error("Error:", error);
      }
    }, */

    async downloadDataProduct(fileName) { // The user downloads it from the frontend
      try {
        const response = await dataProductAPI.downloadDataProduct(fileName);
        const content = response.headers['content-type'];
        download(response.data, fileName, content);
      } catch (error) {
        notify.negative("Error downloading the data");
        console.error("Error:", error);
      }
    }
  }
});