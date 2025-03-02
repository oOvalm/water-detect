<template>
  <PreviewImage
      ref="imageViewerRef"
      :imageList="[imageUrl]"
      v-if="fileInfo.file_type === 2"
  ></PreviewImage>
  <Window
      :show="windowShow"
      @close="closeWindow"
      :width="fileInfo.file_type === 3 ? 1500 : 900"
      :title="fileInfo.filename"
      :align="fileInfo.file_type === 3 ? 'center' : 'top'"
      v-else
  >
    <PreviewVideo :url="url" v-if="fileInfo.file_type === 3"></PreviewVideo>
    <!--    <PreviewExcel :url="url" v-if="fileInfo.file_type === 6"></PreviewExcel>-->
    <!--    <PreviewDoc :url="url" v-if="fileInfo.file_type === 5"></PreviewDoc>-->
    <!--    <PreviewPdf :url="url" v-if="fileInfo.file_type === 4"></PreviewPdf>-->
    <!--    <PreviewTxt-->
    <!--        :url="url"-->
    <!--        v-if="fileInfo.file_type === 7 || fileInfo.file_type === 8"-->
    <!--    ></PreviewTxt>-->
    <!--    &lt;!&ndash;特殊预览&ndash;&gt;-->
    <!--    <PreviewMusic-->
    <!--        :url="url"-->
    <!--        :fileName="fileInfo.fileName"-->
    <!--        v-if="fileInfo.fileCategory === 2"-->
    <!--    ></PreviewMusic>-->
    <!--    <PreviewDownload-->
    <!--        :createDownloadUrl="createDownloadUrl"-->
    <!--        :downloadUrl="downloadUrl"-->
    <!--        :fileInfo="fileInfo"-->
    <!--        v-if="fileInfo.fileCategory === 5 && fileInfo.file_type != 8"-->
    <!--    ></PreviewDownload>-->
  </Window>
</template>

<script setup>
import PreviewDoc from "@/components/preview/PreviewDoc.vue";
import PreviewExcel from "@/components/preview/PreviewExcel.vue";
import PreviewImage from "@/components/preview/PreviewImage.vue";
import PreviewPdf from "@/components/preview/PreviewPdf.vue";
import PreviewVideo from "@/components/preview/PreviewVideo.vue";
import PreviewTxt from "@/components/preview/PreviewTxt.vue";
import PreviewDownload from "@/components/preview/PreviewDownload.vue";
import PreviewMusic from "@/components/preview/PreviewMusic.vue";

import {ref, reactive, getCurrentInstance, nextTick, computed} from "vue";
import {useRouter, useRoute} from "vue-router";
import Window from "@/components/Window.vue";
import message from "@/utils/Message.js";

const {proxy} = getCurrentInstance();
const router = useRouter();
const route = useRoute();
const fileTypes = getCurrentInstance().appContext.config.globalProperties.$FileType

const imageUrl = computed(() => {
  return (
      proxy.globalInfo.imageUrl + fileInfo.value.fileCover.replaceAll("_.", ".")
  );
});

const windowShow = ref(false);
const closeWindow = () => {
  windowShow.value = false;
};
const FILE_URL_MAP = {
  0: {
    fileUrl: "/directory/getFile",
    videoUrl: "/directory/ts/getVideoInfo",
    createDownloadUrl: "/file/createDownloadUrl",
    downloadUrl: "/api/file/download",
  },
  1: {
    fileUrl: "/admin/getFile",
    videoUrl: "/admin/ts/getVideoInfo",
    createDownloadUrl: "/admin/createDownloadUrl",
    downloadUrl: "/api/admin/download",
  },
  2: {
    fileUrl: "/showShare/getFile",
    videoUrl: "/showShare/ts/getVideoInfo",
    createDownloadUrl: "/showShare/createDownloadUrl",
    downloadUrl: "/api/showShare/download",
  },
};
const url = ref(null);
const createDownloadUrl = ref(null);
const downloadUrl = ref(null);

const fileInfo = ref({});

const imageViewerRef = ref();
const showPreview = (data, showPart) => {
  console.log("showPreview", data);
  fileInfo.value = data;
  if (data.file_type === fileTypes.Image) {
    nextTick(() => {
      imageViewerRef.value.show(0);
    });
  } else {
    windowShow.value = true;
    let _url = FILE_URL_MAP[showPart].fileUrl;
    //视频地址单独处理
    if (data.file_type === fileTypes.Video) {
      _url = FILE_URL_MAP[showPart].videoUrl;
    }
    let _createDownloadUrl = FILE_URL_MAP[showPart].createDownloadUrl;
    let _downloadUrl = FILE_URL_MAP[showPart].downloadUrl;
    if (showPart === 0) {
      _url = _url + "/" + data.id;
      _createDownloadUrl = _createDownloadUrl + "/" + data.id;
    } else if (showPart === 1) {
      message.error("todo")
      // _url = _url + "/" + data.userId + "/" + data.fileId;
      // _createDownloadUrl =
      //     _createDownloadUrl + "/" + data.userId + "/" + data.fileId;
    } else if (showPart === 2) {
      message.error("todo")
      // _url = _url + "/" + data.shareId + "/" + data.fileId;
      // _createDownloadUrl =
      //     _createDownloadUrl + "/" + data.shareId + "/" + data.fileId;
    }
    url.value = _url;
    createDownloadUrl.value = _createDownloadUrl;
    downloadUrl.value = _downloadUrl;
  }
};
defineExpose({showPreview});
</script>

<style lang="scss">
</style>
