<template>
  <div>
    <div class="top">
      <div class="top-op">
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
      </div>
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
            <!--          <template-->
            <!--              v-if="(row.fileType == 3 || row.fileType == 1) && row.status == 2"-->
            <!--          >-->
            <!--            <icon :cover="row.fileCover" :width="32"></icon>-->
            <!--          </template>-->
            <!--          <template v-else>-->
            <icon :fileType="row.file_type"></icon>
            <!--          </template>-->
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
            <span class="op">
              <template v-if="row.showOp && row.id">
                <span class="iconfont icon-share1" @click="share(row)"
                >分享</span
                >
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
      </Table>
    </div>
    <FolderSelect
        ref="folderSelectRef"
        @folderSelect="moveFolderDone"
    ></FolderSelect>
  </div>
</template>

<script setup>

import {nextTick, onMounted, ref} from "vue";
import httpRequest from "@/api/httpRequest.ts";
import message from "@/utils/Message.js";
import * as Utils from "@/utils/Utils.ts";
import Icon from "@/components/Icon.vue";
import Table from '@/components/Table.vue'
import {ElMessageBox} from "element-plus";

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

onMounted(() => {
  loadDataList()
})

const loadDataList = () => {
  let params = {
    pageNo: tableData.value.pageNo || 1,
    pageSize: tableData.value.pageSize || 20,
    filePid: currentFolder.value.fileID,
  }
  httpRequest.get("/directory/fileList", {
    params
  }).then(({data}) => {
    console.log(data)
    if (data.code !== 0) {
      throw data.msg
    }
    tableData.value = data.data
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

const moveFolderBatch = () => {
  message.warning("todo")
}
const search = () => {
  message.warning(`todo search ${filenameSearchText.value}`)
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
  console.log(currentData)
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
    console.log(selectFileIdList.value)
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
  message.warning("todo")
  // if (data.folderType == 1) {
  //   openFolder(data);
  // navigationRef.value.openFolder(data);
  // return;
  // }
  // if (data.status != 2) {
  //   proxy.Message.warning("文件正在转码中，无法预览");
  //   return;
  // }
  // previewRef.value.showPreview(data, 0);
};
//目录
const navChange = (data) => {
  message.warning(`todo navChage ${data}`)
  // const {curFolder, categoryId} = data;
  // currentFolder.value = curFolder;
  // showLoading.value = true;
  // category.value = categoryId;
  // loadDataList();
};

//下载文件
const download = async (row) => {
  message.warning("todo download")
  // let result = await proxy.Request({
  //   url: api.createDownloadUrl + "/" + row.fileId,
  // });
  // if (!result) {
  //   return;
  // }
  // window.location.href = api.download + "/" + result.data;
};


</script>

<style lang="scss" scoped>
@import "@/assets/file.list.scss";
</style>
