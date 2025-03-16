<template>
  <div class="top">
    <div class="top-op">
      <el-button class="btn" type="primary" @click="uploadRTSPStream">RTSP流</el-button>
      <el-button class="btn" type="success" @click="startAnalysis">开始分析</el-button>
      <el-progress type="dashboard" :percentage="analyseProgress" v-if="fileInfo.id">
        <template #default="{ percentage }">
          <span class="percentage-value">{{ percentage }}%</span>
          <span class="percentage-label">分析进度</span>
        </template>
      </el-progress>
    </div>
  </div>
  <div class="box" ref="doubleVideoRef" v-if="fileInfo.id">
    <div class="left" ref="leftRef">
      <PreviewVideo ref="player1Ref" v-if="originStatus === 0" :url="originUrl"
                    @play="()=>{syncVideo('play', 1)}"
                    @pause="()=>{syncVideo('pause', 1)}"
                    @seeked="(newTime) => {syncVideo('seeked', 1, {newTime: newTime})}"
      ></PreviewVideo>
      <div class="loading" v-else>
        <el-icon class="is-loading" v-if="originStatus === 1">
          <Loading/>
        </el-icon>
        <el-icon color="red" v-else>
          <WarningFilled/>
        </el-icon>
        <input type="text" :value="originStatus === 1 ? '视频转码中' : '转码失败'"/>
      </div>
    </div>
    <div class="resize" ref="splitterRef" title="分界线">
      <div class="dots">⋮</div>
    </div>
    <div class="right" ref="rightRef">
      <PreviewVideo ref="player2Ref" v-if="isShowAnalysedVideo()" :url="analysedUrl"
                    @play="()=>{syncVideo('play', 2)}"
                    @pause="()=>{syncVideo('pause', 2)}"
                    @seeked="(newTime) => {syncVideo('seeked', 2, {newTime: newTime})}"
      ></PreviewVideo>
      <div class="loading" v-else>
        <el-icon class="is-loading">
          <Loading/>
        </el-icon>
      </div>
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
import {Loading, UploadFilled, WarningFilled} from "@element-plus/icons-vue";
import Preview from "@/components/preview/Preview.vue";
import PreviewVideo from "@/components/preview/PreviewVideo.vue";
import {useRoute} from "vue-router";

const emit = defineEmits(["addFile"]);
const fileInfo = ref({}); // 原始文件信息

const route = useRoute();
const uploadedID = route.query.id;

// html组件ref, 加listener的
const splitterRef = ref();
const leftRef = ref();
const rightRef = ref();
const doubleVideoRef = ref();
const player1Ref = ref();
const player2Ref = ref();

// 两个视频路径
const originUrl = ref("");
const analysedUrl = ref("");

const originStatus = ref(1);
// 分析进度
const analyseStatus = ref(0);
const analyseProgress = ref(0);

let timer = null;

const uploadRTSPStream = () => {
  message.error('todo');
};
const startAnalysis = () => {
  message.error('todo');
};

const syncVideo = (op, srcPlayerID, extra) => {
  let destPlayer = null;
  if (srcPlayerID === 1) destPlayer = player2Ref.value
  else destPlayer = player1Ref.value
  if (op === 'play') {
    destPlayer.playVideo();
  } else if (op === 'pause') {
    destPlayer.pauseVideo();
  } else if (op === 'seeked') {
    const newTime = extra.newTime
    destPlayer.seekVideo(newTime);
  }
}

const uploadFile = async (fileData) => {
  emit("addFile", {file: fileData.file, filePid: -2});
}

const isShowAnalysedVideo = () => {
  return analyseStatus.value === 2 || analyseStatus.value === 3
}

const fetchProcess = () => {
  if (originStatus.value === 1) {
    httpRequest.get(`/directory/FileInfo/id/${fileInfo.value.id}`).then(({data}) => {
      if (data.code !== 0) return
      fileInfo.value = data.data;
      originStatus.value = fileInfo.value.file_status
      if (originStatus.value === 0) {
        originUrl.value = `/directory/ts/getVideoInfo/${data.data.id}`;
      }
    })
  }


  if (analyseStatus.value !== 3) {
    httpRequest.get(`/analyse/getAnalyseProcess/${fileInfo.value.file_uid}`).then(({data}) => {
      if (data.code !== 0) return
      data = data.data;
      analyseStatus.value = data.analyseStatus
      if (analyseStatus.value === 3) {
        analysedUrl.value = `/directory/ts/getVideoInfo/${fileInfo.value.id}?analysed=true`;
        analyseProgress.value = 100;
      } else if (analyseStatus.value === 2) {
        analysedUrl.value = `/directory/ts/getVideoInfo/${fileInfo.value.id}?analysed=true`;
        analyseProgress.value = data.finished / data.total * 100;
      } else {
        analyseProgress.value = 0;
      }
    })
  }
}

const uploadDone = ({fileUID, ty, fileID}) => {
  let url = ''
  if (ty === 'id') {
    url = `/directory/FileInfo/id/${fileID}`
  } else {
    url = `/directory/FileInfo/uid/${fileUID}`
  }
  httpRequest.get(url).then(({data}) => {
    if (data.code == null || data.code !== 0) {
      throw new Error(data.msg);
    }
    fileInfo.value = data.data;
    fetchProcess()
    timer = setInterval(() => {
      fetchProcess()
    }, 5000)
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

onMounted(() => {
  if (uploadedID) {
    console.log(uploadedID)
    uploadDone({
      ty: 'id',
      fileID: uploadedID
    })
  }
});

onUnmounted(() => {
  removeListener();
  if (timer) {
    clearInterval(timer);
  }
});

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

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 100px;
}

.percentage-value {
  display: block;
  margin-top: 10px;
  font-size: 28px;
}

.percentage-label {
  display: block;
  margin-top: 10px;
  font-size: 12px;
}
</style>
