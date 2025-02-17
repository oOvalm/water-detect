<template>
  <div>
    <el-upload
        ref="uploadRef"
        v-model:file-list="fileList"
        class="upload-demo"
        action="/api/"
        :auto-upload="false"
        :on-change="handleChange"
        :on-progress="handleProgress"
        multiple
    >
      <template #trigger>
        <el-button size="large" type="primary">选择视频</el-button>
      </template>
      <el-button style="margin-left: 10px" size="large" type="success" @click="submitUpload">上传视频</el-button>
      <template #tip>
        <div class="el-upload__tip">只能上传视频文件</div>
      </template>

      <!-- 自定义文件列表 -->
      <template #file="{ file }">
        <div class="slot-file">
          <!-- 显示视频缩略图 -->
          <img
              v-if="file.thumbnail"
              :src="file.thumbnail"
              alt="Video Thumbnail"
              class="video-thumbnail"
          />
          <div class="file-info">
            <div class="file-name">{{ file.name }}</div>
            <div class="file-size">{{ size2Str(file.size) }}</div>
            <div v-if="file.percentage" class="file-progress">{{ file.percentage }}%</div>
          </div>
          <el-button
              size="small"
              type="danger"
              @click="onRemove(file)"
          >删除
          </el-button>
        </div>
      </template>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import {getCurrentInstance, ref} from "vue";
import {ElMessage, ElMessageBox, UploadUserFile} from "element-plus";
import {size2Str} from '@/utils/Utils'
import type {UploadInstance} from 'element-plus'

const uploadRef = ref<UploadInstance>()
const {proxy} = getCurrentInstance();
const fileList = ref<UploadUserFile[]>([])
const submitUpload = () => {
  if (fileList.value.length > 0) {
    console.log(fileList.value)
    uploadRef.value.submit()
  } else {
    ElMessage.error('请选择文件后再上传')
  }
}


const onRemove = async (file) => {
  console.log(fileList.value)
  const index = fileList.value.findIndex((f) => f.uid === file.uid);
  console.log(fileList.value, index)
  if (index !== -1) {
    fileList.value.splice(index, 1);
  }
  // return ElMessageBox.confirm(
  //     `确定要删除 ${file.name} 吗？`
  // ).then(() => {
  //   return true;
  // }).catch(() => {
  //   return false;
  // });
};

const handleProgress = (event, file, fileList) => {
  const index = fileList.findIndex((f) => f.raw === file.raw);
  if (index !== -1) {
    fileList[index].percentage = event.percent;
  }
};

const handleChange = async (file, list) => {
  // console.log(list[0])
  // console.log(fileList)
  // getVideoThumbnail(file.raw).then((thumb) => {
  //   console.log(thumb);
  //   file.thumbnail = thumb;
  // }).catch((err) => {
  //   console.log(err)
  // })
};


const getVideoThumbnail = (videoFile) => {
  return new Promise((resolve) => {
    const videoUrl = URL.createObjectURL(videoFile);
    const videoElement = document.createElement('video');
    videoElement.src = URL.createObjectURL(videoFile);
    videoElement.src = videoUrl;
    videoElement.width = 640;
    videoElement.height = 360;
    videoElement.controls = true;
    videoElement.addEventListener("loadeddata", () => {
      const canvas = document.createElement("canvas");
      canvas.width = 640;
      canvas.height = 360;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
      const thumbnail = canvas.toDataURL("image/jpeg");
      URL.revokeObjectURL(videoElement.src);
      resolve(thumbnail);
    });
  });
};

</script>

<style scoped>
.upload-demo {
  .slot-file {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }

  .video-thumbnail {
    width: 100px;
    height: auto;
    margin-right: 10px;
  }

  .file-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
}
</style>
