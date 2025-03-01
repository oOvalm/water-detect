<template>
  <el-container class="app-container">
    <!--  头部   -->
    <el-header>
      <home-header
          ref="homeHeader"
          @changeUploader="()=>{showUploader = !showUploader}"
          @uploadCallback="uploadCallbackHandler"
          :showUploader="showUploader"></home-header>
    </el-header>
    <el-container>
      <!--  侧边栏   -->
      <el-aside>
        <home-menu></home-menu>
      </el-aside>
      <el-main>
        <!--        <f-tag-list></f-tag-list>-->
        <router-view v-slot="{ Component }">
          <component
              @addFile="addFile"
              ref="routerViewRef"
              :is="Component"
          />
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import HomeHeader from "@/components/header/HomeHeader.vue";
import HomeMenu from "@/components/HomeMenu.vue";
import {nextTick, ref} from "vue";


const routerViewRef = ref();
const showUploader = ref(false);

const uploadCallbackHandler = () => {
  nextTick(() => {
    console.log("xxxx")
    // routerViewRef.value.reload();
  });
};
const homeHeader = ref()
const addFile = ({file, filePid}) => {
  showUploader.value = true
  homeHeader.value.addFile(file, filePid);
}

</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh; /* 占满整个视口高度 */
}

.el-aside {
  width: auto !important;
}
</style>
