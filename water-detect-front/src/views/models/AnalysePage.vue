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
      <template #trigger>
        <el-button type="primary">上传 MP4 文件</el-button>
      </template>
      <template #default>
        <el-button style="margin-left:10px" type="danger" @click="clearList">清空列表</el-button>
      </template>
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
          <template #default="{ item }">
            <div class="op-btn">
            <span v-if="item.status === STATUS.uploading.value">
              <icon
                  :width="28"
                  class="btn-item"
                  iconName="upload"
                  v-if="item.pause"
                  title="上传"
                  @click="startUpload(item.uid)"
              ></icon>
              <icon
                  :width="28"
                  class="btn-item"
                  iconName="pause"
                  title="暂停"
                  @click="pauseUpload(item.uid)"
                  v-else
              ></icon>
            </span>
              <icon
                  :width="28"
                  class="del btn-item"
                  iconName="del"
                  title="删除"
                  v-if="
                item.status !== STATUS.init.value &&
                item.status !== STATUS.upload_finish.value &&
                item.status !== STATUS.upload_seconds.value
              "
                  @click="delUpload(item.uid, index)"
              ></icon>
              <icon
                  :width="28"
                  class="clean btn-item"
                  iconName="clean"
                  title="清除"
                  v-if="
                item.status === STATUS.upload_finish.value ||
                item.status === STATUS.upload_seconds.value
              "
                  @click="delUpload(item.uid, index)"
              ></icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="文件大小">
          <template #default="{ row }">
            {{ size2Str(row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="上传进度">
          <template #default="{ row }">
            <el-progress :status="row.uploadStatus"
                         :percentage="row.uploadProgress ?? 0.0"></el-progress>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue';
import {ElButton, ElMessage, ElProgress, ElTable, ElTableColumn, ElUpload} from 'element-plus';
import {formatDuration, size2Str} from "@/utils/Utils.ts";
import httpRequest from "@/api/httpRequest.ts";
import router from "@/router/index.js";
import {Exception} from "sass";
import message from "@/utils/Message.js";
import Icon from "@/components/Icon.vue";

const uploadRef = ref(null);
const fileList = ref([]);
const uploadProgress = ref(0);

const STATUS = {
  emptyfile: {
    value: "emptyfile",
    desc: "文件为空",
    color: "#F75000",
    icon: "close",
  },
  fail: {
    value: "fail",
    desc: "上传失败",
    color: "#F75000",
    icon: "close",
  },
  init: {
    value: "init",
    desc: "解析中",
    color: "#e6a23c",
    icon: "clock",
  },
  uploading: {
    value: "uploading",
    desc: "上传中",
    color: "#409eff",
    icon: "upload",
  },
  upload_finish: {
    value: "upload_finish",
    desc: "上传完成",
    color: "#67c23a",
    icon: "ok",
  },
  upload_seconds: {
    value: "upload_seconds",
    desc: "秒传",
    color: "#67c23a",
    icon: "ok",
  },
};

// 上传前的钩子函数
const beforeUpload = (file) => {
  return file.type === 'video/mp4';
};

// 处理文件选择变化
const handleFileChange = async (file, newFileList) => {
  const newFiles = [];
  for (const fileItem of newFileList) {
    const duration = await getVideoDuration(fileItem.raw);
    const thumbnail = await getVideoThumbnail(fileItem.raw);
    newFiles.push({
      file: fileItem,
      duration,
      thumbnail,
      uid: fileItem.uid,
      pause: false,
      status: STATUS.uploading.value,
      chunkIndex: 0,
      filePid
    });
  }
  fileList.value = newFiles;
  console.log(fileList.value)
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

const clearList = () => {
  fileList.value = [];
}

// 上传文件
const uploadFiles = async () => {
  const uploadPromises = [];
  console.log(fileList.value)
  for (const file of fileList.value) {
    if (file.upload !== 2) {
      uploadPromises.push(uploadSingleFile(file));
    }
  }
  if (uploadPromises.length === 0) {
    message.warning("没有文件需要上传")
  }
  try {
    await Promise.all(uploadPromises);
  } catch (error) {
    console.error('部分文件上传失败:', error);
    message.warning('文件上传失败')
    return
  }
  if (fileList.value.length === 1 && uploadPromises.length === 1) {
    message.success("文件上传完成！检测到上传单个文件，跳转至分析预览页面")
    router.push("/analyse/detail")
    return
  }
  message.success("文件上传完成！")
};

// 上传单个文件
const uploadSingleFile = async (file) => {
  return new Promise((resolve, reject) => {
    console.log(file)
    file.upload = 1;
    const formData = new FormData();
    formData.append('video', file.raw);
    httpRequest.post('/directory/video', formData, {
      onUploadProgress: (progressEvent) => {
        file.uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      },
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    }).then(({data}) => {
      data = JSON.parse(data)
      if (data.code !== 0) {
        throw data.msg
      }
      file.uploadStatus = 'success'
      file.id = data.data.fileID
      resolve()
    }).catch((error) => {
      console.error('文件上传出错:', error);
      file.upload = 2;
      file.uploadStatus = 'exception'
      reject(error)
    });
  })
};

</script>

<style scoped>
/* 可以添加一些自定义样式 */
</style>
