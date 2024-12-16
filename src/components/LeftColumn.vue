<template>
  <div id="left-column-root" style="height:100%; box-sizing: border-box;">
    <div class="titled-document-root" style="height:90%; box-sizing: border-box;" v-if="hisData() && hisData().reference_documents">
      <TitledDocument v-for="(referenceDocument, index) in hisData().reference_documents" :key="index"
        v-show="selectedMenuItemIndex === index" :value="referenceDocument.text" @update:value="(value) => {
            referenceDocument.text = value;
          }
          " @buttonClicked="handleButtonClicked(referenceDocument)"
        :shouldShowButton="getDocumentAction(referenceDocument) != ''" :titleText="referenceDocument.title"
        :textAreaPlaceholder="textAreaPlaceholder" :buttonText="getDocumentAction(referenceDocument)"
        :isDisabled="referenceDocument.isDisabled" :isLoading="referenceDocument.isLoading"
        :readonly="referenceDocument.readonly"/>
    </div>
  </div>
</template>

<script>
import TitledDocument from "./TitledDocument.vue";
import axios from "axios";


export default {
  name: "LeftColumn",
  inject: ["hisData"],
  components: {
    TitledDocument,
  },

  props: {
    selectedMenuItemIndex: {
      type: Number,
      default: 0,
    },
  },

  data() {
    return {
      textAreaPlaceholder:
        "No Data in this section. You may add your own memo here or copy and paste from other sources.",
    };
  },

  methods: {
    getDocumentAction(referenceDocument) {
      // Description: This function returns the action of the reference document, which represent
      // the button behavior. If the reference document title is "Prompt", then the button should be
      // "" here. If the reference document title is "Quality Analysis", then the button should be
      // "Analyze".

      if (referenceDocument.title === "Prompt") {
        return "";
      } else if (referenceDocument.title === "Quality Analysis") {
        return "Perform";
      } else {
        return "";
      }
    },
    handleButtonClicked(referenceDocument) {
      // Description: This function handles the button click event.
      // If the reference document title is "Quality Analysis", do the following steps.
      // Else, do nothing.
      if (referenceDocument.title === "Quality Analysis") {
        this.saveQualityAnalysis(referenceDocument);
      }
    },

    async saveQualityAnalysis(referenceDocument) {
      // Description: This function handles the Perform Quality Analysis button click event.
      // index is the index of the reference document in the hisData().reference_documents array,
      // which is used to identify which button is clicked and which reference document is selected.
      // 1. Call server API: save_quality_analysis with parameters of "user_id", "medical_specialty",
      // "generation_preset", and "text" whose value = hisData().reference_documents[index_of_quality_analysis].text"
      // 2. If getting a success response, call uploadHisData.

      console.log("saveQualityAnalysis");
      // Disable the button and show loading spinner
      referenceDocument.isDisabled = true;
      referenceDocument.isLoading = true;

      try {
        const response = await axios.post(
          "/save_quality_analysis",
          {
            user_id: this.hisData().user_id,
            medical_specialty: this.hisData().medical_specialty,
            generation_preset: this.hisData().generation_preset,
            text: referenceDocument.text,
          }
        );
        if (response.data.status === "success") {
          // If getting a success response, call uploadHisData.
          this.uploadHisData(referenceDocument);
        } else {
          // If getting a Fail response, show the error message.
          console.log("Fail response", response.data.message);
          referenceDocument.isDisabled = false;
          referenceDocument.isLoading = false;
        }
      } catch (error) {
        console.log("Error", error);
        referenceDocument.isDisabled = false;
        referenceDocument.isLoading = false;
      }
    },

    async uploadHisData(referenceDocument) {
      // Description: Call server API: upload_his_data
      // 1. Make a http post request with parameters of "his_data".
      // 2. The response is a json having 2 keys named "status" and "value"(his_data_id).
      // 3. If the status is "Success", then call the getQualityAnalysisResult() function.
      // 4. If the status is "Fail", then show the error message.
      try {
        const inputData = this.hisData();
        const response = await axios.post(
          "/upload_his_data",
          inputData
        );
        if (response.data.status === "success") {
          const hisDataId = response.data.value;
          console.log("hisDataId", hisDataId);
          this.getQualityAnalysisResult(referenceDocument, hisDataId);
        } else {
          console.log("Fail response", response.data.message);
          this.isDisabled = false;
          this.isLoading = false;
        }
      } catch (error) {
        this.isDisabled = false;
        this.isLoading = false;
      }
    },
    async getQualityAnalysisResult(referenceDocument, hisDataId) {
      // Description: Call server API: get_quality_analysis_result
      // 1. Make a http post request with parameters of "his_data_id".
      // 2. The response is a json having 2 keys named "status" and 'quality_analysis_result'.
      // 3. If the status is "Success",
      // add a new item to the referenceDocuments,
      // with "title" of "Quality Report" and "text" is the qualityAnalysisResult.
      // The menu should show the "Quality Report" item.
      // 4. If the status is "Fail", then show the error message.
      try {
        const response = await axios.post(
          "/get_quality_analysis_result",
          {
            his_data_id: hisDataId,
          }
        );
        if (response.data.status === "success") {
          const qualityAnalysisResult = response.data.value;
          console.log("qualityAnalysisResult", qualityAnalysisResult);
          // If "Quality Report" item is already in the referenceDocuments, then replace it.
          // Else, add a new item to the referenceDocuments.

          const qualityReportIndex = this.hisData().reference_documents.findIndex(
            (item) => item.title === "Quality Report"
          );
          if (qualityReportIndex !== -1) {
            this.hisData().reference_documents[
              qualityReportIndex
            ].text = qualityAnalysisResult;
          } else {
            this.hisData().reference_documents.push({
              title: "Quality Report",
              text: qualityAnalysisResult,
            });
          }

          this.hisData().selected_menu_item_index =
            this.hisData().reference_documents.length - 1;

          referenceDocument.isDisabled = false;
          referenceDocument.isLoading = false;
        } else {
          console.log("Fail response", response.data.message);
          referenceDocument.isDisabled = false;
          referenceDocument.isLoading = false;
        }
      } catch (error) {
        console.log("Error", error);
        referenceDocument.isDisabled = false;
        referenceDocument.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>

</style>
