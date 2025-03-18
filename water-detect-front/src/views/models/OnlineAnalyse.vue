<template>
  <div class="top">
    <div class="top-op">
      <el-button class="btn" type="primary" @click="uploadRTSPStream">RTSP流</el-button>
      <!--      <el-button class="btn" type="success" @click="startAnalysis">开始分析</el-button>-->
      <el-button class="btn" type="primary" @click="switchSync">{{ isSyncVideo ? "取消同步" : "开启同步" }}</el-button>
      <el-progress type="dashboard" :percentage="analyseProgress" v-if="fileInfo.id">
        <template #default="{ percentage }">
          <span class="percentage-value">{{ percentage }}%</span>
          <span class="percentage-label">分析进度</span>
        </template>
      </el-progress>
    </div>
  </div>
  <div class="video-container" v-if="fileInfo.id">
    <DoubleVideo
        style="width: 100%"
        :originUrl="originUrl"
        :analysedUrl="analysedUrl"
        :show-origin="originStatus === 0"
        :show-analysed="isShowAnalysedVideo()"
        :is-sync="isSyncVideo"
    ></DoubleVideo>
  </div>
  <div v-else>
    <el-upload
        :multiple="false"
        :show-file-list="false"
        drag
        :http-request="uploadFile"
        accept="video/*,image/*"
    >
      <el-icon class="el-icon--upload">
        <upload-filled/>
      </el-icon>
      <div class="el-upload__text">
        拖动文件到此处或 <em>点击上传文件</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          仅支持视频, 图片
        </div>
      </template>
    </el-upload>
  </div>
  <Dialog :show="streamDialogConfig.show" :title="streamDialogConfig.title" @close="cancelStream"
          :buttons="streamDialogConfig.buttons" width="600px">
    <el-form :model="streamDialogConfig.formData">

      <el-form-item prop="streamName" label="串流key">
        <div class="stream-key-panel">
          <el-input clearable v-model.trim="streamDialogConfig.formData.streamName"></el-input>
          <!--          <el-button class="btn" @click="getStreamKey">我的串流key</el-button>-->
        </div>
      </el-form-item>
    </el-form>
  </Dialog>
</template>

<script setup>
import {ref, onMounted, onUnmounted, watch, nextTick} from 'vue';
import message from "@/utils/Message.js";
import httpRequest from "@/api/httpRequest.ts";
import {Loading, UploadFilled, WarningFilled} from "@element-plus/icons-vue";
import Preview from "@/components/preview/Preview.vue";
import PreviewVideo from "@/components/preview/PreviewVideo.vue";
import {useRoute} from "vue-router";
import DoubleVideo from "@/components/DoubleVideo.vue";
import Dialog from "@/components/Dialog.vue";
import {ElMessageBox} from "element-plus";
import {RTMP_HOST} from "@/constants";

const emit = defineEmits(["addFile"]);
const fileInfo = ref({}); // 原始文件信息

const route = useRoute();
const uploadedID = route.query.id;

// 两个视频路径
const originUrl = ref("");
const analysedUrl = ref("");

const originStatus = ref(1);
// 分析进度
const analyseStatus = ref(0);
const analyseProgress = ref(0);

// 是否同步两侧
const isSyncVideo = ref(true);

let timer = null;
const streamDialogConfig = ref({
  show: false,
  title: "连接在线流",
  formData: {
    streamName: "",
  },
  buttons: [
    {
      type: "primary",
      click: () => {
        playStream();
      },
      text: "播放",
    },
  ]
})
const getStreamKey = () => {
  httpRequest.get("/stream/getMyStreamKey").then(({data}) => {
    if (data.code !== 0) throw data.msg
    ElMessageBox.alert(`获取串流可以成功, 你的串流key为${data.data.key}\n服务器连接: ${RTMP_HOST}`, '获取串流key成功', {confirmButtonText: 'OK'});
    if (streamDialogConfig.value.formData.streamName === "") {
      streamDialogConfig.value.formData.streamName = data.data.key;
    }
  })
}
const uploadRTSPStream = () => {
  streamDialogConfig.value.show = true;
};
const cancelStream = () => {
  streamDialogConfig.value.show = false;
}
const playStream = () => {
  message.info(`confirm, ${streamDialogConfig.value.formData.streamName}`)
}

const startAnalysis = () => {
  message.error('todo');
};

const switchSync = async () => {
  isSyncVideo.value = !isSyncVideo.value;
  localStorage.setItem("isSyncVideo", isSyncVideo.value);
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
        analyseProgress.value = (data.finished / data.total * 100).toFixed(2);
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
    console.log(originUrl.value)
    timer = setInterval(() => {
      fetchProcess()
    }, 5000)
  }).catch((e) => {
    console.log(e)
  })
}
defineExpose({uploadDone});

// watch(fileInfo, (newVal) => {
//   if (newVal) {
//     console.log(newVal);
//     nextTick(() => {
//       if (newVal.id) {
//         addListener();
//       }
//     })
//   }
// })


onMounted(() => {
  let tmp = localStorage.getItem("isSyncVideo")
  console.log(tmp);
  if (tmp !== null) {
    isSyncVideo.value = tmp === "true";
  }
  if (uploadedID) {
    console.log(uploadedID)
    uploadDone({
      ty: 'id',
      fileID: uploadedID
    })
  }
});

onUnmounted(() => {
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
  display: flex;
  height: 300px;
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


.stream-key-panel {
  display: flex;
  width: 100%;
  justify-content: space-between;

  .btn {
    margin-left: 5px;
  }
}
</style>
