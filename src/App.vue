<template>
  <div>
    <!-- a hidden div with id:"output" with value=generated_text
    to be retrieved by the outer web view component-->
    <div id="output" style="display: none; visibility: hidden">
      {{ hisData.output.value }}
    </div>
    <el-container class="container" style="height: 100vh">
      <el-aside class="aside" width="200px">
        <SideBar
          class="side-bar"
          @menu-item-selected="updateReferenceDocuments"
        />
      </el-aside>

      <el-main class="main" style="height: 100%">
        <el-row style="height: 100%">
          <el-col class="left-column" :span="12">
            <LeftColumn
              :selectedMenuItemIndex="selectedMenuItemIndex"
              style="height: 100%; box-sizing: border-box"
            />
          </el-col>
          <el-col class="right-column" :span="12">
            <RightColumn style="height: 100%; box-sizing: border-box" />
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import LeftColumn from "./components/LeftColumn.vue";
import RightColumn from "./components/RightColumn.vue";
import SideBar from "./components/SideBar.vue";
import axios from "axios";

export default {
  // Using provide/inject to pass hisData between components
  provide() {
    return {
      hisData: () => this.hisData,
    };
  },
  components: {
    LeftColumn,
    RightColumn,
    SideBar,
  },
  data() {
    return {
      hisData: {
        _id: "",
        user_id: "",
        medical_specialty: "",
        generation_preset: "",
        reference_documents: [
          {
            title: "Error",
            text: "Fails to get the data. Please see the console.log and check the if backend API is out of service (500 server error) or any frontend input parameter is wrong (400 client error).",
          },
        ],
        generated_text: "",
        output: {
          type: "",
          value: "",
          structure: {
            "1. Discharge Diagnosis": "",
            "2. Surgical Procedures": "",
            "3. Hospital Course": "",
            "4. Therapeutic Procedures": "",
            "5. Complication": "",
          },
        },
      },
      outputValue: "output value here",
      hisDataId: "",
      selectedMenuItemIndex: 0,
    };
  },
  created() {
    // Get the his_data
    // 1. Make a http post request to "/get_his_data" with parameter
    //    named "his_data_id" and get the response when the web page is loaded.
    // 2. The response is a json having at least 4 keys named "user_id", "generation_preset",
    //    "reference_documents", and "output".
    //    The referenceDocuments has value of a list of json objects, which contains 2 keys named "title" and "text".
    //    The output has two keys named "type" and "content".
    // 3. Saved the response.data.value to hisData.

    let urlParams = new URLSearchParams(window.location.search);
    this.hisDataId = urlParams.get("his_data_id");
    console.log("his_data_id:", this.hisDataId);
    console.log("baseURL:", axios.defaults.baseURL);

    if (this.hisDataId === "test") {
      console.log(
        "Using the default hisData which is stored in the frontend:",
        this.hisData
      );
      return;
    }

    axios
      .post("/get_his_data", {
        his_data_id: this.hisDataId,
      })
      .then((response) => {
        this.hisData = response.data.value;
        // initiate the output.value by output.structure
        this.hisData.output.value = this.hisData.output.structure;
        // set the Prompt to readonly if the output.type is "json"
        this.hisData.reference_documents.forEach((referenceDocument) => {
          referenceDocument.readonly = false;
          if (referenceDocument.title === "Prompt") {
            if (this.hisData.output.type === "json") {
              referenceDocument.readonly = true;
            }
          }
        });
        console.log("hisData:", this.hisData);
      })
      .catch((error) => {
        console.log(error);
      });
  },
  methods: {
    // Function: getPersonalPrompt(user_id, medical_specialty, generation_preset) -> personalPrompt
    // 1. Make a http post request with parameters of user_id and generation_preset
    // 2. Get the response and extract response.data.value of personalPrompt
    // 3. Return personalPrompt
    getPersonalPrompt(user_id, medical_specialty, generation_preset) {
      let personalPrompt = "";
      axios
        .post("/get_personal_prompt", {
          user_id: user_id,
          medical_specialty: medical_specialty,
          generation_preset: generation_preset,
        })
        .then((response) => {
          console.log("response from get_personal_prompt:", response.data);
          personalPrompt = response.data.value;
        })
        .catch((error) => {
          console.log(error);
        });
      return personalPrompt;
    },
    // Function: getQualityAnalysis(user_id, medical_specialty, generation_preset) -> personalPrompt
    // 1. Make a http post request with parameters of user_id, medical_specialty, and generation_preset
    // 2. Get the response and extract response.data.value of qulityAnalysis
    // 3. Return qulityAnalysis
    getQualityAnalysis(user_id, medical_specialty, generation_preset) {
      let qulityAnalysis = "";
      axios
        .post("/get_quality_analysis", {
          user_id: user_id,
          medical_specialty: medical_specialty,
          generation_preset: generation_preset,
        })
        .then((response) => {
          console.log("response from get_quality_analysis:", response.data);
          qulityAnalysis = response.data.value;
        })
        .catch((error) => {
          console.log(error);
        });
      return qulityAnalysis;
    },

    updateReferenceDocuments(index) {
      this.selectedMenuItemIndex = index;
    },
  },
};
</script>

<style>

</style>
