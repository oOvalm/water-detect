<template>
  <el-header class="home-header">
    <!-- 左边图标 -->
    <div class="left-icon">
      <span class="iconfont icon-pan"></span>
      <span class="name">xxx logo</span>
    </div>
    <!-- 右边头像及下拉框 -->
    <div class="right-avatar">
      <el-popover
          :width="800"
          trigger="click"
          :visible="showUploader"
          :offset="20"
          transition="none"
          :hide-after="0"
          :popper-style="{ padding: '0px' }"
      >
        <template #reference>
          <span class="iconfont icon-transfer" @click="()=>{emit('changeUploader')}"></span>
        </template>
        <template #default>
          <Uploader
              ref="uploaderRef"
              @uploadCallback="uploadCallbackHandler"
          ></Uploader>
        </template>
      </el-popover>
      <el-dropdown>
        <span class="el-dropdown-link">
          <img src="@/assets/qq.png" alt="Avatar" class="avatar"/>
          {{ username }}
          <el-icon class="el-icon--right"><arrow-down/></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item :icon="Avatar">个人中心</el-dropdown-item>
            <el-dropdown-item :icon="InfoFilled">关于</el-dropdown-item>
            <el-dropdown-item :icon="SwitchButton" @click="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>


<script setup>
import {nextTick, onMounted, ref} from 'vue';
import {ArrowDown, Avatar, CirclePlus, InfoFilled, SwitchButton} from "@element-plus/icons-vue";
import router from "@/router/index.js";
import httpRequest from "@/api/httpRequest.ts";
import Uploader from "@/components/header/Uploader.vue";

const emit = defineEmits(['uploadCallback', 'changeUploader']);
const props = defineProps({
  showUploader: {
    type: Boolean,
    default: false,
  },
})
const uploadCallbackHandler = () => {
  emit("uploadCallback");
}
const uploaderRef = ref();
const addFile = (file, filePid) => {
  uploaderRef.value.addFile(file, filePid);
};
defineExpose({addFile});

const username = ref()
const logout = () => {
  localStorage.removeItem("jwt");
  router.push("/login");
}
onMounted(() => {
  httpRequest.get("account/selfInfo").then(({data}) => {
    if (data.code == null || data.code !== 0) {
      logout()
    } else {
      username.value = data.data.username
    }
  }).catch((e) => {
    console.log(e);
    logout();
  })
})
</script>

<style scoped lang="scss">
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #f5f5f5;
  height: 60px;
}

.left-icon {
  display: flex;
  align-items: center;

  .icon-pan {
    font-size: 40px;
    color: #1296db;
  }

  .name {
    font-weight: bold;
    margin-left: 5px;
    font-size: 25px;
    color: #05a1f5;
  }
}

.right-avatar {
  position: relative;
  color: #222222;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  cursor: pointer;
}
</style>
