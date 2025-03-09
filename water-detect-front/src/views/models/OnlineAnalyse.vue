<template>
  <div class="top">
    <div class="top-op">
      <el-button type="primary" @click="uploadRTSPStream">RTSP流</el-button>
      <el-button type="success" @click="startAnalysis">开始分析</el-button>
    </div>
  </div>
  <div class="box" ref="doubleVideoRef" v-if="fileInfo.id">
    <div class="left" ref="leftRef">
      <PreviewVideo :url="originUrl"></PreviewVideo>
    </div>
    <div class="resize" ref="splitterRef" title="分界线">
      <div class="dots">⋮</div>
    </div>
    <div class="right" ref="rightRef">
      <PreviewVideo :url="analysedUrl"></PreviewVideo>
    </div>
  </div>
  <div v-else>
    <el-upload
        :multiple="false"
        :show-file-list="false"
        drag
        :http-request="uploadFile"
    >
      <el-icon class="el-icon--upload">
        <upload-filled/>
      </el-icon>
      <div class="el-upload__text">
        拖动文件到此处或 <em>点击上传文件</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          视频仅支持分析mp4, 图片仅支持jpg/png
        </div>
      </template>
    </el-upload>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted, watch, nextTick} from 'vue';
import message from "@/utils/Message.js";
import httpRequest from "@/api/httpRequest.ts";
import {UploadFilled} from "@element-plus/icons-vue";
import Preview from "@/components/preview/Preview.vue";
import PreviewVideo from "@/components/preview/PreviewVideo.vue";

const emit = defineEmits(["addFile"]);
const fileInfo = ref({});

const originRef = ref();
const analysedRef = ref();
const splitterRef = ref();
const leftRef = ref();
const rightRef = ref();
const doubleVideoRef = ref();
const originUrl = ref();

const uploadRTSPStream = () => {
  message.error('todo');
};
const startAnalysis = () => {
  message.error('todo');
};

const uploadFile = async (fileData) => {
  emit("addFile", {file: fileData.file, filePid: -2});
}
const uploadDone = ({fileUID}) => {
  httpRequest.get(`/directory/FileInfo/uid/${fileUID}`).then(({data}) => {
    if (data.code == null || data.code !== 0) {
      throw new Error(data.msg);
    }
    fileInfo.value = data.data;
    originUrl.value = `/directory/ts/getVideoInfo/${data.data.id}`;
    originUrl.value = `/directory/ts/getVideoInfo/${data.data.id}?analysed=true`;
    // console.log(originRef)
    // originRef.value.showPreview(fileInfo, 0);
    console.log(fileInfo.value);
  }).catch((e) => {
    console.log(e)
  })
}
defineExpose({uploadDone});

watch(fileInfo, (newVal) => {
  if (newVal) {
    console.log(newVal);
    nextTick(() => {
      if (newVal.id) {
        addListener();
      }
    })
  }
})


const addListener = () => {
  let resize = splitterRef.value;
  let left = leftRef.value;
  let right = rightRef.value;
  let doubleVideo = doubleVideoRef.value;
  console.log(resize)
  // 鼠标按下事件
  resize.onmousedown = function (e) {
    // 颜色改变提醒
    resize.style.background = '#818181';
    var startX = e.clientX;
    var leftWidth = left.offsetWidth;

    // 鼠标拖动事件
    document.onmousemove = function (e) {
      var endX = e.clientX;
      var moveLen = leftWidth + (endX - startX); // 计算移动的距离
      var maxT = doubleVideo.clientWidth - resize.offsetWidth; // 容器宽度 - 分隔条的宽度

      if (moveLen < 30) moveLen = 30; // 最小宽度
      if (moveLen > maxT - 30) moveLen = maxT - 30; // 最大宽度

      left.style.width = moveLen + 'px';
      right.style.width = (doubleVideo.clientWidth - moveLen - 10) + 'px';
    };

    // 鼠标松开事件
    document.onmouseup = function () {
      // 颜色恢复
      resize.style.background = '#d6d6d6';
      document.onmousemove = null;
      document.onmouseup = null;
      resize.releaseCapture && resize.releaseCapture(); // 释放鼠标捕获
    };

    resize.setCapture && resize.setCapture(); // 设置鼠标捕获
    return false;
  };
}

const removeListener = () => {
  // 移除鼠标事件
  if (splitterRef.value) {
    splitterRef.value.onmousedown = null;
    document.onmousemove = null;
    document.onmouseup = null;
  }
}

// onMounted(() => {
//   addListener()
// });

onUnmounted(removeListener);

</script>

<style lang="scss" scoped>
@use "@/assets/file.list.scss";

.double-video-player {
  display: flex;
  height: 100%; /* 可根据需要调整高度 */
  width: 100%;
  --separator-left: 50%; /* 初始分隔条位置 */
}

.video-container {
  overflow: hidden;
}

.double-video-player .video-container:nth-child(1) {
  width: calc(var(--separator-left) - 2.5px);
}

.double-video-player .video-container:nth-child(3) {
  width: calc(100% - var(--separator-left) - 2.5px);
}

.separator {
  width: 5px;
  background-color: #ccc;
  cursor: col-resize;
  position: relative;
  left: calc(var(--separator-left) - 2.5px);
  transition: left 0.2s ease;
  z-index: 1;
}

/* 拖拽相关样式 */
/*包围div样式*/
.box {
  width: 100%;
  height: 100%;
  margin: 1% 0px;
  overflow: hidden;
  box-shadow: -1px 9px 10px 3px rgba(0, 0, 0, 0.11);
}

/*左侧div样式*/
.left {
  width: calc(32% - 10px);
  height: 100%;
  background: #FFFFFF;
  float: left;
}

/*拖拽区div样式*/
.resize {
  cursor: col-resize;
  float: left;
  position: relative;
  top: 0;
  background-color: #d6d6d6;
  border-radius: 5px;
  margin-top: -10px;
  width: 10px;
  height: 100%;
  background-size: cover;
  background-position: center;
  font-size: 32px;
  color: white;

  .dots {
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    display: -webkit-box;
    display: -webkit-flex;
    display: flex;
    -webkit-flex-direction: column;
    flex-direction: column;
  }
}

/*拖拽区鼠标悬停样式*/
.resize:hover {
  color: #444444;
}

/*右侧div'样式*/
.right {
  float: left;
  width: 68%; /*右侧初始化宽度*/
  height: 100%;
  background: #fff;
  box-shadow: -1px 4px 5px 3px rgba(0, 0, 0, 0.11);
}
</style>
