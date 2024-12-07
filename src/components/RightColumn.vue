<template>
  <div id="right-column-root" style="height: 100%; box-sizing: border-box">
    <div class="titled-document-root" style="height: 90%; box-sizing: border-box">
      <TitledDocument :documentType="hisData().output.type" :value="hisData().generated_text" :readonly="isReadOnly"
        @update:value="(value) => {
          hisData().generated_text = value;
        }
          " @buttonClicked="generateButtonClicked" :shouldShowButton="true"
        :titleText="this.hisData().generation_preset" :textAreaPlaceholder="generativeResultPlaceholder"
        :isDisabled="isDisabled" :isLoading="isLoading" :buttonText="buttonText" />

      <el-dialog v-model="dialogVisible" title="" width="30%" :before-close="handleClose">
        <span>{{ alert_message }}</span>
        <template #footer>
          <span class="dialog-footer">
            <el-button type="primary" @click="dialogVisible = false">
              Confirm
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import TitledDocument from "./TitledDocument.vue";
import { socket } from "@/socket";

export default {
  inject: ["hisData"],
  components: { TitledDocument },
  data() {
    return {
      buttonText: "Generate",
      prompt: "",
      generativeResultPlaceholder: "Click the 'Generate' button.",
      isLoading: false,
      isDisabled: false,
      isReadOnly: false,
      promptIndex: 0,
      dialogVisible: false,
      alert_message: "",
      jsonObject: {},
      // generative_stream_enabled: false,
      generative_stream_enabled: true,
    };
  },
  mounted() {
    // this.dialogVisible=true;
    socket.on("generative_stream", (msg) => {
      // Description: Handles the socket.io event "generative_stream", which is
      // triggered by the API get_generative_stream.
      // msg format : {status:<status>, value:<value>, message:<message>}}
      // If not finished: {status: 'stream', value: <word>, message: <message>}
      // If finished:   {status: 'finish', value: "", message: ""}
      // If failed:     {status: 'fail', value: "", message: <error message>}
      // console.log("generative_stream:", msg);
      if (msg.status === "finish") {
        console.log("generated_text:", this.hisData().generated_text);

        this.unlock_ui();
        this.generativeResultPlaceholder += "\nGenerating stream: finished.";
        console.log("message:", msg.message);
      } else if (msg.status === "fail") {
        this.unlock_ui();
        this.generativeResultPlaceholder +=
          "\nGenerating stream: fail. Message: " + msg.message;
        return;
      } else if (msg.status === "stream") {
        this.hisData().generated_text += msg.value;
        // if the output type is "text", assign the generated text to the this.hisData().output.value.
        // if the output type is "json", parse the json and assign the json to the this.hisData().output.value.
        if (this.hisData().output.type === "text") {
          this.hisData().output.value = this.hisData().generated_text;
        } else if (this.hisData().output.type === "json") {
          // this.hisData().output.value = JSON.parse(this.hisData().generated_text);
        } else {
          this.generativeResultPlaceholder +=
            "\nGenerating stream with unknown output type. Please contact with the system administrators: \n" +
            this.hisData().output.type;
          console.log("generative_stream: unknown output type:", this.hisData().output.type
          );
          return;
        }
      } else {
        this.generativeResultPlaceholder +=
          "\nGenerating stream with unknown status: " + msg.status + "\nMessage: " + msg.message;
        console.log("generative_stream: unknown status:", msg.status, "Message:", msg.message);
        return;
      }
    });
    socket.on("redacting_sensitive_info", (msg) => {
      console.log("redacting_sensitive_info:", msg);
      if (msg.status === "start") {
        this.generativeResultPlaceholder +=
          "\nRedacting sensitive info: start.";
      } else if (msg.status === "finish") {
        this.generativeResultPlaceholder +=
          "\nRedacting sensitive info: finish.";
      } else if (msg.status === "fail") {
        this.unlock_ui();
        this.generativeResultPlaceholder +=
          "\nRedacting sensitive info: fail. Message: " + msg.message;
      }
    });
    socket.on("alert_message", (msg) => {
      console.log("alert_message:", msg);
      this.generativeResultPlaceholder +=
        "\n" + "status: " + msg["status"] + "\n" + "message: " + msg["message"];

      this.alert_message = msg["message"];
      this.dialogVisible = true;
      this.unlock_ui();
    });
  },
  unmounted() {
    socket.off("generative_stream");
    socket.off("redacting_sensitive_info");
    socket.off("alert_message");
  },

  methods: {
    lock_ui() {
      this.isLoading = true;
      this.isDisabled = true;
      this.isReadOnly = true;
    },
    unlock_ui() {
      this.isLoading = false;
      this.isDisabled = false;
      this.isReadOnly = false;
    },
    stringifyWithoutEscape(jsonData) {
      let jsonString = JSON.stringify(jsonData);

      // Replaces escaped forward slashes
      jsonString = jsonString.replace(/\\\//g, "\\/");

      // Replaces escaped new line characters
      jsonString = jsonString.replace(/\\n/g, "\n");

      // Replaces escaped carriage return characters
      jsonString = jsonString.replace(/\\r/g, "\r");

      return jsonString;
    },
    reEscape(str) {
      let result = str;
      result = result.replace(/\n/g, "\\n");
      result = result.replace(/\r/g, "\\r");
      result = result.replace(/\//g, "\\/");
      return result;
    },

    handleClose(done) {
      done();
    },
    generateButtonClicked() {
      // Set the isLoading, isDisabled, and isReadOnly to true to lock the generate button.
      this.lock_ui();

      // If the output type is "json", turn the stream off.
      if (this.hisData().output.type === "json") {
        this.generative_stream_enabled = false;
        // clear the output.structure by looping the keys of the output.structure.
        for (let key in this.hisData().output.structure) {
          this.hisData().output.structure[key] = "";
        }
      } else {
        this.generative_stream_enabled = true;
      }
      // Clear the text area
      this.hisData().generated_text = "";
      console.log("generateButtonClicked, hisData:", this.hisData());
      // savePrompt() will call the consecutive API step by step and report the progress.
      this.savePrompt();
    },

    async savePrompt() {
      // Description: Make a http post request with parameters of "prompt", "user_id",
      // "medical_specialty", and "generation_preset", and save the prompt.
      // 1. Find the prompt in the reference_documents.
      // 2. Make a http post request with parameters of "text", "user_id",
      //  "medical_specialty", and "generation_preset".
      // 3. The response is a json having a key named "status".
      //  If the status is "success", then call the uploadHisData() function.
      //  If the status is "fail", then show the error message.
      this.generativeResultPlaceholder = "Saving the prompt...";

      try {
        // Find the prompt
        for (let i = 0; i < this.hisData().reference_documents.length; i++) {
          if (this.hisData().reference_documents[i].title === "Prompt") {
            this.prompt = this.hisData().reference_documents[i].text;
            break;
          }
        }
        const inputData = {
          text: this.prompt,
          user_id: this.hisData().user_id,
          medical_specialty: this.hisData().medical_specialty,
          generation_preset: this.hisData().generation_preset,
        };
        console.log("savePrompt()", inputData);
        const response = await axios.post("/save_prompt", inputData);
        if (response.data.status === "success") {
          this.generativeResultPlaceholder += "Success.\n";
          this.uploadHisData();
        } else {
          this.generativeResultPlaceholder += "Fail.\n" + response.data.message;
          this.unlock_ui();
        }
      } catch (error) {
        this.generativeResultPlaceholder += "Fail.\nAPI error: " + error;
        this.unlock_ui();
      }
    },
    // Cal API: uploadHisData
    // 1. Make a http post request with parameters of "his_data".
    // 2. The response is a json having 2 keys named "status" and 'value'(hisDataId).
    // 3. If the status is "success", then call the getGenerativeResult() function.
    // 4. If the status is "fail", then show the error message.
    async uploadHisData() {
      console.log("uploadHisData()", this.hisData());
      this.generativeResultPlaceholder += "Uploading the his_data...";
      try {
        const inputData = this.hisData();

        const response = await axios.post("/upload_his_data", inputData);
        if (response.data.status === "success") {
          this.generativeResultPlaceholder += "Success.\n";
          const hisDataId = response.data.value;

          console.log("hisDataId", hisDataId);
          if (this.generative_stream_enabled) {
            this.getGenerativeStream(hisDataId);
          } else {
            this.getGenerativeResult(hisDataId);
          }
        } else {
          this.generativeResultPlaceholder += "Fail.\n" + response.data.message;
          console.log("uploadHisData() fail:", response.data.message);
          this.unlock_ui();
        }
      } catch (error) {
        if (error.response) {
          console.log("uploadHisData() fail:", error.response.data.message);
          this.generativeResultPlaceholder += "Fail.\nAPI error: " + error.response.data.message;
        } else {
          console.log("uploadHisData() fail:", error);
          this.generativeResultPlaceholder += "Fail.\nAPI error: " + error;
        }
        this.unlock_ui();
      }
    },
    // Call API: get_generative_stream
    // Description: Initiates socket.io to get the generative stream word by word.
    // Callback function: socket.on("generative_stream", (msg) => {...})
    async getGenerativeStream(hisDataId) {
      console.log("Start get_generative_stream");
      socket.emit("get_generative_stream", hisDataId, () => {
        console.log("Finished get_generative_stream");
      });
    },
    // Call API: get_generative_result
    async getGenerativeResult(hisDataId) {
      this.generativeResultPlaceholder +=
        "Generating the result (might take a bit long time)...";
      try {
        const inputData = {
          his_data_id: hisDataId,
        };

        const response = await axios.post("/get_generative_result", inputData);
        console.log("response", response);
        if (response.data.status === "success") {
          this.generativeResultPlaceholder += "Success.\n";
          this.hisData().generated_text = response.data.value;

          // if the output type is "json", then parse the json string to json object.
          if (this.hisData().output.type === "json") {
            console.log("type json");
            this.hisData().output.value = this.hisData().output.structure;
            this.jsonObject = JSON.parse(this.hisData().generated_text);
            console.log("jsonObject", this.jsonObject);
            console.log(
              "this.hisData().output.structure",
              this.hisData().output.structure
            );
            // check if the jsonData's keys are the same as the output.structure's keys.
            if (
              Object.keys(this.jsonObject).sort().join(",") !==
              Object.keys(this.hisData().output.structure).sort().join(",")
            ) {
              // alert the user that the output structure is not the same as the output json data.
              this.alert_message =
                "The generated structure is not the same as the required json structure.";
              this.unlock_ui();
              return;
            } else {
              const jsonString = JSON.stringify(this.jsonObject);
              console.log(
                "this.hisData().output.value (jsonString): \n",
                jsonString
              );
              this.hisData().output.structure = this.jsonObject; // render the json structure to the textarea
              this.hisData().output.value = jsonString; // place the json string to the output div
            }
          } else {
            console.log(
              "outputValue (text): \n",
              this.hisData().generated_text
            );
            // if the output type is "text", then replace the outputValue with the generated text.
            this.hisData().output.value = this.hisData().generated_text;
          }
        } else {
          // If http call fails, display the alert dialog
          this.alert_message = response.data.message;
          this.dialogVisible = true;
          console.log("getGenerativeResult() failed:", response.data.message);
          this.generativeResultPlaceholder +=
            "Fail.\nAPI error:" + response.data.message;
        }
      } catch (error) {
        console.log(
          "Error when get_generative_result: ",
          error.response.data.message
        );
        this.generativeResultPlaceholder +=
          "\nFail.\nError when get_generative_result: " +
          error.response.data.message;
        // show the alert dialog
        this.alert_message = error.response.data.message;
        this.dialogVisible = true;
      } finally {
        this.unlock_ui();
      }
    },
  },
};
</script>

<style scoped>
.dialog-footer button:first-child {
  margin-right: 10px;
}
</style>
