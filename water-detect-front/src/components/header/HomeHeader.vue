<template>
  <el-header class="home-header">
    <div class="left-icon">
      <img src="../../assets/logo-nobg.png" alt="Logo" class="logo"/>
      <span class="name">水域检测平台</span>
    </div>
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
          <img :src="`/api/${userInfo.avatar}`" v-if="userInfo.avatar && userInfo.avatar.length > 0" alt="Avatar"
               class="avatar"/>
          <el-avatar v-else :size="80" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png"/>
          {{ userInfo.username }}
          <el-icon class="el-icon--right"><arrow-down/></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item :icon="Avatar" @click="gotoProfile">个人中心</el-dropdown-item>
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
const uploadCallbackHandler = (data) => {
  emit("uploadCallback", data);
}
const userInfo = ref({
  username: '',
  avatar: '',
});
const uploaderRef = ref();
const addFile = (file, filePid) => {
  uploaderRef.value.addFile(file, filePid);
};
const gotoProfile = () => {
  router.push('/profile')
}
const updateProfile = () => {
  httpRequest.get("account/selfInfo").then(({data}) => {
    if (data.code == null || data.code !== 0) {
      logout()
    } else {
      userInfo.value = data.data;
    }
  }).catch((e) => {
    console.log(e);
    logout();
  })
}
defineExpose({addFile, updateProfile});

const logout = () => {
  localStorage.removeItem("jwt");
  router.push("/login");
}

onMounted(() => {
  updateProfile()
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

  .logo {
    height: 40px;
    margin-right: 5px;
  }

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
