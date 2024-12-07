<template>
  <div class="fit-parent">
    <div class="json-item-container" v-for="(value, title, index) in this.hisData().output.structure" :key="index">
      <div class="flex-container-title">{{ title }}</div>

      <div v-if="Array.isArray(value)">
        <!-- <el-button @click="addElement">Add Element</el-button> -->
        <div v-for="(item, i) in value" :key="i">
          <div class="flex-container-input-single-line">
            <input :id="`input-${i}`" type="textarea" ref="inputs" v-model="value[i]" class="fit-parent"
              :tabindex="i * 2 + 1" />
            <el-button class="square" @click="moveUp(value, i)" :disabled="i == 0"><el-icon class="square">
                <CaretTop />
              </el-icon></el-button>
            <el-button class="square" @click="moveDown(value, i)" :disabled="i == value.length - 1"><el-icon
                class="square">
                <CaretBottom />
              </el-icon></el-button>
            <el-button class="square" @click="() => insertElement(title, i, '')" :tabindex="i * 2 + 2"><el-icon
                class="square">
                <plus />
              </el-icon>
            </el-button>
            <el-button v-if="value.length > 1" class="square" @click="removeElement(title, i)"><el-icon class="square">
                <delete />
              </el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <div v-else>
        <textarea class="fit-parent-width document-textarea" :id="`textarea-${title}`" @click="adjustHeight(title)"
          @input="adjustHeight(title)" v-model="this.hisData().output.structure[title]"></textarea>
      </div>
    </div>
  </div>
</template>

<script>

import { nextTick } from "vue";

export default {
  name: "TitledDocument",
  inject: ["hisData"],
  setup() {
    // const jsonStructure = reactive({
    //   "Discharge Diagnosis": [""],
    //   "Surgical Procedures": "",
    //   "Hospital Course": "",
    //   "Therapeutic Procedures": "",
    //   Complication: "",
    // });


    function adjustHeight(title) {
      console.log(`adjustHeight(${title})`);
      const textarea = document.getElementById(`textarea-${title}`);
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    }

    function moveUp(arr, index) {
      if (index > 0) {
        const temp = arr[index - 1];
        arr[index - 1] = arr[index];
        arr[index] = temp;
      }
    }

    function moveDown(arr, index) {
      if (index < arr.length - 1) {
        const temp = arr[index + 1];
        arr[index + 1] = arr[index];
        arr[index] = temp;
      }
    }

    function addElement() {
      this.jsonStructure["Discharge Diagnosis"].push("");
    }
    function insertElement(title, index, element) {
      this.hisData().output.structure.splice(index + 1, 0, element);
      nextTick(() => {
        document.getElementById(`input-${index + 1}`).focus();
      });
    }

    function removeElement(title, index) {
      if (this.hisData().output.structure.length > 1) {
        this.hisData().output.structure.splice(index, 1);
      }
    }
    return {
      adjustHeight,
      moveUp,
      moveDown,
      addElement,
      insertElement,
      removeElement,
    };
  },
};
</script>

<style scoped>
.json-item-container {
  box-sizing: border-box;
  margin-bottom: 16px;
}

/* input {
  padding: 8px;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  border-bottom-left-radius: 4px;
  margin-right: 8px;
} */

/* textarea {
  padding: 8px;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  border-bottom-left-radius: 4px;
} */

.container {
  box-sizing: border-box;
  margin: 20px;
  border: 1px solid rgb(195, 195, 195);

}

.fit-parent {
  box-sizing: border-box;
  width: 100%;
  height: 100%;
}

.fit-parent-width {
  box-sizing: border-box;
  width: 100%;
}

.flex-container {
  box-sizing: border-box;
  display: flex;
}

.flex-container-title {
  box-sizing: border-box;
  padding-top: 6px;
  padding-bottom: 6px;
  padding-left: 8px;
  padding-right: 8px;
  border-radius: 8px 8px 0 0;
  /* margin-top:20px; */
  width: fit-content;
  display: flex;
  align-items: center;
  background-color: rgb(237, 237, 237);
}

.flex-container-textarea {
  box-sizing: border-box;
  display: flex;
  align-items: center;
}

.flex-container-input-single-line {
  box-sizing: border-box;
  height: 32px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.button-container {
  display: flex;
  margin-left: 10px;
  /* Optional: to add some space between the textarea and the buttons */
}

.square {
  display: flex;
  box-sizing: border-box;
  align-items: center;
  width: 24px;
  height: 24px;
  margin: 0 2px;
  padding: 0;
  border-radius: 4px;
}

.bold {
  font-weight: bold;
}

.document-textarea {
  overflow: hidden;
  z-index: 100;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  border-bottom-right-radius: 6px;
  border-bottom-left-radius: 6px;
  border-color: beige;
  background-color: white;
  padding: 8px;
  line-height: 1.5;
  text-align: justify;
}

/* input,
textarea {
  border: 1px solid rgb(195, 195, 195);
  text-align: justify;
} */
</style>
