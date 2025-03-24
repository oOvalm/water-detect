<template>
  <div class="share">
    <div class="header">
      <div class="header-content">
        <div class="logo" @click="jump">
          <span class="iconfont icon-pan"></span>
          <span class="name">水域检测系统 - 文件分享</span>
        </div>
      </div>
    </div>
    <div class="share-body">
      <template v-if="Object.keys(shareInfo).length === 0">
        <div
            v-loading="Object.keys(shareInfo).length === 0"
            class="loading"
        ></div>
      </template>
      <template v-else>
        <div class="share-panel">
          <div class="share-user-info">
            <div class="avatar">
              <el-avatar v-if="shareUserInfo.avatar && shareUserInfo.avatar.length > 0" :size="80"
                         :src="`/api/${shareUserInfo.avatar}`"/>
              <el-avatar v-else :size="80" src='https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'/>
            </div>
            <div class="share-info">
              <div class="user-info">
                <span class="nick-name">{{ shareUserInfo.username }} </span>
                <span class="share-time">分享于 {{ formatDate(shareUserInfo.share_time) }}</span>
              </div>
              <div class="file-name">分享文件：{{ shareUserInfo.filename }}</div>
            </div>
          </div>
          <div class="share-op-btn">
            <el-button
                type="primary"
                v-if="shareInfo.currentUser"
                @click="cancelShare"
            ><span class="iconfont icon-cancel"></span>取消分享
            </el-button
            >
            <el-button
                v-else
                type="primary"
                :disabled="selectFileIdList.length === 0"
                @click="save2MyPan"
            ><span class="iconfont icon-import"></span
            >保存到我的网盘
            </el-button
            >
          </div>
        </div>
        <!--导航-->
        <Navigation
            ref="navigationRef"
            @navChange="navChange"
            :shareId="shareId"
        ></Navigation>
        <div class="file-list">
          <Table
              :columns="columns"
              :showPagination="true"
              :dataSource="tableData"
              :fetch="loadDataList"
              :initFetch="false"
              :options="tableOptions"
              :showPageSize="false"
              @rowSelected="rowSelected"
          >
            <template #filename="{ index, row }">
              <div
                  class="file-item"
                  @mouseenter="showOp(row)"
                  @mouseleave="cancelShowOp(row)"
              >
                <template
                    v-if="(row.file_type === 2 || row.file_type === 3)"
                >
                  <icon :cover="row.id" :width="32"></icon>
                </template>
                <template v-else>
                  <icon :fileType="row.file_type"></icon>
                </template>
                <span class="file-name" :title="row.filename">
                  <span @click="preview(row)">{{ row.filename }}</span>
                </span>
                <span class="op">
                  <span
                      v-if="row.file_type !== 1"
                      class="iconfont icon-download"
                      @click="download(row.id)"
                  >下载</span
                  >
                  <template v-if="row.showOp && !shareInfo.currentUser">
                    <span
                        class="iconfont icon-import"
                        @click="save2MyPanSingle(row)"
                    >保存到我的网盘</span
                    >
                  </template>
                </span>
              </div>
            </template>
            <template #size="{ index, row }">
              <span v-if="row.file_type !== 1">
                {{ Utils.size2Str(row.size) || 0 }}
              </span>
            </template>
          </Table>
        </div>
      </template>
      <!--选择目录-->
      <FolderSelect
          ref="folderSelectRef"
          @folderSelect="save2MyPanDone"
          buttonText="保存到此"
      ></FolderSelect>
      <!--预览-->
      <Preview ref="previewRef"></Preview>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, getCurrentInstance, watch} from "vue";
import {useRouter, useRoute} from "vue-router";
import httpRequest from "@/api/httpRequest.ts";
import message from "@/utils/Message.js";
import FolderSelect from "@/components/FolderSelect.vue";
import Preview from "@/components/preview/Preview.vue"
import Icon from "@/components/Icon.vue";
import Navigation from "@/components/Navigation.vue";
import * as Utils from "@/utils/Utils.ts";
import Confirm from "@/utils/Confirm.js";
import {formatDate} from "@/utils/Utils.ts";
import Table from "@/components/Table.vue"

const router = useRouter();
const route = useRoute();
const api = {
  getShareInfo: "/share/web/getShareInfo",
  getShareLoginInfo: "/share/web/getShareLoginInfo",
  loadFileList: "/share/web/loadFileList",
  createDownloadUrl: "/directory/createDownload",
  download: "/api/directory/download",
  cancelShare: "/share/cancelShare",
  saveShare: "/share/web/saveShare",
};
const currentUserID = ref(-1);
const shareId = route.params.shareId;
const shareInfo = ref({});
const shareUserInfo = ref({})

//列表
const columns = [
  {
    label: "文件名",
    prop: "filename",
    scopedSlots: "filename",
  },
  {
    label: "修改时间",
    prop: "update_time",
    width: 200,
  },
  {
    label: "大小",
    prop: "size",
    scopedSlots: "size",
    width: 200,
  },
];
const currentFolder = ref({fileId: 0});
const tableData = ref({});
const tableOptions = {
  extHeight: 80,
  selectType: "checkbox",
};

const loadDataList = async () => {
  let params = {
    pageNo: tableData.value.pageNo ? tableData.value.pageNo : 1,
    pageSize: tableData.value.pageSize ? tableData.value.pageSize : 20,
    shareId: shareId,
    filePid: currentFolder.value.fileId,
  };
  httpRequest(api.loadFileList, {params: params}).then(({data}) => {
    tableData.value = data.data;
    const formattedData = data.data.list.map(row => {
      row.update_time = formatDate(row.update_time);
      return row;
    });
    tableData.value.list = formattedData
  }).catch((e) => {
    message.error("加载数据失败");
    console.log(e);
  })
};

