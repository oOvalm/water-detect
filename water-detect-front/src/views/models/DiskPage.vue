<template>
  <div>
    <div class="top">
      <div class="top-op">
        <div class="btn">
          <el-upload
              :show-file-list="false"
              :with-credentials="true"
              :multiple="true"
              :http-request="addFile"
              accept="image/*,video/*"
          >
            <el-button type="primary">
              <span class="iconfont icon-upload"></span>
              上传
            </el-button>
          </el-upload>
        </div>
        <el-button type="success" @click="newFolder">
          <span class="iconfont icon-folder-add"></span>
          新建文件夹
        </el-button>
        <el-button
            @click="delFileBatch"
            type="danger"
            :disabled="selectFileIdList.length === 0"
        >
          <span class="iconfont icon-del"></span>
          批量删除
        </el-button>
        <el-button
            @click="moveFolderBatch"
            type="warning"
            :disabled="selectFileIdList.length === 0"
        >
          <span class="iconfont icon-move"></span>
          批量移动
        </el-button>
        <div class="search-panel">
          <el-input
              clearable
              placeholder="输入文件名搜索"
              v-model="filenameSearchText"
              @keyup.enter="search"
          >
            <template #suffix>
              <i class="iconfont icon-search" @click="search"></i>
            </template>
          </el-input>
        </div>
        <div class="iconfont icon-refresh" @click="loadDataList"></div>
      </div>
      <!--导航-->
      <Navigation
          ref="navigationRef"
          @navChange="navChange"
          :watchPath="false"></Navigation>
    </div>
    <!-- ========================================================== -->

    <div class="file-list">
      <Table
          ref="dataTableRef"
          :columns="columns"
          :showPagination="true"
          :dataSource="tableData"
          :fetch="loadDataList"
          :initFetch="false"
          :options="tableOptions"
          @rowSelected="rowSelected"
          :border="true"
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
            <div class="edit-panel" v-if="row.showEdit">
              <el-input
                  v-model.trim="row.filenameReal"
                  ref="editNameRef"
                  :maxLength="190"
                  @keyup.enter="saveNameEdit(index)"
              >
              </el-input>
              <span
                  :class="[
                  'iconfont icon-right1',
                  row.filenameReal ? '' : 'not-allow',
                ]"
                  @click="saveNameEdit(index)"
              ></span>
              <span
                  class="iconfont icon-error"
                  @click="cancelNameEdit(index)"
              ></span>
            </div>
            <span class="op" v-if="!row.showEdit" :style="{width: row.showOp && row.id?'300px':'0px'}">
              <template v-if="row.showOp && row.id">
                <span class="iconfont icon-share1" @click="share(row)">分享</span>
                <span
                    class="iconfont icon-download"
                    @click="download(row)"
                    v-if="row.file_type !== 1"
                >下载</span
                >
                <span class="iconfont icon-del" @click="delFile(row)"
                >删除</span
                >
                <span
                    class="iconfont icon-edit"
                    @click.stop="editFileName(index)"
                >重命名</span
                >
                <span class="iconfont icon-move" @click="moveFolder(row)"
                >移动</span
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
        <template #moreOp="{index, row}">
          <span v-if="row.file_type !== 1 && !row.is_analysed">
            <el-button @click="openWithCompare(row)">进入对比页</el-button>
          </span>
        </template>
      </Table>
    </div>
    <FolderSelect
        ref="folderSelectRef"
        @folderSelect="moveFolderDone"
    ></FolderSelect>
    <Preview ref="previewRef"></Preview>
    <FileShare ref="shareRef"></FileShare>
  </div>
</template>

<script setup>

import FileShare from "@/views/share/ShareFile.vue";
import {nextTick, onMounted, ref} from "vue";
import httpRequest from "@/api/httpRequest.ts";
import message from "@/utils/Message.js";
import * as Utils from "@/utils/Utils.ts";
import Icon from "@/components/Icon.vue";
import Table from '@/components/Table.vue'
import FolderSelect from '@/components/FolderSelect.vue'
import {ElMessageBox} from "element-plus";
import Navigation from "@/components/Navigation.vue";
import Preview from "@/components/preview/Preview.vue";
import {useRouter} from "vue-router";
import {formatDate} from "@/utils/Utils.ts";

