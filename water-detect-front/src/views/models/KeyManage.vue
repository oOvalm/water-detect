<template>
  <div>
    <el-row :gutter="10">
      <el-col :span="20">
        <el-button type="primary" @click="openCreateDialog">新增</el-button>
        <el-button type="danger" @click="batchDelete">批量删除</el-button>
      </el-col>
      <el-col :span="3">
        <el-popover
            placement="top"
            title="提示信息"
            trigger="hover"
            :width="400"
        >
          <template #reference>
            <el-icon>
              <QuestionFilled/>
            </el-icon>
          </template>
          <div>本系统使用的推流协议为 rtmp 协议</div>
          <div>推流服务器 ip 地址为 <code>8.148.229.47</code>，rtmp 端口为 <code>1935</code></div>
          <div>推流链接为 <code>rtmp://8.148.229.47:1935/live/${唯一标识符}</code></div>
          <div>如果你使用 obs 进行推流，服务器地址为 <code>rtmp://8.148.229.47:1935/live</code>，串流密钥为唯一标识符
          </div>
        </el-popover>
        如何使用推流？
      </el-col>
    </el-row>

    <el-table
        ref="tableRef"
        :data="currentTableData"
        style="width: 100%;"
        :row-key="(row) => row.id"
        @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column prop="stream_name" label="流名称"></el-table-column>
      <el-table-column prop="stream_key" label="流唯一标识"></el-table-column>
      <el-table-column prop="stream_description" label="流描述"></el-table-column>
      <el-table-column prop="create_time" label="创建时间"></el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="mini" @click="openDetailDialog(scope.row)">详情</el-button>
          <el-button size="mini" type="danger" @click="openDeleteConfirm(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
        class="pagination-container"
        v-if="totalCount"
        background
        :total="totalCount"
        :page-sizes="[15, 30, 50, 100]"
        :page-size="pageSize"
        :current-page.sync="pageNo"
        :layout="layout"
        @size-change="handlePageSizeChange"
        @current-change="handlePageNoChange"
    ></el-pagination>
    <el-dialog v-model="createDialogVisible" title="新建数据">
      <el-form :model="formData" label-width="80px">
        <el-form-item label="流名称">
          <el-input v-model="formData.stream_name"></el-input>
        </el-form-item>
        <el-form-item label="流描述">
          <el-input v-model="formData.stream_description"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createData">确定</el-button>
        </span>
      </template>
    </el-dialog>
    <el-dialog v-model="deleteConfirmVisible" title="确认删除">
      <p>是否确认删除该条数据？</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteConfirmVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteRow(deleteRowData)">确定</el-button>
        </span>
      </template>
    </el-dialog>
    <el-dialog v-model="detailDialogVisible" title="详情">
      <el-form :model="detailFormData" label-width="100px">
        <el-form-item label="流名称">
          <el-input v-model="detailFormData.stream_name"></el-input>
        </el-form-item>
        <el-form-item label="流唯一标识">
          <el-input v-model="detailFormData.stream_key" readonly></el-input>
        </el-form-item>
        <el-form-item label="流描述">
          <el-input v-model="detailFormData.stream_description"></el-input>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-input v-model="detailFormData.create_time" readonly></el-input>
        </el-form-item>
        <el-form-item label="观看授权范围">
          <el-radio-group v-model="detailFormData.authType">
            <el-radio :label="3">所有人</el-radio>
            <el-radio :label="2">指定范围</el-radio>
            <el-radio :label="1">仅自己</el-radio>
          </el-radio-group>

        </el-form-item>
        <el-form-item label="">
          <el-select
              v-if="detailFormData.authType === 2"
              v-model="detailFormData.authUsers"
              multiple
              filterable
              default-first-option
              :reserve-keyword="false"
              allow-create
              placeholder="请选择授权的用户邮箱"
          >
            <!--            <el-option-->
            <!--                v-for="name in names"-->
            <!--                :key="name"-->
            <!--                :label="name"-->
            <!--                :value="name"-->
            <!--            >-->
            <!--            </el-option>-->
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveDetailChanges">保存更改</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted} from 'vue';
import {ElTable, ElDialog, ElForm, ElFormItem, ElInput, ElButton, ElPagination, ElMessageBox} from 'element-plus';
import httpRequest from "@/api/httpRequest.ts";
import {QuestionFilled} from '@element-plus/icons-vue';
import {formatDate} from "@/utils/Utils.ts"