const getShareInfo = async () => {
  if (localStorage.getItem('userID')) {
    currentUserID.value = Number(localStorage.getItem('userID'));
  }
  let config = {
    showLoading: false,
    params: {shareId}
  };
  httpRequest.get(api.getShareLoginInfo, config).then(({data}) => {
    if (data.code !== 0) throw data.msg;
    shareInfo.value = data.data;
    shareInfo.value.currentUser = (shareInfo.value.user_id === currentUserID.value);
    loadDataList();
    httpRequest.get(api.getShareInfo, {params: {shareId: shareId}}).then(({data}) => {
      if (data.code !== 0) throw data.msg;
      shareUserInfo.value = data.data;
    }).catch((e) => {
      message.error('获取用户信息失败');
      console.log(e);
    })
  }).catch((e) => {
    router.push("/shareCheck/" + shareId);
  });
};
getShareInfo();


//展示操作按钮
const showOp = (row) => {
  tableData.value.list.forEach((element) => {
    element.showOp = false;
  });
  row.showOp = true;
};

const cancelShowOp = (row) => {
  row.showOp = false;
};

//多选 批量选择
const selectFileIdList = ref([]);
const rowSelected = (rows) => {
  selectFileIdList.value = [];
  rows.forEach((item) => {
    selectFileIdList.value.push(item.id);
  });
};

//目录
const navChange = (data) => {
  const {curFolder} = data;
  currentFolder.value.fileId = curFolder.id;
  loadDataList();
};

//查看
const previewRef = ref();
const navigationRef = ref();
const preview = (data) => {
  console.log(data);
  if (data.file_type === 1) {
    navigationRef.value.openFolder(data);
    return;
  }
  data.shareId = shareId;
  previewRef.value.showPreview(data, 2);
};

//下载文件
const download = async (fileId) => {
  httpRequest.get(`${api.createDownloadUrl}/${fileId}`).then(({data}) => {
    if (data.code !== 0) throw data.msg
    window.location.href = "/api/directory/download/" + data.data.code;
  }).catch((e) => {
    message.error("获取下载链接错误")
  })
};

//保存到我的网盘
const folderSelectRef = ref();
const save2MyPanFileIdArray = [];
const save2MyPan = () => {
  console.log(selectFileIdList.value)
  if (selectFileIdList.value.length === 0) {
    return;
  }
  if (!localStorage.getItem("jwt")) {
    router.push("/login?redirectUrl=" + route.path);
    return;
  }
  save2MyPanFileIdArray.values = selectFileIdList.value;
  folderSelectRef.value.showFolderDialog();
};
const save2MyPanSingle = (row) => {
  if (!localStorage.getItem("jwt")) {
    router.push("/login?redirectUrl=" + route.path);
    return;
  }
  save2MyPanFileIdArray.values = [row.id];
  folderSelectRef.value.showFolderDialog();
};
//执行保存操作
const save2MyPanDone = async (folderId) => {
  httpRequest.post(api.saveShare, {
    shareId: shareId,
    shareFileIds: save2MyPanFileIdArray.values,
    filePid: folderId,
  }).then(({data}) => {
    if (data.code !== 0) throw data.msg;
    message.success("保存成功");
    folderSelectRef.value.close();
  }).catch((e) => {
    message.error("保存失败");
    console.error(e);
  });
};

//取消分享
const cancelShare = () => {
  Confirm(`你确定要取消分享吗？`, async () => {
    let data = {
      shareIds: shareId,
    }
    httpRequest.post(api.cancelShare, data).then(({data}) => {
      if (data.code !== 0) {
        message.error(`取消分享失败, ${data.msg}`)
      }
      message.success("取消分享成功");
      jump();
    }).catch((e) => {
      message.error(`取消分享失败, ${data.msg}`)
      console.log(e)
    });
  });
};

const jump = () => {
  router.push("/");
};
</script>

<style lang="scss" scoped>
@use "@/assets/file.list.scss";

.header {
  width: 100%;
  position: fixed;
  background: #0c95f7;
  height: 50px;

  .header-content {
    width: 70%;
    margin: 0px auto;
    color: #fff;
    line-height: 50px;

    .logo {
      display: flex;
      align-items: center;
      cursor: pointer;

      .icon-pan {
        font-size: 40px;
      }

      .name {
        font-weight: bold;
        margin-left: 5px;
        font-size: 25px;
      }
    }
  }
}

.share-body {
  width: 70%;
  margin: 0px auto;
  padding-top: 50px;

  .loading {
    height: calc(100vh / 2);
    width: 100%;
  }

  .share-panel {
    margin-top: 20px;
    display: flex;
    justify-content: space-around;
    border-bottom: 1px solid #ddd;
    padding-bottom: 10px;

    .share-user-info {
      flex: 1;
      display: flex;
      align-items: center;

      .avatar {
        margin-right: 5px;
      }

      .share-info {
        .user-info {
          display: flex;
          align-items: center;

          .nick-name {
            font-size: 15px;
          }

          .share-time {
            margin-left: 20px;
            font-size: 12px;
          }
        }

        .file-name {
          margin-top: 10px;
          font-size: 12px;
        }
      }
    }
  }
}

.file-list {
  margin-top: 10px;

  .file-item {
    .op {
      width: 170px;
    }
  }
}
</style>
