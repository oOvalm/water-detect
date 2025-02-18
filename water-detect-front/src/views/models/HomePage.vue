<template>
  <div>
    <el-upload
        ref="uploadRef"
        action="#"
        :auto-upload="false"
        :multiple="true"
        :before-upload="beforeUpload"
        accept=".mp4"
        :file-list="fileList"
        @change="handleFileChange"
        :show-file-list="false"
    >
      <el-button type="primary">选择 MP4 文件</el-button>
    </el-upload>
    <div v-if="fileList.length > 0">
      <h3>选择的视频文件信息</h3>
      <el-table :data="fileList" stripe>
        <el-table-column prop="thumbnail" label="缩略图">
          <template #default="{ row }">
            <img :src="row.thumbnail" alt="视频缩略图" width="100">
          </template>
        </el-table-column>
        <el-table-column prop="name" label="文件名"></el-table-column>
        <el-table-column prop="duration" label="时长">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="size" label="文件大小">
          <template #default="{ row }">
            {{ size2Str(row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="removeFile(row)">取消上传</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button type="primary" @click="uploadFiles">确定上传</el-button>
    </div>
    <el-progress v-if="uploading" :percentage="uploadProgress"></el-progress>
  </div>
</template>

<script setup>
import {ref} from 'vue';
import {ElUpload, ElButton, ElTable, ElTableColumn, ElProgress} from 'element-plus';
import {formatDuration, size2Str} from "@/utils/Utils.ts";

const uploadRef = ref(null);
const fileList = ref([]);
const uploading = ref(false);
const uploadProgress = ref(0);

// 上传前的钩子函数
const beforeUpload = (file) => {
  return file.type === 'video/mp4';
};

// 处理文件选择变化
const handleFileChange = async (file, newFileList) => {
  const newFiles = [];
  for (const fileItem of newFileList) {
    console.log(fileItem.raw)
    console.log(file.raw instanceof File)
    const duration = await getVideoDuration(fileItem.raw);
    const thumbnail = await getVideoThumbnail(fileItem.raw);
    newFiles.push({
      ...fileItem,
      duration,
      thumbnail,
    });
  }
  fileList.value = newFiles;
};

// 获取视频时长
const getVideoDuration = (file) => {
  return new Promise((resolve) => {
    const video = document.createElement('video');
    video.preload = 'metadata';
    video.src = URL.createObjectURL(file);
    video.onloadedmetadata = () => {
      URL.revokeObjectURL(video.src);
      resolve(video.duration);
    };
  });
};

// 获取视频缩略图
const getVideoThumbnail = (file) => {
  return new Promise((resolve) => {
    const video = document.createElement('video');
    video.preload = 'metadata';
    video.src = URL.createObjectURL(file);

    video.onloadedmetadata = () => {
      const duration = video.duration;
      const randomTime = Math.random() * duration;

      // 设置视频当前时间为随机时间点
      video.currentTime = randomTime;

      if ('requestVideoFrameCallback' in video) {
        video.requestVideoFrameCallback(() => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          URL.revokeObjectURL(video.src);
          resolve(canvas.toDataURL('image/jpeg'));
        });
      } else {
        console.warn('当前浏览器不支持 requestVideoFrameCallback，尝试备用方案');
        // 可以在这里添加备用方案，如下面的 setTimeout 方式
      }
    };

    video.onerror = () => {
      console.error('视频加载出错');
      resolve('');
    };
  });
};

// 移除文件
const removeFile = (file) => {
  const index = fileList.value.findIndex((f) => f.uid === file.uid);
  if (index !== -1) {
    fileList.value.splice(index, 1);
  }
};

// 上传文件
const uploadFiles = () => {
  uploading.value = true;
  const formData = new FormData();
  fileList.value.forEach((file) => {
    formData.append('videos', file.raw);
  });

  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/upload', true);
  xhr.upload.addEventListener('progress', (event) => {
    if (event.lengthComputable) {
      uploadProgress.value = (event.loaded / event.total) * 100;
    }
  });
  xhr.onreadystatechange = () => {
    if (xhr.readyState === 4 && xhr.status === 200) {
      uploading.value = false;
      window.location.href = '/';
    }
  };
  xhr.send(formData);
};
</script>

<style scoped>
/* 可以添加一些自定义样式 */
</style>
