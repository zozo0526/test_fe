<template>
  <div class="parent-container">
    <div class="child-top">
      <h1>GenLab</h1>
      <el-menu class="el-menu-vertical no-right-border" @select="handleSelect">
        <div v-if="hisData() && hisData().reference_documents">
          <el-menu-item v-for="(item, i) in hisData().reference_documents" :key="i" :index="i.toString()">
            <div class="icon-container">
              <i :class="getIconName(item.title)"></i>
            </div>
            {{ item.title }}
          </el-menu-item>
        </div>
      </el-menu>
    </div>
    <div class="child-bottom">
      <el-popover
          :width="200"
          popper-style="box-shadow: rgb(14 18 22 / 35%) 0 10px 38px -10px, rgb(14 18 22 / 20%) 0 10px 20px -15px; padding: 20px;"
      >
        <template #reference>
          <div class="h-left">
            <img alt="Vue logo" src="../assets/question_mark.png">
            <p>Service Center</p>
          </div>

        </template>
        <template #default>
          <div
              class="demo-rich-conent"
              style="display: flex; gap: 16px; flex-direction: column"
          >
            <img
                src="../assets/qr_code.png"
                style="margin-bottom: 8px"
                alt=""/>
            <div>
              <p
                  class="demo-rich-content__name"
                  style="margin: 0; font-weight: 500"
              >
                Line 客服
              </p>
              <p
                  class="demo-rich-content__mention"
                  style="margin: 0; font-size: 14px; color: var(--el-color-info)"
              >
                Line ID: @197vmbxk
              </p>
            </div>

            <p class="demo-rich-content__desc" style="margin: 0">
              使用上有什麼心得或建議，歡迎加 Line 告訴我們！😀
            </p>
          </div>
        </template>
      </el-popover>
    </div>
  </div>
</template>

<script>
export default {
  name: "SideBar",
  inject: ["hisData"],

  data() {
    return {
      iconName: "",
      selectedMenuItemIndex: "0",
    };
  },

  methods: {
    handleSelect(index) {
      // transmit the selected menu item index to the parent component
      this.$emit("menu-item-selected", parseInt(index)); // convert string to number because the index is a string
    },

    getIconName(title) {
      const titleLowerCase = title.toLowerCase();
      const prefix = "icon fa-solid fa-";
      if (titleLowerCase === "prompt") {
        return prefix + "comment";
      } else if (titleLowerCase === "admission note") {
        return prefix + "book-medical";
      } else if (titleLowerCase === "discharge summary") {
        return prefix + "file-medical";
      } else if (titleLowerCase === "progress note") {
        return prefix + "calendar-day";
      } else if (titleLowerCase === "nursing note") {
        return prefix + "user-nurse";
      } else if (titleLowerCase === "physician note") {
        return prefix + "user-md";
      } else if (titleLowerCase === "ecg report") {
        return prefix + "heartbeat";
      } else if (titleLowerCase === "pathology report") {
        return prefix + "microscope";
      } else if (titleLowerCase === "lab data") {
        return prefix + "vial";
      } else if (titleLowerCase === "exam report") {
        return prefix + "lungs";
      } else if (titleLowerCase === "vital sign") {
        return prefix + "heart-pulse";
      } else if (titleLowerCase === "medication") {
        return prefix + "pills";
      } else if (titleLowerCase === "custom info") {
        return prefix + "user-pen";
      } else if (titleLowerCase === "operation note") {
        return prefix + "file-waveform";
      } else if (titleLowerCase === "quality analysis") {
        return prefix + "list-check";
      } else {
        return prefix + "file-lines";
      }
    },
  },
};
</script>

<style scoped>
.parent-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}
.child-top {
  /* Additional styling as needed */
}

.child-bottom {
  margin-top: auto;
  margin-bottom: 24px;
}


.h-left {
  display: flex;
  justify-content: flex-start;
}

.child-bottom img {
  margin: 16px;
  width: 18px;
  height: 18px;
}

.child-bottom p {
  margin-top: 16px;
  margin-bottom: 16px;
}

.no-right-border {
  border-right-width: 0;
}

.el-menu-item {
  font-size: 18px;
}

.icon {
  margin-right: 12px;
}

el-menu {
  background-color: rgb(234, 255, 234);
  height: 100%;
  width: 100%;
  border-right-width: 0;
}

.icon-container {
  display: flex;
  justify-content: center;
  /* Horizontal centering */
  align-items: center;
  /* Vertical centering */
  height: 24px;
  width: 24px;
}
</style>