const emit = defineEmits(["addFile"]);
const showLoading = ref(false)
const addFile = async (fileData) => {
  emit("addFile", {file: fileData.file, filePid: currentFolder.value.fileID});
};
const reload = () => {
  showLoading.value = false;
  loadDataList();
};
const uploadDone = (data) => {
  reload();
}
defineExpose({
  uploadDone,
});

const shareRef = ref();
const share = (row) => {
  shareRef.value.show(row);
};
const currentFolder = ref({fileID: -1})
const tableData = ref({})
const filenameSearchText = ref();
const tableOptions = {
  extHeight: 50,
  selectType: "checkbox",
};
//列表
const columns = [
  {
    label: "文件名",
    prop: "filename",
    scopedSlots: "filename",
    width: 500,
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
  {
    label: '操作',
    scopedSlots: 'moreOp',
    width: 200,
  }
];

onMounted(() => {
  loadDataList()
})

const loadDataList = () => {
  let params = {
    pageNo: tableData.value.pageNo || 1,
    pageSize: tableData.value.pageSize || 20,
    filePid: currentFolder.value.fileID,
    searchFilename: filenameSearchText.value
  }
  httpRequest.get("/directory/fileList", {
    params
  }).then(({data}) => {
    if (data.code !== 0) {
      throw data.msg
    }
    tableData.value = data.data
    const formattedData = data.data.list.map(row => {
      row.update_time = formatDate(row.update_time);
      row.create_time = formatDate(row.create_time);
      return row;
    });
    tableData.value.list = formattedData
    console.log(tableData.value)
  }).catch((e) => {
    console.log(e);
    message.error("加载文件失败")
  })
}

const newFolder = () => {
  httpRequest.post("/directory/fileList", {
    filePid: currentFolder.value.fileID
  }).then(({data}) => {
    if (data.code !== 0) {
      throw data.msg;
    } else {
      loadDataList()
    }
  }).catch((e) => {
    message.error(e)
  })
}

//多选 批量选择
const selectFileIdList = ref([]);
const selectFileList = ref([]);
const rowSelected = (rows) => {
  selectFileList.value = rows;
  selectFileIdList.value = [];
  rows.forEach((item) => {
    selectFileIdList.value.push(item.id);
  });
};
const search = () => {
  loadDataList();
}

const editing = ref(false);
const editNameRef = ref();
const saveNameEdit = async (index) => {
  const {id, file_pid, filenameReal} = tableData.value.list[index];
  if (filenameReal === "" || filenameReal.indexOf("/") !== -1) {
    proxy.Message.warning("文件名不能为空且不能含有斜杠");
    return;
  }
  httpRequest.put("directory/fileList", {
    type: "rename",
    id: id,
    filePid: file_pid,
    newFileName: filenameReal,
  }).then(({data}) => {
    if (data.code !== 0) throw data.msg
    tableData.value.list[index] = data.data;
    editing.value = false;
    message.success("修改成功")
  }).catch((e) => {
    console.log(e);
    message.error("重命名失败")
    editing.value = false;
  })
};

//编辑文件名
const editFileName = (index) => {
  if (tableData.value.list[0].fileId === "") {
    tableData.value.list.splice(0, 1);
    index = index - 1;
  }
  tableData.value.list.forEach((element) => {
    element.showEdit = false;
  });
  let currentData = tableData.value.list[index];
  currentData.showEdit = true;
  //编辑文件
  currentData.filenameReal = currentData.filename;
  editing.value = true;
  nextTick(() => {
    editNameRef.value.focus();
  });
};

const cancelNameEdit = (index) => {
  const fileData = tableData.value.list[index];
  if (fileData.id) {
    fileData.showEdit = false;
  } else {
    tableData.value.list.splice(index, 1);
  }
  editing.value = false;
};


const delFile = (row) => {
  ElMessageBox.confirm(`你确定要删除【${row.filename}】吗？删除的文件可在10天内通过回收站还原`,
  ).then(() => {
    httpRequest.delete("/directory/fileList", {
      params: {
        fileIDs: row.id,
      }
    }).then(({data}) => {
      if (data.code !== 0) throw data.msg
      message.success("删除成功")
      loadDataList();
    }).catch((e) => {
      console.log(e);
      message.error("删除失败")
    })
  });
};
//批量删除
const delFileBatch = () => {
  if (selectFileIdList.value.length === 0) {
    message.error("error!")
    return;
  }
  ElMessageBox.confirm(`你确定要删除这些文件吗？(共${selectFileIdList.value.length}个文件)`,
  ).then(() => {
    httpRequest.delete("/directory/fileList", {
      params: {
        fileIDs: selectFileIdList.value.join(','),
      }
    }).then(({data}) => {
      if (data.code !== 0) throw data.msg
      loadDataList();
    }).catch((e) => {
      console.log(e);
      message.error("删除失败")
    })
  });
};


//移动目录
const folderSelectRef = ref();
const currentMoveFile = ref({});
const moveFolder = (data) => {
  currentMoveFile.value = data;
  folderSelectRef.value.showFolderDialog([data.id]);
};

//批量移动
const moveFolderBatch = () => {
  currentMoveFile.value = {};
  //批量移动如果选择的是文件夹，那么要讲文件夹也过滤
  const excludeFileIdList = [currentFolder.value.id];
  selectFileList.value.forEach((item) => {
    if (item.file_type === 1) {
      excludeFileIdList.push(item.id);
    }
  });
  folderSelectRef.value.showFolderDialog(excludeFileIdList);
};

const moveFolderDone = async (folderId) => {
  if (
      currentMoveFile.value.id === folderId ||
      currentFolder.value.id === folderId
  ) {
    message.warning("文件正在当前目录，无需移动");
    return;
  }
  let filedIdsArray = [];
  if (currentMoveFile.value.id) {
    filedIdsArray.push(currentMoveFile.value.id);
  } else {
    filedIdsArray = filedIdsArray.concat(selectFileIdList.value);
  }
  httpRequest.post("/directory/folderList", {
    newFolderPid: folderId,
    moveFileIDs: filedIdsArray
  }).then(({data}) => {
    if (data.code !== 0) throw data.msg;
    message.success("操作成功");
    folderSelectRef.value.close();
    loadDataList();
  }).catch((e) => {
    message.error("移动失败")
    console.log(e)
  })
};


const showOp = (row) => {
  tableData.value.list.forEach((element) => {
    element.showOp = false;
  });
  row.showOp = true;
};

const cancelShowOp = (row) => {
  row.showOp = false;
};


const previewRef = ref();
const navigationRef = ref();
const preview = (data) => {
  if (data.file_type === 1) {
    navigationRef.value.openFolder(data);
    return;
  }
  if (data.file_status === 1) {
    message.error('文件解析中，无法打开')
    return
  }
  previewRef.value.showPreview(data, 0);
};
//目录
const navChange = (data) => {
  const {curFolder, categoryId} = data;
  currentFolder.value = {fileID: curFolder.id};
  // showLoading.value = true;
  loadDataList();
};

//下载文件
const download = async (row) => {
  httpRequest.get('directory/createDownload/' + row.id).then(({data}) => {
    if (data.code !== 0) throw data.msg
    window.location.href = "/api/directory/download/" + data.data.code;
  }).catch((e) => {
    message.error("获取下载链接错误")
  })
};

const router = useRouter();
const openWithCompare = (row) => {
  console.log('compare,', row)
  router.push({
    path: '/',
    query: {
      id: row.id,
    }
  })
}


</script>

<style lang="scss" scoped>
@use "@/assets/file.list.scss";
</style>
