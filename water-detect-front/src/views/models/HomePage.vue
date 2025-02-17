<template>
  <!--<TheWelcome/>-->
  <el-upload
      class="avatar-uploader"
      action="https://run.mocky.io/v3/9d059bf9-4660-45f2-925d-ce80ad6c4d15"
      v-bind:data="{ FoldPath: '上传目录', SecretKey: '安全验证' }"
      v-bind:on-progress="uploadVideoProcess"
      v-bind:on-success="handleVideoSuccess"
      v-bind:before-upload="beforeUploadVideo"
      v-bind:show-file-list="false"
      :headers="headers"
  >
    <video
        v-if="videoForm.showVideoPath != '' && !videoFlag"
        v-bind:src="videoForm.showVideoPath"
        class="avatar video-avatar"
        controls="controls">
      您的浏览器不支持视频播放
    </video>
    <i v-else-if="videoForm.showVideoPath == '' && !videoFlag"
       class="el-icon-plus avatar-uploader-icon"
    ></i>
    <el-progress v-if="videoFlag == true" type="circle"
                 v-bind:percentage="videoUploadPercent"
                 style="margin-top: 7px"></el-progress>
  </el-upload>
</template>
<script setup>

import TheWelcome from "@/components/TheWelcome.vue";
import {ref} from "vue";

const videoFlag = ref(false)
//是否显示进度条
const videoUploadPercent = ref("")
//进度条的进度，
const isShowUploadVideo = ref(false)
//显示上传按钮
const videoForm = ref({
  showVideoPath: "",  //回显的变量
})

//上传前回调
const beforeUploadVideo = (file) => {
  var fileSize = file.size / 1024 / 1024 < 50;   //控制大小  修改50的值即可
  if (
      [
        "video/mp4",
        "video/ogg",
        "video/flv",
        "video/avi",
        "video/wmv",
        "video/rmvb",
        "video/mov",
      ].indexOf(file.type) == -1     //控制格式
  ) {
    layer.msg("请上传正确的视频格式");
    return false;
  }
  if (!fileSize) {
    layer.msg("视频大小不能超过50MB");
    return false;
  }
  isShowUploadVideo.value = false;
}
//进度条
const uploadVideoProcess = (event, file, fileList) => {    //注意在data中添加对应的变量名
  videoFlag.value = true;
  videoUploadPercent.value = file.percentage.toFixed(0) * 1;
}
//上传成功回调
const handleVideoSuccess = (res, file) => {
  isShowUploadVideo.value = true;
  videoFlag.value = false;
  videoUploadPercent.value = 0;

  console.log(res);
  //后台上传数据
  if (res.success == true) {
    videoForm.value.showVideoPath = res.data.url;    //上传成功后端返回视频地址 回显
  } else {
    this.$message.error("上传失败！");
  }
}


</script>

<style scoped>
.avatar-uploader-icon {
  border: 1px dashed #d9d9d9 !important;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9 !important;
  border-radius: 6px !important;
  position: relative !important;
  overflow: hidden !important;
}

.avatar-uploader .el-upload:hover {
  border: 1px dashed #d9d9d9 !important;
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 300px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  width: 300px;
  height: 178px;
  display: block;
}
</style>
