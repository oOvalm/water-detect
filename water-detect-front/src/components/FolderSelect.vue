<template>
  <div>
    <Dialog
        :show="dialogConfig.show"
        :title="dialogConfig.title"
        :buttons="dialogConfig.buttons"
        width="600px"
        :showCancel="true"
        @close="close"
    >
      <div class="navigation-panel">
        <Navigation
            ref="navigationRef"
            @navChange="navChange"
            :watchPath="false"
        ></Navigation>
      </div>
      <div class="folder-list" v-if="folderList.length > 0">
        <div
            class="folder-item"
            v-for="item in folderList"
            @click="selectFolder(item)"
        >
          <icon :fileType="1"></icon>
          <span class="file-name">{{ item.filename }}</span>
        </div>
      </div>
      <div v-else class="tips">
        移动到 <span>{{ currentFolder.filename }}</span> 文件夹
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import {ref, reactive, getCurrentInstance, nextTick} from "vue";
import {useRouter, useRoute} from "vue-router";
import Navigation from '@/components/Navigation.vue'
import Dialog from '@/components/Dialog.vue'
import icon from '@/components/Icon.vue'
import httpRequest from "@/api/httpRequest.ts";
import message from "@/utils/Message.js";

const dialogConfig = ref({
  show: false,
  title: "移动到",
  buttons: [
    {
      type: "primary",
      click: () => {
        folderSelect();
      },
      text: "移动到此",
    },
  ],
});

//父级ID
const filePid = ref(-1);
const selectedFileIDs = ref([]);
const folderList = ref([]);
const currentFolder = ref({});

const loadFolder = async () => {
  httpRequest.get("/directory/folderList", {
    params: {
      filePid: filePid.value,
      excludeFileIDs: selectedFileIDs.value.join(",")
    }
  }).then(({data}) => {
    if (data.code !== 0) throw data.msg;
    folderList.value = data.data;
  }).catch((e) => {
    console.log(e);
    message.error("获取目录信息失败")
  })
};

const close = () => {
  dialogConfig.value.show = false;
};

//展示弹出框对外的方法
const showFolderDialog = (_selectedFileIDs) => {
  dialogConfig.value.show = true;
  selectedFileIDs.value = _selectedFileIDs;
  filePid.value = -1;
  nextTick(() => {
    navigationRef.value.init();
  });
};

defineExpose({
  showFolderDialog,
  close,
});
//选择目录
const navigationRef = ref();
const selectFolder = (data) => {
  navigationRef.value.openFolder(data);
};

const emit = defineEmits(["folderSelect"]);
const folderSelect = () => {
  emit("folderSelect", filePid.value);
};

//导航改变回调
const navChange = (data) => {
  const {curFolder} = data;
  currentFolder.value = curFolder;
  filePid.value = curFolder.fileId;
  loadFolder();
};
</script>
<style lang="scss" scoped>
.navigation-panel {
  padding-left: 10px;
  background: #f1f1f1;
}

.folder-list {
  .folder-item {
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 10px;

    .file-name {
      display: inline-block;
      margin-left: 10px;
    }

    &:hover {
      background: #f8f8f8;
    }
  }

  max-height: calc(100vh - 200px);
  min-height: 200px;
}

.tips {
  text-align: center;
  line-height: 200px;

  span {
    color: #06a7ff;
  }
}
</style>
