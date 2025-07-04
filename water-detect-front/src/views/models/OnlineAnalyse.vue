<template>
  <div class="top">
    <div class="top-op">
      <div>
        <el-input class="stream-key-input" v-model="streamKey" placeholder="请输入 串流id"/>
        <el-button class="btn" type="primary" @click="uploadRTSPStream"> {{
            isStreaming ? '重新加载流' : '播放流'
          }}
        </el-button>
        <!--      <el-button class="btn" type="success" @click="startAnalysis">开始分析</el-button>-->
        <el-checkbox class="btn" v-model="isSyncVideo" label="是否同步两侧视频" @click="switchSync"/>
        <el-progress type="dashboard" :percentage="analyseProgress"
                     v-if="fileInfo.id && fileInfo.file_type === fileTypes.Video"
                     :status="analyseProgress >= 100?'success':''">
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">分析进度</span>
          </template>
        </el-progress>
      </div>
      <div>
        <el-form :model="fileInfo" v-if="fileInfo.id" size="small" class="file-info-form" title="当前为文件对比分析"
                 label-width="auto">
          <el-form-item label="文件名">
            <span>{{ fileInfo.filename }}</span>
          </el-form-item>
          <el-form-item label="文件类型">
            <span>{{ fileInfo.file_type === fileTypes.Video ? "视频" : "图片" }}</span>
          </el-form-item>
          <el-form-item label="文件大小">
            <span>{{ Utils.size2Str(fileInfo.size) || 0 }}</span>
          </el-form-item>
          <el-form-item label="上传时间">
            <span>{{ formatDate(fileInfo.create_time) }}</span>
          </el-form-item>
        </el-form>
        <el-form :model="streamInfo" v-if="streamInfo.id" size="small" class="file-info-form"
                 title="当前为实时检测对比分析" label-width="auto">
          <el-form-item label="串流id">
            <span>{{ streamInfo.id }}</span>
          </el-form-item>
          <el-form-item label="来自用户">
            <span>{{ streamInfo.username }}</span>
          </el-form-item>
          <el-form-item label="名称">
            <span>{{ streamInfo.stream_name }}</span>
          </el-form-item>
          <el-form-item label="详情">
            <span>{{ streamInfo.stream_description }}</span>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
  <div class="video-container" v-if="(fileInfo.id && fileInfo.file_type === fileTypes.Video) || isStreaming">
    <DoubleVideo
        style="width: 100%"
        :originUrl="originUrl"
        :analysedUrl="analysedUrl"
        :live="isStreaming"
        :show-origin="originStatus === 0 || isStreaming"
        :show-analysed="isShowAnalysedVideo()"
        :is-sync="isSyncVideo"
    ></DoubleVideo>
  </div>
  <div class="video-container" v-else-if="fileInfo.file_type === fileTypes.Image">
    <!--    <el-image :src="``"></el-image>-->
    <DoubleImage :originUrl="originUrl" :analysedUrl="analysedUrl"></DoubleImage>
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
</template>

<script setup>
import {ref, onMounted, onUnmounted, watch, nextTick, getCurrentInstance} from 'vue';
import message from "@/utils/Message.js";
import httpRequest from "@/api/httpRequest.ts";
import {Loading, UploadFilled, WarningFilled} from "@element-plus/icons-vue";
import Preview from "@/components/preview/Preview.vue";
import PreviewVideo from "@/components/preview/PreviewVideo.vue";
import {useRoute} from "vue-router";
import DoubleVideo from "@/components/DoubleVideo.vue";
import Dialog from "@/components/Dialog.vue";
import {ElButton, ElInput, ElMessageBox} from "element-plus";
import {RTMP_HOST} from "@/constants";
import DPlayer from "dplayer";
import Hls from "hls.js";
import DoubleImage from "@/components/DoubleImage.vue";
import * as Utils from "@/utils/Utils.ts";
import {formatDate} from "@/utils/Utils.ts";

const fileTypes = getCurrentInstance().appContext.config.globalProperties.$FileType

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
const streamKey = ref('');
const isStreaming = ref(false);
const showStreamAnalysed = ref(false);
const streamInfo = ref({});
const uploadRTSPStream = () => {
  fileInfo.value = {};
  httpRequest.get(`/stream/proxy/live/${streamKey.value}`).then(({data}) => {
    console.log(data)
    originUrl.value = `/stream/${data}`;
    isStreaming.value = true;
    httpRequest.get(`/stream/proxy/live/${streamKey.value}?analyse=true`).then(({data}) => {
      analysedUrl.value = `/stream/${data}`;
      showStreamAnalysed.value = true;
    })
  }).catch((e) => {
    console.log(e)
    message.error(`获取直播连接失败: ${e.response.data}`)
  })
  httpRequest.get('stream/streamkeyinfo/byid', {
    params: {id: streamKey.value},
  }).then(({data}) => {
    if (data.code !== 0) throw data.msg
    streamInfo.value = data.data
    httpRequest.get(`account/${streamInfo.value.user_id}`).then(({data}) => {
      if (data.code !== 0) return;
      streamInfo.value.username = data.data.username;
    })
  }).catch((e) => {
    message.error("获取流信息失败")
  })
};

const switchSync = async () => {
  localStorage.setItem("isSyncVideo", isSyncVideo.value);
}

const uploadFile = async (fileData) => {
  emit("addFile", {file: fileData.file, filePid: -2});
}
const isShowAnalysedVideo = () => {
  return analysedUrl.value !== '' || showStreamAnalysed.value
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

  if (analyseStatus.value !== 3 && analyseProgress.value !== 100) {
    httpRequest.get(`/analyse/getAnalyseProcess/${fileInfo.value.file_uid}`).then(({data}) => {
      if (data.code !== 0) return
      data = data.data;
      analyseStatus.value = data.analyseStatus
      if (analyseStatus.value === 3) {
        analyseProgress.value = 100;
      } else if (analyseStatus.value === 2) {
        analyseProgress.value = (data.finished / data.total * 100).toFixed(2);
      } else {
        analyseProgress.value = 0;
      }
    })
  }

  if (analysedUrl.value === '') {
    httpRequest.get(`/directory/ts/getVideoInfo/${fileInfo.value.id}?analysed=true`).then((resp) => {
      analysedUrl.value = `/directory/ts/getVideoInfo/${fileInfo.value.id}?analysed=true`;
    })
  }
}

const uploadDone = ({fileUID, ty, fileID}) => {
  streamInfo.value = {};
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
    console.log(data.data.file_type, fileTypes.Image)
    if (data.data.file_type === fileTypes.Video) {
      fileInfo.value = data.data;
      fetchProcess()
      console.log(originUrl.value)
      timer = setInterval(() => {
        fetchProcess()
      }, 5000)
    } else if (data.data.file_type === fileTypes.Image) {
      console.log(data.data)
      originUrl.value = `/api/directory/image?fileID=${data.data.id}`
      analysedUrl.value = `/api/directory/image?fileID=${data.data.id}&is_analysed=true`
      fileInfo.value = data.data;
    }
  }).catch((e) => {
    console.log(e)
  })
}
defineExpose({uploadDone});

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

.top-op {
  display: flex;
  justify-content: space-between; // 让子元素左右分布
  align-items: center;
}

.double-video-player {
  display: flex;
  height: 100%; /* 可根据需要调整高度 */
  width: 100%;
  --separator-left: 50%; /* 初始分隔条位置 */
}

.video-container {
  display: flex;
  height: 700px;
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

.stream-key-input {
  width: 200px;
}

.file-info-form {
  width: 500px;
  background-color: #f5f5f5f5;
}
</style>