// 当前显示的表格数据
const currentTableData = ref([]);
// 分页相关
const totalCount = ref(0);
const pageSize = ref(15);
const pageNo = ref(1);
const layout = ref('total, sizes, prev, pager, next');

// 选中的行数据
const selectedRows = ref([]);

// 创建对话框的显示状态
const createDialogVisible = ref(false);
// 删除确认对话框的显示状态
const deleteConfirmVisible = ref(false);
// 详情对话框的显示状态
const detailDialogVisible = ref(false);

// 新建数据的表单数据
const formData = reactive({
  stream_name: '',
  stream_description: ''
});

// 删除时存储的当前行数据
const deleteRowData = ref(null);

// 详情表单数据
const detailFormData = reactive({
  stream_name: '',
  stream_key: '',
  stream_description: '',
  create_time: '',
  id: null
});

// 获取数据
const fetchData = async () => {
  try {
    const response = await httpRequest.get(`/stream/streamkeyinfo/?page=${pageNo.value}&page_size=${pageSize.value}`);
    const formattedData = response.data.results.map(row => {
      row.create_time = formatDate(row.create_time);
      return row;
    });
    currentTableData.value = formattedData;
    totalCount.value = response.data.count;
  } catch (error) {
    console.error('获取数据失败:', error);
  }
};

// 处理分页每页大小变化
const handlePageSizeChange = (size) => {
  pageSize.value = size;
  handlePageNoChange(1);
};

// 处理分页当前页变化
const handlePageNoChange = async (page) => {
  pageNo.value = page;
  await fetchData();
};

// 处理行选择变化
const handleSelectionChange = (rows) => {
  selectedRows.value = rows;
};

// 打开创建对话框
const openCreateDialog = () => {
  createDialogVisible.value = true;
  formData.stream_name = '';
  formData.stream_description = '';
};

// 新建数据
const createData = async () => {
  try {
    const response = await httpRequest.post("/stream/streamkeyinfo/", {
      stream_name: formData.stream_name,
      stream_description: formData.stream_description,
    });
    ElMessageBox.confirm(`创建成功, 你的流key为: ${response.data.stream_key}`);
    createDialogVisible.value = false;
    await fetchData();
  } catch (error) {
    console.error('创建数据失败:', error);
  }
};

// 打开删除确认对话框
const openDeleteConfirm = (row) => {
  deleteRowData.value = row;
  deleteConfirmVisible.value = true;
};

// 删除单行数据
const deleteRow = async (row) => {
  try {
    await httpRequest.delete(`/stream/streamkeyinfo/${row.id}/`);
    deleteConfirmVisible.value = false;
    await fetchData();
  } catch (error) {
    console.error('删除数据失败:', error);
  }
};

// 打开详情对话框
const openDetailDialog = (row) => {
  detailFormData.stream_name = row.stream_name;
  detailFormData.stream_key = row.stream_key;
  detailFormData.stream_description = row.stream_description;
  detailFormData.create_time = row.create_time;
  detailFormData.id = row.id;
  detailDialogVisible.value = true;
};

// 保存详情更改
const saveDetailChanges = async () => {
  try {
    await httpRequest.put(`/stream/streamkeyinfo/${detailFormData.id}/`, {
      stream_name: detailFormData.stream_name,
      stream_description: detailFormData.stream_description
    });
    detailDialogVisible.value = false;
    await fetchData();
  } catch (error) {
    console.error('更新数据失败:', error);
  }
};

// 批量删除数据
const batchDelete = async () => {
  try {
    const deletePromises = selectedRows.value.map(row => httpRequest.delete(`/stream/streamkeyinfo/${row.id}/`));
    await Promise.all(deletePromises);
    selectedRows.value = [];
    await fetchData();
  } catch (error) {
    console.error('批量删除数据失败:', error);
  }
};

onMounted(async () => {
  await fetchData();
});
</script>

<style scoped>
.pagination-container {
  margin-top: 10px;
  float: right;
}

.code-container {
  position: relative;
}

.code-container button {
  position: absolute;
  right: 0;
  top: 0;
  margin-left: 5px;
}

</style>
