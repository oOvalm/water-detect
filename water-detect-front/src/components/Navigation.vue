<template>
  <div class="top-navigation">
    <template v-if="folderList.length > 0">
      <span class="back link" @click="backParent">返回上一级</span>
      <el-divider direction="vertical"/>
    </template>
    <span v-if="folderList.length === 0" class="all-file">全部文件</span>
    <span
        class="link"
        @click="setCurrentFolder(-1)"
        v-if="folderList.length > 0"
    >全部文件</span
    >
    <template v-for="(item, index) in folderList">
      <span class="iconfont icon-right"></span>
      <span
          class="link"
          @click="setCurrentFolder(index)"
          v-if="index < folderList.length - 1"
      >{{ item.filename }}</span
      >
      <span v-if="index === folderList.length - 1" class="text">{{
          item.filename
        }}</span>
    </template>
  </div>
</template>

<script setup>
import {ref, reactive, getCurrentInstance, watch} from "vue";
import {useRouter, useRoute} from "vue-router";
import message from "@/utils/Message.js";
import httpRequest from "@/api/httpRequest.ts";

const {proxy} = getCurrentInstance();
const router = useRouter();
const route = useRoute();

const props = defineProps({
  watchPath: {
    type: Boolean, //是否监听路径变化
    default: true,
  },
  shareId: {
    type: String,
  },
  adminShow: {
    type: Boolean,
    default: false,
  },
});

const api = {
  getFolderInfo: "/file/getFolderInfo",
  getFolderInfo4Share: "/share/web/getFolderInfo",
  getFolderInfo4Admin: "/admin/getFolderInfo",
};

//分类
const category = ref();
//目录
const folderList = ref([]);
//当前目录
const currentFolder = ref({id: "-1"});

//初始化
const init = () => {
  folderList.value = [];
  currentFolder.value = {id: "-1"};
  doCallback();
};

//点击目录
const openFolder = (data) => {
  const {id, filename} = data;
  const folder = {
    filename: filename,
    id: Number(id),
  };
  folderList.value.push(folder);
  currentFolder.value = folder;
  setPath();
};

defineExpose({openFolder, init});

//返回上一级
const backParent = () => {
  let currentIndex = null;
  console.log(folderList.value);
  console.log(currentFolder.value);
  for (let i = 0; i < folderList.value.length; i++) {
    if (folderList.value[i].id === currentFolder.value.id) {
      currentIndex = i;
      break;
    }
  }
  console.log(currentIndex);
  setCurrentFolder(currentIndex - 1);
};

//点击导航 设置当前目录
const setCurrentFolder = (index) => {
  if (index === -1) {
    //返回全部
    currentFolder.value = {id: "-1"};
    folderList.value = [];
  } else {
    currentFolder.value = folderList.value[index];
    folderList.value.splice(index + 1, folderList.value.length);
  }
  setPath();
};

//设置URL路径
const setPath = () => {
  if (!props.watchPath) {
    doCallback();
    return;
  }
  let pathArray = [];
  folderList.value.forEach((item) => {
    pathArray.push(item.id);
  });
  router.push({
    path: route.path,
    query:
        pathArray.length === 0
            ? ""
            : {
              path: pathArray.join("/"),
            },
  });
};

//获取当前路径的目录
const getNavigationFolder = async (path) => {
  console.log(path);
  let url = api.getFolderInfo;
  if (props.shareId) {
    url = api.getFolderInfo4Share;
  }
  // if (props.adminShow) {
  //   url = api.getFolderInfo4Admin;
  // }

  httpRequest.get(url, {
    params: {
      path: path,
      shareId: props.shareId,
    }
  }).then(({data}) => {
    folderList.value = data.data;
  }).catch((e) => {
    message.error("获取文件夹信息失败")
  });
};

const emit = defineEmits(["navChange"]);
const doCallback = () => {
  emit("navChange", {
    categoryId: category.value,
    curFolder: currentFolder.value,
  });
};

watch(
    () => route,
    (newVal, oldVal) => {
      if (!props.watchPath) {
        return;
      }
      //路由切换到其他路由  首页和管理员查看文件列表页面需要监听
      if (
          newVal.path.indexOf("/main") === -1 &&
          newVal.path.indexOf("/settings/fileList") === -1 &&
          newVal.path.indexOf("/share") === -1
      ) {
        return;
      }
      const path = newVal.query.path;
      const categoryId = newVal.params.category;
      category.value = categoryId;
      if (path === undefined) {
        init();
      } else {
        // getNavigationFolder(path);
        //设置当前目录
        let pathArray = path.split("/");
        currentFolder.value = {
          id: Number(pathArray[pathArray.length - 1]),
        };
        doCallback();
      }
    },
    {immediate: true, deep: true}
);
</script>

<style lang="scss" scoped>
.top-navigation {
  font-size: 13px;
  display: flex;
  align-items: center;
  line-height: 40px;

  .all-file {
    font-weight: bold;
  }

  .link {
    color: #06a7ff;
    cursor: pointer;
  }

  .icon-right {
    color: #06a7ff;
    padding: 0px 5px;
    font-size: 13px;
  }
}
</style>
