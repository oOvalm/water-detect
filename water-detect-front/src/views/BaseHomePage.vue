
<template>
  <el-container>
    <!--  头部   -->
    <el-header>
      <home-header></home-header>
    </el-header>
    <el-container>
      <!--  侧边栏   -->
      <el-aside>
        <home-menu></home-menu>
      </el-aside>
      <el-main>
<!--        <f-tag-list></f-tag-list>-->
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>

import HomeHeader from "@/components/HomeHeader.vue";
import HomeMenu from "@/components/HomeMenu.vue";
</script>

<style scoped>

</style>
